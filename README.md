# Appointment Service (Telegram Bot)

A Telegram bot for booking appointments. Users browse services, pick a date and time slot, and reserve it. Admins define services and availability; SQLite stores users, services, time slots, and bookings.

## Features

- **Users**: Register on `/start`, book appointments via inline keyboards, view **My Appointments**.
- **Admins** (Telegram user IDs listed in `bot.py`): **Add Service** with multiple dates and comma-separated times per date; **My Appointments** shows all bookings for services they own (with booker `@username`).
- **Slots**: Only `available` slots are shown; after booking, the slot is marked `booked`.

## Tech Stack

- Python 3
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (`telebot`)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- SQLite (`sqlite3` in the standard library)

## Project Structure

| File | Purpose |
|------|---------|
| `bot.py` | Telegram handlers, user/admin flows, `user_state` for multi-step admin input |
| `query.py` | Database access: users, services, slots, appointments |
| `schema.py` | Creates SQLite tables if they do not exist |
| `seed_data.py` | Optional sample users, services, slots, and demo bookings |
| `.env` | `BOT_TOKEN` and `BOT_DB` (not committed if you use `.gitignore`) |

## Prerequisites

- Python 3.8+ recommended
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Installation

```bash
cd "Appointment Service"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pyTelegramBotAPI python-dotenv
```

## Configuration

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
BOT_DB=/absolute/or/relative/path/to/appointments.db
```

**Admin access**: In `bot.py`, set `ADMINS` to a list of Telegram user ID strings (the same IDs Telegram sends as `from_user.id`). Example:

```python
ADMINS = ['7588646786']
```

## Database Setup

Initialize tables once (before first run or after deleting the DB file):

```bash
python schema.py
```

Tables:

- **users** — `user_id` (primary key), `username`
- **services** — `service_id`, `name`, `admin_id`
- **slots** — `slot_id`, `service_id`, `date`, `time`, `status` (`available` / `booked`)
- **appointments** — `appointment_id`, `user_id`, `slot_id`

## Running the Bot

```bash
python bot.py
```

The process uses long polling (`bot.polling()`).

## Optional: Seed Sample Data

After `schema.py` has created the database:

```bash
python seed_data.py
```

This inserts demo users, services, slots, and sample bookings. Adjust user IDs, admin ID, dates, and slot IDs in `seed_data.py` to match your environment. Slot IDs in the sample `appointments` list assume a fresh DB where slots are inserted in order (IDs 1, 2, 3).

## User Flow

1. **Start** — Keyboard: *Book Appointment*, *My Appointments* (admins also see *Add Service*).
2. **Book Appointment** — Choose service → date → time; booking is confirmed and the slot is reserved.
3. **My Appointments** — Lists the user’s bookings; for admins, lists bookings on their services.

## Admin Flow (Add Service)

1. Tap *Add Service*.
2. Enter the service name.
3. Enter dates as `YYYY-MM-DD`, one per message; type `done` when finished (at least one date required).
4. For each date, enter times separated by commas (e.g. `10:00, 11:00, 14:30`).
5. The service and all slots are saved to the database.

## Limitations & Notes

- `user_state` is in-memory only; restarting the bot clears in-progress admin flows.
- Admins are configured in code, not in the database.
- Ensure `BOT_DB` points to a writable path the bot process can access.
