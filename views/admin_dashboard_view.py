import csv
from tkinter import filedialog

import customtkinter as ctk
import tkinter.messagebox as messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utils.constants import ACCENT, BG_CARD, DANGER, PRIMARY, SCHOOL_NAME, SUCCESS, TEXT_MUTED, WARNING
from views.base_view import BaseView, MAP_AVAILABLE


class AdminDashboardView(BaseView):
    def __init__(self, app, admin_controller):
        super().__init__(app)
        self.admin_controller = admin_controller
        self.admin_tabs = None
        self.stats_label = None
        self.search_var = None
        self.status_filter = None
        self.program_filter = None
        self.grade_filter = None
        self.sort_var = None
        self.order_var = None
        self.scroll_frame = None
        self.sections_container = None
        self.schedule_program_var = None
        self.schedule_container = None
        self._table_cols = []

    def show_dashboard(self):
        self.clear_window()
        self.geometry("1250x750")

        top_bar = ctk.CTkFrame(self.app, height=56, corner_radius=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        if self.logo_small:
            ctk.CTkLabel(top_bar, text="", image=self.logo_small).pack(side="left", padx=(15, 5))
        ctk.CTkLabel(top_bar, text=SCHOOL_NAME, font=("Roboto", 14, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(top_bar, text="| Admin Dashboard", font=("Roboto", 14), text_color=TEXT_MUTED).pack(side="left")

        ctk.CTkButton(top_bar, text="Log Out", command=self.show_login, width=90, height=32, fg_color=DANGER, hover_color="#C03030", corner_radius=8, font=("Roboto", 12, "bold")).pack(side="right", padx=15, pady=12)
        ctk.CTkButton(top_bar, text="Announcements", command=self.show_announcements_manager, width=140, height=32, fg_color=ACCENT, hover_color="#0A2647", corner_radius=8, font=("Roboto", 12)).pack(side="right", padx=5, pady=12)

        self.admin_tabs = ctk.CTkTabview(self.app, corner_radius=10)
        self.admin_tabs.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        tab_users = self.admin_tabs.add("User Management")
        tab_sections = self.admin_tabs.add("Sections")
        tab_schedules = self.admin_tabs.add("Schedule Templates")
        tab_analytics = self.admin_tabs.add("Analytics & Export")

        top_row = ctk.CTkFrame(tab_users, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(8, 4))
        self.stats_label = ctk.CTkLabel(top_row, text="", font=("Roboto", 12), text_color=TEXT_MUTED)
        self.stats_label.pack(side="left")
        ctk.CTkButton(top_row, text="Refresh", command=self.refresh_dashboard, width=80, height=28, fg_color=ACCENT, hover_color="#0A2647", corner_radius=6, font=("Roboto", 11)).pack(side="right")

        filter_bar = ctk.CTkFrame(tab_users, corner_radius=8)
        filter_bar.pack(fill="x", padx=15, pady=(0, 8))
        filter_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=8)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_args: self.refresh_dashboard())
        ctk.CTkEntry(filter_frame, placeholder_text="Search...", width=200, height=30, corner_radius=8, textvariable=self.search_var).pack(side="left", padx=(0, 12))

        for label, attr_name, values, width in [
            ("Status:", "status_filter", ["All", "Pending", "Approved"], 95),
            ("Program:", "program_filter", ["All", "STE", "Regular", "SPJ", "SPA"], 100),
            ("Level:", "grade_filter", ["All", "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"], 100),
        ]:
            ctk.CTkLabel(filter_frame, text=label, font=("Roboto", 11)).pack(side="left", padx=(0, 3))
            menu = ctk.CTkOptionMenu(filter_frame, values=values, width=width, height=28, corner_radius=6, command=lambda _value: self.refresh_dashboard())
            menu.pack(side="left", padx=(0, 10))
            setattr(self, attr_name, menu)

        ctk.CTkLabel(filter_frame, text="Sort:", font=("Roboto", 11)).pack(side="left", padx=(0, 3))
        self.sort_var = ctk.StringVar(value="id")
        ctk.CTkOptionMenu(filter_frame, values=["id", "full_name", "grade", "section", "course_category"], variable=self.sort_var, command=lambda _value: self.refresh_dashboard(), width=100, height=28, corner_radius=6).pack(side="left", padx=(0, 6))
        self.order_var = ctk.StringVar(value="Descending")
        ctk.CTkSegmentedButton(filter_frame, values=["Ascending", "Descending"], variable=self.order_var, command=lambda _value: self.refresh_dashboard(), width=160, height=28).pack(side="left")

        self._table_cols = [
            ("ID", 40),
            ("Username", 100),
            ("Full Name", 160),
            ("Program", 95),
            ("Grade", 75),
            ("Section", 90),
            ("Status", 85),
        ]

        header_frame = ctk.CTkFrame(tab_users, height=32, corner_radius=6, fg_color=ACCENT)
        header_frame.pack(fill="x", padx=15, pady=(0, 2))
        header_frame.pack_propagate(False)
        for name, width in self._table_cols:
            ctk.CTkLabel(header_frame, text=name, width=width, anchor="w", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Actions", anchor="w", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=4, fill="x", expand=True)

        self.scroll_frame = ctk.CTkScrollableFrame(tab_users, corner_radius=8)
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.build_sections_tab(tab_sections)
        self.build_schedules_tab(tab_schedules)
        self.build_analytics_tab(tab_analytics)
        self.load_dashboard_users()

    def build_sections_tab(self, parent):
        top_frame = ctk.CTkFrame(parent, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(top_frame, text="Manage Sections", font=("Roboto", 16, "bold")).pack(side="left", padx=(0, 15))
        ctk.CTkButton(top_frame, text="+ Create Section", width=140, height=32, corner_radius=8, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 12, "bold"), command=self.open_create_section_dialog).pack(side="left")
        ctk.CTkButton(top_frame, text="Refresh", width=80, height=32, corner_radius=8, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 11), command=self.refresh_sections_list).pack(side="right")

        self.sections_container = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        self.sections_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.refresh_sections_list()

    def refresh_sections_list(self):
        for widget in self.sections_container.winfo_children():
            widget.destroy()

        sections = self.admin_controller.get_sections_with_counts()
        if not sections:
            ctk.CTkLabel(self.sections_container, text="No sections created yet. Click '+ Create Section' to add one.", text_color=TEXT_MUTED, font=("Roboto", 13)).pack(pady=30)
            return

        header_frame = ctk.CTkFrame(self.sections_container, fg_color=ACCENT, height=35)
        header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header_frame, text="Section Name", width=200, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Template", width=120, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Schedule Rows", width=100, font=("Roboto", 12, "bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Actions", font=("Roboto", 12, "bold"), text_color="white").pack(side="right", padx=15)

        for section in sections:
            row = ctk.CTkFrame(self.sections_container, corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=section["name"], width=200, font=("Roboto", 12), anchor="w").pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=section.get("program_type") or "-", width=120, font=("Roboto", 11), text_color=TEXT_MUTED, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(section["schedule_count"]), width=100, font=("Roboto", 11)).pack(side="left", padx=5)

            button_frame = ctk.CTkFrame(row, fg_color="transparent")
            button_frame.pack(side="right", padx=10)
            ctk.CTkButton(button_frame, text="Schedule", width=70, height=28, corner_radius=5, fg_color=PRIMARY, hover_color="#185A8C", font=("Roboto", 10), command=lambda sid=section["id"], name=section["name"]: self.open_section_schedule_editor(sid, name)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="Rename", width=60, height=28, corner_radius=5, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 10), command=lambda sid=section["id"], name=section["name"]: self.open_rename_section_dialog(sid, name)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="X", width=30, height=28, corner_radius=5, fg_color=DANGER, hover_color="#C03030", font=("Roboto", 10), command=lambda sid=section["id"], name=section["name"]: self.delete_section_action(sid, name)).pack(side="left", padx=2)

    def open_create_section_dialog(self):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Create Section")
        dialog.geometry("380x280")
        dialog.grab_set()
        dialog.resizable(False, False)
        self.setup_dialog_close(dialog)

        ctk.CTkLabel(dialog, text="Create New Section", font=("Roboto", 18, "bold")).pack(pady=(20, 15))
        ctk.CTkLabel(dialog, text="Section Name:", font=("Roboto", 12)).pack(anchor="w", padx=40)
        name_entry = ctk.CTkEntry(dialog, placeholder_text="e.g. Newton, Rizal...", width=300, height=36, corner_radius=8)
        name_entry.pack(pady=(0, 10), padx=40)

        ctk.CTkLabel(dialog, text="Schedule Template (program):", font=("Roboto", 12)).pack(anchor="w", padx=40)
        template_var = ctk.StringVar(value="Regular")
        ctk.CTkOptionMenu(dialog, variable=template_var, values=["STE", "Regular", "SPJ", "SPA"], width=300, height=36, corner_radius=8).pack(pady=(0, 15), padx=40)

        def confirm():
            result = self.admin_controller.create_section(name_entry.get(), template_var.get())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=dialog)
                dialog.destroy()
                self.refresh_sections_list()
                return
            messagebox.showerror("Error", result["message"], parent=dialog)

        ctk.CTkButton(dialog, text="Create Section", command=confirm, width=300, height=40, fg_color=SUCCESS, hover_color="#248A5E", corner_radius=10, font=("Roboto", 13, "bold")).pack(padx=40)

    def open_rename_section_dialog(self, section_id, current_name):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Rename Section")
        dialog.geometry("380x220")
        dialog.grab_set()
        dialog.resizable(False, False)
        self.setup_dialog_close(dialog)

        ctk.CTkLabel(dialog, text="Rename Section", font=("Roboto", 18, "bold")).pack(pady=(20, 15))
        ctk.CTkLabel(dialog, text="New Name:", font=("Roboto", 12)).pack(anchor="w", padx=40)
        name_entry = ctk.CTkEntry(dialog, width=300, height=36, corner_radius=8)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=(0, 15), padx=40)

        def confirm():
            result = self.admin_controller.rename_section(section_id, current_name, name_entry.get())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=dialog)
                dialog.destroy()
                self.refresh_sections_list()
                self.refresh_dashboard()
                return
            messagebox.showerror("Error", result["message"], parent=dialog)

        ctk.CTkButton(dialog, text="Save", command=confirm, width=300, height=40, fg_color=SUCCESS, hover_color="#248A5E", corner_radius=10, font=("Roboto", 13, "bold")).pack(padx=40)

    def delete_section_action(self, section_id, section_name):
        if not messagebox.askyesno("Confirm Delete", f"Delete section '{section_name}'?\n\nStudents assigned to this section will keep the name but it won't appear in the dropdown."):
            return
        result = self.admin_controller.delete_section(section_id, section_name)
        if result.get("success"):
            self.refresh_sections_list()
            return
        messagebox.showerror("Error", result["message"])

    def open_section_schedule_editor(self, section_id, section_name):
        window = ctk.CTkToplevel(self.app)
        window.title(f"Schedule: {section_name}")
        window.geometry("750x550")
        window.grab_set()
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text=f"Schedule for Section: {section_name}", font=("Roboto", 18, "bold")).pack(pady=(15, 10))

        def add_row():
            result = self.admin_controller.add_section_schedule(section_id)
            if result.get("success"):
                refresh()

        ctk.CTkButton(window, text="+ Add Row", width=100, height=30, corner_radius=6, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 11, "bold"), command=add_row).pack(pady=(0, 5))

        scroll = ctk.CTkScrollableFrame(window, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        def refresh():
            for widget in scroll.winfo_children():
                widget.destroy()

            schedules = self.admin_controller.get_section_schedule(section_id)
            if not schedules:
                ctk.CTkLabel(scroll, text="No schedule rows. Click '+ Add Row' to begin.", text_color=TEXT_MUTED).pack(pady=20)
                return

            header = ctk.CTkFrame(scroll, fg_color=ACCENT, height=35)
            header.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(header, text="Time", width=130, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Subject", width=200, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Teacher", width=200, font=("Roboto", 12, "bold"), text_color="white", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Actions", font=("Roboto", 12, "bold"), text_color="white").pack(side="right", padx=15)

            for schedule in schedules:
                row = ctk.CTkFrame(scroll)
                row.pack(fill="x", pady=2)

                time_entry = ctk.CTkEntry(row, width=130, font=("Roboto", 12))
                time_entry.insert(0, schedule["time_range"])
                time_entry.pack(side="left", padx=5, pady=5)

                subject_entry = ctk.CTkEntry(row, width=200, font=("Roboto", 12))
                subject_entry.insert(0, schedule["subject"])
                subject_entry.pack(side="left", padx=5, pady=5)

                teacher_entry = ctk.CTkEntry(row, width=200, font=("Roboto", 12))
                teacher_entry.insert(0, schedule["teacher"] if schedule.get("teacher") else "")
                teacher_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

                button_frame = ctk.CTkFrame(row, fg_color="transparent")
                button_frame.pack(side="right", padx=5)

                def make_save(schedule_id, save_button, time_widget, subject_widget, teacher_widget):
                    def save_schedule():
                        result = self.admin_controller.update_section_schedule(schedule_id, time_widget.get().strip(), subject_widget.get().strip(), teacher_widget.get().strip())
                        if result.get("success"):
                            save_button.configure(fg_color=SUCCESS, text="Saved")
                            save_button.after(1500, lambda: save_button.configure(fg_color=PRIMARY, text="Save"))
                            return
                        messagebox.showerror("Error", result["message"], parent=window)

                    return save_schedule

                save_button = ctk.CTkButton(button_frame, text="Save", width=50, height=28, fg_color=PRIMARY, hover_color="#185A8C", font=("Roboto", 10))
                save_button.configure(command=make_save(schedule["id"], save_button, time_entry, subject_entry, teacher_entry))
                save_button.pack(side="left", padx=2)
                ctk.CTkButton(button_frame, text="X", width=28, height=28, fg_color=DANGER, hover_color="#C03030", font=("Roboto", 10), command=lambda sid=schedule["id"]: [self.admin_controller.delete_section_schedule(sid), refresh()]).pack(side="left", padx=2)

        refresh()

    def build_schedules_tab(self, parent):
        top_frame = ctk.CTkFrame(parent, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(top_frame, text="Program:", font=("Roboto", 14, "bold")).pack(side="left", padx=(0, 10))
        self.schedule_program_var = ctk.StringVar(value="STE")
        ctk.CTkOptionMenu(top_frame, values=["STE", "Regular", "SPJ", "SPA"], variable=self.schedule_program_var, command=lambda _value: self.load_admin_schedules(), width=150).pack(side="left")
        self.schedule_container = ctk.CTkScrollableFrame(parent, corner_radius=10, fg_color="transparent")
        self.schedule_container.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        self.load_admin_schedules()

    def load_admin_schedules(self):
        for widget in self.schedule_container.winfo_children():
            widget.destroy()

        program = self.schedule_program_var.get()
        schedules = self.admin_controller.get_program_schedule(program)
        if not schedules:
            ctk.CTkLabel(self.schedule_container, text=f"No schedules found for {program} program. Run migration script first.", text_color=TEXT_MUTED).pack(pady=20)
            return

        header_frame = ctk.CTkFrame(self.schedule_container, fg_color=ACCENT, height=35)
        header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header_frame, text="Time", width=120, font=("Roboto", 12, "bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Subject", width=200, font=("Roboto", 12, "bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Teacher", width=200, font=("Roboto", 12, "bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Actions", width=80, font=("Roboto", 12, "bold")).pack(side="right", padx=15)

        for schedule in schedules:
            self.create_schedule_row(schedule)

    def create_schedule_row(self, schedule_row):
        row = ctk.CTkFrame(self.schedule_container)
        row.pack(fill="x", pady=2)

        time_entry = ctk.CTkEntry(row, width=120, font=("Roboto", 12))
        time_entry.insert(0, schedule_row["time_range"])
        time_entry.pack(side="left", padx=5, pady=5)

        subject_entry = ctk.CTkEntry(row, width=200, font=("Roboto", 12))
        subject_entry.insert(0, schedule_row["subject"])
        subject_entry.pack(side="left", padx=5, pady=5)

        teacher_entry = ctk.CTkEntry(row, width=200, font=("Roboto", 12))
        teacher_entry.insert(0, schedule_row["teacher"] if schedule_row.get("teacher") else "")
        teacher_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        def save_edit():
            new_time = time_entry.get().strip()
            new_subject = subject_entry.get().strip()
            new_teacher = teacher_entry.get().strip()
            result = self.admin_controller.update_program_schedule(schedule_row["id"], new_time, new_subject, new_teacher)
            if result.get("success"):
                schedule_row["time_range"] = new_time
                schedule_row["subject"] = new_subject
                schedule_row["teacher"] = new_teacher
                save_button.configure(fg_color=SUCCESS, text="Saved")
                row.after(2000, lambda: save_button.configure(fg_color=PRIMARY, text="Save"))
                return
            messagebox.showerror("Error", result["message"])

        def cancel_edit():
            time_entry.delete(0, "end")
            time_entry.insert(0, schedule_row["time_range"])
            subject_entry.delete(0, "end")
            subject_entry.insert(0, schedule_row["subject"])
            teacher_entry.delete(0, "end")
            teacher_entry.insert(0, schedule_row["teacher"] if schedule_row.get("teacher") else "")

        button_frame = ctk.CTkFrame(row, fg_color="transparent")
        button_frame.pack(side="right", padx=5)
        save_button = ctk.CTkButton(button_frame, text="Save", width=50, height=28, fg_color=PRIMARY, hover_color="#185A8C", command=save_edit)
        save_button.pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Cancel", width=50, height=28, fg_color="transparent", text_color=TEXT_MUTED, border_width=1, border_color=TEXT_MUTED, hover_color="#333", command=cancel_edit).pack(side="left", padx=2)

    def build_analytics_tab(self, parent):
        content = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        export_frame = ctk.CTkFrame(content, corner_radius=12)
        export_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(export_frame, text="Data Export", font=("Roboto", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        button_container = ctk.CTkFrame(export_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(button_container, text="Export Student Records", width=180, height=36, corner_radius=8, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 12, "bold"), command=self.export_student_data).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_container, text="Export Attendance Logs", width=180, height=36, corner_radius=8, fg_color=PRIMARY, hover_color="#185A8C", font=("Roboto", 12, "bold"), command=self.export_attendance_data).pack(side="left")

        chart_frame = ctk.CTkFrame(content, corner_radius=12)
        chart_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(chart_frame, text="Analytics Overview", font=("Roboto", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 10))

        analytics = self.admin_controller.get_analytics_data()
        figure = Figure(figsize=(10, 4), dpi=100, facecolor=BG_CARD)

        axis_one = figure.add_subplot(121)
        axis_one.set_facecolor(BG_CARD)
        for spine in axis_one.spines.values():
            spine.set_color(TEXT_MUTED)
        axis_one.tick_params(colors=TEXT_MUTED)
        axis_one.yaxis.label.set_color("white")
        axis_one.xaxis.label.set_color("white")
        axis_one.title.set_color("white")

        category_averages = analytics["category_averages"]
        if category_averages:
            labels = list(category_averages.keys())
            averages = list(category_averages.values())
            bars = axis_one.bar(labels, averages, color=SUCCESS)
            axis_one.set_title("Average Final Grades by Program Category")
            axis_one.set_ylabel("Average Grade (%)")
            axis_one.set_ylim([0, 100])
            for bar in bars:
                height = bar.get_height()
                axis_one.annotate(f"{height:.1f}", xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", color="white")
        else:
            axis_one.text(0.5, 0.5, "No Grade Data Available", ha="center", va="center", color=TEXT_MUTED, transform=axis_one.transAxes)

        axis_two = figure.add_subplot(122)
        axis_two.set_facecolor(BG_CARD)
        enrollment_counts = analytics["enrollment_counts"]
        if enrollment_counts:
            wedges, texts, autotexts = axis_two.pie(enrollment_counts.values(), labels=enrollment_counts.keys(), autopct="%1.1f%%", startangle=90, colors=[PRIMARY, SUCCESS, WARNING])
            for text in texts:
                text.set_color("white")
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_weight("bold")
            axis_two.axis("equal")
            axis_two.set_title("Enrollment Distribution by Category", color="white")
        else:
            axis_two.text(0.5, 0.5, "No Enrollment Data", ha="center", va="center", color=TEXT_MUTED, transform=axis_two.transAxes)

        figure.tight_layout(pad=3.0)
        canvas = FigureCanvasTkAgg(figure, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def export_student_data(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="Student_RecordsExport.csv", title="Export Student Records")
        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["ID", "Username", "Full Name", "Gender", "Age", "Email", "Phone", "Category", "Program", "Course", "Grade", "Section", "Status"])
                writer.writerows(self.admin_controller.get_student_export_rows())
            messagebox.showinfo("Export Successful", f"Student records exported to {filepath}.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    def export_attendance_data(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="Attendance_LogsExport.csv", title="Export Attendance Logs")
        if not filepath:
            return

        result = self.admin_controller.get_attendance_export_rows()
        if not result.get("success"):
            messagebox.showerror("Export Error", result["message"])
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Student Name", "Student ID", "Course", "Date", "Status", "Remarks"])
                writer.writerows(result["rows"])
            messagebox.showinfo("Export Successful", f"Attendance logs exported to {filepath}.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    def refresh_dashboard(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.load_dashboard_users()

    def load_dashboard_users(self):
        data = self.admin_controller.get_user_management_data(
            search_query=self.search_var.get().strip() if self.search_var else "",
            status_filter=self.status_filter.get() if self.status_filter else "All",
            program_filter=self.program_filter.get() if self.program_filter else "All",
            grade_filter=self.grade_filter.get() if self.grade_filter else "All",
            sort_by=self.sort_var.get() if self.sort_var else "id",
            sort_order="ASC" if self.order_var and self.order_var.get() == "Ascending" else "DESC",
        )

        stats = data["stats"]
        self.stats_label.configure(text=f"{stats['total']} total | {stats['pending']} pending | {stats['approved']} approved")

        users = data["users"]
        if not users:
            ctk.CTkLabel(self.scroll_frame, text="No users found.", font=("Roboto", 13), text_color=TEXT_MUTED).pack(pady=30)
            return

        button_height = 26
        button_radius = 5
        for index, user in enumerate(users):
            row = ctk.CTkFrame(self.scroll_frame, height=38, corner_radius=6)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            program = user.get("program_type", "") or ""
            if program in ("N/A", ""):
                program = "Regular"

            cell_values = [str(user["id"]), user["username"], user.get("full_name", ""), program, user.get("grade", "") or "-", user.get("section", "") or "-"]
            for value, (_, width) in zip(cell_values, self._table_cols):
                ctk.CTkLabel(row, text=value, width=width, anchor="w", font=("Roboto", 11)).pack(side="left", padx=4)

            status = user.get("status", "N/A")
            status_color = SUCCESS if status == "Approved" else WARNING
            ctk.CTkLabel(row, text=f"? {status}", width=self._table_cols[-1][1], text_color=status_color, anchor="w", font=("Roboto", 11, "bold")).pack(side="left", padx=4)

            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(side="right", padx=(4, 8))

            if status != "Approved":
                ctk.CTkButton(action_frame, text="Approve", width=72, height=button_height, corner_radius=button_radius, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 10), command=lambda uid=user["id"]: self.approve_user(uid)).pack(side="left", padx=1)
            else:
                ctk.CTkButton(action_frame, text="Grades", width=52, height=button_height, corner_radius=button_radius, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 10), command=lambda uid=user["id"]: self.admin_edit_grades(uid)).pack(side="left", padx=1)
                ctk.CTkButton(action_frame, text="Attendance", width=68, height=button_height, corner_radius=button_radius, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 10), command=lambda uid=user["id"]: self.admin_manage_attendance(uid)).pack(side="left", padx=1)

            ctk.CTkButton(action_frame, text="Edit", width=40, height=button_height, corner_radius=button_radius, fg_color=PRIMARY, hover_color="#185A8C", font=("Roboto", 10), command=lambda current_user=user: self.edit_user(current_user)).pack(side="left", padx=1)
            ctk.CTkButton(action_frame, text="View", width=42, height=button_height, corner_radius=button_radius, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 10), command=lambda current_user=user: self.view_user_details(current_user)).pack(side="left", padx=1)
            ctk.CTkButton(action_frame, text="X", width=28, height=button_height, corner_radius=button_radius, fg_color=DANGER, hover_color="#C03030", font=("Roboto", 10), command=lambda uid=user["id"]: self.delete_user_action(uid)).pack(side="left", padx=1)

            row.after(index * 20, lambda widget=row: self.slide_in_frame(widget, start_y=10, step=4))
    def view_user_details(self, user_data):
        window = ctk.CTkToplevel(self.app)
        window.title(f"User Details: {user_data['username']}")
        window.geometry("420x580")
        window.grab_set()
        window.resizable(False, False)
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text="User Details", font=("Roboto", 20, "bold")).pack(pady=(20, 15))
        info_frame = ctk.CTkFrame(window, corner_radius=12)
        info_frame.pack(fill="x", padx=25, pady=(0, 15))

        details = [
            ("ID", user_data.get("id", "")),
            ("Username", user_data.get("username", "")),
            ("Full Name", user_data.get("full_name", "")),
            ("Age", user_data.get("age", "") or "-"),
            ("Gender", user_data.get("gender", "") or "-"),
            ("Email", user_data.get("email", "")),
            ("Phone", user_data.get("phone", "")),
            ("Address", user_data.get("address", "")),
            ("Student ID", user_data.get("student_id", "") or "-"),
            ("Course", user_data.get("course", "") or "-"),
            ("Grade", user_data.get("grade", "") or "-"),
            ("Section", user_data.get("section", "") or "-"),
            ("Status", user_data.get("status", "")),
        ]

        for label, value in details:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(row, text=f"{label}:", font=("Roboto", 12, "bold"), width=110, anchor="w").pack(side="left")
            color = SUCCESS if value == "Approved" else (WARNING if value == "Pending" else None)
            kwargs = {"text": str(value), "font": ("Roboto", 12), "anchor": "w"}
            if color:
                kwargs["text_color"] = color
            ctk.CTkLabel(row, **kwargs).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(window, text="Close", command=window.destroy, width=200, height=38, corner_radius=10).pack(pady=15)

    def admin_edit_grades(self, user_id):
        data = self.admin_controller.prepare_grade_editor(user_id)
        if not data:
            return

        user = data["user"]
        grades = data["grades"]

        window = ctk.CTkToplevel(self.app)
        window.title(f"Edit Grades - {user['full_name']}")
        window.geometry("950x700")
        window.grab_set()
        self.setup_dialog_close(window)

        header = ctk.CTkFrame(window, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(header, text=f"Editing Grades for: {user['full_name']}", font=("Roboto", 18, "bold")).pack(side="left")
        ctk.CTkLabel(header, text=f"{user.get('grade', '')} - {user.get('section', '')}", font=("Roboto", 14), text_color=TEXT_MUTED).pack(side="right")

        grades_map = {}
        ctk.CTkButton(window, text="SAVE ALL CHANGES", width=220, height=40, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold"), command=lambda: self.save_all_grades(grades_map, window)).pack(pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(window, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ["Subject", "Q1", "Q2", "Q3", "Q4", "Final", "Remarks"]
        widths = [220, 70, 70, 70, 70, 80, 200]
        header_row = ctk.CTkFrame(scroll, fg_color=ACCENT, height=35, corner_radius=5)
        header_row.pack(fill="x", pady=(0, 5))
        for column, width in zip(columns, widths):
            ctk.CTkLabel(header_row, text=column, width=width, font=("Roboto", 12, "bold"), text_color="white").pack(side="left", padx=2)

        for grade in grades:
            row = ctk.CTkFrame(scroll, height=40)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=grade["subject"], width=widths[0], anchor="w", font=("Roboto", 12)).pack(side="left", padx=5)

            entries = {}
            for index, quarter in enumerate(["q1", "q2", "q3", "q4"]):
                value = grade.get(quarter)
                entry = ctk.CTkEntry(row, width=widths[index + 1], justify="center", font=("Roboto", 12))
                entry.insert(0, str(value) if value is not None else "")
                entry.pack(side="left", padx=2)
                entries[quarter] = entry

            final_label = ctk.CTkLabel(row, text=str(grade.get("final")) if grade.get("final") is not None else "-", width=widths[5], font=("Roboto", 12, "bold"))
            final_label.pack(side="left", padx=2)
            entries["final_lbl"] = final_label

            remarks_entry = ctk.CTkEntry(row, width=widths[6], font=("Roboto", 12))
            remarks_entry.insert(0, grade.get("remarks") or "")
            remarks_entry.pack(side="left", padx=2)
            entries["remarks"] = remarks_entry
            grades_map[grade["id"]] = entries

    def save_all_grades(self, grades_map, parent_window):
        raw_updates = {}
        for grade_id, widgets in grades_map.items():
            raw_updates[grade_id] = {
                "q1": widgets["q1"].get(),
                "q2": widgets["q2"].get(),
                "q3": widgets["q3"].get(),
                "q4": widgets["q4"].get(),
                "remarks": widgets["remarks"].get(),
            }

        result = self.admin_controller.save_grade_changes(raw_updates)
        if not result.get("success"):
            messagebox.showerror("Error", result["message"], parent=parent_window)
            return

        for grade_id, final_value in result["computed_finals"].items():
            grades_map[grade_id]["final_lbl"].configure(text=str(final_value) if final_value is not None else "-")

        message = result["message"]
        if result.get("general_average") is not None:
            message += f"\n\nGeneral Average: {result['general_average']:.2f}"
        messagebox.showinfo("Success", message, parent=parent_window)

    def admin_manage_attendance(self, user_id):
        context = self.admin_controller.get_attendance_context(user_id)
        if not context:
            return

        user = context["user"]
        window = ctk.CTkToplevel(self.app)
        window.title(f"Attendance: {user['full_name']}")
        window.geometry("500x620")
        window.grab_set()
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text=f"Attendance - {user['full_name']}", font=("Roboto", 18, "bold")).pack(pady=(20, 10))

        entry_frame = ctk.CTkFrame(window, corner_radius=12)
        entry_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(entry_frame, text="Mark New Attendance", font=("Roboto", 13, "bold"), text_color=PRIMARY).pack(pady=(10, 5))

        date_row = ctk.CTkFrame(entry_frame, fg_color="transparent")
        date_row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(date_row, text="Date (YYYY-MM-DD):", font=("Roboto", 12)).pack(side="left")
        date_entry = ctk.CTkEntry(date_row, width=150)
        date_entry.insert(0, str(self.current_date.date()))
        date_entry.pack(side="right")

        status_row = ctk.CTkFrame(entry_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(status_row, text="Status:", font=("Roboto", 12)).pack(side="left")
        status_var = ctk.StringVar(value="Present")
        ctk.CTkOptionMenu(status_row, variable=status_var, values=["Present", "Absent", "Late", "Excused"], width=150).pack(side="right")

        remarks_entry = ctk.CTkEntry(entry_frame, placeholder_text="Remarks (optional)", width=380)
        remarks_entry.pack(pady=10, padx=20)
        scroll = ctk.CTkScrollableFrame(window, height=250)
        scroll.pack(padx=30, pady=(0, 20), fill="both", expand=True)

        def refresh_history():
            for widget in scroll.winfo_children():
                widget.destroy()
            attendance_context = self.admin_controller.get_attendance_context(user_id)
            history = attendance_context["history"] if attendance_context else []
            if not history:
                ctk.CTkLabel(scroll, text="No records yet.", font=("Roboto", 12), text_color=TEXT_MUTED).pack(pady=20)
                return
            for record in history:
                row = ctk.CTkFrame(scroll, corner_radius=8)
                row.pack(fill="x", pady=2)
                color = SUCCESS if record["status"] == "Present" else (DANGER if record["status"] == "Absent" else WARNING)
                ctk.CTkLabel(row, text=str(record["date"]), font=("Roboto", 12, "bold"), width=90).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=record["status"], font=("Roboto", 12), text_color=color, width=70).pack(side="left")
                if record["remarks"]:
                    ctk.CTkLabel(row, text=f"({record['remarks']})", font=("Roboto", 11), text_color=TEXT_MUTED, wraplength=180, justify="left").pack(side="left", padx=5, fill="x", expand=True)

        def save_attendance():
            result = self.admin_controller.record_attendance(user_id, date_entry.get().strip(), status_var.get(), remarks_entry.get().strip())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=window)
                refresh_history()
                return
            messagebox.showerror("Error", result["message"], parent=window)

        ctk.CTkButton(entry_frame, text="Record Attendance", command=save_attendance, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold"), width=380, height=38).pack(pady=(5, 15), padx=20)
        ctk.CTkLabel(window, text="Recent History", font=("Roboto", 14, "bold")).pack(pady=(10, 5))
        refresh_history()

    def approve_user(self, user_id):
        user = self.admin_controller.get_user(user_id)
        if not user:
            messagebox.showerror("Error", "User not found.")
            return

        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Approve & Assign")
        dialog.geometry("320x300")
        dialog.grab_set()
        self.setup_dialog_close(dialog)

        ctk.CTkLabel(dialog, text="Assign Academic Level", font=("Roboto", 16, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Grade Level:", font=("Roboto", 12)).pack(anchor="w", padx=40)
        grade_var = ctk.StringVar(value="Grade 7")
        ctk.CTkOptionMenu(dialog, variable=grade_var, values=["Grade 7", "Grade 8", "Grade 9", "Grade 10"], width=240).pack(pady=(0, 15))

        ctk.CTkLabel(dialog, text="Section / Class:", font=("Roboto", 12)).pack(anchor="w", padx=40)
        section_names = self.admin_controller.get_section_names()
        if section_names:
            section_var = ctk.StringVar(value=section_names[0])
            ctk.CTkOptionMenu(dialog, variable=section_var, values=section_names, width=240).pack(pady=(0, 20))
        else:
            section_var = None
            ctk.CTkLabel(dialog, text="No sections available. Create sections first in the Sections tab.", font=("Roboto", 11), text_color=DANGER, wraplength=240).pack(pady=(0, 20))

        def confirm():
            if not section_var:
                messagebox.showerror("Error", "No sections available. Please create sections first.", parent=dialog)
                return
            result = self.admin_controller.approve_user(user_id, grade_var.get(), section_var.get().strip())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=dialog)
                dialog.destroy()
                self.refresh_dashboard()
                return
            messagebox.showerror("Error", result["message"], parent=dialog)

        ctk.CTkButton(dialog, text="Confirm Approval", command=confirm, width=240, height=40, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold")).pack()

    def delete_user_action(self, user_id):
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?\nThis action cannot be undone."):
            return
        result = self.admin_controller.delete_user(user_id)
        if result.get("success"):
            messagebox.showinfo("Success", result["message"])
            self.refresh_dashboard()
            return
        messagebox.showerror("Error", result["message"])

    def show_announcements_manager(self):
        window = ctk.CTkToplevel(self.app)
        window.title("Manage Announcements")
        window.geometry("500x600")
        window.grab_set()
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text="Post New Announcement", font=("Roboto", 18, "bold")).pack(pady=(20, 10))
        message_entry = ctk.CTkTextbox(window, width=420, height=100, corner_radius=10)
        message_entry.pack(pady=10, padx=40)
        scroll = ctk.CTkScrollableFrame(window, width=420, height=250)
        scroll.pack(pady=10, padx=40, fill="both", expand=True)

        def refresh_announcements():
            for widget in scroll.winfo_children():
                widget.destroy()
            for item in self.admin_controller.list_announcements():
                frame = ctk.CTkFrame(scroll, corner_radius=8)
                frame.pack(fill="x", pady=2)
                ctk.CTkLabel(frame, text=item["message"], wraplength=300, justify="left", font=("Roboto", 11)).pack(side="left", padx=10, pady=5)
                ctk.CTkButton(frame, text="X", width=30, height=30, fg_color=DANGER, hover_color="#C03030", command=lambda announcement_id=item["id"]: delete_announcement_action(announcement_id)).pack(side="right", padx=5)

        def post_announcement():
            result = self.admin_controller.post_announcement(message_entry.get("1.0", "end").strip())
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=window)
                message_entry.delete("1.0", "end")
                refresh_announcements()
                return
            messagebox.showerror("Error", result["message"], parent=window)

        def delete_announcement_action(announcement_id):
            if messagebox.askyesno("Confirm", "Delete this announcement?", parent=window):
                if self.admin_controller.delete_announcement(announcement_id):
                    refresh_announcements()

        ctk.CTkButton(window, text="Post Announcement", command=post_announcement, width=420, height=40, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold")).pack(pady=10)
        ctk.CTkLabel(window, text="Existing Announcements", font=("Roboto", 14, "bold")).pack(pady=(20, 5))
        refresh_announcements()
    def edit_user(self, user_data):
        edit_window = ctk.CTkToplevel(self.app)
        edit_window.title(f"Edit: {user_data['username']}")
        edit_window.geometry("480x700")
        edit_window.grab_set()
        self.setup_dialog_close(edit_window)

        scroll = ctk.CTkScrollableFrame(edit_window, corner_radius=0, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(scroll, text="Edit Student Details", font=("Roboto", 18, "bold")).pack(pady=(5, 15))

        fields = {}
        basic_defs = [
            ("full_name", "Full Name"),
            ("username", "Username"),
            ("email", "Email (@yourdomain.com)"),
            ("phone", "Phone (+63XXXXXXXXXX)"),
            ("student_id", "Student ID"),
        ]

        for key, label in basic_defs:
            ctk.CTkLabel(scroll, text=label, font=("Roboto", 11, "bold"), anchor="w").pack(padx=30, anchor="w")
            entry = ctk.CTkEntry(scroll, placeholder_text=label, width=360, height=36, corner_radius=8)
            value = user_data.get(key, "") or ""
            if key == "phone" and not value:
                value = "+63"
            entry.insert(0, value)
            entry.pack(pady=(0, 10), padx=30)
            fields[key] = entry

        ctk.CTkLabel(scroll, text="Section", font=("Roboto", 11, "bold"), anchor="w").pack(padx=30, anchor="w")
        section_names = self.admin_controller.get_section_names()
        current_section = user_data.get("section", "") or ""
        if current_section and current_section not in section_names:
            section_names = [current_section] + section_names
        if not section_names:
            section_names = ["(No sections created)"]
        section_option = ctk.CTkOptionMenu(scroll, values=section_names, width=360, height=36, corner_radius=8)
        section_option.set(current_section if current_section else section_names[0])
        section_option.pack(pady=(0, 10), padx=30)
        fields["section"] = section_option

        ctk.CTkLabel(scroll, text="Age & Gender", font=("Roboto", 11, "bold"), anchor="w").pack(padx=30, anchor="w")
        demographic_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        demographic_frame.pack(fill="x", padx=30, pady=(0, 10))

        age_entry = ctk.CTkEntry(demographic_frame, placeholder_text="Age", width=175, height=36, corner_radius=8)
        age_entry.insert(0, str(user_data.get("age", "") or ""))
        age_entry.pack(side="left", padx=(0, 10))
        fields["age"] = age_entry

        gender_option = ctk.CTkOptionMenu(demographic_frame, values=["Male", "Female", "Other"], width=175, height=36, corner_radius=8)
        gender_option.set(user_data.get("gender", "Select Gender") or "Select Gender")
        gender_option.pack(side="left")
        fields["gender"] = gender_option

        ctk.CTkLabel(scroll, text="Academic Program Selection", font=("Roboto", 11, "bold"), anchor="w").pack(padx=30, anchor="w")

        class CourseManager:
            def __init__(self, master, current_data):
                self.category = ctk.CTkOptionMenu(master, values=["Regular Program", "Special Programs"], width=360, height=36, corner_radius=8, command=self.update_options)
                current_category = current_data.get("course_category", "Select Category") or "Select Category"
                self.category.set(current_category)
                self.category.pack(pady=(0, 6), padx=30)

                self.program = ctk.CTkOptionMenu(master, values=["STE", "SPJ", "SPA"], width=360, height=36, corner_radius=8, command=self.update_spa)
                self.spec = ctk.CTkOptionMenu(master, values=["Dancing", "Theatre", "Arts", "Music"], width=360, height=36, corner_radius=8)
                self.grade_option = ctk.CTkOptionMenu(master, values=["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"], width=360, height=36, corner_radius=8)

                current_grade = current_data.get("grade", "") or "Select Grade Level"
                self.grade_option.set(current_grade if str(current_grade).startswith("Grade") else f"Grade {current_grade}" if str(current_grade).isdigit() else "Select Grade Level")
                self.grade_option.pack(pady=(0, 10), padx=30)

                self.update_options(self.category.get(), initial=True)
                if current_data.get("program_type") == "SPA":
                    self.update_spa("SPA", initial=True)

            def update_options(self, choice, initial=False):
                self.program.pack_forget()
                self.spec.pack_forget()
                self.grade_option.pack_forget()
                if choice == "Special Programs":
                    self.program.pack(pady=(0, 6), padx=30)
                    self.program.set(user_data.get("program_type", "STE") if initial else "Select Special Program")
                self.grade_option.pack(pady=(0, 10), padx=30)

            def update_spa(self, choice, initial=False):
                self.spec.pack_forget()
                self.grade_option.pack_forget()
                if choice == "SPA":
                    self.spec.pack(pady=(0, 6), padx=30)
                    self.spec.set(user_data.get("specialization", "Music") if initial else "Select SPA Specialization")
                self.grade_option.pack(pady=(0, 10), padx=30)

        course_manager = CourseManager(scroll, user_data)

        ctk.CTkLabel(scroll, text="Address", font=("Roboto", 11, "bold"), anchor="w").pack(padx=30, anchor="w")
        address_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        address_frame.pack(fill="x", padx=30, pady=(0, 10))

        address_entry = ctk.CTkEntry(address_frame, placeholder_text="Address", width=280, height=36, corner_radius=8)
        address_entry.insert(0, user_data.get("address", "") or "")
        address_entry.pack(side="left", padx=(0, 5))
        fields["address"] = address_entry

        if MAP_AVAILABLE:
            ctk.CTkButton(address_frame, text="Map", width=75, height=36, corner_radius=8, fg_color=ACCENT, hover_color="#0A2647", font=("Roboto", 11), command=lambda: self.open_map_picker(address_entry)).pack(side="left")

        def save_user():
            updates = {key: widget.get().strip() for key, widget in fields.items()}
            updates["section"] = "" if updates["section"] == "(No sections created)" else updates["section"]
            updates["course_category"] = course_manager.category.get()
            updates["program_type"] = course_manager.program.get() if updates["course_category"] == "Special Programs" else "N/A"
            updates["specialization"] = course_manager.spec.get() if updates["program_type"] == "SPA" else "N/A"
            updates["grade"] = course_manager.grade_option.get()

            if "Select" in [updates["gender"], updates["course_category"], updates["grade"]]:
                messagebox.showerror("Error", "Please make all selections.", parent=edit_window)
                return
            if updates["course_category"] == "Special Programs" and updates["program_type"].startswith("Select"):
                messagebox.showerror("Error", "Please select a special program.", parent=edit_window)
                return
            if updates["program_type"] == "SPA" and updates["specialization"].startswith("Select"):
                messagebox.showerror("Error", "Please select an SPA specialization.", parent=edit_window)
                return

            result = self.admin_controller.update_user(user_data["id"], updates)
            if result.get("success"):
                messagebox.showinfo("Success", result["message"], parent=edit_window)
                edit_window.destroy()
                self.refresh_dashboard()
                return
            messagebox.showerror(result.get("title", "Error"), result["message"], parent=edit_window)

        ctk.CTkButton(scroll, text="Save Changes", command=save_user, width=360, height=42, corner_radius=10, fg_color=SUCCESS, hover_color="#248A5E", font=("Roboto", 13, "bold")).pack(pady=(20, 20), padx=30)

