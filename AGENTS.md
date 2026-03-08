# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A **Student Registration System** — a desktop GUI application for a Philippine junior high school. Students self-register and await admin approval. Admins manage users, grades, attendance, schedules, and announcements. Built with Python, CustomTkinter, and MySQL (XAMPP).

## Prerequisites

- Python 3.13+ with a virtual environment in `.venv`
- XAMPP with MySQL running on `127.0.0.1` (root, no password)
- The database `registration_db` is auto-created by `initialize_db()`
- `requirements.txt` is not fully complete for the full GUI: `main.py` also requires `matplotlib`, `Pillow` (for logo/image loading), and optionally `geopy` (for map reverse-geocoding). Install them manually if missing: `pip install matplotlib Pillow geopy`

## Commands

### Install dependencies
```
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run the application
There is no build step; the desktop app is launched directly.
```
python main.py
```

### Lint / format
No linting or formatting tool is configured in the repository. Do not invent `ruff`, `flake8`, or `black` commands unless you add that tooling first.

### Run tests
Tests require a live MySQL instance (XAMPP running). They create and clean up real database records.
```
python -m unittest test_core.py
```

Run a single test:
```
python -m unittest test_core.TestRegistration.test_schedule_conflicts
```

### Run database migrations
Migrations are standalone scripts run manually in order. They are **not idempotent** — most truncate and re-seed data. Always back up first.
```
python -m migrations.migrate_program_schedules
python -m migrations.migrate_v8
python -m migrations.migrate_sections
```

## Architecture

### Core modules (all in project root, no packages)

- **`main.py`** — The entire GUI in a single `App(ctk.CTk)` class. Contains login, student registration, admin dashboard (user management, sections, schedule templates, analytics tabs), student dashboard (profile, grades, attendance, timetable, settings tabs), map picker, validation helpers, and UI animation helpers. This file is ~2500 lines.
- The app entrypoint is at the bottom of `main.py`: it calls `initialize_db()` and then starts `App().mainloop()`.
- **`database.py`** — All MySQL operations. Each function opens and closes its own connection via `get_connection()`. Defines table schemas in `initialize_db()` and provides CRUD for: `users`, `announcements`, `grades`, `attendance`, `timetable`, `schedules`, `audit_logs`, `program_schedules`, `sections`, `section_schedules`. Also contains recurring schedule occurrence logic (`_iter_occurrences`).
- **`auth.py`** — Single function: `hash_password()` using SHA-256.
- **`config.py`** — MySQL connection dict (`db_config`). Default: localhost/root/no password/registration_db.

### Database tables

The key tables (created in `database.initialize_db()`):
- `users` — Central table. Stores credentials, profile, enrollment info (course_category, program_type, specialization), grade level, section, approval status.
- `grades` — Per-subject quarterly grades (q1–q4) with auto-computed final. Foreign key to users (CASCADE delete).
- `attendance` — Daily records per student with UNIQUE(user_id, date).
- `program_schedules` — Schedule templates per program type (STE, Regular, SPJ, SPA). Seeded by `migrations/migrate_program_schedules.py`. Used as templates when creating new sections.
- `sections` — Named sections created by the admin (e.g. "Rizal", "Newton"). Each stores a `program_type` indicating which template was used. Created/managed in the admin Sections tab.
- `section_schedules` — Per-section timetable rows (FK to sections, CASCADE delete). Initially copied from `program_schedules` template, then independently editable.
- `schedules` — Per-user recurring events with conflict detection.
- `announcements` — Admin-posted messages visible to all students.
- `audit_logs` — Action log for admin operations.

### Data flow

1. Student registers → must select a program category (and sub-type/specialization if applicable) → status = "Pending", grade = "Pending"
2. Admin creates sections in the Sections tab (choosing a program schedule template), then approves students → assigns grade level and selects a section from the dropdown → `initialize_grades()` seeds subject rows based on program type → status = "Approved"
3. Admin edits quarterly grades → final is auto-computed as average of available quarters
4. Student dashboard displays profile, report card, attendance summary, and section-specific timetable (falls back to program template if no section schedule exists)

### Program types

- **Regular Program** — course = "REGULAR", has TLE and Science
- **Special Programs**: STE (has Enhanced Science, Creative Tech, Research), SPJ, SPA (has specializations: Dancing, Theatre, Arts, Music)

Subject lists for grade initialization differ by program — see `initialize_grades()` and `get_required_subjects()` in `database.py`.

### Key patterns

- All DB functions use the pattern: `try/get_connection()/execute/finally close`. No connection pooling.
- Admin authentication uses a hardcoded password (`ADMIN_PASSWORD = "12345"` in `main.py`), separate from the user table.
- Phone validation requires Philippine format: `+63` followed by 10 digits.
- The map picker uses `tkintermapview` with Google Maps tiles and `geopy.Nominatim` for geocoding. Both are optional — the app degrades gracefully if they're unavailable.
- `main.py` uses `concurrent.futures.ThreadPoolExecutor` for background geocoding tasks to avoid blocking the Tkinter event loop.
- Migration scripts in `migrations/` (`migrate_v*.py`) modify schema and data directly. `migrations/migrate_v8.py` creates a backup table before altering columns. `migrations/migrate_sections.py` creates the `sections`/`section_schedules` tables and migrates existing section names from users into proper section records.
- Registration validation requires all dropdowns (gender, program category, program type, specialization) to be explicitly selected before submission.
- Admin assigns sections via dropdown (populated from the `sections` table) rather than free-text input, both when approving and editing students.

### Test conventions

- All tests are in `test_core.py` using `unittest.TestCase`.
- Tests hit the real database — each test creates test records and cleans them up in try/except blocks.
- Tests import `validate_phone` and `validate_email` from `main.py`.
- Because tests import from `main.py`, running tests also requires the GUI/runtime imports in that file to be available, not just `database.py`.
