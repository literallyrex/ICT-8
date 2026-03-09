import customtkinter as ctk
import tkinter.messagebox as messagebox

from utils.constants import ACCENT, DANGER, PRIMARY, SCHOOL_NAME, TEXT_MUTED
from utils.theme import apply_theme_to_app, apply_widget_colors
from views.base_view import BaseView


class LoginView(BaseView):
    def __init__(self, app, auth_controller):
        super().__init__(app)
        self.auth_controller = auth_controller
        self.login_username = None
        self.login_password = None
        self.admin_user = None
        self.admin_pass = None

    def show_login(self):
        self.clear_window()
        self.geometry("500x600")
        self.app.current_user = None

        frame = ctk.CTkFrame(self.app, corner_radius=15)
        frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        frame.grid_columnconfigure(0, weight=1)

        if self.logo_large:
            ctk.CTkLabel(frame, text="", image=self.logo_large).grid(row=0, column=0, pady=(20, 5))
        else:
            ctk.CTkLabel(frame, text="Student", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=(20, 5))
        ctk.CTkLabel(frame, text=SCHOOL_NAME, font=("Roboto", 15, "bold")).grid(row=1, column=0, pady=(0, 3))
        ctk.CTkLabel(frame, text="Student Registration System", font=("Roboto", 13), text_color=TEXT_MUTED).grid(row=2, column=0, pady=(0, 20))

        self.login_username = ctk.CTkEntry(frame, placeholder_text="Username", width=300, height=40, corner_radius=10)
        self.login_username.grid(row=3, column=0, pady=(0, 10))

        self.login_password = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300, height=40, corner_radius=10)
        self.login_password.grid(row=4, column=0, pady=(0, 20))

        ctk.CTkButton(frame, text="Log In", command=self.handle_login, width=300, height=42, corner_radius=10, font=("Roboto", 14, "bold")).grid(row=5, column=0, pady=(0, 10))
        ctk.CTkButton(
            frame,
            text="Register as Student",
            command=self.show_register,
            width=300,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=PRIMARY,
            font=("Roboto", 13),
        ).grid(row=6, column=0, pady=(0, 8))
        ctk.CTkButton(
            frame,
            text="Admin Login",
            command=self.show_admin_login,
            width=300,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=ACCENT,
            font=("Roboto", 13),
        ).grid(row=7, column=0, pady=(0, 8))
        ctk.CTkButton(
            frame,
            text="Forgot Password?",
            command=self.show_forgot_password,
            width=300,
            height=32,
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color=("#2B2B3E", "#2B2B3E"),
            font=("Roboto", 12),
        ).grid(row=8, column=0, pady=(0, 25))

        self.after(50, lambda: self.animate_children(frame, 30))

    def handle_login(self):
        result = self.auth_controller.login_student(self.login_username.get(), self.login_password.get())
        if result.get("success"):
            self.app.current_user = result["user"]
            apply_theme_to_app(self.app, self.app.current_user)
            self.show_student_dashboard()
            apply_widget_colors(self.app, self.app.current_user)
            return

        if result.get("level") == "warning":
            messagebox.showwarning("Status", result["message"])
        else:
            messagebox.showerror(result.get("title", "Error"), result["message"])

    def show_admin_login(self):
        self.clear_window()
        self.geometry("500x500")

        frame = ctk.CTkFrame(self.app, corner_radius=15)
        frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        frame.grid_columnconfigure(0, weight=1)

        if self.logo_large:
            ctk.CTkLabel(frame, text="", image=self.logo_large).grid(row=0, column=0, pady=(20, 5))
        else:
            ctk.CTkLabel(frame, text="Admin", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=(20, 5))
        ctk.CTkLabel(frame, text=SCHOOL_NAME, font=("Roboto", 15, "bold")).grid(row=1, column=0, pady=(0, 3))
        ctk.CTkLabel(frame, text="Admin Login", font=("Roboto", 13), text_color=TEXT_MUTED).grid(row=2, column=0, pady=(0, 20))

        self.admin_user = ctk.CTkEntry(frame, placeholder_text="Admin Username", width=300, height=40, corner_radius=10)
        self.admin_user.grid(row=3, column=0, pady=(0, 10))

        self.admin_pass = ctk.CTkEntry(frame, placeholder_text="Admin Password", show="*", width=300, height=40, corner_radius=10)
        self.admin_pass.grid(row=4, column=0, pady=(0, 20))

        ctk.CTkButton(
            frame,
            text="Log In as Admin",
            command=self.handle_admin_login,
            width=300,
            height=42,
            corner_radius=10,
            fg_color=ACCENT,
            hover_color="#0A2647",
            font=("Roboto", 14, "bold"),
        ).grid(row=5, column=0, pady=(0, 10))
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
        ).grid(row=6, column=0, pady=(0, 25))

        self.after(50, lambda: self.animate_children(frame, 30))

    def handle_admin_login(self):
        result = self.auth_controller.login_admin(self.admin_user.get(), self.admin_pass.get())
        if result.get("success"):
            self.show_admin_dashboard()
            return
        messagebox.showerror("Error", result["message"])

    def show_forgot_password(self):
        window = ctk.CTkToplevel(self.app)
        window.title("Forgot Password")
        window.geometry("420x380")
        window.grab_set()
        window.resizable(False, False)
        self.setup_dialog_close(window)

        ctk.CTkLabel(window, text="Reset Password", font=("Roboto", 20, "bold")).pack(pady=(25, 20))

        entry_user = ctk.CTkEntry(window, placeholder_text="Enter your username", width=300, height=40, corner_radius=10)
        entry_user.pack(pady=10)

        def verify_username():
            result = self.auth_controller.start_password_reset(entry_user.get())
            if not result.get("success"):
                messagebox.showerror("Error", result["message"], parent=window)
                return
            step_two(result["username"], result["user_data"])

        ctk.CTkButton(window, text="Next", command=verify_username, width=300, height=40, corner_radius=10, font=("Roboto", 13, "bold")).pack(pady=10)

        def step_two(username, user_data):
            for widget in window.winfo_children():
                widget.destroy()

            ctk.CTkLabel(window, text="Verify Identity", font=("Roboto", 20, "bold")).pack(pady=(25, 8))
            ctk.CTkLabel(window, text=f"Verifying for: {username}", font=("Roboto", 12), text_color=TEXT_MUTED).pack(pady=(0, 15))

            email_entry = ctk.CTkEntry(window, placeholder_text="Confirm your email", width=300, height=40, corner_radius=10)
            email_entry.pack(pady=8)
            phone_entry = ctk.CTkEntry(window, placeholder_text="Confirm your phone", width=300, height=40, corner_radius=10)
            phone_entry.pack(pady=8)

            def verify_identity():
                result = self.auth_controller.verify_password_reset_identity(user_data, email_entry.get(), phone_entry.get())
                if not result.get("success"):
                    messagebox.showerror("Error", result["message"], parent=window)
                    return
                step_three(username)

            ctk.CTkButton(window, text="Verify", command=verify_identity, width=300, height=40, corner_radius=10, font=("Roboto", 13, "bold")).pack(pady=10)

        def step_three(username):
            for widget in window.winfo_children():
                widget.destroy()

            ctk.CTkLabel(window, text="New Password", font=("Roboto", 20, "bold")).pack(pady=(25, 20))

            password_entry = ctk.CTkEntry(window, placeholder_text="Enter new password", show="*", width=300, height=40, corner_radius=10)
            password_entry.pack(pady=8)
            confirm_entry = ctk.CTkEntry(window, placeholder_text="Confirm new password", show="*", width=300, height=40, corner_radius=10)
            confirm_entry.pack(pady=8)

            def save_password():
                result = self.auth_controller.reset_password(username, password_entry.get(), confirm_entry.get())
                if result.get("success"):
                    messagebox.showinfo("Success", result["message"], parent=window)
                    window.destroy()
                    return
                messagebox.showerror("Error", result["message"], parent=window)

            ctk.CTkButton(
                window,
                text="Update Password",
                command=save_password,
                width=300,
                height=40,
                corner_radius=10,
                fg_color=DANGER,
                hover_color="#C03030",
                font=("Roboto", 13, "bold"),
            ).pack(pady=15)
