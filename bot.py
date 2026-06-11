from telebot import TeleBot, types
import query
import os 
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = TeleBot(token)


user_state = {}

ADMINS = []
ADMIN_IDS_ENV = os.getenv('ADMIN_IDS', '')
if ADMIN_IDS_ENV:
    ADMINS = [a.strip() for a in ADMIN_IDS_ENV.split(',') if a.strip()]

if not ADMINS:
    ADMINS = ['7588646786']  # fallback

# Handle Start 
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "no_username"
    query.insert_user(user_id, username)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📅 Book Appointment", "📋 My Appointments")
    if user_id in ADMINS:
        markup.row("➕ Add Service", "⏳ Pending Bookings")
    bot.send_message(
        message.chat.id, 
        "👋 Welcome! Choose an option:\n\n"
        "• 📅 Book Appointment — book a time slot\n"
        "• 📋 My Appointments — view your bookings",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📅 Book Appointment")
def show_services(message):
    services = query.get_services()
    if not services:
        bot.send_message(message.chat.id, "❌ No services available yet.")
        return
    markup = types.InlineKeyboardMarkup()
    for sid, name in services:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"service_{sid}"))
    bot.send_message(message.chat.id, "Choose a service:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("service_"))
def choose_date(call):
    service_id = int(call.data.split("_")[1])
    user_state[call.from_user.id] = {"service_id": service_id}
    dates = query.get_dates(service_id)
    if not dates:
        bot.send_message(call.message.chat.id, "❌ No dates available for this service.")
        return
    markup = types.InlineKeyboardMarkup()
    for d in dates:
        markup.add(types.InlineKeyboardButton(d, callback_data=f"date_{d}"))
    bot.send_message(call.message.chat.id, "Choose a date:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("date_"))
def choose_time(call):
    date = call.data.split("_")[1]
    user_state[call.from_user.id]["date"] = date
    service_id = user_state[call.from_user.id]["service_id"]
    times = query.get_times(service_id, date)
    if not times:
        bot.send_message(call.message.chat.id, "❌ No available slots for this date.")
        return
    markup = types.InlineKeyboardMarkup()
    for slot_id, time in times:
        markup.add(types.InlineKeyboardButton(time, callback_data=f"time_{slot_id}"))
    bot.send_message(call.message.chat.id, "Choose a time:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def confirm_booking(call):
    slot_id = int(call.data.split("_")[1])
    user_id = str(call.from_user.id)
    username = call.from_user.username or "no_username"
    
    # Create pending booking
    appointment_id = query.book_appointment(user_id, slot_id)
    
    # Get appointment details for notification
    appt = query.get_appointment_by_id(appointment_id)
    if not appt:
        bot.send_message(call.message.chat.id, "❌ Error creating booking. Please try again.")
        user_state.pop(call.from_user.id, None)
        return
    
    bot.send_message(
        call.message.chat.id, 
        f"✅ Your booking request has been sent!\n"
        f"Service: {appt['service_name']}\n"
        f"Date: {appt['date']} at {appt['time']}\n"
        f"Status: ⏳ Awaiting confirmation\n\n"
        f"You'll be notified when the admin confirms."
    )
    
    # Notify admin with confirm/reject buttons
    admin_id = appt['admin_id']
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{appointment_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{appointment_id}")
    )
    bot.send_message(
        admin_id,
        f"⚠️ *New Booking Request!*\n\n"
        f"👤 User: @{username} (ID: {user_id})\n"
        f"💇 Service: {appt['service_name']}\n"
        f"📅 Date: {appt['date']}\n"
        f"⏰ Time: {appt['time']}",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    user_state.pop(call.from_user.id, None)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def handle_confirm(call):
    appointment_id = int(call.data.split("_")[1])
    appt = query.get_appointment_by_id(appointment_id)
    
    if not appt or appt['status'] != 'pending':
        bot.answer_callback_query(call.id, "❌ This booking was already processed.")
        return
    
    query.confirm_appointment(appointment_id)
    
    # Update the admin message
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + "\n\n✅ *Confirmed!*",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "✅ Booking confirmed!")
    
    # Notify user
    bot.send_message(
        appt['user_id'],
        f"✅ *Your booking is confirmed!*\n\n"
        f"💇 Service: {appt['service_name']}\n"
        f"📅 Date: {appt['date']}\n"
        f"⏰ Time: {appt['time']}",
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def handle_reject(call):
    appointment_id = int(call.data.split("_")[1])
    appt = query.get_appointment_by_id(appointment_id)
    
    if not appt or appt['status'] != 'pending':
        bot.answer_callback_query(call.id, "❌ This booking was already processed.")
        return
    
    query.reject_appointment(appointment_id)
    
    # Update the admin message
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + "\n\n❌ *Rejected*",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "❌ Booking rejected!")
    
    # Notify user
    bot.send_message(
        appt['user_id'],
        f"❌ *Your booking was rejected*\n\n"
        f"💇 Service: {appt['service_name']}\n"
        f"📅 Date: {appt['date']}\n"
        f"⏰ Time: {appt['time']}\n\n"
        f"Please try another time slot.",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == "📋 My Appointments")
def show_appointments(message):
    user_id = str(message.from_user.id)
    
    if user_id in ADMINS:
        appointments = query.get_admin_appointments(user_id)
        if not appointments:
            bot.send_message(message.chat.id, "📭 No bookings yet.")
            return
        text = "📋 *All Bookings:*\n\n"
        for date, time, service, username, status in appointments:
            status_emoji = {"pending": "⏳", "confirmed": "✅", "rejected": "❌"}
            icon = status_emoji.get(status, "❓")
            text += f"{icon} *{service}* — {date} at {time}\n"
            text += f"   👤 @{username} — {status}\n\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        appointments = query.get_user_appointments(user_id)
        if not appointments:
            bot.send_message(message.chat.id, "📭 You have no appointments yet.")
            return
        text = "📅 *Your Appointments:*\n\n"
        for date, time, service, status in appointments:
            status_emoji = {"pending": "⏳ Awaiting", "confirmed": "✅ Confirmed", "rejected": "❌ Rejected"}
            icon = status_emoji.get(status, "❓")
            text += f"• *{service}* — {date} at {time}\n"
            text += f"  Status: {icon}\n\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(func=lambda m: m.text == "⏳ Pending Bookings")
def show_pending(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMINS:
        return
    
    pending = query.get_pending_appointments(user_id)
    if not pending:
        bot.send_message(message.chat.id, "✅ No pending bookings.")
        return
    
    text = "⏳ *Pending Bookings:*\n\n"
    for appt_id, date, time, service, username in pending:
        text += f"📌 #{appt_id}\n"
        text += f"   💇 {service} — {date} at {time}\n"
        text += f"   👤 @{username}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# Admin Flow: Add Service
@bot.message_handler(func=lambda m: m.text == "➕ Add Service")
def ask_service_name(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMINS:
        bot.send_message(message.chat.id, "❌ You are not authorized to add services.")
        return
    user_state[user_id] = {"step": "service_name", "dates": [], "slots": []}
    bot.send_message(message.chat.id, "📝 Enter the name of the new service:")


@bot.message_handler(func=lambda m: str(m.from_user.id) in user_state)
def handle_admin_input(message):
    user_id = str(message.from_user.id)
    state = user_state[user_id]
    step = state["step"]

    if step == "service_name":
        state["service_name"] = message.text.strip()
        state["step"] = "add_date"
        bot.send_message(message.chat.id, "📅 Enter a date (YYYY-MM-DD), or type 'done' when finished:")

    elif step == "add_date":
        text = message.text.strip()
        if text.lower() == "done":
            if not state["dates"]:
                bot.send_message(message.chat.id, "⚠️ You must enter at least one date.")
                return
            state["date_index"] = 0
            state["step"] = "add_times"
            bot.send_message(message.chat.id, f"⏰ Enter times for {state['dates'][0]} (comma-separated, e.g. 10:00, 11:00, 14:30):")
        else:
            state["dates"].append(text)
            bot.send_message(message.chat.id, "✅ Date added. Enter another date or type 'done':")

    elif step == "add_times":
        times = [t.strip() for t in message.text.split(",") if t.strip()]
        if not times:
            bot.send_message(message.chat.id, "⚠️ Please enter at least one time.")
            return
        date = state["dates"][state["date_index"]]
        state["slots"].append((date, times))
        state["date_index"] += 1
        if state["date_index"] < len(state["dates"]):
            next_date = state["dates"][state["date_index"]]
            bot.send_message(message.chat.id, f"⏰ Enter times for {next_date} (comma-separated):")
        else:
            service_id = query.insert_service(state["service_name"], user_id)
            for date, times in state["slots"]:
                query.insert_slots(service_id, date, times)
            bot.send_message(
                message.chat.id, 
                f"✅ Service '{state['service_name']}' added with {len(state['dates'])} dates."
            )
            user_state.pop(user_id)


print("🤖 Booking bot started...")
bot.polling()
