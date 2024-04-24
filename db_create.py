import sqlite3

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('classroom_allotment_system.db')

# Function to create database tables
def create_tables():
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('DROP TABLE IF EXISTS clubs_new;')
    c.execute('DROP TABLE IF EXISTS clublogin_new;')
    c.execute('DROP TABLE IF EXISTS swlogin_new;')
    c.execute('DROP TABLE IF EXISTS sologin_new;')
    c.execute('DROP TABLE IF EXISTS rooms_new;')
    c.execute('DROP TABLE IF EXISTS requests_new;')
    c.execute('DROP TABLE IF EXISTS status_new;')
    c.execute('DROP TABLE IF EXISTS slots_new;')

    # Create clubs table
    c.execute('''CREATE TABLE IF NOT EXISTS clubs_new (
        club_id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        club_name VARCHAR(50),
        fa_name VARCHAR(50),
        fa_email VARCHAR(50),
        club_email VARCHAR(50)
    )''')

    # Create clublogin table
    c.execute('''CREATE TABLE IF NOT EXISTS clublogin_new (
        club_id INTEGER,
        club_username VARCHAR(50) NOT NULL UNIQUE,
        club_password VARCHAR(50) NOT NULL,
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    )''')

    # Create rooms table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms_new (
        room_block VARCHAR(10),
        room_no VARCHAR(10),
        capacity INTEGER,
        PRIMARY KEY (room_block, room_no)
    )''')

    # Create swlogin table
    c.execute('''CREATE TABLE IF NOT EXISTS swlogin_new (
        sw_username VARCHAR(50) PRIMARY KEY NOT NULL UNIQUE,
        sw_password VARCHAR(50) NOT NULL
    )''')

    # Create sologin table
    c.execute('''CREATE TABLE IF NOT EXISTS sologin_new (
        so_username VARCHAR(50) PRIMARY KEY NOT NULL UNIQUE,
        so_password VARCHAR(50)
    )''')

    # Create requests table
    c.execute('''CREATE TABLE IF NOT EXISTS requests_new (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
        date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        room_block VARCHAR(10) NOT NULL,
        room_no VARCHAR(10) NOT NULL,
        club_id INTEGER NOT NULL,
        reason VARCHAR(100),
        type_of_event VARCHAR(100),
        remarks VARCHAR(1000),
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    )''')

    # Create status table
    c.execute('''CREATE TABLE IF NOT EXISTS status_new (
        request_id INTEGER NOT NULL UNIQUE,
        fa_approved INTEGER,
        sw_approved INTEGER,
        so_approved INTEGER,
        ongoing BOOLEAN,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
    )''')

    # Create slots table
    c.execute('''CREATE TABLE IF NOT EXISTS slots_new (
        request_id INTEGER NOT NULL UNIQUE,
        booked BOOLEAN,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
    )''')

    c.execute('ALTER TABLE clubs_new RENAME TO clubs;')
    c.execute('ALTER TABLE clublogin_new RENAME TO clublogin;')
    c.execute('ALTER TABLE swlogin_new RENAME TO swlogin;')
    c.execute('ALTER TABLE sologin_new RENAME TO sologin;')
    c.execute('ALTER TABLE rooms_new RENAME TO rooms;')
    c.execute('ALTER TABLE requests_new RENAME TO requests;')
    c.execute('ALTER TABLE status_new RENAME TO status;')
    c.execute('ALTER TABLE slots_new RENAME TO slots;')

    c.execute('''CREATE TABLE IF NOT EXISTS deleted_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
        date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        room_block VARCHAR(10) NOT NULL,
        room_no VARCHAR(10) NOT NULL,
        club_id INTEGER NOT NULL,
        reason VARCHAR(100),
        type_of_event VARCHAR(100),
        remarks VARCHAR(1000),
        FOREIGN KEY (club_id) REFERENCES clubs(club_id)
    )''')

    c.execute('''CREATE TRIGGER IF NOT EXISTS t1
        AFTER DELETE ON requests
        FOR EACH ROW
        BEGIN
        INSERT INTO deleted_requests 
        VALUES (
        OLD.request_id,
        OLD.date,
        OLD.start_time,
        OLD.end_time,
        OLD.room_block,
        OLD.room_no,
        OLD.club_id,
        OLD.reason,
        OLD.type_of_event,
        OLD.remarks
        );
        END;
    ''')

    conn.commit()
    conn.close()

# Call the function to create tables
create_tables()