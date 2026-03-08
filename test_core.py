import unittest
import database
import mysql.connector
import sys
import os
import datetime
from utils import auth

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import validation functions
from main import validate_phone, validate_email


class TestRegistration(unittest.TestCase):
    def test_hashing(self):
        pw = "password123"
        hashed = auth.hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertEqual(len(hashed), 64)

    def test_db_connection(self):
        try:
            conn = database.get_connection()
            self.assertTrue(conn.is_connected())
            conn.close()
        except mysql.connector.Error:
            self.fail("Database connection failed")

    def test_user_flow(self):
        database.initialize_db()
        username = "test_data_user"
        password = "password123"
        fullname = "Test User"
        email = "test@gmail.com"
        phone = "+639171234567"
        role = "Student"
        hashed = auth.hash_password(password)
        
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

        self.assertTrue(database.add_user(username, hashed, fullname, email, phone, role))
        self.assertTrue(database.username_exists(username))
        self.assertFalse(database.add_user(username, hashed, fullname, email, phone, role))

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_password_reset(self):
        database.initialize_db()
        username = "test_reset_user"
        password = "oldpassword"
        fullname = "Reset User"
        email = "reset@gmail.com"
        phone = "+639181234567"
        role = "Student"
        old_hash = auth.hash_password(password)
        
        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

        # Create user
        database.add_user(username, old_hash, fullname, email, phone, role)

        # Verify get_user_by_username
        user_data = database.get_user_by_username(username)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['email'], email)
        self.assertEqual(user_data['phone'], phone)

        # Update password
        new_password = "newpassword"
        new_hash = auth.hash_password(new_password)
        self.assertTrue(database.update_password(username, new_hash))

        # Verify new password hash in DB
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        stored_hash = result[0]
        conn.close()
        self.assertEqual(stored_hash, new_hash)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_role_specific_data(self):
        database.initialize_db()
        username = "test_student"
        password = "password123"
        fullname = "Student User"
        email = "student@gmail.com"
        phone = "+639123456789"
        address = "Manila, Philippines"
        role = "Student"
        student_id = "2023-12345"
        course = "BSIT-2"
        hashed = auth.hash_password(password)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

        # Add user with role specific data
        self.assertTrue(database.add_user(username, hashed, fullname, email, phone, role, 
                                          address=address, student_id=student_id, course=course))

        # Verify data in DB
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['user_role'], 'Student')
        self.assertEqual(user_data['student_id'], student_id)
        self.assertEqual(user_data['course'], course)
        self.assertEqual(user_data['address'], address)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_get_all_users(self):
        database.initialize_db()
        username = "test_admin_view"
        password = "password"
        hashed = auth.hash_password(password)
        
        try:
             database.add_user(username, hashed, "Admin View User", "admin@gmail.com", "+639001234567", "Student", address="Test Addr")
        except:
             pass 

        users = database.get_all_users()
        self.assertIsInstance(users, list)
        self.assertTrue(len(users) > 0)
        
        found = False
        for user in users:
            if user['username'] == username:
                found = True
                break
        self.assertTrue(found)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_admin_management(self):
        database.initialize_db()
        username = "test_status_user"
        password = "password"
        hashed = auth.hash_password(password)
        
        # Cleanup first
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

        # 1. Create user (should be Pending)
        database.add_user(username, hashed, "Status User", "status@gmail.com", "+639001112222", "Student", address="Status Addr")
        
        # We need ID for management functions
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, status, full_name FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(user)
        self.assertEqual(user['status'], 'Pending')
        user_id = user['id']

        # 2. Approve User
        self.assertTrue(database.update_user_status(user_id, 'Approved', section="Rizal", grade="Grade 8"))
        
        # Verify status
        details = database.get_user_details(user_id)
        self.assertEqual(details['status'], 'Approved')

        # 3. Update Details
        new_name = "Updated Name"
        self.assertTrue(database.update_user_details(user_id, full_name=new_name))
        
        details = database.get_user_details(user_id)
        self.assertEqual(details['full_name'], new_name)

        # 4. Delete User
        self.assertTrue(database.delete_user(user_id))
        
        details = database.get_user_details(user_id)
        self.assertIsNone(details)

    # ─── Validation Tests ───
    def test_phone_validation(self):
        # Valid Philippine numbers
        self.assertTrue(validate_phone("+639171234567"))
        self.assertTrue(validate_phone("+639991234567"))
        self.assertTrue(validate_phone("+639001112222"))

        # Invalid numbers
        self.assertFalse(validate_phone("09171234567"))       # No +63 prefix
        self.assertFalse(validate_phone("+6391712345"))       # Too short
        self.assertFalse(validate_phone("+63917123456789"))   # Too long
        self.assertFalse(validate_phone("+1234567890"))       # Wrong country
        self.assertFalse(validate_phone(""))                   # Empty
        self.assertFalse(validate_phone("+63abcdefghij"))     # Letters

    def test_email_validation(self):
        # Valid email addresses
        self.assertTrue(validate_email("juan@gmail.com"))
        self.assertTrue(validate_email("juan.delacruz@yahoo.com"))
        self.assertTrue(validate_email("test123@outlook.com"))
        self.assertTrue(validate_email("user.name+tag@domain.net"))
        # Invalid emails
        self.assertFalse(validate_email(""))
        self.assertFalse(validate_email("notanemail"))
        self.assertFalse(validate_email("@gmail.com"))
        self.assertFalse(validate_email("user@"))

    def test_search_users(self):
        database.initialize_db()
        username = "test_search_user"
        password = "password"
        hashed = auth.hash_password(password)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

        database.add_user(username, hashed, "Search Test User", "search@gmail.com", 
                         "+639171111111", "Student", address="Manila", 
                         student_id="SRCH-001", course="BSIT-1")

        # Search by username
        results = database.search_users("test_search", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Search by name
        results = database.search_users("Search Test", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Search by student ID
        results = database.search_users("SRCH-001", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Search by course (full-column search)
        results = database.search_users("BSIT", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Search by email
        results = database.search_users("search@gmail", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Search by address
        results = database.search_users("Manila", "All")
        self.assertTrue(any(u['username'] == username for u in results))

        # Filter by status
        results = database.search_users("", "Pending")
        self.assertTrue(any(u['username'] == username for u in results))

        results = database.search_users("", "Approved")
        self.assertFalse(any(u['username'] == username for u in results))

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_grade_column(self):
        database.initialize_db()
        username = "test_grade_user"
        password = "password"
        hashed = auth.hash_password(password)

        # Cleanup
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass

    def test_schedule_conflicts(self):
        database.initialize_db()
        username = "test_schedule_user"
        password = "password"
        hashed = auth.hash_password(password)
        
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
        except:
            pass
        
        database.add_user(username, hashed, "Schedule User", "schedule@gmail.com",
                         "+639171113333", "Student", address="Manila",
                         student_id="SCH-001", course="BSIT-2")
        
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(user)
        user_id = user['id']
        
        start1 = datetime.datetime(2026, 1, 10, 9, 0)
        end1 = datetime.datetime(2026, 1, 10, 10, 0)
        sched_id = database.add_schedule(user_id, "Math Session", start1, end1, "None", 1, None, None, "Admin", "")
        self.assertTrue(sched_id)
        
        conflict = database.check_schedule_conflict(user_id, start1 + datetime.timedelta(minutes=30), end1 + datetime.timedelta(minutes=30), "None", 1, None, None)
        self.assertTrue(conflict)
        
        no_conflict = database.check_schedule_conflict(user_id, start1 + datetime.timedelta(hours=2), start1 + datetime.timedelta(hours=3), "None", 1, None, None)
        self.assertFalse(no_conflict)
        
        weekly_start = datetime.datetime(2026, 1, 12, 14, 0)
        weekly_end = datetime.datetime(2026, 1, 12, 15, 0)
        sched_weekly = database.add_schedule(user_id, "Weekly Lab", weekly_start, weekly_end, "Weekly", 1, 3, None, "Admin", "")
        self.assertTrue(sched_weekly)
        
        week2_start = weekly_start + datetime.timedelta(weeks=1)
        week2_end = weekly_end + datetime.timedelta(weeks=1)
        conflict_weekly = database.check_schedule_conflict(user_id, week2_start, week2_end, "None", 1, None, None)
        self.assertTrue(conflict_weekly)
        
        database.delete_schedule(sched_id)
        database.delete_schedule(sched_weekly)
        database.delete_user(user_id)

    def test_program_subjects(self):
        # Test STE
        ste_subjects = database.get_required_subjects("STE")
        self.assertIn("Enhanced Science", ste_subjects)
        self.assertIn("Creative Tech", ste_subjects)
        self.assertIn("Research", ste_subjects)
        self.assertNotIn("TLE", ste_subjects)
        self.assertNotIn("Science", ste_subjects) # Should be Enhanced Science

        # Test Regular
        reg_subjects = database.get_required_subjects("Regular")
        self.assertIn("Science", reg_subjects)
        self.assertIn("TLE", reg_subjects)
        self.assertNotIn("Research", reg_subjects)
        self.assertNotIn("Enhanced Science", reg_subjects)
        self.assertNotIn("Creative Tech", reg_subjects)

    def test_program_schedules(self):
        from migrations.migrate_program_schedules import migrate_program_schedules

        migrate_program_schedules()
        
        # Test STE Schedule
        ste_sched = database.get_program_schedule("STE")
        self.assertTrue(len(ste_sched) > 0)
        has_research = any("RESEARCH 8" in s['subject'] for s in ste_sched)
        self.assertTrue(has_research, "STE should have Research")
        
        # Test Regular Schedule
        reg_sched = database.get_program_schedule("Regular")
        self.assertTrue(len(reg_sched) > 0)
        has_research_reg = any("RESEARCH" in s['subject'] for s in reg_sched)
        self.assertFalse(has_research_reg, "Regular should not have Research")
        
        science_block = next((s for s in reg_sched if s['subject'] == "Science"), None)
        self.assertIsNotNone(science_block, "Regular should have Science instead of Enhanced Science")
        self.assertEqual(science_block['time_range'], "08:00-08:45")
        
        # Test Admin Edit Persists
        success = database.update_program_schedule(science_block['id'], "08:00-09:00", "Science Lab", "Ms. Tester")
        self.assertTrue(success)
        
        # Reload and verify
        updated_sched = database.get_program_schedule("Regular")
        updated_block = next((s for s in updated_sched if s['id'] == science_block['id']), None)
        self.assertEqual(updated_block['time_range'], "08:00-09:00")
        self.assertEqual(updated_block['subject'], "Science Lab")
        self.assertEqual(updated_block['teacher'], "Ms. Tester")

    def test_audit_logging(self):
        database.initialize_db()
        action = "unit_test_event"
        database.log_audit_event("Admin", action, "tests", None, "Audit log test")
        
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM audit_logs WHERE action = %s", (action,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        
        cursor.execute("DELETE FROM audit_logs WHERE action = %s", (action,))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    unittest.main()
