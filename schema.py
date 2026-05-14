import sqlite3
from dotenv import load_dotenv
import os 

load_dotenv()
BOT_DB = os.getenv('BOT_DB')

conn = sqlite3.connect(BOT_DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    admin_id TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT DEFAULT 'available'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    slot_id INTEGER
)
""")

conn.commit()
conn.close()
