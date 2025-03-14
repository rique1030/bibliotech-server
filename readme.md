# BiblioTech Server 📡  

![GitHub release](https://img.shields.io/github/v/release/riquelicious/BiblioTechServer?style=flat-square)  
![GitHub issues](https://img.shields.io/github/issues/riquelicious/BiblioTechServer?style=flat-square)  
![GitHub last commit](https://img.shields.io/github/last-commit/riquelicious/BiblioTechServer?style=flat-square)  

BiblioTech Server is the **backend** for **BiblioTech Manager** (a desktop library management system) and **BiblioTech Mobile** (a book catalog and borrowing app). It provides an API and real-time communication to handle book transactions and user roles.  

## 📌 Features  
- 📚 **Book Catalog & Copy Management** – Stores library data  
- 🔄 **Borrow & Return System** – Processes book transactions  
- 📡 **Real-time Updates** – Uses WebSockets (Socket.IO) for instant updates  
- ⚡ **Asynchronous Performance** – Fast & non-blocking backend (Quart + async SQLAlchemy)  
- 💾 **MariaDB Support** – Uses MySQL-compatible database  

## 🛠 Tech Stack  
- **Backend Framework**: Quart (async Flask alternative)  
- **Database**: MariaDB  
- **Realtime Communication**: Socket.IO  
- **ORM**: Async SQLAlchemy  

## 📥 Installation & Setup  
### Prerequisites  
- **Python 3.x** installed  
- **MariaDB 11.5.2+** ([Download](https://mariadb.org/download/))  

### Steps  
1. Clone the repository:  
   ```
   git clone https://github.com/riquelicious/BiblioTechServer.git  
   cd BiblioTechServer  
   ```

2. Install dependencies:  
   ```
   pip install -r requirements.txt
   ```

4. Configure the database:  
   - Start MariaDB  
   - Create a database for BiblioTech Server  
   - Set up tables (schema details needed)  

5. Run the server:  
   python main.py  

## 🚀 Usage  
BiblioTech Server handles API requests and WebSocket events for managing the library system.  

## 🤝 Contributions  
This is a personal project, and contributions are not expected at this time.  

## 📄 License  
No license has been chosen yet.  
