import uuid
from sqlalchemy import func, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import BorrowedBook, Copy, Role, User, Catalog
import random
import string
from Components.config import SERVER_EMAIL, SERVER_PASSWORD
import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# KEY = b"1234567890123456" # testing purposes \\ put it in env || should be 16 byte

users = [{
    "id": "4DM1N",
    "profile_pic": "default",
    "first_name": "admin",
    "last_name": "admin",
    "email": "admin@dyci.edu.ph",
    "password": "admin",
    "school_id": "4DM1N",
    "role_id": "ADMIN",
    "is_verified": True,
    "created_at": None,
}]

chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9


class UserQueries(BaseQuery):

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    # ? Insert
    async def insert_users(self, users: list):

        async def operation(session):
            for user in users:
                existing = await session.execute(
                    select(User).where(User.email == user["email"]))
                if existing.scalar_one_or_none():
                    return {
                        "message":
                        f"User with email {user['email']} already exists",
                        "data": None
                    }
                # removing unnecessary fields
                if not user.get("id") == "4DM1N":
                    user.pop("id", None)
                    user["id"] = str(uuid.uuid4())
                user.pop("color", None)
                user.pop("role_name", None)
                profile_pic_buffer = user.pop("profile_pic_buffer", None)
                if profile_pic_buffer:
                    profile_pic = await self.image_helper.convert_to_image(
                        profile_pic_buffer)
                    profile_pic_name = await self.image_helper.save_image(
                        profile_pic, user["id"], self.user_photos_path)
                    user["profile_pic"] = profile_pic_name
                else:
                    user["profile_pic"] = "default"
                if user["id"] != "4DM1N":
                    user["password"] = "BTECH" + ''.join(
                        random.choices(chars, k=6))
                user["password_updated"] = "0000-00-00 00:00:00"
                b = User(**user)
                session.add(b)
                if user["id"] != "4DM1N":
                    await self.send_email(user["email"], user["id"],
                                          user["password"])
                # await self.send_email(user["email"], user["id"])
            return {
                "message": self.generate_user_message(len(users), "added"),
                "data": None
            }

        return await self.execute_query(operation)

    # ? select
    async def paged_users(self, payload: dict):

        async def operation(session):
            user = aliased(User)
            role = aliased(Role)
            query = select(user.id, user.profile_pic, user.first_name,
                           user.last_name, user.email, user.school_id,
                           role.role_name, role.color, user.is_verified,
                           user.created_at).join(role, user.role_id == role.id)
            result = await self.query_helper.get_paged_data(
                session, [user, role], payload, query)
            return {
                "data": {
                    "items": result["data"],
                    "total_count": result["total_count"]
                },
                "message": "Users fetched successfully"
            }

        return await self.execute_query(operation)

    async def fetch_via_id(self, ids: list):

        async def operation(session):
            result = await session.execute(
                select(User).where(User.id.in_(ids)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data, "message": "User fetched successfully"}

        return await self.execute_query(operation)

    async def fetch_via_email_and_password(self, email: str, password: str):

        async def operation(session):
            result = await session.execute(
                select(User).where(User.email == email,
                                   User.password == password))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data, "message": "User fetched successfully"}

        return await self.execute_query(operation)

    async def fetch_via_school_id(self, school_id: str):

        async def operation(session):
            result = await session.execute(
                select(User).where(User.school_id == school_id))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data, "message": "User fetched successfully"}

        return await self.execute_query(operation)

    # ? Update

    async def update_users(self, users: list):

        async def operation(session):
            for user in users:
                # fetch existing data
                existing_user = await session.execute(
                    select(User).where(User.id == user["id"]))
                existing_user = existing_user.scalar_one_or_none()
                if not existing_user:
                    continue

                # remove unecessary fields
                user.pop("color", None)
                user.pop("role_name", None)
                user.pop("profile_pic_blob", None)
                user.pop("created_at", None)
                user.pop("name_updated", None)
                user.pop("password_updated", None)
                user.pop("email_updated", None)

                if "password" in user and user[
                        "password"] != existing_user.password:
                    if user["password"] == "":
                        user.pop("password")
                    else:
                        user["password_updated"] = func.now()
                if ("first_name" in user and user["first_name"] != existing_user.first_name) or \
                    ("last_name" in user and user["last_name"] != existing_user.last_name):
                    user["name_updated"] = func.now()
                if "email" in user and user["email"] != existing_user.email:
                    user["email_updated"] = func.now()

                # save profile pic
                profile_pic_buffer = user.pop("profile_pic_buffer", None)
                if profile_pic_buffer:
                    profile_pic = await self.image_helper.convert_to_image(
                        profile_pic_buffer)
                    profile_pic_name = await self.image_helper.save_image(
                        profile_pic, user["id"], self.user_photos_path)
                    user["profile_pic"] = profile_pic_name

                # update user
                stmt = (update(User).where(User.id == user["id"]).values(
                    **{
                        key: value
                        for key, value in user.items() if key != "id"
                    }))
                await session.execute(stmt)
            return {
                "message": self.generate_user_message(len(users), "updated"),
                "data": None
            }

        return await self.execute_query(operation)

    # ? Delete

    async def delete_users(self, user_ids: list):

        async def operation(session):
            result = await session.execute(User.__table__.delete().where(
                User.id.in_(user_ids)))
            await session.commit()
            return {
                "message": self.generate_user_message(result.rowcount,
                                                      "deleted"),
                "data": None
            }

        return await self.execute_query(operation)

    async def populate_users(self):

        async def operation(session):
            print("Populating users...")
            user_count = await session.execute(select(func.count(User.id)))
            count = user_count.scalar()
            if count == 0:
                await self.insert_users(users)
                return {
                    "data": None,
                    "message": "Users populated successfully"
                }
            return {"data": None, "message": "Users already populated"}

        return await self.execute_query(operation)

    async def get_borrowed_books(self, user_id: str):

        async def operation(session):
            catalog = aliased(Catalog)
            copy = aliased(Copy)
            borrow = aliased(BorrowedBook)
            result = await session.execute(
                select(borrow.id, borrow.copy_id, copy.access_number,
                       copy.status, copy.catalog_id, catalog.call_number,
                       catalog.title, catalog.author, catalog.publisher,
                       catalog.cover_image, catalog.description).join(
                           copy, borrow.copy_id == copy.id).join(
                               catalog, copy.catalog_id == catalog.id).where(
                                   borrow.user_id == user_id))
            result = [dict(row) for row in result.mappings()]
            return {"data": result, "message": "User fetched successfully"}

        return await self.execute_query(operation)

    async def count_all_users(self):

        async def operation(session):
            user_count = await session.execute(select(func.count(User.id)))
            count = user_count.scalar()
            return {
                "data": count,
                "message": "User count fetched successfully"
            }

        return await self.execute_query(operation)

    async def count_user_roles(self):

        async def operation(session):
            role = aliased(Role)
            user = aliased(User)
            role_count = await session.execute(
                select(role.role_name, role.color,
                       func.count(user.id).label("count")).join(
                           user, role.id == user.role_id).group_by(
                               role.role_name, role.color))
            count = [{
                "label": row[0],
                "color": row[1],
                "value": row[2]
            } for row in role_count]
            return {
                "data": count,
                "message": "User count by role fetched successfully"
            }

        return await self.execute_query(operation)

    def generate_user_message(self, user_count, query_type):
        return f"{user_count} User{'' if user_count == 1 else 's'} {query_type} successfully"

    async def send_email(self, to_email: str, id: str, temp_password: str):
        smtp_server = "smtp.postmarkapp.com"
        smtp_port = 587
        sender_email = SERVER_EMAIL or ""
        sender_password = SERVER_PASSWORD or ""

        base_url = "https://9f18c471-dfad-4417-b17a-ebc878c70378-00-48vowcrk1hff.sisko.replit.dev/verify-email?id=" + id  #change

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = "Verify your email - Bibliotech"
        msg["X-PM-Message-Stream"] = "verifyemail"

        body = f"""
        <html>

        <body>
            <H2>Hello,</H2>
            <h4>Please verify your email by clicking the button below:</h4>
            <p><a href="{base_url}" style="
                    	text-decoration: none;
                    	background-color: #5b40e4;
                    	color: #FFFFFF;
                    	padding:5px 50px;
                        border-radius: 5px;
				text-transform: uppercase;
                    	font-weight: bold;
                    	box-sizing: border-box;
                    ">Verify Email</a></p>
            <p style="color: rgba(0,0,0,0.5); font-size: 12px;">If you did not request this, please ignore this email.</p>
            <h3>Your temporary password is: </h3> <code style="background-color: rgba(0,0,0,0.2);
                               padding:5px;
                               border-radius: 5px;">{temp_password}</code>
            <h5>Thank you!</h5>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))
        print(f"Sending email to {to_email}...")

        try:
            smtp = aiosmtplib.SMTP(hostname=smtp_server, port=smtp_port)
            await smtp.connect()
            await smtp.login(sender_password, sender_password)
            await smtp.sendmail(sender_email, to_email, msg.as_string())
            await smtp.quit()
            print(f"✅ Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
