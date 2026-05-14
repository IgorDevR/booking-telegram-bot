import sqlite3
from dotenv import load_dotenv
import os 

load_dotenv()
BOT_DB = os.getenv('BOT_DB')

def connect():
    conn = sqlite3.connect(BOT_DB)
    cursor = conn.cursor()
    return conn , cursor


def insert_user(user_id, username):
    conn ,cursor = connect()

    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

    conn.commit()
    conn.close()

def get_services():
    conn, cursor = connect()

    cursor.execute("SELECT service_id, name FROM services")
    services = cursor.fetchall()

    conn.close()
    return services

def get_dates(service_id):
    conn, cursor  = connect()

    cursor.execute("SELECT DISTINCT date FROM slots WHERE service_id = ?", (service_id,))
    dates = [row[0] for row in cursor.fetchall()]

    conn.close()
    return dates

def get_times(service_id, date):
    conn, cursor  = connect()

    cursor.execute("""
        SELECT slot_id, time FROM slots
        WHERE service_id = ? AND date = ? AND status = 'available'
        ORDER BY time ASC
    """, (service_id, date))
    times = cursor.fetchall()

    conn.close()
    return times

def book_appointment(user_id, slot_id):
    conn, cursor  = connect()

    cursor.execute("INSERT INTO appointments (user_id, slot_id) VALUES (?, ?)", (user_id, slot_id))
    
    conn.commit()
    conn.close()






def get_user_appointments(user_id):
    conn, cursor  = connect()
    cursor.execute("""
        SELECT s.date, s.time, sv.name
        FROM appointments a
        JOIN slots s ON a.slot_id = s.slot_id
        JOIN services sv ON s.service_id = sv.service_id
        WHERE a.user_id = ?
        ORDER BY s.date, s.time
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_admin_appointments(admin_id):
    conn, cursor  = connect()
    cursor.execute("""
        SELECT s.date, s.time, sv.name, u.username
        FROM appointments a
        JOIN slots s ON a.slot_id = s.slot_id
        JOIN services sv ON s.service_id = sv.service_id
        JOIN users u ON a.user_id = u.user_id
        WHERE sv.admin_id = ?
        ORDER BY s.date, s.time
    """, (admin_id,))
    results = cursor.fetchall()
    conn.close()
    return results


def insert_slots(service_id, date, times):
    conn, cursor  = connect()
    
    for t in times:
        cursor.execute("INSERT INTO slots (service_id, date, time, status) VALUES (?, ?, ?, 'available')", (service_id, date, t))

    conn.commit()
    conn.close()

def update_slot_status(slot_id):
    conn, cursor  = connect()
    
    cursor.execute("UPDATE slots SET status = 'booked' WHERE slot_id = ?", (slot_id,))
    
    conn.commit()
    conn.close()

def insert_service(name, admin_id):
    conn, cursor  = connect()
    cursor.execute("INSERT INTO services (name, admin_id) VALUES (?, ?)", (name, admin_id))
    service_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return service_id