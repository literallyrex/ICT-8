from database import (
    add_announcement,
    create_section,
    delete_announcement,
    delete_section,
    delete_user,
    get_all_sections,
    get_all_users,
    get_announcements,
    get_connection,
    get_section_names,
    get_student_grades,
    get_user_by_id,
    log_audit_event,
    search_users,
    update_program_schedule,
    update_section,
    update_user_details,
    update_user_status,
)
from services import AttendanceService, GradeService, ProfilePictureService, ScheduleService
from utils.validation import validate_email, validate_phone


class AdminController:
    def __init__(self, grade_service=None, attendance_service=None, schedule_service=None, profile_picture_service=None):
        self.grade_service = grade_service or GradeService()
        self.attendance_service = attendance_service or AttendanceService()
        self.schedule_service = schedule_service or ScheduleService()
        self.profile_picture_service = profile_picture_service or ProfilePictureService()

    def get_user_management_data(self, search_query="", status_filter="All", program_filter="All", grade_filter="All", sort_by="id", sort_order="DESC"):
        users = search_users(search_query, status_filter, program_filter, grade_filter, sort_by, sort_order)
        all_users = get_all_users()
        return {
            "users": users,
            "stats": {
                "total": len(all_users),
                "pending": sum(1 for user in all_users if user.get("status") == "Pending"),
                "approved": sum(1 for user in all_users if user.get("status") == "Approved"),
            },
        }

    def get_sections_with_counts(self):
        sections = get_all_sections()
        enriched = []
        for section in sections:
            copy_row = dict(section)
            copy_row["schedule_count"] = len(self.schedule_service.get_section_schedules(section["id"]))
            enriched.append(copy_row)
        return enriched

    def create_section(self, name, program_type):
        name = name.strip()
        if not name:
            return {"success": False, "message": "Section name is required."}
        if len(name) < 2:
            return {"success": False, "message": "Section name is too short."}

        result = create_section(name, program_type)
        if not result:
            return {"success": False, "message": "Failed to create section. Name may already exist."}

        log_audit_event("Admin", "create_section", "sections", result, f"Created section '{name}' with template {program_type}")
        return {"success": True, "message": f"Section '{name}' created!", "section_id": result}

    def rename_section(self, section_id, current_name, new_name):
        new_name = new_name.strip()
        if not new_name or len(new_name) < 2:
            return {"success": False, "message": "Please enter a valid name (at least 2 characters)."}

        if not update_section(section_id, new_name):
            return {"success": False, "message": "Rename failed. Name may already be taken."}

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET section = %s WHERE section = %s", (new_name, current_name))
            conn.commit()
        except Exception:
            pass
        finally:
            if "conn" in locals() and conn.is_connected():
                conn.close()

        log_audit_event("Admin", "rename_section", "sections", section_id, f"'{current_name}' -> '{new_name}'")
        return {"success": True, "message": f"Section renamed to '{new_name}'."}

    def delete_section(self, section_id, section_name):
        if not delete_section(section_id):
            return {"success": False, "message": "Failed to delete section."}
        log_audit_event("Admin", "delete_section", "sections", section_id, f"Deleted section '{section_name}'")
        return {"success": True}

    def get_section_names(self):
        return get_section_names()

    def get_section_schedule(self, section_id):
        return self.schedule_service.get_section_schedules(section_id)

    def add_section_schedule(self, section_id):
        result = self.schedule_service.add_section_schedule(section_id, "0:00-0:00", "New Subject")
        return {"success": bool(result), "id": result}

    def update_section_schedule(self, schedule_id, time_range, subject, teacher):
        if not time_range or not subject:
            return {"success": False, "message": "Time and Subject are required."}
        if not self.schedule_service.update_section_schedule(schedule_id, time_range, subject, teacher):
            return {"success": False, "message": "Failed to save."}
        return {"success": True}

    def delete_section_schedule(self, schedule_id):
        return self.schedule_service.delete_section_schedule(schedule_id)

    def get_program_schedule(self, program_type):
        return self.schedule_service.get_program_schedule(program_type)

    def update_program_schedule(self, schedule_id, time_range, subject, teacher):
        if not time_range or not subject:
            return {"success": False, "message": "Time and Subject cannot be empty."}
        if not update_program_schedule(schedule_id, time_range, subject, teacher):
            return {"success": False, "message": "Failed to update schedule."}
        return {"success": True}

    def get_analytics_data(self):
        users = get_all_users()
        students = [user for user in users if user.get("user_role") == "Student" and user.get("status") == "Approved"]

        category_grade_map = {}
        for student in students:
            category = student.get("course_category") or "Unknown"
            grades = get_student_grades(student["id"])
            for grade in grades:
                if grade.get("final"):
                    category_grade_map.setdefault(category, []).append(grade["final"])

        category_averages = {
            category: sum(values) / len(values)
            for category, values in category_grade_map.items()
            if values
        }

        enrollment_counts = {}
        for student in students:
            category = student.get("course_category") or "Unknown"
            enrollment_counts[category] = enrollment_counts.get(category, 0) + 1

        return {
            "category_averages": category_averages,
            "enrollment_counts": enrollment_counts,
        }

    def get_student_export_rows(self):
        rows = []
        for user in search_users():
            if user.get("user_role") == "Admin":
                continue
            rows.append([
                user.get("id", ""),
                user.get("username", ""),
                user.get("full_name", ""),
                user.get("gender", ""),
                user.get("age", ""),
                user.get("email", ""),
                user.get("phone", ""),
                user.get("course_category", ""),
                user.get("program_type", ""),
                user.get("course", ""),
                user.get("grade", ""),
                user.get("section", ""),
                user.get("status", ""),
            ])
        return rows

    def get_attendance_export_rows(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT u.full_name, u.student_id, u.course, a.date, a.status, a.remarks
                FROM attendance a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.date DESC
                """
            )
            return {
                "success": True,
                "rows": [
                    [row["full_name"], row["student_id"], row["course"], row["date"], row["status"], row["remarks"]]
                    for row in cursor.fetchall()
                ],
            }
        except Exception as error:
            return {"success": False, "message": str(error)}
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def get_user(self, user_id):
        return get_user_by_id(user_id)

    def prepare_grade_editor(self, user_id):
        user = get_user_by_id(user_id)
        if not user:
            return None
        grades = self.grade_service.get_student_grades(user_id, initialize_if_missing=True)
        return {"user": user, "grades": grades}

    def save_grade_changes(self, raw_updates):
        return self.grade_service.save_grade_updates(raw_updates)

    def get_attendance_context(self, user_id):
        user = get_user_by_id(user_id)
        if not user:
            return None
        return {
            "user": user,
            "history": self.attendance_service.get_history(user_id),
        }

    def record_attendance(self, user_id, date_text, status, remarks=""):
        return self.attendance_service.record_attendance(user_id, date_text, status, remarks)

    def approve_user(self, user_id, grade, section):
        if not section:
            return {"success": False, "message": "Section/Class is required."}
        if not update_user_status(user_id, "Approved", section, grade):
            return {"success": False, "message": "Failed to approve user."}

        log_audit_event("Admin", "approve_user", "users", user_id, f"Assigned {grade} - {section}")
        return {"success": True, "message": f"User approved!\nAssigned to {grade} - {section}"}

    def delete_user(self, user_id):
        if delete_user(user_id):
            return {"success": True, "message": "User deleted successfully."}
        return {"success": False, "message": "Failed to delete user."}

    def list_announcements(self):
        return get_announcements()

    def post_announcement(self, message):
        message = message.strip()
        if not message:
            return {"success": False, "message": "Message cannot be empty."}
        if not add_announcement(message):
            return {"success": False, "message": "Failed to post."}
        return {"success": True, "message": "Announcement posted!"}

    def delete_announcement(self, announcement_id):
        return delete_announcement(announcement_id)

    def update_user(self, user_id, updates):
        clean_updates = {key: (value.strip() if isinstance(value, str) else value) for key, value in updates.items()}

        if clean_updates.get("email") and not validate_email(clean_updates["email"]):
            return {"success": False, "title": "Invalid Email", "message": "Please enter a valid email address."}

        if clean_updates.get("phone") and not validate_phone(clean_updates["phone"]):
            return {"success": False, "title": "Invalid Phone", "message": "Phone must start with +63 followed by 10 digits."}

        category = clean_updates.get("course_category", "")
        program_type = clean_updates.get("program_type", "N/A")

        if category == "Regular Program":
            clean_updates["course"] = "REGULAR"
            clean_updates["program_type"] = "N/A"
        elif program_type == "STE":
            clean_updates["course"] = "STE"
        elif program_type == "SPJ":
            clean_updates["course"] = "SPJ"
        elif program_type == "SPA":
            clean_updates["course"] = "SPA"
        else:
            clean_updates["course"] = "UNKNOWN"

        if not update_user_details(user_id, **clean_updates):
            return {"success": False, "message": "Update failed."}

        return {"success": True, "message": "Details updated successfully."}

    def load_profile_picture(self, relative_path, size=(150, 150)):
        return self.profile_picture_service.load_profile_picture(relative_path, size=size)
