from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

user = Blueprint('user', __name__, template_folder='templates/user')
sw = Blueprint('sw', __name__, template_folder='templates/sw')
so = Blueprint('so', __name__, template_folder='templates/so')

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('classroom_allotment_system.db')

def is_logged_in():
    return 'club_id' in session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect', methods=['POST'])
def redirect_to_portal():
    portal = request.form['portal']
    if portal == 'user':
        return redirect(url_for('user.index'))
    elif portal == 'sw':
        return redirect(url_for('sw.sw_index'))
    elif portal == 'so':
        return redirect(url_for('so.so_index'))
    else:
        return "Invalid portal selected"

@user.route('/')
def index():
    return render_template('login.html')

@user.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = connect_db()
    c = conn.cursor()

    # Query the database to check if the provided username and password are valid
    c.execute("SELECT club_username, club_password, club_id FROM clublogin WHERE club_username = ? AND club_password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = user[0]
        session['club_id'] = user[2]  # Store the club_id in the session
        flash('Login successful!', 'success')
        return redirect(url_for('user.dashboard'))  # Redirect to the dashboard route of the user blueprint
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('user.index'))  # Redirect to the index route of the user blueprint

@user.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('index'))

    club_id = session['club_id']
     # Connect to the SQLite database
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    # Fetch data from the joined tables requests and status
    cursor.execute("SELECT r.request_id, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id WHERE r.club_id = ?", (club_id,))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    # Pass the fetched data to the HTML template
    return render_template('dashboard.html', data=data)

@app.route('/approve_request/<int:request_id>', methods=['GET'])
def approve_request(request_id):
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET fa_approved = 1 WHERE request_id = ?", (request_id,))
    conn.commit()
    conn.close()
    flash('Request approved successfully!', 'success')
    return redirect(url_for('user.dashboard'))

def send_email(to_email, request_id):
    subject = "Approval Request for Request ID {}".format(request_id)
    print(f"Email: {os.environ.get('CRAS_Email')}")
    print(f"Pass: {os.environ.get('CRAS_App_Password_Google')}")
    root_url = request.host_url
    # Construct the approval URL by appending the route to it
    approval_url = root_url + url_for('approve_request', request_id=request_id, _external=True)

    print(approval_url)

    body = "Please click the following link to approve the request: {}".format(approval_url)
    msg = MIMEMultipart()
    msg['From'] = os.environ.get('CRAS_Email')
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(os.environ.get('CRAS_Email'),os.environ.get('CRAS_App_Password_Google'))
    text = msg.as_string()
    smtp_server.sendmail(os.environ.get('CRAS_Email'), to_email, text)
    smtp_server.quit()
    print(f"Email sent successfully to {to_email} for request {request_id}!")

@user.route('/submit_request', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        # Access form data
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        block = request.form['block']
        room = request.form['room']
        reason = request.form['reason']
        type_of_event = request.form['type_of_event']
        remarks = request.form['remarks']
        print(request.form)

        conn = sqlite3.connect('classroom_allotment_system.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (date, start_time, end_time, room_block, room_no, club_id, reason, type_of_event, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (date, start_time, end_time, block, room, session['club_id'], reason, type_of_event, remarks))
        # Retrieve request id
        cursor.execute("SELECT last_insert_rowid()")
        request_id = cursor.fetchone()[0]
        print(request_id)
        cursor.execute("INSERT INTO status VALUES ((SELECT request_id FROM requests ORDER BY request_id DESC LIMIT 1), 0, 0, 0, True)")
        conn.commit()
        cursor.execute("SELECT fa_email FROM clubs WHERE club_id = ?", (session['club_id'],))
        fa_email = cursor.fetchone()[0]
        print(fa_email)
        conn.close()
        
        # Send approval request email to fa_email
        send_email(fa_email, request_id)
        
        return redirect(url_for('user.dashboard'))

@app.route('/get_existing_requests')
def get_existing_requests():
    block = request.args.get('block')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    room = request.args.get('room')
    
    # Query the database to fetch existing requests for the selected block, room, date, start time, and end time
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT room_no FROM requests WHERE room_block = ? AND room_no = ? AND date = ? AND ((start_time <= ? AND end_time >= ?) OR (start_time <= ? AND end_time >= ?))", 
                   (block, room, date, start_time, start_time, end_time, end_time))
    existing_requests = [row[0] for row in cursor.fetchall()]
    print(date)
    print(existing_requests)
    conn.close()
    return jsonify(existing_requests)

@app.route('/get_ongoing_slots')
def get_ongoing_slots():
    block = request.args.get('block')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    print(request.args)
    # Query the database to fetch ongoing slots for the selected block, room, and date
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT room_no FROM slots JOIN requests ON requests.request_id = slots.request_id WHERE requests.room_block = ? AND requests.date = ? AND requests.start_time <= ? AND requests.end_time >= ?", 
                   (block, date, start_time, end_time))
    ongoing_slots = [row[0] for row in cursor.fetchall()]
    print(date)
    print(ongoing_slots)
    conn.close()
    return jsonify(ongoing_slots)

@user.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('user.index'))

@sw.route('/')
def sw_index():
    return render_template('sw_login.html')

@sw.route('/login', methods=['POST'])
def sw_login():
    username = request.form['username']
    password = request.form['password']

    conn = connect_db()
    c = conn.cursor()

    # Query the database to check if the provided username and password are valid
    c.execute("SELECT sw_username, sw_password FROM swlogin WHERE sw_username = ? AND sw_password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('sw.dashboard'))  # Redirect to the dashboard route of the sw blueprint
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('sw.sw_index'))
    
@sw.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('sw.sw_index'))

    club_id = session['club_id']
     # Connect to the SQLite database
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    # Fetch data from the joined tables requests and status
    cursor.execute("SELECT r.request_id, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id WHERE (fa_approved + sw_approved + so_approved)=1")
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    # Pass the fetched data to the HTML template
    return render_template('sw_dashboard.html', data=data)

@app.route('/sw_approve')
def sw_approve():
    request_id = int(request.args.get('request_id'))
    print(request_id)
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET sw_approved = 1 WHERE request_id = ?",(request_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated successfully'})

@app.route('/so_approve')
def so_approve():
    request_id = int(request.args.get('request_id'))
    print(request_id)
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET so_approved = 1 WHERE request_id = ?",(request_id,))
    cursor.execute("INSERT INTO slots values(?, 1)",(request_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated successfully'})
    
@so.route('/')
def so_index():
    return render_template('so_login.html')

@so.route('/login', methods=['POST'])
def so_login():
    username = request.form['username']
    password = request.form['password']

    conn = connect_db()
    c = conn.cursor()

    # Query the database to check if the provided username and password are valid
    c.execute("SELECT so_username, so_password FROM sologin WHERE so_username = ? AND so_password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('so.dashboard'))  # Redirect to the dashboard route of the so blueprint
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('so.so_index'))
    
@so.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('so.so_index'))

    club_id = session['club_id']
     # Connect to the SQLite database
    conn = sqlite3.connect('classroom_allotment_system.db')
    cursor = conn.cursor()
    # Fetch data from the joined tables requests and status
    cursor.execute("SELECT r.request_id, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id WHERE (fa_approved + sw_approved + so_approved)=2")
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    # Pass the fetched data to the HTML template
    return render_template('so_dashboard.html', data=data)

@sw.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('sw.sw_index'))

@so.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('so.so_index'))

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(sw, url_prefix='/sw')
app.register_blueprint(so, url_prefix='/so')

if __name__ == '__main__':
    app.run(debug=True)