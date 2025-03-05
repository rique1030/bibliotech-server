# Bibliotech Server

Bibliotech Server is the backend for Bibliotech Manager (a Library Management System) and Bibliotech App (a catalog and book borrowing application). It is designed for use in a school environment to facilitate book management, tracking, and borrowing.

## Features
- Handles book catalog and borrowing system
- Supports real-time communication via Socket.IO
- Uses an asynchronous database connection with SQLAlchemy

## Tech Stack
- **Backend Framework**: Quart
- **Database**: MariaDB
- **Realtime Communication**: Socket.IO
- **ORM**: Async SQLAlchemy

## Installation & Setup
### Prerequisites
- Python 3.x installed
- MariaDB 11.5.2 (or later) installed ([Download](https://mariadb.org/download/))

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/bibliotech-server.git
   cd bibliotech-server
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure the database:
   - Start MariaDB
   - Create a database for Bibliotech Server
   - Set up any required tables (schema details needed)
4. Run the server:
   ```sh
   python main.py
   ```

## Usage
Bibliotech Server provides APIs and WebSocket events for managing the library system. Details on endpoints and events will be added later.

## Deployment
Bibliotech Server can be run locally or hosted using a service that supports Quart and MariaDB. No authentication is implemented.

## License
No license has been chosen yet.

## Future Plans
- Add authentication and authorization
- Improve API documentation
- Implement logging and error handling

## Contributions
This is a personal project, and contributions are not expected at this time.

