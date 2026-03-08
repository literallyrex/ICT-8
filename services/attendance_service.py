import datetime

from database import get_attendance_summary, get_user_attendance, mark_attendance


class AttendanceService:
    def get_history(self, user_id):
        return get_user_attendance(user_id)

    def get_summary(self, user_id):
        return get_attendance_summary(user_id)

    def calculate_attendance_percentage(self, summary_rows):
        total_days = sum(row["count"] for row in summary_rows)
        present_count = next((row["count"] for row in summary_rows if row["status"] == "Present"), 0)
        if total_days <= 0:
            return 0.0
        return (present_count / total_days) * 100

    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."

    def record_attendance(self, user_id, date_text, status, remarks=""):
        valid, message = self.validate_date(date_text)
        if not valid:
            return {"success": False, "message": message}

        if not mark_attendance(user_id, date_text, status, remarks):
            return {"success": False, "message": "Failed to save attendance."}

        return {"success": True, "message": "Attendance recorded!"}
