import sqlite3
import time
from datetime import datetime
import threading

def maintainance():
    while True:
        print("Maintainance!")
        current_date = datetime.today().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        conn = sqlite3.connect('classroom_allotment_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM status WHERE EXISTS (SELECT 1 FROM requests WHERE requests.request_id = status.request_id AND ((requests.date = ? AND requests.end_time <= ?) OR (requests.date < ?)));", (current_date, current_time, current_date))
        cursor.execute("DELETE FROM slots WHERE EXISTS (SELECT 1 FROM requests WHERE requests.request_id = slots.request_id AND ((requests.date = ? AND requests.end_time <= ?) OR (requests.date < ?)));", (current_date, current_time, current_date))
        cursor.execute("DELETE FROM requests WHERE ((requests.date = ? AND requests.end_time <= ?) OR (requests.date < ?));", (current_date, current_time, current_date, ))
        cursor.close()
        conn.commit()
        time.sleep(86400) #daily deletion

maintainance_thread = threading.Thread(target=maintainance)
maintainance_thread.start()