from tkinter import filedialog

import customtkinter as ctk
import tkinter.messagebox as messagebox

from utils.constants import ACCENT, PRIMARY, SCHOOL_NAME, SUCCESS, TEXT_MUTED
from views.base_view import BaseView, MAP_AVAILABLE


class RegisterView(BaseView):
    def __init__(self, app, auth_controller):
        super().__init__(app)
        self.auth_controller = auth_controller
        self.reg_entries = {}
        self.reg_age = None
        self.reg_gender = None
        self.reg_category = None
        self.reg_program_type = None
        self.reg_address = None
        self.reg_profile_picture_path = None
        self.reg_profile_preview = None
        self.reg_profile_preview_label = None
        self.reg_profile_status_label = None
        self.row_marker = 0

    def show_register(self):
        self.clear_window()
        self.geometry("520x1040")

        frame = ctk.CTkFrame(self.app, corner_radius=15)
        frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, pady=(10, 3))
        if self.logo_small:
            ctk.CTkLabel(header, text="", image=self.logo_small).pack()
        ctk.CTkLabel(header, text=SCHOOL_NAME, font=("Roboto", 12, "bold")).pack()
        ctk.CTkLabel(header, text="Student Registration", font=("Roboto", 18, "bold")).pack(pady=(3, 0))

        ctk.CTkLabel(frame, text="Fill in all fields to create your account", font=("Roboto", 12), text_color=TEXT_MUTED).grid(row=1, column=0, pady=(0, 8))

        self.reg_profile_picture_path = None
        self.reg_profile_preview = None

        picture_frame = ctk.CTkFrame(frame, corner_radius=12)
        picture_frame.grid(row=2, column=0, pady=(0, 12))

        ctk.CTkLabel(picture_frame, text="Profile Picture", font=("Roboto", 13, "bold"), text_color=PRIMARY).pack(pady=(12, 6))

        preview_frame = ctk.CTkFrame(picture_frame, width=160, height=160, corner_radius=12)
        preview_frame.pack(padx=20, pady=(0, 8))
        preview_frame.pack_propagate(False)

        self.reg_profile_preview_label = ctk.CTkLabel(preview_frame, text="No image\nselected", font=("Roboto", 12), justify="center")
        self.reg_profile_preview_label.pack(expand=True)

        ctk.CTkButton(
            picture_frame,
            text="Upload Profile Picture",
            command=self.select_profile_picture,
            width=220,
            height=36,
            corner_radius=10,
            fg_color=ACCENT,
            hover_color="#0A2647",
            font=("Roboto", 12, "bold"),
        ).pack(pady=(0, 6))

        self.reg_profile_status_label = ctk.CTkLabel(picture_frame, text="Supported formats: JPG, JPEG, PNG", font=("Roboto", 11), text_color=TEXT_MUTED)
        self.reg_profile_status_label.pack(pady=(0, 12))

        self.reg_entries = {}
        field_defs = [
            ("username", "Username", None),
            ("password", "Password", "*"),
            ("full_name", "Full Name", None),
            ("email", "Email (@yourdomain.com)", None),
            ("phone", "Phone (+63XXXXXXXXXX)", None),
            ("student_id", "Student ID", None),
        ]

        row_index = 3
        for key, placeholder, show_char in field_defs:
            kwargs = {"master": frame, "placeholder_text": placeholder, "width": 300, "height": 36, "corner_radius": 10}
            if show_char:
                kwargs["show"] = show_char
            entry = ctk.CTkEntry(**kwargs)
            entry.grid(row=row_index, column=0, pady=(0, 6))
            if key == "phone":
                entry.insert(0, "+63")
            self.reg_entries[key] = entry
            row_index += 1

        demographic_frame = ctk.CTkFrame(frame, fg_color="transparent")
        demographic_frame.grid(row=row_index, column=0, pady=(0, 6))
        row_index += 1

        self.reg_age = ctk.CTkEntry(demographic_frame, placeholder_text="Age", width=145, height=36, corner_radius=10)
        self.reg_age.pack(side="left", padx=(0, 10))

        self.reg_gender = ctk.CTkOptionMenu(demographic_frame, values=["Male", "Female", "Other"], width=145, height=36, corner_radius=10)
        self.reg_gender.pack(side="left")
        self.reg_gender.set("Select Gender")

        ctk.CTkLabel(frame, text="Academic Program Selection", font=("Roboto", 11, "bold"), text_color=PRIMARY).grid(row=row_index, column=0, pady=(4, 2))
        row_index += 1

        self.reg_category = ctk.CTkOptionMenu(
            frame,
            values=["Regular Program", "Special Programs"],
            width=300,
            height=36,
            corner_radius=10,
            command=self.update_course_options,
        )
        self.reg_category.grid(row=row_index, column=0, pady=(0, 6))
        self.reg_category.set("Select Program Category")
        row_index += 1

        self.reg_program_type = ctk.CTkOptionMenu(
            frame,
            values=["STE", "SPJ", "SPA"],
            width=300,
            height=36,
            corner_radius=10,
        )

        self.row_marker = row_index

        address_frame = ctk.CTkFrame(frame, fg_color="transparent")
        address_frame.grid(row=50, column=0, pady=(0, 6))
        address_frame.grid_columnconfigure(0, weight=1)

        self.reg_address = ctk.CTkEntry(address_frame, placeholder_text="Address (Philippines)", width=230, height=36, corner_radius=10)
        self.reg_address.pack(side="left", padx=(0, 5))

        map_button_text = "Map" if MAP_AVAILABLE else "Map (N/A)"
        ctk.CTkButton(
            address_frame,
            text=map_button_text,
            width=65,
            height=36,
            corner_radius=10,
            fg_color=ACCENT,
            hover_color="#0A2647",
            font=("Roboto", 11),
            command=lambda: self.open_map_picker(self.reg_address),
            state="normal" if MAP_AVAILABLE else "disabled",
        ).pack(side="left")

        ctk.CTkButton(
            frame,
            text="Register",
            command=self.handle_register,
            width=300,
            height=42,
            corner_radius=10,
            fg_color=SUCCESS,
            hover_color="#248A5E",
            font=("Roboto", 14, "bold"),
        ).grid(row=51, column=0, pady=(12, 8))

        ctk.CTkButton(
            frame,
            text="Back to Login",
            command=self.show_login,
            width=300,
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=ACCENT,
            font=("Roboto", 13),
        ).grid(row=52, column=0, pady=(0, 15))

        self.after(50, lambda: self.animate_children(frame, 25))

    def update_course_options(self, choice):
        self.reg_program_type.grid_forget()

        if choice == "Special Programs":
            self.reg_program_type.grid(row=self.row_marker, column=0, pady=(0, 6))
            self.reg_program_type.set("Select Special Program")

    def select_profile_picture(self):
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("PNG Files", "*.png"),
            ],
        )
        if not file_path:
            return

        username_hint = self.reg_entries.get("username").get().strip() if self.reg_entries.get("username") else "student"
        result = self.auth_controller.upload_profile_picture(
            file_path,
            username_hint=username_hint or "student",
            previous_path=self.reg_profile_picture_path,
        )
        if not result.get("success"):
            messagebox.showerror("Image Error", result["message"])
            return

        self.reg_profile_picture_path = result["relative_path"]
        preview_result = self.auth_controller.load_profile_picture(self.reg_profile_picture_path, size=(150, 150))
        if preview_result.get("success") and preview_result.get("image") is not None:
            self.reg_profile_preview = ctk.CTkImage(
                light_image=preview_result["image"],
                dark_image=preview_result["image"],
                size=(150, 150),
            )
            self.reg_profile_preview_label.configure(text="", image=self.reg_profile_preview)
            self.reg_profile_status_label.configure(text=f"Saved to: {self.reg_profile_picture_path}")
            return

        self.reg_profile_preview = None
        self.reg_profile_preview_label.configure(text="Preview\nunavailable", image=None)
        self.reg_profile_status_label.configure(text=result["relative_path"])

    def handle_register(self):
        payload = {
            "username": self.reg_entries["username"].get(),
            "password": self.reg_entries["password"].get(),
            "full_name": self.reg_entries["full_name"].get(),
            "email": self.reg_entries["email"].get(),
            "phone": self.reg_entries["phone"].get(),
            "student_id": self.reg_entries["student_id"].get(),
            "address": self.reg_address.get(),
            "age": self.reg_age.get(),
            "gender": self.reg_gender.get(),
            "course_category": self.reg_category.get(),
            "program_type": self.reg_program_type.get() if self.reg_category.get() == "Special Programs" else "N/A",
            "profile_picture": self.reg_profile_picture_path,
        }

        result = self.auth_controller.register_student(payload)
        if result.get("success"):
            messagebox.showinfo("Success", result["message"])
            self.show_login()
            return

        messagebox.showerror(result.get("title", "Error"), result["message"])
