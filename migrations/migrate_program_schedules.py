import database

def migrate_program_schedules():
    # Make sure tables exist
    database.initialize_db()
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Clear existing
    cursor.execute("DELETE FROM program_schedules")
    
    if True:
        ste_schedule = [
            ("7:15-7:30", "Hygiene Activity", ""),
            ("7:30-8:00", "FLAG CEREMONY", ""),
            ("7:25-8:45", "ENHANCED SCIENCE 8", ""),
            ("8:45-9:30", "MAPEH 8", ""),
            ("9:30-10:15", "NATIONAL MATHEMATICS PROGRAM (NMP)", ""),
            ("10:15-10:30", "HEALTH BREAK", ""),
            ("10:30-11:15", "MATHEMATICS 8", ""),
            ("11:15-12:00", "ENGLISH 8", ""),
            ("12:00-1:00", "LUNCH BREAK", ""),
            ("1:00-1:45", "TLE-CTE II", ""),
            ("1:45-2:30", "FILIPINO 8", ""),
            ("2:30-3:15", "ARALING PANLIPUNAN 9", ""),
            ("3:15-4:00", "RESEARCH 8", ""),
            ("4:00-4:45", "EDUKASYONG PAGPAPAHALAGA 8", "")
        ]
        
        regular_schedule = [
            ("7:15-7:30", "Hygiene Activity", ""),
            ("7:30-8:00", "FLAG CEREMONY", ""),
            ("08:00-08:45", "Science", ""),
            ("8:45-9:30", "MAPEH 8", ""),
            ("9:30-10:15", "NATIONAL MATHEMATICS PROGRAM (NMP)", ""),
            ("10:15-10:30", "HEALTH BREAK", ""),
            ("10:30-11:15", "MATHEMATICS 8", ""),
            ("11:15-12:00", "ENGLISH 8", ""),
            ("12:00-1:00", "LUNCH BREAK", ""),
            ("1:00-1:45", "TLE", ""),
            ("1:45-2:30", "FILIPINO 8", ""),
            ("2:30-3:15", "ARALING PANLIPUNAN 9", ""),
            # Research removed
            ("4:00-4:45", "EDUKASYONG PAGPAPAHALAGA 8", "")
        ]
        
        for time_range, subject, teacher in ste_schedule:
            cursor.execute("INSERT INTO program_schedules (program_type, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                           ("STE", time_range, subject, teacher))
                           
        for time_range, subject, teacher in regular_schedule:
            cursor.execute("INSERT INTO program_schedules (program_type, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                           ("Regular", time_range, subject, teacher))
                           
        # Add basic for SPJ and SPA based on Regular (since not specified, just copy Regular)
        for time_range, subject, teacher in regular_schedule:
            cursor.execute("INSERT INTO program_schedules (program_type, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                           ("SPJ", time_range, subject, teacher))
            cursor.execute("INSERT INTO program_schedules (program_type, time_range, subject, teacher) VALUES (%s, %s, %s, %s)",
                           ("SPA", time_range, subject, teacher))
                           
        conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_program_schedules()
    print("Migration complete!")
