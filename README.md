# Student Registration System

A desktop GUI application for a Philippine junior high school, built with Python, CustomTkinter, and MySQL. Students can register and wait for approval, while admins manage users, grades, attendance, sections, schedules, and announcements.

## Features

- Student account registration and login
- Admin login and student approval flow
- Student profile picture upload with image preview
- Friends system with student search and friend requests
- Chat messaging between accepted friends
- Student dashboard with:
  - Profile
  - Grades
  - Attendance
  - Timetable
  - Friends & Chat
  - Settings (with UI Customization)
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
```

Pillow is already included in `requirements.txt` and is used for profile picture resizing and preview.

## Run the Application

```powershell
python main.py
```

## Profile Picture Upload

- During student registration, click `Upload Profile Picture`.
- Supported file types are `JPG`, `JPEG`, and `PNG`.
- The app resizes the selected image, shows a preview in the form, and saves it inside `profile_pictures/`.
- The saved relative path is stored in the `users.profile_picture` column.
- When the student logs in later, the saved profile picture is shown in the Profile tab.

## UI Customization

- Students can personalize the application's appearance from the `Settings` tab.
- Options include Primary UI Color, Button Color, Dark/Light Mode, Background Style, and Profile Accent Color.
- Changes are applied instantly for a live preview.
- Settings are saved to the `users` table in the database and automatically restored on the next login.

## Friends and Chat

- Students can search for other approved students by name or username in the `Friends & Chat` tab.
- Clicking `Add Friend` sends a pending friend request.
- Incoming requests can be accepted or rejected from the same tab.
- Accepted connections appear in the friends list sidebar.
- Students can open a conversation with any accepted friend and send messages.
- The chat area refreshes automatically every few seconds to load new messages and requests.

## Build EXE

Use the included batch script so Tcl/Tk is bundled correctly for CustomTkinter. The script also converts `logo.png` into a Windows `.ico` file and uses it as the EXE icon:

```powershell
.\build_exe.bat
```

The generated file will be:

```text
dist\StudentRegistrationSystem.exe
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
python -m migrations.migrate_v9
python -m migrations.migrate_v10
python -m migrations.migrate_v11
python -m migrations.migrate_v12
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
- `friend_requests`
- `friends`
- `messages`

## Status

This project has been refactored from a monolithic GUI file into an MVC-style structure to make it easier to maintain and extend.
Totally not vibecoded
