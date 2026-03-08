# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A Student Registration System desktop GUI application for a Philippine junior high school. Students self-register and wait for admin approval. Admins manage users, grades, attendance, sections, schedule templates, analytics, and announcements.

Built with:

- Python
- CustomTkinter
- MySQL via `mysql-connector-python`
- XAMPP MySQL on `127.0.0.1`

## Prerequisites

- Python 3.13+
- A virtual environment in `.venv`
- XAMPP with MySQL running on `127.0.0.1`
- The database `registration_db` is auto-created by `initialize_db()`

`requirements.txt` is not fully complete for the whole GUI. Install these manually if needed:

```powershell
pip install matplotlib Pillow geopy
```

`tkintermapview` is used for the map picker and is already listed in `requirements.txt`.

## Commands

### Install dependencies

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
pip install matplotlib Pillow geopy
```

### Run the application

```powershell
python main.py
```

### Build the Windows EXE

Use the provided spec file or helper script so Tcl/Tk data is bundled correctly:

```powershell
.\build_exe.bat
```

This generates:

```text
dist\StudentRegistrationSystem.exe
```

### Lint / format

No linting or formatting tool is configured in the repository. Do not invent `ruff`, `flake8`, or `black` commands unless you add that tooling first.

### Run tests

Tests require a live MySQL instance. They create and clean up real database records.

```powershell
python -m unittest test_core.py
```

Run a single test:

```powershell
python -m unittest test_core.TestRegistration.test_schedule_conflicts
```

### Run database migrations

Migration scripts are manual and not idempotent. Back up the database first.

```powershell
python -m migrations.migrate_program_schedules
python -m migrations.migrate_v8
python -m migrations.migrate_sections
```

## Architecture

### Current layout

- `main.py`
  - Thin app shell
  - Configures Tk/Matplotlib startup
  - Creates controllers and views
  - Starts the app and handles top-level navigation
- `views/`
  - CustomTkinter UI screens and dialogs
  - `base_view.py` contains shared UI helpers such as animations, dialog close setup, and map picker behavior
- `controllers/`
  - Auth flow
  - Student dashboard flow
  - Admin dashboard flow
- `services/`
  - Reusable business logic for grades, attendance, and schedules
- `database/database.py`
  - MySQL connection helpers and CRUD/database operations
  - Table creation in `initialize_db()`
  - Schedule recurrence/conflict helpers
- `utils/`
  - `auth.py` for password hashing
  - `config.py` for DB config
  - `constants.py` for app/theme constants
  - `validation.py` for shared validators
- `migrations/`
  - Manual database migration scripts
- `archive/`
  - Non-runtime diagnostics and generated artifacts grouped out of the main app

### Test/runtime compatibility

- Tests still import `validate_phone` and `validate_email` from `main.py`, so keep those imports available there.
- App code should import config and auth helpers from `utils.config` and `utils.auth` directly.

## Database tables

Main tables created in `database/database.py`:

- `users`
- `announcements`
- `grades`
- `attendance`
- `timetable`
- `schedules`
- `audit_logs`
- `program_schedules`
- `sections`
- `section_schedules`

## Data flow

1. Student registers and must select a program category and, when applicable, a program type or specialization.
2. New student accounts are stored with `Pending` status.
3. Admin creates sections and program-based section schedules.
4. Admin approves students, assigns grade level and section, and grade records are initialized.
5. Student dashboard loads profile, grades, attendance, timetable, announcements, and settings from the MVC layers.

## Program types

- Regular Program
  - Stored course value: `REGULAR`
- Special Programs
  - `STE`
  - `SPJ`
  - `SPA`
  - SPA specializations: `Dancing`, `Theatre`, `Arts`, `Music`

Subject initialization differs by program. See `initialize_grades()` and related grade logic in `database/database.py` and `services/grade_service.py`.

## Key patterns

- Views should stay focused on UI composition and dialog flow.
- Controllers should handle action flow and call services/database helpers.
- Services should contain reusable business logic instead of widget code.
- All DB functions still follow the open connection -> execute -> close pattern. There is no pooling.
- Admin authentication is still a configured constant in `utils/constants.py`, not a row in the `users` table.
- Phone validation expects `+63` followed by 10 digits.
- The map picker uses `tkintermapview` and optional `geopy` reverse geocoding. The app should degrade gracefully if those imports are unavailable.
- `main.py` still exposes `validate_phone` and `validate_email` by importing them from `utils.validation`.

## Test conventions

- Tests live in `test_core.py`
- Tests use `unittest.TestCase`
- Tests hit the real database
- Tests import from `main.py`, so GUI/runtime imports must still be available when tests run

## Notes for future edits

- Keep `main.py` small. New app logic should usually go into controllers or services, not back into the app shell.
- If you move migration files again, update command examples in this file and in `README.md`.
