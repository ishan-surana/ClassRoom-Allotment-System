import sqlite3

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('classroom_allotment_system.db')

# Function to create database tables
def create_tables():
    conn = connect_db()
    c = conn.cursor()

    # Create clubs table
    c.execute('''CREATE TABLE IF NOT EXISTS clubs (
        club_id INTEGER PRIMARY KEY,
        club_name VARCHAR(50),
        fa_name VARCHAR(50),
        fa_email VARCHAR(50),
        club_email VARCHAR(50)
    )''')

    # Create clublogin table
    c.execute('''CREATE TABLE IF NOT EXISTS clublogin (
        club_id INTEGER,
        club_username VARCHAR(50),
        club_password VARCHAR(50),
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    )''')

    # Create rooms table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
        room_block VARCHAR(10),
        room_no VARCHAR(10),
        capacity INTEGER,
        PRIMARY KEY (room_block, room_no)
    )''')

    # Create swlogin table
    c.execute('''CREATE TABLE IF NOT EXISTS swlogin (
        sw_username VARCHAR(50) PRIMARY KEY,
        sw_password VARCHAR(50)
    )''')

    # Create sologin table
    c.execute('''CREATE TABLE IF NOT EXISTS sologin (
        so_username VARCHAR(50) PRIMARY KEY,
        so_password VARCHAR(50)
    )''')

    # Create requests table
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        start_time TIME,
        end_time TIME,
        room_block VARCHAR(10),
        room_no VARCHAR(10),
        club_id INTEGER,
        reason VARCHAR(100),
        type_of_event VARCHAR(100),
        remarks VARCHAR(1000),
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    )''')

    # Create status table
    c.execute('''CREATE TABLE IF NOT EXISTS status (
        request_id INTEGER,
        fa_approved INTEGER,
        sw_approved INTEGER,
        so_approved INTEGER,
        ongoing BOOLEAN,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
    )''')

    # Create slots table
    c.execute('''CREATE TABLE IF NOT EXISTS slots (
        request_id INTEGER,
        booked BOOLEAN,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
    )''')

    conn.commit()
    conn.close()

# Call the function to create tables
create_tables()