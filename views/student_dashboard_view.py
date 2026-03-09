from tkinter import filedialog

import customtkinter as ctk
import tkinter.messagebox as messagebox

from utils.constants import ACCENT, BG_CARD, DANGER, PRIMARY, SCHOOL_NAME, SUCCESS, TEXT_MUTED, WARNING
from views.base_view import BaseView, MAP_AVAILABLE


class StudentDashboardView(BaseView):
    def __init__(self, app, student_controller, auth_controller):
        super().__init__(app)
        self.student_controller = student_controller
        self.auth_controller = auth_controller
        self.profile_picture_image = None
        self.student_tab_view = None
        self.chat_refresh_job = None
        self.active_chat_friend = None
        self.social_search_var = None
        self.social_search_results_frame = None
        self.social_requests_frame = None
        self.social_friends_frame = None
        self.social_friends_label = None
        self.chat_friends_frame = None
        self.chat_friends_label = None
        self.chat_header_avatar_label = None
        self.chat_header_avatar_image = None
        self.chat_header_label = None
        self.chat_messages_frame = None
        self.chat_entry = None
        self.chat_send_button = None
        self.chat_empty_state_label = None
        self.settings_profile_picture_image = None

    def show_dashboard(self):
        self._cancel_chat_refresh()
        self.clear_window()
        self.geometry("1100x760")

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
            command=self.logout_student,
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
        self.student_tab_view = tab_view

        tab_profile = tab_view.add("Profile")
        tab_grades = tab_view.add("Grades")
        tab_attendance = tab_view.add("Attendance")
        tab_timetable = tab_view.add("Timetable")
        tab_friends = tab_view.add("Friends")
        tab_chat = tab_view.add("Chat")
        tab_settings = tab_view.add("Settings")

        self.build_profile_tab(tab_profile, context)
        self.build_grades_tab(tab_grades, context)
        self.build_attendance_tab(tab_attendance, context)
        self.build_timetable_tab(tab_timetable, context)
        self.build_friends_tab(tab_friends, context)
        self.build_chat_tab(tab_chat, context)
        self.build_settings_tab(tab_settings, context)
        self.render_search_results(None)
        self.refresh_social_lists(context.get("social", {}))
        self._schedule_social_refresh()

    def logout_student(self):
        self._cancel_chat_refresh()
        self.show_login()

    def _cancel_chat_refresh(self):
        if self.chat_refresh_job is not None:
            try:
                self.app.after_cancel(self.chat_refresh_job)
            except Exception:
                pass
            self.chat_refresh_job = None

    def build_profile_tab(self, parent, context):
        user = context["user"]
        content = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        content.pack(fill="both", expand=True)

        profile_card = ctk.CTkFrame(content, corner_radius=12)
        profile_card.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(profile_card, text="My Profile", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 10))

        overview_row = ctk.CTkFrame(profile_card, fg_color="transparent")
        overview_row.pack(fill="x", padx=18, pady=(0, 10))

        picture_frame = ctk.CTkFrame(overview_row, width=160, height=160, corner_radius=12)
        picture_frame.pack(side="left", padx=(0, 15))
        picture_frame.pack_propagate(False)

        picture_result = self.student_controller.load_profile_picture(user.get("profile_picture"), size=(150, 150))
        if picture_result.get("success") and picture_result.get("image") is not None:
            self.profile_picture_image = ctk.CTkImage(
                light_image=picture_result["image"],
                dark_image=picture_result["image"],
                size=(150, 150),
            )
            ctk.CTkLabel(picture_frame, text="", image=self.profile_picture_image).pack(expand=True)
        else:
            self.profile_picture_image = None
            placeholder_text = "No Profile\nPicture"
            if user.get("profile_picture"):
                placeholder_text = "Profile Picture\nMissing"
            ctk.CTkLabel(picture_frame, text=placeholder_text, font=("Roboto", 12), justify="center").pack(expand=True)

        summary_frame = ctk.CTkFrame(overview_row, fg_color="transparent")
        summary_frame.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(summary_frame, text=user.get("full_name", "Student"), font=("Roboto", 18, "bold")).pack(anchor="w", pady=(10, 4))
        ctk.CTkLabel(summary_frame, text=f"Student ID: {user.get('student_id', '-') or '-'}", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=2)
        ctk.CTkLabel(summary_frame, text=f"Program: {user.get('course', '-') or '-'}", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=2)
        ctk.CTkLabel(summary_frame, text=f"Grade / Section: {user.get('grade', '-') or '-'} / {user.get('section', '-') or '-'}", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=2)

        profile_fields = [
            ("Username", user.get("username", "")),
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
        ctk.CTkLabel(tips_frame, text="- Use the Friends tab to add classmates, then open the Chat tab to message them.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 5))
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

    def _get_display_name(self, person):
        return person.get("full_name") or person.get("username") or "Student"

    def _get_person_initials(self, person):
        letters = [part[:1].upper() for part in self._get_display_name(person).split() if part]
        initials = "".join(letters[:2])
        return initials or "?"

    def _get_person_subtitle(self, person):
        return f"@{person.get('username', '')} | {person.get('grade', '-') or '-'} | {person.get('section', '-') or '-'}"

    def _create_social_avatar(self, parent, person, size=(48, 48)):
        avatar_frame = ctk.CTkFrame(parent, width=size[0], height=size[1], corner_radius=max(12, size[0] // 2), fg_color=ACCENT)
        avatar_frame.pack_propagate(False)

        picture_result = self.student_controller.load_profile_picture(person.get("profile_picture"), size=size)
        if picture_result.get("success") and picture_result.get("image") is not None:
            avatar_image = ctk.CTkImage(
                light_image=picture_result["image"],
                dark_image=picture_result["image"],
                size=size,
            )
            avatar_label = ctk.CTkLabel(avatar_frame, text="", image=avatar_image)
            avatar_label.image = avatar_image
        else:
            avatar_label = ctk.CTkLabel(
                avatar_frame,
                text=self._get_person_initials(person),
                font=("Roboto", max(12, size[0] // 3), "bold"),
            )

        avatar_label.pack(expand=True, fill="both")
        return avatar_frame, avatar_label

    def _bind_chat_open(self, widgets, friend_data, switch_tab=False):
        for widget in widgets:
            if widget is None:
                continue
            widget.bind("<Button-1>", lambda _event, data=dict(friend_data), change_tab=switch_tab: self.open_chat(data, switch_tab=change_tab))
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass

    def _update_chat_header(self):
        if not self.chat_header_label or not self.chat_header_label.winfo_exists():
            return

        if not self.active_chat_friend:
            self.chat_header_label.configure(text="Select a friend to start chatting")
            if self.chat_header_avatar_label and self.chat_header_avatar_label.winfo_exists():
                self.chat_header_avatar_image = None
                self.chat_header_avatar_label.configure(text="?", image=None)
            return

        self.chat_header_label.configure(text=f"Chat with {self._get_display_name(self.active_chat_friend)}")
        if not self.chat_header_avatar_label or not self.chat_header_avatar_label.winfo_exists():
            return

        picture_result = self.student_controller.load_profile_picture(self.active_chat_friend.get("profile_picture"), size=(44, 44))
        if picture_result.get("success") and picture_result.get("image") is not None:
            self.chat_header_avatar_image = ctk.CTkImage(
                light_image=picture_result["image"],
                dark_image=picture_result["image"],
                size=(44, 44),
            )
            self.chat_header_avatar_label.configure(text="", image=self.chat_header_avatar_image)
        else:
            self.chat_header_avatar_image = None
            self.chat_header_avatar_label.configure(text=self._get_person_initials(self.active_chat_friend), image=None)

    def build_friends_tab(self, parent, context):
        social_container = ctk.CTkFrame(parent, fg_color="transparent")
        social_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = ctk.CTkFrame(social_container, width=360, corner_radius=12)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        right_panel = ctk.CTkFrame(social_container, corner_radius=12)
        right_panel.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left_panel, text="Find Students", font=("Roboto", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 8))
        search_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_row.pack(fill="x", padx=15, pady=(0, 8))

        self.social_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_row, placeholder_text="Search by name or username", textvariable=self.social_search_var, height=34)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        search_entry.bind("<Return>", lambda _event: self.run_student_search())
        ctk.CTkButton(search_row, text="Search", width=74, height=34, corner_radius=8, fg_color=ACCENT, hover_color="#0A2647", command=self.run_student_search).pack(side="left")

        self.social_search_results_frame = ctk.CTkScrollableFrame(left_panel, height=190, corner_radius=10)
        self.social_search_results_frame.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkLabel(left_panel, text="Incoming Requests", font=("Roboto", 15, "bold")).pack(anchor="w", padx=15, pady=(0, 8))
        self.social_requests_frame = ctk.CTkScrollableFrame(left_panel, height=190, corner_radius=10)
        self.social_requests_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(right_panel, text="Friends", font=("Roboto", 16, "bold")).pack(anchor="w", padx=18, pady=(15, 6))
        ctk.CTkLabel(
            right_panel,
            text="Click a friend to open the Chat tab and start messaging.",
            font=("Roboto", 12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=18, pady=(0, 10))

        self.social_friends_label = ctk.CTkLabel(right_panel, text="Friends (0)", font=("Roboto", 15, "bold"))
        self.social_friends_label.pack(anchor="w", padx=18, pady=(0, 8))
        self.social_friends_frame = ctk.CTkScrollableFrame(right_panel, corner_radius=10)
        self.social_friends_frame.pack(fill="both", expand=True, padx=18, pady=(0, 15))

    def build_chat_tab(self, parent, context):
        chat_container = ctk.CTkFrame(parent, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)

        sidebar = ctk.CTkFrame(chat_container, width=300, corner_radius=12)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)

        chat_panel = ctk.CTkFrame(chat_container, corner_radius=12)
        chat_panel.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(sidebar, text="Chat Friends", font=("Roboto", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 6))
        ctk.CTkLabel(
            sidebar,
            text="Select any friend below to load your conversation.",
            font=("Roboto", 12),
            text_color=TEXT_MUTED,
            wraplength=240,
            justify="left",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        self.chat_friends_label = ctk.CTkLabel(sidebar, text="Friends (0)", font=("Roboto", 15, "bold"))
        self.chat_friends_label.pack(anchor="w", padx=15, pady=(0, 8))
        self.chat_friends_frame = ctk.CTkScrollableFrame(sidebar, corner_radius=10)
        self.chat_friends_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        header_frame = ctk.CTkFrame(chat_panel, height=70, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)

        avatar_frame = ctk.CTkFrame(header_frame, width=48, height=48, corner_radius=24, fg_color=ACCENT)
        avatar_frame.pack(side="left", padx=(15, 10), pady=11)
        avatar_frame.pack_propagate(False)
        self.chat_header_avatar_label = ctk.CTkLabel(avatar_frame, text="?", font=("Roboto", 16, "bold"))
        self.chat_header_avatar_label.pack(expand=True, fill="both")

        self.chat_header_label = ctk.CTkLabel(header_frame, text="Select a friend to start chatting", font=("Roboto", 16, "bold"))
        self.chat_header_label.pack(side="left", padx=(0, 15), pady=15)

        self.chat_messages_frame = ctk.CTkScrollableFrame(chat_panel, corner_radius=12)
        self.chat_messages_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        composer_frame = ctk.CTkFrame(chat_panel, corner_radius=12)
        composer_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.chat_entry = ctk.CTkEntry(composer_frame, placeholder_text="Type a message...", height=40)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=12)
        self.chat_entry.bind("<Return>", lambda _event: self.send_chat_message())
        self.chat_send_button = ctk.CTkButton(
            composer_frame,
            text="Send",
            width=100,
            height=40,
            corner_radius=10,
            fg_color=SUCCESS,
            hover_color="#248A5E",
            font=("Roboto", 12, "bold"),
            command=self.send_chat_message,
        )
        self.chat_send_button.pack(side="left", padx=(0, 12), pady=12)
        self._set_chat_input_enabled(False)
        self.render_chat_messages([])

    def refresh_social_lists(self, social_data):
        requests = social_data.get("incoming_requests", [])
        friends = social_data.get("friends", [])
        current_friend_id = self.active_chat_friend["id"] if self.active_chat_friend else None
        friend_lookup = {friend["id"]: dict(friend) for friend in friends}

        if current_friend_id in friend_lookup:
            self.active_chat_friend = friend_lookup[current_friend_id]
        elif friends:
            self.active_chat_friend = dict(friends[0])
        else:
            self.active_chat_friend = None

        self.render_request_list(requests)
        if self.social_friends_label and self.social_friends_label.winfo_exists():
            self.social_friends_label.configure(text=f"Friends ({len(friends)})")
        if self.chat_friends_label and self.chat_friends_label.winfo_exists():
            self.chat_friends_label.configure(text=f"Friends ({len(friends)})")

        self.render_friends_list(friends)
        self.render_chat_friend_list(friends)
        self._update_chat_header()
        self._set_chat_input_enabled(bool(self.active_chat_friend))

        if self.active_chat_friend:
            self.refresh_active_chat(show_errors=False)
        else:
            self.render_chat_messages([])

    def run_student_search(self):
        current_user = self.app.current_user
        if not current_user:
            return

        query = self.social_search_var.get().strip() if self.social_search_var else ""
        if not query:
            self.render_search_results(None)
            return

        results = self.student_controller.search_students(current_user["id"], query)
        self.render_search_results(results)

    def render_search_results(self, results):
        if not self.social_search_results_frame or not self.social_search_results_frame.winfo_exists():
            return

        for widget in self.social_search_results_frame.winfo_children():
            widget.destroy()

        if results is None:
            ctk.CTkLabel(
                self.social_search_results_frame,
                text="Search approved students by name or username.",
                text_color=TEXT_MUTED,
                font=("Roboto", 12),
                wraplength=230,
                justify="left",
            ).pack(anchor="w", padx=8, pady=12)
            return

        if not results:
            ctk.CTkLabel(self.social_search_results_frame, text="No students found.", text_color=TEXT_MUTED, font=("Roboto", 12)).pack(pady=12)
            return

        status_map = {
            "friends": ("Open Chat", "chat"),
            "incoming_request": ("Check Requests", "disabled"),
            "outgoing_request": ("Request Sent", "disabled"),
            "none": ("Add Friend", "add"),
        }

        for student in results:
            row = ctk.CTkFrame(self.social_search_results_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=2)

            content_row = ctk.CTkFrame(row, fg_color="transparent")
            content_row.pack(fill="x", padx=10, pady=10)

            avatar_frame, _avatar_label = self._create_social_avatar(content_row, student, size=(42, 42))
            avatar_frame.pack(side="left", padx=(0, 10))

            text_column = ctk.CTkFrame(content_row, fg_color="transparent")
            text_column.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(text_column, text=self._get_display_name(student), font=("Roboto", 12, "bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_column, text=self._get_person_subtitle(student), font=("Roboto", 11), text_color=TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 2))

            button_text, action_type = status_map.get(student.get("relationship_status", "none"), ("Add Friend", "add"))
            button_color = SUCCESS if action_type == "add" else PRIMARY if action_type == "chat" else BG_CARD
            button_state = "normal" if action_type in {"add", "chat"} else "disabled"
            command = None
            if action_type == "add":
                command = lambda user_id=student["id"]: self.send_friend_request(user_id)
            elif action_type == "chat":
                command = lambda friend_data=dict(student): self.open_chat(friend_data, switch_tab=True)
            ctk.CTkButton(
                content_row,
                text=button_text,
                width=110,
                height=30,
                corner_radius=8,
                fg_color=button_color,
                hover_color="#248A5E" if action_type == "add" else "#185A8C" if action_type == "chat" else BG_CARD,
                font=("Roboto", 11, "bold"),
                state=button_state,
                command=command,
            ).pack(side="right", padx=(10, 0))

    def render_request_list(self, requests):
        if not self.social_requests_frame or not self.social_requests_frame.winfo_exists():
            return

        for widget in self.social_requests_frame.winfo_children():
            widget.destroy()

        if not requests:
            ctk.CTkLabel(self.social_requests_frame, text="No incoming requests.", text_color=TEXT_MUTED, font=("Roboto", 12)).pack(pady=12)
            return

        for request in requests:
            row = ctk.CTkFrame(self.social_requests_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=2)

            top_row = ctk.CTkFrame(row, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 6))
            avatar_frame, _avatar_label = self._create_social_avatar(top_row, request, size=(40, 40))
            avatar_frame.pack(side="left", padx=(0, 10))

            text_column = ctk.CTkFrame(top_row, fg_color="transparent")
            text_column.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(text_column, text=self._get_display_name(request), font=("Roboto", 12, "bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_column, text=f"@{request.get('username', '')}", font=("Roboto", 11), text_color=TEXT_MUTED).pack(anchor="w")

            button_row = ctk.CTkFrame(row, fg_color="transparent")
            button_row.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkButton(
                button_row,
                text="Accept",
                width=82,
                height=28,
                corner_radius=8,
                fg_color=SUCCESS,
                hover_color="#248A5E",
                font=("Roboto", 11, "bold"),
                command=lambda request_id=request["id"]: self.handle_friend_request(request_id, "accept"),
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                button_row,
                text="Reject",
                width=82,
                height=28,
                corner_radius=8,
                fg_color=DANGER,
                hover_color="#C03030",
                font=("Roboto", 11, "bold"),
                command=lambda request_id=request["id"]: self.handle_friend_request(request_id, "reject"),
            ).pack(side="left")

    def render_friends_list(self, friends):
        if not self.social_friends_frame or not self.social_friends_frame.winfo_exists():
            return

        active_friend_id = self.active_chat_friend["id"] if self.active_chat_friend else None
        for widget in self.social_friends_frame.winfo_children():
            widget.destroy()

        if not friends:
            ctk.CTkLabel(
                self.social_friends_frame,
                text="No friends yet. Accept a request or add a classmate to start chatting.",
                text_color=TEXT_MUTED,
                font=("Roboto", 12),
                wraplength=420,
                justify="left",
            ).pack(anchor="w", padx=10, pady=12)
            return

        for friend in friends:
            is_active = active_friend_id == friend["id"]
            row = ctk.CTkFrame(self.social_friends_frame, corner_radius=8, fg_color=ACCENT if is_active else BG_CARD)
            row.pack(fill="x", pady=3, padx=2)
            friend_snapshot = dict(friend)

            content_row = ctk.CTkFrame(row, fg_color="transparent")
            content_row.pack(fill="x", padx=10, pady=10)

            avatar_frame, avatar_label = self._create_social_avatar(content_row, friend, size=(48, 48))
            avatar_frame.pack(side="left", padx=(0, 12))

            text_column = ctk.CTkFrame(content_row, fg_color="transparent")
            text_column.pack(side="left", fill="x", expand=True)
            name_label = ctk.CTkLabel(
                text_column,
                text=self._get_display_name(friend),
                font=("Roboto", 12, "bold"),
                anchor="w",
                text_color="white" if is_active else ("gray10", "gray95"),
            )
            name_label.pack(anchor="w")

            subtitle_label = ctk.CTkLabel(
                text_column,
                text=self._get_person_subtitle(friend),
                font=("Roboto", 11),
                text_color="white" if is_active else TEXT_MUTED,
                anchor="w",
            )
            subtitle_label.pack(anchor="w", pady=(0, 2))

            ctk.CTkButton(
                content_row,
                text="Open Chat",
                width=100,
                height=32,
                corner_radius=8,
                fg_color=PRIMARY,
                hover_color="#185A8C",
                font=("Roboto", 11, "bold"),
                command=lambda friend_data=friend_snapshot: self.open_chat(friend_data, switch_tab=True),
            ).pack(side="right")

            self._bind_chat_open(
                [row, content_row, avatar_frame, avatar_label, text_column, name_label, subtitle_label],
                friend_snapshot,
                switch_tab=True,
            )

    def render_chat_friend_list(self, friends):
        if not self.chat_friends_frame or not self.chat_friends_frame.winfo_exists():
            return

        active_friend_id = self.active_chat_friend["id"] if self.active_chat_friend else None
        for widget in self.chat_friends_frame.winfo_children():
            widget.destroy()

        if not friends:
            ctk.CTkLabel(
                self.chat_friends_frame,
                text="No friends available yet. Add classmates in the Friends tab first.",
                text_color=TEXT_MUTED,
                font=("Roboto", 12),
                wraplength=220,
                justify="left",
            ).pack(anchor="w", padx=8, pady=12)
            return

        for friend in friends:
            is_active = active_friend_id == friend["id"]
            row = ctk.CTkFrame(self.chat_friends_frame, corner_radius=8, fg_color=ACCENT if is_active else BG_CARD)
            row.pack(fill="x", pady=3, padx=2)
            friend_snapshot = dict(friend)

            content_row = ctk.CTkFrame(row, fg_color="transparent")
            content_row.pack(fill="x", padx=10, pady=10)

            avatar_frame, avatar_label = self._create_social_avatar(content_row, friend, size=(44, 44))
            avatar_frame.pack(side="left", padx=(0, 10))

            text_column = ctk.CTkFrame(content_row, fg_color="transparent")
            text_column.pack(side="left", fill="x", expand=True)
            name_label = ctk.CTkLabel(
                text_column,
                text=self._get_display_name(friend),
                font=("Roboto", 12, "bold"),
                anchor="w",
                text_color="white" if is_active else ("gray10", "gray95"),
            )
            name_label.pack(anchor="w")
            subtitle_label = ctk.CTkLabel(
                text_column,
                text=self._get_person_subtitle(friend),
                font=("Roboto", 10),
                text_color="white" if is_active else TEXT_MUTED,
                anchor="w",
            )
            subtitle_label.pack(anchor="w", pady=(0, 2))

            self._bind_chat_open(
                [row, content_row, avatar_frame, avatar_label, text_column, name_label, subtitle_label],
                friend_snapshot,
            )

    def send_friend_request(self, receiver_id):
        current_user = self.app.current_user
        if not current_user:
            return

        result = self.student_controller.send_friend_request(current_user["id"], receiver_id)
        if result.get("success"):
            messagebox.showinfo("Friends", result["message"])
            self._refresh_social_content()
            return

        messagebox.showwarning("Friends", result["message"])

    def handle_friend_request(self, request_id, action):
        current_user = self.app.current_user
        if not current_user:
            return

        result = self.student_controller.respond_to_friend_request(current_user["id"], request_id, action)
        if result.get("success"):
            messagebox.showinfo("Friends", result["message"])
            self._refresh_social_content()
            return

        messagebox.showerror("Friends", result["message"])

    def open_chat(self, friend_data, switch_tab=False):
        self.active_chat_friend = dict(friend_data)
        self._update_chat_header()
        self._set_chat_input_enabled(True)
        if switch_tab and self.student_tab_view and self.student_tab_view.winfo_exists():
            self.student_tab_view.set("Chat")
        self._refresh_social_content()
        if self.chat_entry and self.chat_entry.winfo_exists():
            self.app.after(50, self.chat_entry.focus_set)

    def refresh_active_chat(self, show_errors=False):
        if not self.active_chat_friend:
            self._update_chat_header()
            self._set_chat_input_enabled(False)
            self.render_chat_messages([])
            return

        current_user = self.app.current_user
        if not current_user:
            return

        result = self.student_controller.get_conversation(current_user["id"], self.active_chat_friend["id"])
        if not result.get("success"):
            if show_errors:
                messagebox.showerror("Chat", result["message"])
            self.active_chat_friend = None
            self._update_chat_header()
            self._set_chat_input_enabled(False)
            self.render_chat_messages([])
            return

        self.active_chat_friend = result["friend"]
        self._update_chat_header()
        self._set_chat_input_enabled(True)
        self.render_chat_messages(result["messages"])

    def render_chat_messages(self, messages):
        if not self.chat_messages_frame or not self.chat_messages_frame.winfo_exists():
            return

        for widget in self.chat_messages_frame.winfo_children():
            widget.destroy()

        if not messages:
            placeholder = "Choose a friend from the Friends tab or the sidebar to open your conversation."
            if self.active_chat_friend:
                placeholder = "No messages yet. Say hello to start the conversation."
            self.chat_empty_state_label = ctk.CTkLabel(
                self.chat_messages_frame,
                text=placeholder,
                font=("Roboto", 13),
                text_color=TEXT_MUTED,
            )
            self.chat_empty_state_label.pack(pady=50)
            return

        current_user_id = self.app.current_user["id"] if self.app.current_user else None
        for message in messages:
            is_sent = message["sender_id"] == current_user_id
            row = ctk.CTkFrame(self.chat_messages_frame, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=6)

            bubble = ctk.CTkFrame(row, corner_radius=12, fg_color=PRIMARY if is_sent else BG_CARD)
            if is_sent:
                bubble.pack(side="right", padx=(80, 0))
            else:
                avatar_frame, _avatar_label = self._create_social_avatar(row, self.active_chat_friend or {}, size=(34, 34))
                avatar_frame.pack(side="left", padx=(0, 8), pady=(6, 0))
                bubble.pack(side="left", padx=(0, 80))

            ctk.CTkLabel(
                bubble,
                text=message.get("message_text", ""),
                wraplength=360,
                justify="left",
                font=("Roboto", 12),
            ).pack(anchor="w", padx=12, pady=(10, 4))

            sent_at = message.get("sent_at")
            time_text = sent_at.strftime("%b %d, %I:%M %p") if hasattr(sent_at, "strftime") else str(sent_at)
            ctk.CTkLabel(bubble, text=time_text, font=("Roboto", 10), text_color=TEXT_MUTED).pack(anchor="e", padx=12, pady=(0, 8))

        canvas = getattr(self.chat_messages_frame, "_parent_canvas", None)
        if canvas is not None:
            self.app.after(10, lambda: canvas.yview_moveto(1.0))

    def send_chat_message(self):
        current_user = self.app.current_user
        if not current_user or not self.active_chat_friend or not self.chat_entry:
            return

        result = self.student_controller.send_message(current_user["id"], self.active_chat_friend["id"], self.chat_entry.get())
        if result.get("success"):
            self.chat_entry.delete(0, "end")
            self.refresh_active_chat(show_errors=False)
            self.chat_entry.focus_set()
            return

        messagebox.showwarning("Chat", result["message"])

    def _set_chat_input_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        if self.chat_entry and self.chat_entry.winfo_exists():
            if not enabled:
                self.chat_entry.configure(state="normal")
                self.chat_entry.delete(0, "end")
            self.chat_entry.configure(state=state)
        if self.chat_send_button and self.chat_send_button.winfo_exists():
            self.chat_send_button.configure(state=state)

    def _refresh_social_content(self):
        current_user = self.app.current_user
        if not current_user:
            return

        social_data = self.student_controller.get_social_dashboard_data(current_user["id"])
        self.refresh_social_lists(social_data)

        if self.social_search_var and self.social_search_var.get().strip():
            results = self.student_controller.search_students(current_user["id"], self.social_search_var.get())
            self.render_search_results(results)

    def _schedule_social_refresh(self):
        # Simple desktop "real-time" behavior: poll the latest requests, friends, and chat messages.
        self._cancel_chat_refresh()
        self.chat_refresh_job = self.app.after(2500, self._run_periodic_social_refresh)

    def _run_periodic_social_refresh(self):
        self.chat_refresh_job = None
        try:
            if not ((self.social_friends_frame and self.social_friends_frame.winfo_exists()) or (self.chat_friends_frame and self.chat_friends_frame.winfo_exists())):
                return
            self._refresh_social_content()
        except Exception:
            pass
        finally:
            if (self.social_friends_frame and self.social_friends_frame.winfo_exists()) or (self.chat_friends_frame and self.chat_friends_frame.winfo_exists()):
                self._schedule_social_refresh()

    def build_settings_tab(self, parent, context):
        user = context["user"]
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Account Settings", font=("Roboto", 18, "bold")).pack(pady=(5, 15), anchor="w", padx=20)

        picture_frame = ctk.CTkFrame(scroll, corner_radius=12)
        picture_frame.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(picture_frame, text="Profile Picture", font=("Roboto", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))

        picture_row = ctk.CTkFrame(picture_frame, fg_color="transparent")
        picture_row.pack(fill="x", padx=15, pady=(0, 15))

        preview_frame = ctk.CTkFrame(picture_row, width=160, height=160, corner_radius=12)
        preview_frame.pack(side="left", padx=(0, 15))
        preview_frame.pack_propagate(False)

        preview_label = ctk.CTkLabel(preview_frame, text="Loading...", font=("Roboto", 12))
        preview_label.pack(expand=True)

        button_column = ctk.CTkFrame(picture_row, fg_color="transparent")
        button_column.pack(side="left", fill="both", expand=True)
        status_label = ctk.CTkLabel(button_column, text="", font=("Roboto", 12), text_color=TEXT_MUTED, justify="left", wraplength=360)
        status_label.pack(anchor="w", pady=(8, 10))

        def refresh_settings_picture(current_user):
            picture_result = self.student_controller.load_profile_picture(current_user.get("profile_picture"), size=(150, 150))
            if picture_result.get("success") and picture_result.get("image") is not None:
                self.settings_profile_picture_image = ctk.CTkImage(
                    light_image=picture_result["image"],
                    dark_image=picture_result["image"],
                    size=(150, 150),
                )
                preview_label.configure(text="", image=self.settings_profile_picture_image)
                status_label.configure(text="Your current profile picture is saved and will appear in your profile tab.")
                return

            self.settings_profile_picture_image = None
            placeholder_text = "No Profile\nPicture"
            if current_user.get("profile_picture"):
                placeholder_text = "Profile Picture\nMissing"
            preview_label.configure(text=placeholder_text, image=None)
            if current_user.get("profile_picture"):
                status_label.configure(text="The saved picture file could not be found. Upload a new one to replace it.")
            else:
                status_label.configure(text="Upload a JPG, JPEG, or PNG image to personalize your account.")

        def change_profile_picture():
            file_path = filedialog.askopenfilename(
                title="Select New Profile Picture",
                filetypes=[
                    ("Image Files", "*.jpg *.jpeg *.png"),
                    ("JPEG Files", "*.jpg *.jpeg"),
                    ("PNG Files", "*.png"),
                ],
            )
            if not file_path:
                return

            result = self.student_controller.update_profile_picture(user["id"], file_path)
            if not result.get("success"):
                messagebox.showerror("Profile Picture", result["message"])
                return

            messagebox.showinfo("Profile Picture", result["message"])
            self.app.current_user = self.student_controller.get_user(user["id"])
            self.show_student_dashboard()

        ctk.CTkButton(
            button_column,
            text="Change Profile Picture",
            command=change_profile_picture,
            width=190,
            height=38,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color="#0A2647",
            font=("Roboto", 12, "bold"),
        ).pack(anchor="w", pady=(12, 6))
        ctk.CTkLabel(button_column, text="Supported formats: JPG, JPEG, PNG", font=("Roboto", 11), text_color=TEXT_MUTED).pack(anchor="w")

        refresh_settings_picture(user)

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

        custom_frame = ctk.CTkFrame(scroll, corner_radius=12)
        custom_frame.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(custom_frame, text="Interface Customization", font=("Roboto", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))

        ui_vars = {
            "ui_color": ctk.StringVar(value=user.get("ui_color") or "Blue"),
            "button_color": ctk.StringVar(value=user.get("button_color") or "Standard"),
            "theme_mode": ctk.StringVar(value=user.get("theme_mode") or "Dark"),
            "background_style": ctk.StringVar(value=user.get("background_style") or "Solid"),
            "profile_accent_color": ctk.StringVar(value=user.get("profile_accent_color") or "Blue"),
            "text_color": ctk.StringVar(value=user.get("text_color") or "Default")
        }

        def on_ui_change(*args):
            updates = {k: v.get() for k, v in ui_vars.items()}
            from utils.theme import apply_theme_to_app, apply_widget_colors
            self.student_controller.update_settings(user["id"], updates)
            user.update(updates)
            
            apply_theme_to_app(self.app, user)
            self.show_dashboard()
            
            if hasattr(self, "student_tab_view"):
                try:
                    self.student_tab_view.set("Settings")
                except Exception:
                    pass
            apply_widget_colors(self.app, user)

        opts = [
            ("Primary UI Color", "ui_color", ["Blue", "Green", "Purple", "Orange", "Red", "Gray"]),
            ("Button Color", "button_color", ["Standard", "Green", "Red", "Purple", "Orange", "Gray"]),
            ("Background Style", "background_style", ["Solid", "Gradient", "Subtle pattern", "Blurred panel style"]),
            ("Profile Accent Color", "profile_accent_color", ["Blue", "Green", "Purple", "Orange", "Red", "Gold"]),
            ("Text Color", "text_color", ["Default", "White", "Light Gray", "Dark Gray", "Black", "Gold", "Cyan"]),
        ]

        for label_text, key, options in opts:
            row_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkLabel(row_frame, text=label_text, font=("Roboto", 11, "bold"), text_color=TEXT_MUTED).pack(side="left")
            menu = ctk.CTkOptionMenu(row_frame, values=options, variable=ui_vars[key], command=lambda v: on_ui_change())
            menu.pack(side="right")
            
        row_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkLabel(row_frame, text="Dark / Light Mode", font=("Roboto", 11, "bold"), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkSwitch(row_frame, text="", variable=ui_vars["theme_mode"], onvalue="Dark", offvalue="Light", command=on_ui_change).pack(side="right")

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
