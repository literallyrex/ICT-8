# Student Registration System

A desktop GUI application for a Philippine junior high school, built with Python, CustomTkinter, and MySQL. Students can register and wait for approval, while admins manage users, grades, attendance, sections, schedules, and announcements.

## Features

- Student account registration and login
- Admin login and student approval flow
- Student dashboard with:
  - Profile
  - Grades
  - Attendance
  - Timetable
  - Settings
- Gamification-based student ranking
- Admin tools for:
  - User management
  - Grade management
  - Attendance management
  - Section management
  - Program schedule templates
  - Announcements
  - Analytics and CSV export

## Tech Stack

- Python 3.13+
- CustomTkinter
- MySQL via `mysql-connector-python`
- XAMPP MySQL on `127.0.0.1`
- Matplotlib
- Pillow
- Optional geolocation/map support with `tkintermapview` and `geopy`

## Project Structure

```text
project/
├── main.py
├── views/
├── controllers/
├── services/
├── database/
├── utils/
├── migrations/
├── test_core.py
├── requirements.txt
└── logo.png
```

### MVC Layout

- `main.py`
  - Application entrypoint
  - Starts the app and manages top-level navigation
- `views/`
  - CustomTkinter screens and dialogs
- `controllers/`
  - Event handling and application flow
- `services/`
  - Reusable business logic for grades, attendance, and schedules
- `database/`
  - MySQL connection and CRUD/database helpers
- `utils/`
  - Shared helpers, constants, auth hashing, and validation
- `migrations/`
  - Manual migration scripts

## Requirements

Before running the project, make sure you have:

- Python 3.13 or newer
- XAMPP installed and MySQL running
- A virtual environment in `.venv`

The app uses this database by default:

- Host: `127.0.0.1`
- User: `root`
- Password: empty
- Database: `registration_db`

The database is created automatically on startup through `initialize_db()`.

## Installation

1. Open the project folder.
2. Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

3. Install the dependencies:

```powershell
pip install -r requirements.txt
pip install matplotlib Pillow geopy
```

## Run the Application

```powershell
python main.py
```

## Run Tests

Tests use a real MySQL database, so make sure XAMPP MySQL is running first.

Run all tests:

```powershell
python -m unittest test_core.py
```

Run a single test:

```powershell
python -m unittest test_core.TestRegistration.test_schedule_conflicts
```

## Database Migrations

Migration scripts are manual and not idempotent. Back up your database first.

Examples:

```powershell
python -m migrations.migrate_program_schedules
python -m migrations.migrate_v8
python -m migrations.migrate_sections
```

## Important Notes

- Admin authentication is currently configured in the code through `utils/constants.py`.
- Phone number validation expects Philippine format: `+63` followed by 10 digits.
- The map picker depends on `tkintermapview`; reverse geocoding support uses `geopy`.
- Some migration and archive files are kept for project history and maintenance.

## Database Tables

Main tables used by the system:

- `users`
- `announcements`
- `grades`
- `attendance`
- `schedules`
- `program_schedules`
- `sections`
- `section_schedules`
- `audit_logs`

## Status

This project has been refactored from a monolithic GUI file into an MVC-style structure to make it easier to maintain and extend.
