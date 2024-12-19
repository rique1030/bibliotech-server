class ACCOUNT_HANDLER_QUERIES:
    INSERT_ACCOUNT = "INSERT INTO accounts (username, password, email, user_type_id) VALUES (%s, %s, %s, %s)"
    INSERT_ACCOUNT_TYPE = "INSERT INTO user_type (user_type, account, books, categories, usertypes) VALUES (%s , %s, %s, %s, %s)"
    SELECT_ACCOUNTS = """
    SELECT 
        accounts.id,
        accounts.username,
        accounts.password,
        accounts.email,
        user_type.user_type
    FROM 
        accounts
    LEFT JOIN 
        user_type 
    ON 
        accounts.user_type_id = user_type.user_type_id
    {search_filter}
    LIMIT %s OFFSET %s;
    """
    COUNT_ACCOUNTS = "SELECT COUNT(*) FROM accounts {search_filter}"
    SELECT_ACCOUNT_BY_ID = "SELECT * FROM accounts WHERE id IN ({placeholders})"
    SELECT_ACCOUNT_TYPES_BY_ID = "SELECT * FROM user_type WHERE user_type_id IN ({placeholders})"
    SELECT_ACCOUNTS_BY_USERNAME = "SELECT * FROM accounts WHERE username = %s"
    SELECT_ACCOUNTS_BY_EMAIL = "SELECT * FROM accounts WHERE email = %s"
    SELECT_ACCOUNTS_BY_USERNAME_AND_PASSWORD = "SELECT * FROM accounts WHERE username = %s AND password = %s"
    UPDATE_ACCOUNTS = "UPDATE accounts SET username = %s, password = %s, email = %s, user_type_id = %s WHERE id = %s"
    UPDATE_ACCOUNT_PASSWORD = "UPDATE accounts SET password = %s WHERE username = %s"
    DELETE_ACCOUNT = "DELETE FROM accounts WHERE id = %s"

    FETCH_USER_TYPES = "SELECT * FROM user_type {search_filter} LIMIT %s OFFSET %s;"
    INSERT_USER_TYPE = "INSERT INTO user_type (user_type) VALUES (%s)"
    SELECT_ACCOUNT_TYPES = "SELECT * FROM user_type"
    UPDATE_USER_TYPES = "UPDATE user_type SET user_type = %s, account = %s, books = %s, categories = %s, usertypes = %s WHERE user_type_id = %s"
    # DELETE_ACCOUNT_TYPE = "DELETE FROM user_type WHERE user_type_id = %s"
    DELETE_ACCOUNT_TYPE = "DELETE FROM user_type WHERE user_type_id IN ({placeholders})"

class BOOK_HANDLER_QUERIES:
    SELECT_BOOKS = "SELECT * FROM books {search_filter} LIMIT %s OFFSET %s"
    SELECT_BOOKS_BY_TITLE = "SELECT * FROM books WHERE title LIKE %s"
    SELECT_BOOKS_BY_AUTHOR = "SELECT * FROM books WHERE author LIKE %s"
    SELECT_BOOKS_BY_ACC_NUM = "SELECT * FROM books WHERE access_number LIKE %s"
    SELECT_BOOK_BY_ID = "SELECT * FROM books WHERE id IN ({placeholders})"
    SELECT_QR_CODE_NAME = "SELECT qr_code_path FROM books WHERE id IN ({placeholders})"
    REQUEST_BOOK = "SELECT id FROM books WHERE access_number = %s AND call_number = %s"

    INSERT_BOOK = "INSERT INTO books (access_number, call_number, title, author, qr_code_path) VALUES (%s, %s, %s, %s, %s)"
    UPDATE_BOOK_STATUS = "UPDATE books SET access_number = %s, call_number = %s, title = %s, author = %s, qr_code_path = %s,  status = %s WHERE id = %s"
    DELETE_BOOK = "DELETE FROM books WHERE id IN ({placeholders})"
    COUNT_BOOKS = "SELECT COUNT(*) FROM books {search_filter}" 

    INSERT_CATEGORY = "INSERT INTO categories (name) VALUES (%s)"
    FETCH_CATEGORIES = "SELECT * FROM categories {search_filter} LIMIT %s OFFSET %s"
    SELECT_CATEGORIES = "SELECT * FROM categories"
    SELECT_CATEGORY_BY_ID = "SELECT * FROM categories WHERE id IN ({placeholders})"
    UPDATE_CATEGORIES = "UPDATE categories SET name = %s WHERE id = %s"
    DELETE_CATEGORY = "DELETE FROM categories WHERE id IN ({placeholders})"

    INSERT_JOINT_CATEGORY = "INSERT INTO books_categories (book_id, category_id) VALUES (%s, %s)"
    DELETE_JOINT_CATEGORY = "DELETE FROM books_categories WHERE book_id = %s AND category_id = %s"
    SELECT_JOINT_CATEGORY_BY_ID = "SELECT * FROM books_categories WHERE book_id in ({placeholders})"
    SELECT_JOINT_CATEGORY = """
    SELECT categories.name 
    FROM categories
    JOIN books_categories ON categories.id = books_categories.category_id
    JOIN books ON books.id = books_categories.book_id
    WHERE books.id = %s
    """
    DELETE_JOINT_CATEGORY_BY_BOOK_ID = "DELETE FROM books_categories WHERE book_id in ({placeholders})"
    INSERT_BORROWED_BOOK = """
    INSERT INTO borrowed_books (book_id, username, borrowed_date, due_date, status)
    VALUES (?, ?, NOW(), DATE_ADD(NOW(), INTERVAL ? DAY), 'borrowed');
    """

class DATABASE_QUERIES:
    CREATE_DATABASE = """
    CREATE DATABASE IF NOT EXISTS {db_name} 
    DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """

    CREATE_USER_TYPE_TABLE = """
    CREATE TABLE IF NOT EXISTS user_type (
        user_type_id INT AUTO_INCREMENT PRIMARY KEY,
        user_type VARCHAR(50) NOT NULL UNIQUE,
        account BOOLEAN DEFAULT 0,
        books BOOLEAN DEFAULT 0,
        categories BOOLEAN DEFAULT 0,
        usertypes BOOLEAN DEFAULT 0
    );
    """


    CREATE_ACCOUNTS_TABLE = """
    CREATE TABLE IF NOT EXISTS accounts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        user_type_id INT DEFAULT 2,
        FOREIGN KEY (user_type_id) REFERENCES user_type(user_type_id) ON DELETE CASCADE
    );
    """ 

    CREATE_BOOKS_TABLE = """
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        access_number VARCHAR(50) NOT NULL UNIQUE,
        call_number VARCHAR(50) NOT NULL,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255) NOT NULL,
        qr_code_path VARCHAR(255) DEFAULT NULL,
        status ENUM('available', 'borrowed') DEFAULT 'available'
    );
    """
    CREATE_CATEGORIES_TABLE = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    );
    """

    CREATE_BOOK_CATEGORIES_TABLE = """
    CREATE TABLE IF NOT EXISTS books_categories (
        book_id INT NOT NULL,
        category_id INT NOT NULL,
        PRIMARY KEY (book_id, category_id),
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    );
    """

    CREATE_BORROWED_BOOKS_TABLE = """
    CREATE TABLE IF NOT EXISTS borrowed_books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_id INT NOT NULL,
        username VARCHAR(50) NOT NULL,
        borrowed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        due_date DATE,
        status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
    );
    """


class RECORD_QUERIES:
    SELECT_COPIES_AVAILABLE = "SELECT title, author, COUNT(*) AS copy_count FROM books  {search_filter}  GROUP BY title, author LIMIT %s OFFSET %s;"

    SELECT_BORROWED_RECORDS = """
    select * from borrowed_books {search_filter} LIMIT %s OFFSET %s;
    """

    SELECT_USER_RECORDS = """
    SELECT 
        a.username,
        ut.user_type AS role,
        a.email,
        GROUP_CONCAT(bk.title) AS borrowed_books
    FROM 
        accounts a
    JOIN 
        user_type ut ON a.user_type_id = ut.user_type_id
    LEFT JOIN 
        borrowed_books b ON a.username = b.username
    LEFT JOIN 
        books bk ON b.book_id = bk.id
    GROUP BY 
        a.username, ut.user_type, a.email
    LIMIT %s OFFSET %s;
    """

    SELECT_CATEGORY_RECORDS = SELECT_CATEGORY_RECORDS = """
    SELECT 
        c.name AS category,
        COUNT(b.id) AS books_available
    FROM 
        categories c
    LEFT JOIN 
        books_categories bc ON c.id = bc.category_id
    LEFT JOIN 
        books b ON bc.book_id = b.id AND b.status = 'available'
    GROUP BY 
        c.id, c.name
    LIMIT %s OFFSET %s;
    """
