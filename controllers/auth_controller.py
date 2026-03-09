from database import add_user, get_user_by_username, update_password, username_exists, verify_login
from services import ProfilePictureService
from utils.auth import hash_password
from utils.constants import ADMIN_PASSWORD
from utils.validation import validate_email, validate_phone


class AuthController:
    def __init__(self, profile_picture_service=None):
        self.profile_picture_service = profile_picture_service or ProfilePictureService()

    def login_student(self, username, password):
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return {"success": False, "message": "All fields are required.", "level": "error"}

        user = verify_login(username, hash_password(password))
        if not user:
            return {"success": False, "message": "Invalid username or password.", "level": "error"}

        status = user.get("status")
        if status == "Pending":
            return {
                "success": False,
                "message": "Your registration is still pending admin approval.\nPlease wait for the admin to approve your account.",
                "level": "warning",
            }
        if status != "Approved":
            return {
                "success": False,
                "message": f"Account status: {status or 'Unknown'}",
                "level": "warning",
            }

        return {"success": True, "user": user}

    def login_admin(self, username, password):
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return {"success": False, "message": "All fields are required."}

        if password != ADMIN_PASSWORD:
            return {"success": False, "message": "Invalid Admin Password."}

        return {"success": True, "username": username}

    def register_student(self, payload):
        username = payload.get("username", "").strip()
        password = payload.get("password", "").strip()
        full_name = payload.get("full_name", "").strip()
        email = payload.get("email", "").strip()
        phone = payload.get("phone", "").strip()
        student_id = payload.get("student_id", "").strip()
        address = payload.get("address", "").strip()
        age = payload.get("age", "").strip()
        gender = payload.get("gender", "")
        category = payload.get("course_category", "")
        program = payload.get("program_type", "N/A")
        profile_picture = payload.get("profile_picture") or None

        if gender.startswith("Select"):
            return {"success": False, "message": "Please select your gender."}
        if category.startswith("Select"):
            return {"success": False, "message": "Please select a program category before registering."}
        if category == "Special Programs" and program.startswith("Select"):
            return {"success": False, "message": "Please select a special program type (STE, SPJ, or SPA)."}

        if not all([username, password, full_name, email, phone, student_id, address, age]):
            return {"success": False, "message": "All fields are required."}

        try:
            age_value = int(age)
        except ValueError:
            return {"success": False, "message": "Age must be a number."}

        if not validate_email(email):
            return {
                "success": False,
                "message": "Please enter a valid email address.\n\nExample: user@example.com",
                "title": "Invalid Email",
            }

        if not validate_phone(phone):
            return {
                "success": False,
                "message": "Phone number must start with +63 followed by 10 digits.\n\nExample: +639171234567",
                "title": "Invalid Phone",
            }

        if username_exists(username):
            return {
                "success": False,
                "message": "Username already exists. Please choose a different one.",
            }

        if category == "Regular Program":
            course = "REGULAR"
            program = "Regular"
        elif program == "STE":
            course = "STE"
        elif program == "SPJ":
            course = "SPJ"
        elif program == "SPA":
            course = "SPA"
        else:
            course = "UNKNOWN"

        success = add_user(
            username,
            hash_password(password),
            full_name,
            email,
            phone,
            "Student",
            address=address,
            student_id=student_id,
            course=course,
            age=age_value,
            gender=gender,
            course_category=category,
            program_type=program,
            grade="Pending",
            profile_picture=profile_picture,
        )

        if not success:
            return {"success": False, "message": "Registration failed. Please try again."}

        return {
            "success": True,
            "message": "Registration submitted!\n\nStatus: Pending Admin Approval\nYou can log in once an admin approves your account.",
        }

    def upload_profile_picture(self, source_path, username_hint="student", previous_path=None):
        result = self.profile_picture_service.save_profile_picture(source_path, filename_hint=username_hint)
        if result.get("success") and previous_path and previous_path != result.get("relative_path"):
            self.profile_picture_service.delete_profile_picture(previous_path)
        return result

    def load_profile_picture(self, relative_path, size=(150, 150)):
        return self.profile_picture_service.load_profile_picture(relative_path, size=size)

    def start_password_reset(self, username):
        username = username.strip()
        if not username:
            return {"success": False, "message": "Username is required."}

        user_data = get_user_by_username(username)
        if not user_data:
            return {"success": False, "message": "Username not found."}

        return {"success": True, "user_data": user_data, "username": username}

    def verify_password_reset_identity(self, user_data, email, phone):
        if email.strip() == user_data["email"] and phone.strip() == user_data["phone"]:
            return {"success": True}
        return {"success": False, "message": "Email or phone number does not match."}

    def reset_password(self, username, password, confirm_password):
        password = password.strip()
        confirm_password = confirm_password.strip()

        if not password:
            return {"success": False, "message": "Password cannot be empty."}
        if password != confirm_password:
            return {"success": False, "message": "Passwords do not match."}
        if update_password(username, hash_password(password)):
            return {"success": True, "message": "Password updated successfully!"}
        return {"success": False, "message": "Update failed."}

    def change_student_password(self, user, current_password, new_password, confirm_password):
        current_password = current_password.strip()
        new_password = new_password.strip()
        confirm_password = confirm_password.strip()

        if not all([current_password, new_password, confirm_password]):
            return {"success": False, "message": "All fields are required."}

        current_hash = hash_password(current_password)
        if not verify_login(user["username"], current_hash):
            return {"success": False, "message": "Current password is incorrect."}

        if new_password != confirm_password:
            return {"success": False, "message": "New passwords do not match."}

        if len(new_password) < 4:
            return {"success": False, "message": "Password must be at least 4 characters."}

        if update_password(user["username"], hash_password(new_password)):
            return {"success": True, "message": "Password changed successfully!"}

        return {"success": False, "message": "Password update failed."}
