"""
Migration: Sections
Creates the sections and section_schedules tables, then migrates existing
section names from the users table into proper section records with
schedules copied from the matching program_schedules template.
"""
import database


def migrate_sections():
    # Ensure all tables (including new ones) exist
    database.initialize_db()

    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Gather unique (section, program_type) pairs from existing users
    cursor.execute("""
        SELECT DISTINCT section, program_type
        FROM users
        WHERE section IS NOT NULL AND section != ''
    """)
    existing = cursor.fetchall()

    migrated = 0
    for row in existing:
        section_name = row['section']
        program_type = row['program_type'] or 'Regular'
        if program_type == 'N/A':
            program_type = 'Regular'

        # Skip if section already exists
        cursor.execute("SELECT id FROM sections WHERE name = %s", (section_name,))
        if cursor.fetchone():
            print(f"  Section '{section_name}' already exists, skipping.")
            continue

        # Create the section
        cursor.execute(
            "INSERT INTO sections (name, program_type) VALUES (%s, %s)",
            (section_name, program_type)
        )
        section_id = cursor.lastrowid

        # Copy schedule rows from the program template
        cursor.execute(
            "SELECT time_range, subject, teacher FROM program_schedules WHERE program_type = %s ORDER BY id ASC",
            (program_type,)
        )
        template_rows = cursor.fetchall()
        for t in template_rows:
            cursor.execute(
                "INSERT INTO section_schedules (section_id, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                (section_id, t['time_range'], t['subject'], t['teacher'])
            )

        migrated += 1
        print(f"  Migrated section '{section_name}' (template: {program_type}, {len(template_rows)} schedule rows)")

    conn.commit()
    conn.close()
    print(f"\nDone. {migrated} section(s) migrated.")


if __name__ == "__main__":
    migrate_sections()
