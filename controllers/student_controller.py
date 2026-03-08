from database import get_announcements, get_user_by_id, update_user_details
from services import AttendanceService, GradeService, ScheduleService
from utils.validation import validate_email, validate_phone


class StudentController:
    def __init__(self, grade_service=None, attendance_service=None, schedule_service=None):
        self.grade_service = grade_service or GradeService()
        self.attendance_service = attendance_service or AttendanceService()
        self.schedule_service = schedule_service or ScheduleService()

    def get_user(self, user_id):
        return get_user_by_id(user_id)

    def calculate_rank(self, attendance_percentage, grade_average):
        level_score = (attendance_percentage * 0.4) + (grade_average * 0.6)
        if level_score >= 90:
            return {
                "label": "Gold Scholar",
                "display": "?? Gold Scholar",
                "color": "#FFD700",
                "score": level_score,
            }
        if level_score >= 80:
            return {
                "label": "Silver Achiever",
                "display": "?? Silver Achiever",
                "color": "#C0C0C0",
                "score": level_score,
            }
        if level_score >= 70:
            return {
                "label": "Bronze Learner",
                "display": "?? Bronze Learner",
                "color": "#CD7F32",
                "score": level_score,
            }
        return {
            "label": "Rising Star",
            "display": "?? Rising Star",
            "color": "#6fa8dc",
            "score": level_score,
        }

    def build_dashboard_context(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return None

        grades = self.grade_service.get_student_grades(user_id)
        attendance_summary = self.attendance_service.get_summary(user_id)
        attendance_history = self.attendance_service.get_history(user_id)
        grade_average = self.grade_service.calculate_general_average(grades) or 0
        attendance_percentage = self.attendance_service.calculate_attendance_percentage(attendance_summary)
        rank = self.calculate_rank(attendance_percentage, grade_average)
        timetable = self.schedule_service.get_student_timetable(user)

        return {
            "user": user,
            "grades": grades,
            "announcements": get_announcements(),
            "attendance_summary": attendance_summary,
            "attendance_history": attendance_history,
            "attendance_percentage": attendance_percentage,
            "grade_average": grade_average,
            "rank": rank,
            "timetable": timetable,
        }

    def update_settings(self, user_id, updates):
        clean_updates = {key: value.strip() for key, value in updates.items()}

        if clean_updates.get("email") and not validate_email(clean_updates["email"]):
            return {"success": False, "title": "Invalid Email", "message": "Please enter a valid email address."}

        if clean_updates.get("phone") and not validate_phone(clean_updates["phone"]):
            return {"success": False, "title": "Invalid Phone", "message": "Phone must start with +63 followed by 10 digits."}

        if update_user_details(user_id, **clean_updates):
            return {"success": True, "message": "Settings updated successfully!"}

        return {"success": False, "message": "Failed to update settings."}
