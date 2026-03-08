import customtkinter as ctk
import tkinter.messagebox as messagebox

from utils.constants import ACCENT, DANGER, PRIMARY, SCHOOL_NAME, SUCCESS, TEXT_MUTED, WARNING
from views.base_view import BaseView, MAP_AVAILABLE


class StudentDashboardView(BaseView):
    def __init__(self, app, student_controller, auth_controller):
        super().__init__(app)
        self.student_controller = student_controller
        self.auth_controller = auth_controller

    def show_dashboard(self):
        self.clear_window()
        self.geometry("900x750")

        current_user = self.app.current_user
        if not current_user:
            self.show_login()
            return

        context = self.student_controller.build_dashboard_context(current_user["id"])
        if not context:
            self.app.current_user = None
            self.show_login()
            return

        self.app.current_user = context["user"]
        user = context["user"]

        top_bar = ctk.CTkFrame(self.app, height=55, corner_radius=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        if self.logo_small:
            ctk.CTkLabel(top_bar, text="", image=self.logo_small).pack(side="left", padx=(15, 5))
        ctk.CTkLabel(top_bar, text=SCHOOL_NAME, font=("Roboto", 13, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(top_bar, text=f"| Welcome, {user.get('full_name', 'Student')}!", font=("Roboto", 13), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(
            top_bar,
            text="Log Out",
            command=self.show_login,
            width=85,
            height=32,
            fg_color=DANGER,
            hover_color="#C03030",
            corner_radius=8,
            font=("Roboto", 12, "bold"),
        ).pack(side="right", padx=20, pady=12)

        rank = context["rank"]
        status = user.get("status", "Pending")
        banner_color = SUCCESS if status == "Approved" else WARNING
        banner_text = f"Account Approved | Rank: {rank['display']}" if status == "Approved" else "Your account is pending approval"

        banner = ctk.CTkFrame(self.app, height=45, fg_color=banner_color, corner_radius=8)
        banner.pack(fill="x", padx=20, pady=(10, 5))
        banner.pack_propagate(False)

        if status != "Approved":
            ctk.CTkLabel(banner, text=banner_text, font=("Roboto", 13, "bold"), text_color="white").pack(expand=True)
        else:
            left_frame = ctk.CTkFrame(banner, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True, padx=20)
            ctk.CTkLabel(left_frame, text=banner_text, font=("Roboto", 13, "bold"), text_color=rank["color"]).pack(side="left")

            if context["attendance_summary"] or context["grades"]:
                progress_frame = ctk.CTkFrame(banner, fg_color="transparent")
                progress_frame.pack(side="right", fill="y", padx=20, pady=10)
                ctk.CTkLabel(progress_frame, text=f"{rank['score']:.1f}%", font=("Roboto", 11, "bold"), text_color="white").pack(side="right", padx=(5, 0))
                progress_bar = ctk.CTkProgressBar(progress_frame, width=150, height=10, progress_color=rank["color"])
                progress_bar.pack(side="right")
                progress_bar.set(min(rank["score"] / 100.0, 1.0))

        tab_view = ctk.CTkTabview(self.app, corner_radius=10)
        tab_view.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        tab_profile = tab_view.add("Profile")
        tab_grades = tab_view.add("Grades")
        tab_attendance = tab_view.add("Attendance")
        tab_timetable = tab_view.add("Timetable")
        tab_settings = tab_view.add("Settings")

        self.build_profile_tab(tab_profile, context)
        self.build_grades_tab(tab_grades, context)
        self.build_attendance_tab(tab_attendance, context)
        self.build_timetable_tab(tab_timetable, context)
        self.build_settings_tab(tab_settings, context)

    def build_profile_tab(self, parent, context):
        user = context["user"]
        content = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        content.pack(fill="both", expand=True)

        profile_card = ctk.CTkFrame(content, corner_radius=12)
        profile_card.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(profile_card, text="My Profile", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        profile_fields = [
            ("Username", user.get("username", "")),
            ("Full Name", user.get("full_name", "")),
            ("Age", user.get("age", "")),
            ("Gender", user.get("gender", "")),
            ("Email", user.get("email", "")),
            ("Phone", user.get("phone", "")),
            ("Address", user.get("address", "") or "-"),
            ("Student ID", user.get("student_id", "") or "-"),
            ("Course", user.get("course", "") or "-"),
            ("Grade", user.get("grade", "") or "-"),
            ("Section", user.get("section", "") or "-"),
        ]

        for label, value in profile_fields:
            field_row = ctk.CTkFrame(profile_card, fg_color="transparent")
            field_row.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(field_row, text=f"{label}:", font=("Roboto", 12, "bold"), width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(field_row, text=str(value), font=("Roboto", 12), anchor="w").pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(profile_card, text="").pack(pady=3)

        announcement_frame = ctk.CTkFrame(content, corner_radius=12)
        announcement_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(announcement_frame, text="Announcements", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        announcements = context["announcements"]
        if not announcements:
            ctk.CTkLabel(announcement_frame, text="No active announcements.", font=("Roboto", 12), text_color=TEXT_MUTED).pack(pady=10)
        else:
            for item in announcements:
                row = ctk.CTkFrame(announcement_frame, fg_color="transparent")
                row.pack(fill="x", padx=18, pady=4)
                ctk.CTkLabel(row, text=item["message"], font=("Roboto", 12), wraplength=550, justify="left").pack(side="left")
                ctk.CTkLabel(row, text=item["created_at"].strftime("%b %d, %H:%M"), font=("Roboto", 11), text_color=TEXT_MUTED).pack(side="right")

        tips_frame = ctk.CTkFrame(content, corner_radius=12)
        tips_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(tips_frame, text="Quick Tips", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))
        ctk.CTkLabel(tips_frame, text="- Navigate to the Settings tab to update your contact info.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 5))
        ctk.CTkLabel(tips_frame, text="- Important announcements will appear here.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 15))

    def build_grades_tab(self, parent, context):
        user = context["user"]
        if user.get("status") != "Approved":
            ctk.CTkLabel(parent, text="Grades are only available for approved students.", font=("Roboto", 14), text_color=WARNING).pack(pady=40)
            return

        grades = context["grades"]
        if not grades:
            ctk.CTkLabel(parent, text="No grade records found. Please contact admin.", font=("Roboto", 14), text_color=TEXT_MUTED).pack(pady=40)
            return

        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 15))
        ctk.CTkLabel(header_frame, text="REPORT ON LEARNING PROGRESS AND ACHIEVEMENT", font=("Roboto", 16, "bold")).pack()
        ctk.CTkLabel(header_frame, text=f"Year: {user.get('grade', '')} | Section: {user.get('section', '')}", font=("Roboto", 12)).pack(pady=(5, 0))

        table_frame = ctk.CTkFrame(parent, corner_radius=0)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ["Learning Areas", "Q1", "Q2", "Q3", "Q4", "Final Grade", "Remarks"]
        widths = [200, 50, 50, 50, 50, 80, 100]

        header_row = ctk.CTkFrame(table_frame, fg_color=ACCENT, height=40, corner_radius=0)
        header_row.pack(fill="x")
        for column, width in zip(columns, widths):
            ctk.CTkLabel(header_row, text=column, width=width, font=("Roboto", 12, "bold"), text_color="white").pack(side="left", padx=1)

        total_final = 0
        total_count = 0
        for grade in grades:
            row = ctk.CTkFrame(table_frame, height=35, corner_radius=0, fg_color=("gray85", "gray20"))
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=grade["subject"], width=widths[0], anchor="w", font=("Roboto", 12)).pack(side="left", padx=5)
            for index, quarter in enumerate(["q1", "q2", "q3", "q4"]):
                value = grade.get(quarter)
                ctk.CTkLabel(row, text=str(value) if value is not None else "", width=widths[index + 1], font=("Roboto", 12)).pack(side="left", padx=1)

            final_grade = grade.get("final")
            ctk.CTkLabel(row, text=str(final_grade) if final_grade is not None else "", width=widths[5], font=("Roboto", 12, "bold")).pack(side="left", padx=1)
            remarks = grade.get("remarks") or ""
            color = SUCCESS if remarks and remarks.lower() == "passed" else (DANGER if remarks and remarks.lower() == "failed" else TEXT_MUTED)
            ctk.CTkLabel(row, text=remarks, width=widths[6], font=("Roboto", 11), text_color=color).pack(side="left", padx=1)

            if final_grade is not None:
                total_final += final_grade
                total_count += 1

        average = round(total_final / total_count) if total_count > 0 else ""
        average_row = ctk.CTkFrame(table_frame, height=40, corner_radius=0, fg_color=ACCENT)
        average_row.pack(fill="x", pady=(2, 0))
        total_width = widths[0] + (widths[1] * 4)
        ctk.CTkLabel(average_row, text="General Average", width=total_width, anchor="e", font=("Roboto", 12, "bold"), text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(average_row, text=str(average), width=widths[5], font=("Roboto", 12, "bold"), text_color="white").pack(side="left", padx=1)

    def build_attendance_tab(self, parent, context):
        content = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        content.pack(fill="both", expand=True)

        summary_card = ctk.CTkFrame(content, corner_radius=12)
        summary_card.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(summary_card, text="Attendance Summary", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        summary_rows = context["attendance_summary"]
        status_map = {row["status"]: row["count"] for row in summary_rows}
        summary_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        summary_frame.pack(fill="x", padx=18, pady=(0, 20))

        for status in ["Present", "Absent", "Late", "Excused"]:
            count = status_map.get(status, 0)
            color = SUCCESS if status == "Present" else (DANGER if status == "Absent" else WARNING)
            box = ctk.CTkFrame(summary_frame, width=150, height=80, corner_radius=12)
            box.pack(side="left", padx=5, fill="x", expand=True)
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=status, font=("Roboto", 13, "bold"), text_color=color).pack(pady=(12, 0))
            ctk.CTkLabel(box, text=str(count), font=("Roboto", 24, "bold")).pack()

        log_card = ctk.CTkFrame(content, corner_radius=12)
        log_card.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(log_card, text="Attendance Log", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        history = context["attendance_history"]
        if not history:
            ctk.CTkLabel(log_card, text="No attendance records found.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(pady=30)
            return

        header_row = ctk.CTkFrame(log_card, fg_color=ACCENT, height=38, corner_radius=5)
        header_row.pack(fill="x", padx=18, pady=(0, 5))
        ctk.CTkLabel(header_row, text="Date", width=120, font=("Roboto", 12, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header_row, text="Status", width=100, font=("Roboto", 12, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header_row, text="Remarks", font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=20, fill="x", expand=True)

        for record in history:
            row = ctk.CTkFrame(log_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=3)
            color = SUCCESS if record["status"] == "Present" else (DANGER if record["status"] == "Absent" else WARNING)
            ctk.CTkLabel(row, text=str(record["date"]), width=120, font=("Roboto", 12)).pack(side="left")
            ctk.CTkLabel(row, text=record["status"], width=100, font=("Roboto", 12, "bold"), text_color=color).pack(side="left")
            ctk.CTkLabel(row, text=record["remarks"] or "-", font=("Roboto", 11), text_color=TEXT_MUTED, anchor="w", justify="left", wraplength=450).pack(side="left", padx=20, fill="x", expand=True)

    def build_timetable_tab(self, parent, context):
        content = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        content.pack(fill="both", expand=True)

        card = ctk.CTkFrame(content, corner_radius=12)
        card.pack(fill="both", expand=True, pady=(5, 10))

        timetable = context["timetable"]
        ctk.CTkLabel(card, text=f"Class Schedule ({timetable['schedule_label']})", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        schedules = timetable["schedules"]
        if not schedules:
            ctk.CTkLabel(card, text="No schedule available. The admin needs to configure it.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(pady=20)
            return

        header_row = ctk.CTkFrame(card, fg_color=ACCENT, height=35, corner_radius=5)
        header_row.pack(fill="x", padx=18, pady=(5, 0))
        ctk.CTkLabel(header_row, text="Time", width=150, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_row, text="Subject", width=250, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_row, text="Teacher", font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=10, fill="x", expand=True)

        for schedule in schedules:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text=schedule["time_range"], width=150, font=("Roboto", 12), anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=schedule["subject"], width=250, font=("Roboto", 12), anchor="w").pack(side="left", padx=10)
            teacher_display = schedule["teacher"] if schedule.get("teacher") else "-"
            ctk.CTkLabel(row, text=teacher_display, font=("Roboto", 12), anchor="w", text_color=TEXT_MUTED if not schedule.get("teacher") else "white").pack(side="left", padx=10, fill="x", expand=True)

    def build_settings_tab(self, parent, context):
        user = context["user"]
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Account Settings", font=("Roboto", 18, "bold")).pack(pady=(5, 15), anchor="w", padx=20)

        fields = {}
        definitions = [
            ("email", "Email (@yourdomain.com)"),
            ("phone", "Phone (+63XXXXXXXXXX)"),
            ("address", "Home Address"),
        ]

        contact_frame = ctk.CTkFrame(scroll, corner_radius=12)
        contact_frame.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(contact_frame, text="Contact Information", font=("Roboto", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))

        for key, label in definitions:
            ctk.CTkLabel(contact_frame, text=label, font=("Roboto", 11, "bold"), anchor="w", text_color=TEXT_MUTED).pack(padx=15, anchor="w")
            entry_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
            entry_frame.pack(fill="x", padx=15, pady=(0, 10))

            entry = ctk.CTkEntry(entry_frame, placeholder_text=label, height=36, corner_radius=8)
            value = user.get(key, "") or ""
            if key == "phone" and not value:
                value = "+63"
            entry.insert(0, value)

            if key == "address":
                entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
                if MAP_AVAILABLE:
                    ctk.CTkButton(
                        entry_frame,
                        text="Map",
                        width=75,
                        height=36,
                        corner_radius=8,
                        fg_color=ACCENT,
                        hover_color="#0A2647",
                        font=("Roboto", 11),
                        command=lambda current_entry=entry: self.open_map_picker(current_entry),
                    ).pack(side="left")
            else:
                entry.pack(fill="x", expand=True)
            fields[key] = entry

        def save_settings():
            updates = {key: entry.get() for key, entry in fields.items()}
            result = self.student_controller.update_settings(user["id"], updates)
            if result.get("success"):
                messagebox.showinfo("Success", result["message"])
                self.app.current_user = self.student_controller.get_user(user["id"])
                self.show_student_dashboard()
                return
            messagebox.showerror(result.get("title", "Error"), result["message"])

        ctk.CTkButton(contact_frame, text="Save Changes", command=save_settings, width=150, height=36, corner_radius=8, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold")).pack(anchor="e", padx=15, pady=(10, 15))

        password_frame = ctk.CTkFrame(scroll, corner_radius=12)
        password_frame.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(password_frame, text="Security", font=("Roboto", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))
        ctk.CTkLabel(password_frame, text="Update your password to keep your account secure.", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=15, pady=(0, 10))
        ctk.CTkButton(password_frame, text="Change Password", width=180, height=36, corner_radius=8, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 13, "bold"), command=self.student_change_password).pack(anchor="w", padx=15, pady=(0, 15))

    def student_change_password(self):
        user = self.app.current_user
        if not user:
            return

        window = ctk.CTkToplevel(self.app)
        window.title("Change Password")
        window.geometry("400x380")
        window.grab_set()
        window.resizable(False, False)
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text="Change Password", font=("Roboto", 18, "bold")).pack(pady=(20, 20))

        ctk.CTkLabel(window, text="Current Password", font=("Roboto", 11), anchor="w").pack(padx=40, anchor="w")
        current_entry = ctk.CTkEntry(window, placeholder_text="Enter current password", show="*", width=310, height=38, corner_radius=10)
        current_entry.pack(pady=(0, 10), padx=40)

        ctk.CTkLabel(window, text="New Password", font=("Roboto", 11), anchor="w").pack(padx=40, anchor="w")
        new_entry = ctk.CTkEntry(window, placeholder_text="Enter new password", show="*", width=310, height=38, corner_radius=10)
        new_entry.pack(pady=(0, 10), padx=40)

        ctk.CTkLabel(window, text="Confirm New Password", font=("Roboto", 11), anchor="w").pack(padx=40, anchor="w")
        confirm_entry = ctk.CTkEntry(window, placeholder_text="Confirm new password", show="*", width=310, height=38, corner_radius=10)
        confirm_entry.pack(pady=(0, 15), padx=40)

        def save_password():
            result = self.auth_controller.change_student_password(user, current_entry.get(), new_entry.get(), confirm_entry.get())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=window)
                window.destroy()
                return
            messagebox.showerror("Error", result["message"], parent=window)

        ctk.CTkButton(window, text="Update Password", command=save_password, width=310, height=40, corner_radius=10, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold")).pack(pady=(5, 15), padx=40)

