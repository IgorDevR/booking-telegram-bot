import sqlite3
from dotenv import load_dotenv
import os 

load_dotenv()
BOT_DB = os.getenv('BOT_DB')

conn = sqlite3.connect(BOT_DB)
cursor = conn.cursor()

# Add sample services
cursor.execute("INSERT OR IGNORE INTO services (service_id, name, admin_id) VALUES (1, 'Haircut', '7588646786')")
cursor.execute("INSERT OR IGNORE INTO services (service_id, name, admin_id) VALUES (2, 'Massage', '7588646786')")

# Add sample slots
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (1, 1, '2025-12-20', '10:00', 'available')")
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (2, 1, '2025-12-20', '11:00', 'available')")
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (3, 1, '2025-12-20', '14:00', 'available')")
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (4, 2, '2025-12-21', '09:00', 'available')")
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (5, 2, '2025-12-21', '10:00', 'available')")
cursor.execute("INSERT OR IGNORE INTO slots (slot_id, service_id, date, time, status) VALUES (6, 2, '2025-12-21', '11:00', 'available')")

conn.commit()
conn.close()
print("✅ Seed data inserted!")
