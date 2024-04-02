from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64
#import maintainance

app = Flask(__name__)
app.secret_key = base64.urlsafe_b64encode(os.urandom(64)).decode('utf-8')

user = Blueprint('user', __name__, template_folder='templates/user')
sw = Blueprint('sw', __name__, template_folder='templates/sw')
so = Blueprint('so', __name__, template_folder='templates/so')

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

@app.route('/approve_request')
def approve_request():
    request_id = int(request.args.get('request_id'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET fa_approved = 1 WHERE request_id = ?", (request_id,))
    conn.commit()
    conn.close()
    flash('Request approved successfully!', 'success')
    return render_template('approval_success.html', request_id=request_id)

@app.route('/reject_request')
def reject_request():
    request_id = int(request.args.get('request_id'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM status WHERE request_id = ?",(request_id,))
    cursor.execute("DELETE FROM requests WHERE request_id = ?",(request_id,))
    conn.commit()
    conn.close()
    flash('Request approved successfully!', 'success')
    return render_template('rejection_success.html', request_id=request_id)

def send_email(to_email, request_id, request):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT club_name FROM clubs where club_id=(SELECT club_id FROM requests WHERE request_id = ?);", (request_id, ))
    club_name = cursor.fetchone()[0]
    subject = "Approval Request from {} (Request ID {})".format(club_name, request_id)
    approval_url = url_for('approve_request', request_id=request_id, _external=True)
    rejection_url = url_for('reject_request', request_id=request_id, _external=True)

    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    block = request.form['block']
    room = request.form['room']
    reason = request.form['reason']
    type_of_event = request.form['type_of_event']
    remarks = request.form['remarks']
    body = "Club {} has requested {} room {} on {} from {} to {}.\nReason:- {}\nType of event:- {}\nRemarks:- {}\n\nPlease click the following link to APPROVE the request: {}\nor the following to REJECT the request: {}".format(club_name, block, room, date, start_time, end_time, reason, type_of_event, remarks, approval_url, rejection_url)
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

@app.route('/user/get_dashboard_data')
def get_dashboard_data():
    if 'club_id' not in session:
        return jsonify(message="Authentication required to access dashboard data")
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM status s JOIN requests r ON r.request_id = s.request_id AND club_id = ?", (session['club_id'], ))
    updated_data = cursor.fetchall()
    conn.close()
    return jsonify(updated_data)

@app.route('/get_existing_requests')
def get_existing_requests():
    block = request.args.get('block')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DROP view IF EXISTS v")
    query = f"CREATE VIEW v AS SELECT * FROM status JOIN requests WHERE room_block = '{block}' AND date = '{date}' AND (('{start_time}' BETWEEN start_time AND end_time) OR ('{end_time}' BETWEEN start_time AND end_time) OR (start_time BETWEEN '{start_time}' AND '{end_time}'));"
    cursor.execute(query)
    cursor.execute("SELECT DISTINCT room_no FROM v")
    existing_requests = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(existing_requests)

@app.route('/get_ongoing_slots')
def get_ongoing_slots():
    block = request.args.get('block')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DROP view IF EXISTS w")
    query = f"CREATE VIEW w AS SELECT * FROM slots JOIN requests ON requests.request_id = slots.request_id WHERE room_block = '{block}' AND date = '{date}' AND (('{start_time}' BETWEEN start_time AND end_time) OR ('{end_time}' BETWEEN start_time AND end_time) OR (start_time BETWEEN '{start_time}' AND '{end_time}'));"
    cursor.execute(query)
    cursor.execute("SELECT DISTINCT room_no FROM w")
    ongoing_slots = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(ongoing_slots)

@app.route('/sw_approve')
def sw_approve():
    request_id = int(request.args.get('request_id'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET sw_approved = 1 WHERE request_id = ?",(request_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated successfully'})

@app.route('/so_approve')
def so_approve():
    request_id = int(request.args.get('request_id'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE status SET so_approved = 1 WHERE request_id = ?",(request_id,))
    cursor.execute("INSERT INTO slots values(?, 1)",(request_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated successfully'})

@user.route('/')
def index():
    return render_template('login.html')

@user.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT club_username, club_password, club_id FROM clublogin WHERE club_username = ? AND club_password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = user[0]
        session['club_id'] = user[2]  # Store the club_id in the session
        flash('Login successful!', 'success')
        return redirect(url_for('user.dashboard'))
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('user.index'))

@user.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('user.index'))

    club_id = session['club_id']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT r.request_id, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id WHERE r.club_id = ?", (club_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

@user.route('/submit_request', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        block = request.form['block']
        room = request.form['room']
        reason = request.form['reason']
        type_of_event = request.form['type_of_event']
        remarks = request.form['remarks']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (date, start_time, end_time, room_block, room_no, club_id, reason, type_of_event, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (date, start_time, end_time, block, room, session['club_id'], reason, type_of_event, remarks))
        
        # Retrieve request id
        cursor.execute("SELECT last_insert_rowid()")
        request_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO status VALUES ((SELECT request_id FROM requests ORDER BY request_id DESC LIMIT 1), 0, 0, 0, True)")
        conn.commit()
        cursor.execute("SELECT fa_email FROM clubs WHERE club_id = ?", (session['club_id'],))
        fa_email = cursor.fetchone()[0]
        conn.close()
        
        send_email(fa_email, request_id, request)
        return redirect(url_for('user.dashboard'))

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
    sw_username = request.form['sw_username']
    sw_password = request.form['sw_password']

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT sw_username, sw_password FROM swlogin WHERE sw_username = ? AND sw_password = ?", (sw_username, sw_password))
    user = c.fetchone()
    conn.close()

    if user:
        session['sw_username'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('sw.dashboard'))
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('sw.sw_index'))
    
@sw.route('/dashboard')
def dashboard():
    if 'sw_username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('sw.sw_index'))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT r.request_id, club_name, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id JOIN clubs c ON r.club_id = c.club_id WHERE (fa_approved + sw_approved + so_approved)=1")
    data = cursor.fetchall()
    conn.close()
    return render_template('sw_dashboard.html', data=data)

@sw.route('/logout')
def logout():
    session.pop('sw_username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('sw.sw_index'))

@so.route('/')
def so_index():
    return render_template('so_login.html')

@so.route('/login', methods=['POST'])
def so_login():
    so_username = request.form['so_username']
    so_password = request.form['so_password']

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT so_username, so_password FROM sologin WHERE so_username = ? AND so_password = ?", (so_username, so_password))
    user = c.fetchone()
    conn.close()

    if user:
        session['so_username'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('so.dashboard'))
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('so.so_index'))
    
@so.route('/dashboard')
def dashboard():
    if 'so_username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('so.so_index'))
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT r.request_id, club_name, r.date, r.start_time, r.end_time, r.room_block, r.room_no, r.club_id, r.reason, r.type_of_event, r.remarks, s.fa_approved, s.sw_approved, s.so_approved, s.ongoing FROM requests r LEFT JOIN status s ON r.request_id = s.request_id JOIN clubs c ON r.club_id = c.club_id WHERE (fa_approved + sw_approved + so_approved)=2")
    data = cursor.fetchall()
    conn.close()
    return render_template('so_dashboard.html', data=data)

@so.route('/logout')
def logout():
    session.pop('so_username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('so.so_index'))

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(sw, url_prefix='/sw')
app.register_blueprint(so, url_prefix='/so')

if __name__ == '__main__':
    app.run(debug=True)