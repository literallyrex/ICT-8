from database import get_announcements, get_user_by_id, update_user_details
from services import AttendanceService, GradeService, ProfilePictureService, ScheduleService, SocialService
from utils.validation import validate_email, validate_phone


class StudentController:
    def __init__(self, grade_service=None, attendance_service=None, schedule_service=None, profile_picture_service=None, social_service=None):
        self.grade_service = grade_service or GradeService()
        self.attendance_service = attendance_service or AttendanceService()
        self.schedule_service = schedule_service or ScheduleService()
        self.profile_picture_service = profile_picture_service or ProfilePictureService()
        self.social_service = social_service or SocialService()

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
            "social": self.social_service.get_dashboard_data(user_id),
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

    def load_profile_picture(self, relative_path, size=(150, 150)):
        return self.profile_picture_service.load_profile_picture(relative_path, size=size)

    def update_profile_picture(self, user_id, source_path):
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        old_picture = user.get("profile_picture")
        result = self.profile_picture_service.save_profile_picture(source_path, filename_hint=user.get("username", "student"))
        if not result.get("success"):
            return result

        new_picture = result["relative_path"]
        if not update_user_details(user_id, profile_picture=new_picture):
            self.profile_picture_service.delete_profile_picture(new_picture)
            return {"success": False, "message": "Failed to save the new profile picture."}

        if old_picture and old_picture != new_picture:
            self.profile_picture_service.delete_profile_picture(old_picture)

        return {
            "success": True,
            "message": "Profile picture updated successfully!",
            "relative_path": new_picture,
        }

    def search_students(self, current_user_id, query):
        return self.social_service.search_students(current_user_id, query)

    def get_social_dashboard_data(self, user_id):
        return self.social_service.get_dashboard_data(user_id)

    def send_friend_request(self, sender_id, receiver_id):
        return self.social_service.send_friend_request(sender_id, receiver_id)

    def respond_to_friend_request(self, user_id, request_id, action):
        return self.social_service.respond_to_friend_request(user_id, request_id, action)

    def get_conversation(self, user_id, friend_id):
        return self.social_service.get_conversation(user_id, friend_id)

    def send_message(self, sender_id, receiver_id, message_text):
        return self.social_service.send_message(sender_id, receiver_id, message_text)
