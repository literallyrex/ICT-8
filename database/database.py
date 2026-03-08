import mysql.connector
import datetime
import calendar
from utils.config import db_config

def get_connection():
    return mysql.connector.connect(**db_config)

def initialize_db():
    start_config = db_config.copy()
    if 'database' in start_config:
        db_name = start_config.pop("database")
    else:
        db_name = "registration_db"
    
    try:
        conn = mysql.connector.connect(**start_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.close()
    except mysql.connector.Error as err:
        print(f"DB creation error: {err}")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(64) NOT NULL,
                full_name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                address VARCHAR(255),
                user_role VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending',
                student_id VARCHAR(50),
                course VARCHAR(100),
                grade VARCHAR(20) DEFAULT NULL,
                age INT,
                gender VARCHAR(20),
                course_category VARCHAR(50),
                program_type VARCHAR(50),
                specialization VARCHAR(100),
                section VARCHAR(20) DEFAULT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                subject VARCHAR(100) NOT NULL,
                q1 INT DEFAULT NULL,
                q2 INT DEFAULT NULL,
                q3 INT DEFAULT NULL,
                q4 INT DEFAULT NULL,
                final INT DEFAULT NULL,
                remarks VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(50) DEFAULT 'Present',
                remarks VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY (user_id, date)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timetable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                subject VARCHAR(100) NOT NULL,
                day VARCHAR(20),
                time VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(120) NOT NULL,
                description TEXT,
                start_datetime DATETIME NOT NULL,
                end_datetime DATETIME NOT NULL,
                recurrence_type VARCHAR(20) DEFAULT 'None',
                recurrence_interval INT DEFAULT 1,
                recurrence_count INT DEFAULT NULL,
                recurrence_until DATE DEFAULT NULL,
                created_by VARCHAR(80),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_schedules_user_start (user_id, start_datetime),
                INDEX idx_schedules_user_end (user_id, end_datetime)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                actor VARCHAR(80) NOT NULL,
                action VARCHAR(80) NOT NULL,
                entity_type VARCHAR(80),
                entity_id INT DEFAULT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS program_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                program_type VARCHAR(50) NOT NULL,
                time_range VARCHAR(50) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                teacher VARCHAR(100) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                program_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS section_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT NOT NULL,
                time_range VARCHAR(50) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                teacher VARCHAR(100) NOT NULL DEFAULT '',
                FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Table creation error: {err}")

def add_user(username, password_hash, full_name, email, phone, role, **kwargs):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        address = kwargs.get('address')
        student_id = kwargs.get('student_id')
        course = kwargs.get('course')

        status = 'Pending'
        
        grade = kwargs.get('grade')
        age = kwargs.get('age')
        gender = kwargs.get('gender')
        course_category = kwargs.get('course_category')
        program_type = kwargs.get('program_type')
        specialization = kwargs.get('specialization')
        section = kwargs.get('section')

        query = """INSERT INTO users 
                   (username, password_hash, full_name, email, phone, user_role, 
                    address, student_id, course, status, grade, age, gender, 
                    course_category, program_type, specialization, section) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(query, (username, password_hash, full_name, email, phone, role,
                               address, student_id, course, status, grade,
                               age, gender, course_category, program_type, 
                               specialization, section))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Registration error: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def username_exists(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_by_username(username):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT email, phone FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_all_users():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users"
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def search_users(search_query="", status_filter="All", program_filter="All", grade_filter="All", sort_by="id", sort_order="DESC"):
    """Search users across all text columns with optional status filter."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        conditions = []
        params = []
        
        if search_query:
            search_cols = ["username", "full_name", "email", "phone", "address",
                           "student_id", "course", "grade", "course_category", 
                           "program_type", "specialization", "gender", "section"]
            like_clause = " OR ".join([f"{col} LIKE %s" for col in search_cols])
            conditions.append(f"({like_clause})")
            like_q = f"%{search_query}%"
            params.extend([like_q] * len(search_cols))
        
        if status_filter and status_filter != "All":
            conditions.append("status = %s")
            params.append(status_filter)
            
        if program_filter and program_filter != "All":
            if program_filter == "Regular":
                # Match Regular Program category or program_type
                conditions.append("(course_category = 'Regular Program' OR program_type = 'Regular')")
            elif program_filter in ["STE", "SPJ", "SPA"]:
                conditions.append("program_type = %s")
                params.append(program_filter)
            else:
                # Fallback for old values if any
                conditions.append("course_category = %s")
                params.append(program_filter)

        if grade_filter and grade_filter != "All":
            conditions.append("grade = %s")
            params.append(grade_filter)
        
        query = "SELECT * FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # Validate sort_by to prevent SQL injection
        allowed_sort_cols = ["id", "username", "full_name", "grade", "course_category", "section", "status"]
        if sort_by not in allowed_sort_cols:
            sort_by = "id"
            
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
            
        query += f" ORDER BY {sort_by} {sort_order}"
        
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_password(username, new_password_hash):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "UPDATE users SET password_hash = %s WHERE username = %s"
        cursor.execute(query, (new_password_hash, username))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_user_status(user_id, status, section=None, grade=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT status, section, grade, course_category, program_type, specialization FROM users WHERE id = %s", (user_id,))
        existing = cursor.fetchone()
        if not existing:
            return False
        
        if grade and section:
            cat = existing['course_category'] or ""
            prog = existing['program_type'] or "N/A"
            spec = existing['specialization'] or "N/A"
            
            course_part = cat
            if prog != "N/A":
                course_part += f" ({prog}"
                if spec != "N/A":
                    course_part += f" - {spec}"
                course_part += ")"
            
            new_course = f"{course_part} - {grade}"
            
            query = "UPDATE users SET status = %s, section = %s, grade = %s, course = %s WHERE id = %s"
            cursor.execute(query, (status, section, grade, new_course, user_id))
        else:
            query = "UPDATE users SET status = %s WHERE id = %s"
            cursor.execute(query, (status, user_id))
            
        conn.commit()
        
        # Initialize grades if approved
        if status == "Approved":
            initialize_grades(user_id)
            initialize_timetable(user_id)
            
        if cursor.rowcount > 0:
            return True
        if grade and section:
            return existing['status'] == status and existing.get('grade') == grade and existing.get('section') == section
        return existing['status'] == status
    except mysql.connector.Error as e:
        print(f"Update status error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def initialize_grades(user_id):
    """Initialize grade records for a new student if not exists."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if grades exist
        cursor.execute("SELECT id FROM grades WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            return # Already initialized
            
        # Get user's program type
        cursor.execute("SELECT program_type FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        program = user['program_type'] if user else "N/A"

        # Base subjects
        subjects = [
            "Filipino", "English", "Mathematics", "Science", 
            "Araling Panlipunan (AP)", "Values Education"
        ]
        
        if program == "STE":
            subjects.append("Creative Tech")
        else:
            subjects.append("TLE")
            
        subjects.extend(["MAPEH", "Music & Arts", "PE & Health"])
        
        if program == "STE":
            subjects.append("Research II")
        
        for subj in subjects:
            cursor.execute("INSERT INTO grades (user_id, subject) VALUES (%s, %s)", (user_id, subj))
            
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error initializing grades: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def initialize_timetable(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM timetable WHERE user_id = %s LIMIT 1", (user_id,))
        if cursor.fetchone():
            return
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error initializing timetable: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_attendance(user_id):
    """Return all attendance records for a specific student."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM attendance WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def mark_attendance(user_id, date, status, remarks=""):
    """Insert or update an attendance record for a student on a specific date."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO attendance (user_id, date, status, remarks)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = %s, remarks = %s
        """
        cursor.execute(query, (user_id, date, status, remarks, status, remarks))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error marking attendance: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_attendance_summary(user_id):
    """Return counts of attendance statuses for a student."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT status, COUNT(*) as count 
            FROM attendance 
            WHERE user_id = %s 
            GROUP BY status
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_student_grades(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM grades WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_grade(grade_id, field, value):
    """Update a specific field (q1, q2, q3, q4, final, remarks) for a grade record."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ["q1", "q2", "q3", "q4", "final", "remarks"]
        if field not in allowed_fields:
            return False
            
        query = f"UPDATE grades SET {field} = %s WHERE id = %s"
        cursor.execute(query, (value, grade_id))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False

def save_grades_batch(updates):
    """Update multiple grades using a single connection.
    updates is a list of tuples: (grade_id, {field: value, ...})
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        allowed_fields = ["q1", "q2", "q3", "q4", "final", "remarks"]
        
        for grade_id, data in updates:
            for field, value in data.items():
                if field in allowed_fields:
                    query = f"UPDATE grades SET {field} = %s WHERE id = %s"
                    cursor.execute(query, (value, grade_id))
                    
        conn.commit()
        return True, ""
    except mysql.connector.Error as e:
        return False, str(e)
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def delete_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_details(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_by_id(user_id):
    """Return full user data by ID (for student dashboard)."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_user_details(user_id, **kwargs):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return False
            
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(query, tuple(values))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def verify_login(username, password_hash):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
        cursor.execute(query, (username, password_hash))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def add_announcement(message):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO announcements (message) VALUES (%s)"
        cursor.execute(query, (message,))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_announcements():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM announcements ORDER BY created_at DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def delete_announcement(announcement_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM announcements WHERE id = %s"
        cursor.execute(query, (announcement_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_required_subjects(program_type):
    # Base subjects for STE (Science, Technology, Engineering)
    # Includes specialized subjects
    subjects = ["Enhanced Science", "Research", "Math", "MAPEH", "English", "Filipino", "Araling Panlipunan", "Creative Tech", "ESP"]
    
    if program_type == "Regular" or program_type == "N/A" or not program_type: # Regular logic
        # For Regular:
        # - Creative Tech -> TLE
        # - Remove Research
        # - Enhanced Science -> Science
        
        regular_subjects = []
        for s in subjects:
            if s == "Creative Tech":
                regular_subjects.append("TLE")
            elif s == "Enhanced Science":
                regular_subjects.append("Science")
            elif s == "Research":
                continue
            else:
                regular_subjects.append(s)
        return regular_subjects
            
    return subjects

def get_student_timetable(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM timetable WHERE user_id = %s ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), time", (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_program_schedule(program_type):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM program_schedules WHERE program_type = %s ORDER BY id ASC", (program_type,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_program_schedule(schedule_id, time_range, subject, teacher):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "UPDATE program_schedules SET time_range = %s, subject = %s, teacher = %s WHERE id = %s"
        cursor.execute(query, (time_range, subject, teacher, schedule_id))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def log_audit_event(actor, action, entity_type=None, entity_id=None, details=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO audit_logs (actor, action, entity_type, entity_id, details) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (actor, action, entity_type, entity_id, details))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Audit log error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def _add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def _iter_occurrences(start_dt, end_dt, recurrence_type, interval, count, until, window_start, window_end):
    if interval is None or interval < 1:
        interval = 1
    current_start = start_dt
    current_end = end_dt
    occurrences = 0
    max_iterations = 1000
    while occurrences < max_iterations:
        if current_end >= window_start and current_start <= window_end:
            yield current_start, current_end
        if recurrence_type == "None":
            break
        occurrences += 1
        if count is not None and occurrences >= count:
            break
        if until is not None and current_start.date() > until:
            break
        if recurrence_type == "Daily":
            delta = datetime.timedelta(days=interval)
            current_start = current_start + delta
            current_end = current_end + delta
        elif recurrence_type == "Weekly":
            delta = datetime.timedelta(weeks=interval)
            current_start = current_start + delta
            current_end = current_end + delta
        elif recurrence_type == "Monthly":
            current_start = _add_months(current_start, interval)
            current_end = _add_months(current_end, interval)
        else:
            break

def get_user_schedules(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM schedules WHERE user_id = %s ORDER BY start_datetime ASC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_schedule_by_id(schedule_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM schedules WHERE id = %s"
        cursor.execute(query, (schedule_id,))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_schedule_occurrences(user_id, window_start, window_end):
    schedules = get_user_schedules(user_id)
    occurrences = []
    for s in schedules:
        r_type = s.get('recurrence_type') or "None"
        r_interval = s.get('recurrence_interval') or 1
        r_count = s.get('recurrence_count')
        r_until = s.get('recurrence_until')
        for occ_start, occ_end in _iter_occurrences(
            s['start_datetime'], s['end_datetime'], r_type, r_interval, r_count, r_until, window_start, window_end
        ):
            occurrences.append({
                "schedule_id": s['id'],
                "title": s['title'],
                "description": s.get('description') or "",
                "start_datetime": occ_start,
                "end_datetime": occ_end
            })
    occurrences.sort(key=lambda o: o["start_datetime"])
    return occurrences

def check_schedule_conflict(user_id, start_dt, end_dt, recurrence_type="None", recurrence_interval=1, recurrence_count=None, recurrence_until=None, exclude_schedule_id=None):
    window_start = start_dt - datetime.timedelta(days=1)
    window_end = start_dt + datetime.timedelta(days=365)
    new_occurrences = list(_iter_occurrences(start_dt, end_dt, recurrence_type, recurrence_interval, recurrence_count, recurrence_until, window_start, window_end))
    existing = get_user_schedules(user_id)
    for s in existing:
        if exclude_schedule_id and s['id'] == exclude_schedule_id:
            continue
        r_type = s.get('recurrence_type') or "None"
        r_interval = s.get('recurrence_interval') or 1
        r_count = s.get('recurrence_count')
        r_until = s.get('recurrence_until')
        for e_start, e_end in _iter_occurrences(s['start_datetime'], s['end_datetime'], r_type, r_interval, r_count, r_until, window_start, window_end):
            for n_start, n_end in new_occurrences:
                if n_start < e_end and e_start < n_end:
                    return True
    return False

def add_schedule(user_id, title, start_dt, end_dt, recurrence_type="None", recurrence_interval=1, recurrence_count=None, recurrence_until=None, created_by="Admin", description=""):
    try:
        if check_schedule_conflict(user_id, start_dt, end_dt, recurrence_type, recurrence_interval, recurrence_count, recurrence_until):
            return False
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO schedules 
            (user_id, title, description, start_datetime, end_datetime, recurrence_type, recurrence_interval, recurrence_count, recurrence_until, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, title, description, start_dt, end_dt, recurrence_type, recurrence_interval, recurrence_count, recurrence_until, created_by))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        print(f"Add schedule error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_schedule(schedule_id, title, start_dt, end_dt, recurrence_type="None", recurrence_interval=1, recurrence_count=None, recurrence_until=None, description=""):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM schedules WHERE id = %s", (schedule_id,))
        row = cursor.fetchone()
        if not row:
            return False
        user_id = row['user_id']
        if check_schedule_conflict(user_id, start_dt, end_dt, recurrence_type, recurrence_interval, recurrence_count, recurrence_until, exclude_schedule_id=schedule_id):
            return False
        query = """
            UPDATE schedules SET title = %s, description = %s, start_datetime = %s, end_datetime = %s,
                recurrence_type = %s, recurrence_interval = %s, recurrence_count = %s, recurrence_until = %s
            WHERE id = %s
        """
        cursor.execute(query, (title, description, start_dt, end_dt, recurrence_type, recurrence_interval, recurrence_count, recurrence_until, schedule_id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Update schedule error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# ─── Section CRUD ───

def create_section(name, program_type=None):
    """Create a new section and copy schedule rows from the program template."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sections (name, program_type) VALUES (%s, %s)", (name, program_type))
        section_id = cursor.lastrowid
        
        # Copy schedule from program_schedules template if a program_type is given
        if program_type:
            cursor.execute("SELECT time_range, subject, teacher FROM program_schedules WHERE program_type = %s ORDER BY id ASC", (program_type,))
            rows = cursor.fetchall()
            for time_range, subject, teacher in rows:
                cursor.execute("INSERT INTO section_schedules (section_id, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                               (section_id, time_range, subject, teacher))
        
        conn.commit()
        return section_id
    except mysql.connector.Error as e:
        print(f"Create section error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_all_sections():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sections ORDER BY name ASC")
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_section_by_name(name):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sections WHERE name = %s", (name,))
        return cursor.fetchone()
    except mysql.connector.Error:
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_section_names():
    """Return a flat list of section name strings for dropdowns."""
    sections = get_all_sections()
    return [s['name'] for s in sections]

def update_section(section_id, name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE sections SET name = %s WHERE id = %s", (name, section_id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Update section error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def delete_section(section_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sections WHERE id = %s", (section_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_section_schedules(section_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM section_schedules WHERE section_id = %s ORDER BY id ASC", (section_id,))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def add_section_schedule(section_id, time_range, subject, teacher=""):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO section_schedules (section_id, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                       (section_id, time_range, subject, teacher))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        print(f"Add section schedule error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def update_section_schedule(schedule_id, time_range, subject, teacher):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE section_schedules SET time_range = %s, subject = %s, teacher = %s WHERE id = %s",
                       (time_range, subject, teacher, schedule_id))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def delete_section_schedule(schedule_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM section_schedules WHERE id = %s", (schedule_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


def delete_schedule(schedule_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM schedules WHERE id = %s"
        cursor.execute(query, (schedule_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Delete schedule error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
