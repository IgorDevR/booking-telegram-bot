# seed_data.py

import query

# Sample users
users = [
    ("7588646786", "admin_user"),  # Admin
    ("1001", "alice"),
    ("1002", "bob"),
    ("1003", "charlie")
]

# Insert users
for user_id, username in users:
    query.insert_user(user_id, username)

# Sample services added by admin
services = [
    ("Haircut", "7588646786"),
    ("Massage", "7588646786"),
    ("Dental Checkup", "7588646786")
]

# Insert services and collect their IDs
service_ids = []
for name, admin_id in services:
    sid = query.insert_service(name, admin_id)
    service_ids.append(sid)

# Sample slots for each service
slot_data = {
    service_ids[0]: {
        "2025-09-10": ["10:00", "11:00", "12:00"],
        "2025-09-11": ["09:00", "10:30"]
    },
    service_ids[1]: {
        "2025-09-12": ["14:00", "15:00"],
        "2025-09-13": ["13:00", "14:30"]
    },
    service_ids[2]: {
        "2025-09-14": ["08:00", "09:00"],
        "2025-09-15": ["10:00", "11:00"]
    }
}

# Insert slots
for service_id, dates in slot_data.items():
    for date, times in dates.items():
        query.insert_slots(service_id, date, times)

# Book sample appointments
appointments = [
    ("1001", 1),  # Alice books slot_id 1
    ("1002", 2),  # Bob books slot_id 2
    ("1003", 3)   # Charlie books slot_id 3
]

for user_id, slot_id in appointments:
    query.book_appointment(user_id, slot_id)
    query.update_slot_status(slot_id)

print("✅ Sample data seeded successfully.")
