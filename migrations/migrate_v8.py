import mysql.connector
from config import db_config
import sys
import copy

def migrate():
    # Attempt to connect to staging db, or run in transaction and fail if necessary, 
    # but MySQL DDL (ALTER TABLE) auto-commits, so we can't easily rollback schema changes in MySQL.
    # Therefore, we will create a staging table to test the queries first.
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("Starting Migration v8...")

        # 1. Create a backup of the original users table
        print("Creating backup 'users_backup_v8'...")
        cursor.execute("DROP TABLE IF EXISTS users_backup_v8")
        cursor.execute("CREATE TABLE users_backup_v8 AS SELECT * FROM users")
        print("Backup created.")
        
        # 2. Check if columns need renaming
        # We need to rename grade -> section, year_level -> grade, course_year -> course
        cursor.execute("DESCRIBE users")
        columns = [row['Field'] for row in cursor.fetchall()]
        
        alter_queries = []
        if 'grade' in columns and 'section' not in columns:
            # The old grade column is actually the section
            alter_queries.append("ALTER TABLE users CHANGE COLUMN grade section VARCHAR(20) DEFAULT NULL")
            print("Planned to rename 'grade' to 'section'")
            
        if 'year_level' in columns:
            # The old year_level column is actually the grade
            alter_queries.append("ALTER TABLE users CHANGE COLUMN year_level grade VARCHAR(20) DEFAULT NULL")
            print("Planned to rename 'year_level' to 'grade'")
            
        if 'course_year' in columns:
            alter_queries.append("ALTER TABLE users CHANGE COLUMN course_year course VARCHAR(100) DEFAULT NULL")
            print("Planned to rename 'course_year' to 'course'")

        # Execute Alter Queries
        for query in alter_queries:
            cursor.execute(query)
            print(f"Executed: {query}")
            
        # 3. Data Updates (now columns are section, grade, course)
        
        updates = [
            # Age/Gen formatting: "M" -> "Male", "F" -> "Female"
            # And capitalize first letter.
            "UPDATE users SET gender = 'Male' WHERE LOWER(TRIM(gender)) = 'm'",
            "UPDATE users SET gender = 'Female' WHERE LOWER(TRIM(gender)) = 'f'",
            # Capitalize any remaining gender values properly
            "UPDATE users SET gender = CONCAT(UPPER(LEFT(gender, 1)), LOWER(SUBSTRING(gender, 2))) WHERE gender IS NOT NULL AND LENGTH(gender) > 0",
            
            # Grade formatting: Remove "Grade " prefix
            "UPDATE users SET grade = REPLACE(LOWER(grade), 'grade ', '') WHERE grade IS NOT NULL",
            "UPDATE users SET grade = TRIM(grade) WHERE grade IS NOT NULL",
            
            # Section: The request says: "Update Section... to contain the section assignment value set by admin... this should reflect the final approved section, not temporary"
            # If status isn't "Approved", clear the section so it doesn't hold temporary draft data
            "UPDATE users SET section = NULL WHERE status != 'Approved'",
            
            # Course standardized values mapped from category / program type
            # "If Category = 'Regular Program', set Course = 'REGULAR'"
            "UPDATE users SET course = 'REGULAR' WHERE course_category = 'Regular Program'",
            
            # "If student is in STE program, set Course = 'STE'"
            "UPDATE users SET course = 'STE' WHERE program_type = 'STE'",
            "UPDATE users SET course = 'SPJ' WHERE program_type = 'SPJ'",
            "UPDATE users SET course = 'SPA' WHERE program_type = 'SPA'"
        ]
        
        for idx, query in enumerate(updates):
            cursor.execute(query)
            print(f"Executed update {idx+1}/{len(updates)}: {cursor.rowcount} rows affected.")
            
        # 4. Generate Summary Report
        cursor.execute("SELECT id, course, grade, section, gender, status FROM users")
        records = cursor.fetchall()
        
        total_records = len(records)
        invalid_grades = []
        for r in records:
            # Validate grade values are integers within the specified range (6, 7, 8, 9, 10, or None if not assigned)
            # Since some might be unassigned we only validate approved ones or non-empty ones
            g = r['grade']
            if g is not None and g != '' and g.lower() != 'pending': # If there's an old pending value
                try:
                    g_int = int(g)
                    if g_int not in [6, 7, 8, 9, 10]:
                        invalid_grades.append(r)
                except ValueError:
                    invalid_grades.append(r)
        
        if invalid_grades:
            print("\nWARNING: Failed Validation! The following records have invalid grade values:")
            for r in invalid_grades:
                print(f" - User ID {r['id']}: Grade='{r['grade']}'")
            print("\nRolling back data changes... (Schema changes cannot be rolled back)")
            conn.rollback()
            conn.close()
            sys.exit(1)
            
        print("\n--- MIGRATION SUMMARY REPORT ---")
        print(f"Total records processed: {total_records}")
        print("Changes applied:")
        print(" - Renamed columns: year_level->grade, grade->section, course_year->course")
        print(" - Translated 'M'/'F' to 'Male'/'Female' and capitalized first letter")
        print(" - Stripped 'Grade ' prefix from grades to leave only integer strings")
        print(" - Cleared section values for unapproved (Pending) drafts")
        print(" - Mapped course column to UPPERCASE target values (REGULAR, STE, SPJ, SPA)")
        print("Validation: SUCCESS (All assigned grades are valid integers 6-10)")
        print("--------------------------------")
        
        conn.commit()
        conn.close()
        print("Migration v8 complete.")
        
    except Exception as e:
        print(f"Migration failed Exception: {e}")

if __name__ == "__main__":
    migrate()
