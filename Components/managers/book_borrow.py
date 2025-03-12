import asyncio
import json
from tqdm.asyncio import tqdm
from quart import request
from tabulate import tabulate
import logging
from Components.config import REQUEST_TIMEOUT, REVIEW_TIMEOUT
from Components.db import Database
from Components.queries.book_borrow import BorrowedBookQueries

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BookBorrowManager:
    def __init__(self, socket, db: Database):
        self.socket = socket
        self.book_query = None
        self.user_query = None
        self.book_borrow = BorrowedBookQueries(db.Session)
        self.available_clients = {}
        self.unauthenticated_connections = set()
        self.requests = {}

        self.socket.on('request', self.handle_request)
        self.socket.on('review_request', self.handle_review_request)
        self.socket.on('request_response', self.handle_request_response)

    def set_queries(self, book_manager, user_manager):
        self.book_query = book_manager.copy
        self.user_query = user_manager.user_queries
        assert self.book_query and self.user_query

    async def emit_response(self, event, message, room):
        """Emit response to client"""
        await self.socket.emit(event, message, room=room, namespace='/')

    async def parse_request(self, data):
        """Parse incoming request data"""
        return json.loads(data) if isinstance(data, str) else data

    async def verify_request(self, data):
        """Verify request data and returns (status, request_id)"""
        if not data or not data.get("request_id"):
            return False, None
        return True, data.get("request_id")

    async def handle_request(self, sid, data):
        data = await self.parse_request(data)
        if not data:
            await self.emit_response('request_denied', "Invalid request", room=sid)
            return
        if await self.is_request_ongoing(sid):
            return
        if not await self.is_client_available(data.get("receiver_id"), sid):
            return

        book_id, user_id = data.get('book_id'), data.get('user_id')
        book = await self.book_query.fetch_via_id([book_id])
        user = await self.user_query.fetch_via_id([user_id])

        if not book or "data" not in book or len(book.get("data")) == 0:
            await self.emit_response('request_denied', "Scanned book does not exist.", room=sid)
            return
        if not user or "data" not in user or len(user.get("data")) == 0:
            await self.emit_response('request_denied', "User does not exist.", room=sid)
            return

        book, user = book.get("data")[0], user.get("data")[0]
        current_request = {
            "request_id": sid,
            "request": {
                "request_id": sid,
                "accepted": False,
                "receiver_id": data.get("receiver_id"),
                "borrow": data.get("borrow", True),
                "book": {key: book[key] for key in ['id', 'title', 'author', 'publisher', 'access_number', 'call_number', 'cover_image']},
                "user": {key: user[key] for key in ['id', 'profile_pic', 'first_name', 'last_name', 'email', 'school_id', 'role_id', 'is_verified']}
            }
        }
        logging.info(f"\nprocessing request: {sid}")
        self.print_json(current_request.get("request"))
        print("\n")
        self.requests[sid] = current_request

        await self.process_request(current_request["request"])

    async def is_request_ongoing(self, request_id, is_review=False):
        if request_id in self.requests:
            if is_review:
                return True
            await self.emit_response('request_denied', "Your request is already on-going", room=request_id)
            return True
        return False

    async def process_request(self, request):
        """Handles borrower verification and client availability"""
        if not await self.is_borrower_verified(request):
            return
        logging.info(f"Processing request {request['request_id']}")
        if await self.is_client_available(request.get("receiver_id"), request.get("request_id")):
            await self.send_client_request(request["receiver_id"], request["request_id"], request)
        else:
            logging.info("Client not available")

    async def is_borrower_verified(self, request):
        logging.info(f"Verifying borrower {request['user']['first_name']} {request['user']['last_name']}")
        if not request["user"].get("is_verified"):
            await self.emit_response('request_denied', "User is not currently verified", room=request["request_id"])
            self.requests.pop(request["request_id"])
            return False
        return True

    async def is_client_available(self, client_id, request_id):
        client = self.available_clients.get(client_id)
        logging.info(f"Checking availability for client {client_id}")
        if not client:
            await self.emit_response('request_denied', "Client is currently unavailble.", room=request_id)
            self.requests.pop(request_id, None)
            return False
        if client.get("busy"):
            await self.emit_response('request_denied', "Client is currently busy", room=request_id)
            self.requests.pop(request_id, None)
            return False
        return True

    async def send_client_request(self, client_id, requester_id, data):
        self.available_clients[client_id]["busy"] = True
        await self.emit_response('request_borrow', data, room=client_id)
        asyncio.get_running_loop().create_task(self.start_timeouts(requester_id))
        logging.info(f"Request sent to client: {client_id} (Request ID: {requester_id})")

    """HANDLE REQUESTS"""

    async def handle_review_request(self, sid, data):
        if not sid in self.available_clients:
            await self.emit_response('request_denied', "You are currently not logged in. Please login first.", room=sid)
            return
        data = await self.parse_request(data)
        if not data or not await self.is_request_ongoing(data.get("request_id"), True):
            logging.info("Request not found")
            return
        if not data.get("request_id") in self.requests:
            await self.emit_response('request_denied', "Request not found", 
            room=sid)
            return
        self.requests[data.get("request_id")]["accepted"] = True


    async def handle_request_response(self, sid, data):
        available, request_id = await self.verify_request(data)
        if not available:
            await self.emit_response('request_denied', "Request not found", room=sid)
            await self.emit_response('client_message', "Request has expired. You only have 30 seconds to respond to a request", room=sid)
            return
        if not request_id in self.requests:
            await self.emit_response('request_denied', "Request not found", room=sid)
            await self.emit_response('client_message', "Request has expired. You only have 30 seconds to respond to a request", room=sid)
            return
        requests = self.requests.pop(request_id, None)
        
        if not requests.get("accepted", False):
            self.requests[request_id] = requests
            await self.emit_response('request_denied', "Request not found", room=sid)
            return
        request = requests.get("request")
        await asyncio.sleep(1)
        if not data["approved"]:
            await self.emit_response('request_denied', "Request denied", room=data["request_id"])
            await self.emit_response('client_message', "Request has been denied", room=request.get("receiver_id"))
            logging.info("Request denied")
        else:
            borrow = data.get("borrow", True)
            days = data.get("num_days", 1)
            result = None
            logging.info("Request approved")
            if borrow:
                result = await self.book_borrow.insert_borrow(request.get("book"), request.get("user"), days)
            else:
                result = await self.book_borrow.delete_borrow(request.get("book"), request.get("user"))
            if result.get("success", False) is False:
                await self.emit_response('request_denied', "Request denied", room=data["request_id"])
                await self.emit_response('client_message', "Request has been denied by the server", room=request.get("receiver_id"))
                return
            await self.emit_response('request_approved', "Request approved", room=data["request_id"])
            await self.emit_response('client_message', "Request has been approved", room=request.get("receiver_id"))
        # self.requests.pop(request_id, None)            
        

    """TIMEOUTS"""

    async def start_timeouts(self, request_id):
        receiver_id = self.requests[request_id]["request"].get("receiver_id")
        try:
            if await self.request_timeout(request_id):
                await self.review_timeout(request_id)
        except TimeoutError:
            logging.info("Request timed out")
            await self.emit_response('request_timed_out', "Request timed out", room=request_id)
            self.requests.pop(request_id, None)
        finally:
            self.available_clients[receiver_id]["busy"] = False

    async def request_timeout(self, request_id) -> bool:
        with tqdm(
                total=REQUEST_TIMEOUT, 
                desc=f"Request {request_id}", 
                bar_format="{desc}|{bar}| {n}s left", 
                initial=REQUEST_TIMEOUT, position=0, 
                ascii="░▒▓█"
            ) as pbar:
                while pbar.n > 0:
                    if self.requests.get(request_id, {}).get("accepted"):
                            pbar.close()
                            logging.info("Request accepted")
                            return True
                    await asyncio.sleep(1)
                    pbar.n -=1
                    pbar.refresh()
        raise TimeoutError


    async def review_timeout(self, request_id):
        if not request_id in self.requests:
            logging.info("Request not found")
            self.emit_response('request_denied', "Request not found", room=request_id)
            return
        with tqdm(
                total=REVIEW_TIMEOUT, 
                desc=f"Request {request_id}", 
                bar_format="{desc}|{bar}| {n}s left", 
                initial=REVIEW_TIMEOUT, position=0, 
                ascii="░▒▓█"
            ) as pbar:
                while pbar.n > 0:
                    if not request_id in self.requests:
                        pbar.close()
                        logging.info("Request Reviewed")
                        return True
                    await asyncio.sleep(1)
                    pbar.n -=1
                    pbar.refresh()
        raise TimeoutError       
        

    def print_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        if isinstance(data, dict):
            data = [{"key": key, "value": json.dumps(value, indent=2)} for key, value in data.items()]
            print(tabulate(data, headers="keys", tablefmt="psql"))


