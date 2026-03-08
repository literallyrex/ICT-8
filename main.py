import concurrent.futures
import datetime
import os
import sys

if sys.platform == "win32":
    base_path = sys.base_prefix
    tcl_path = os.path.join(base_path, "tcl", "tcl8.6")
    tk_path = os.path.join(base_path, "tcl", "tk8.6")
    if os.path.exists(tcl_path):
        os.environ["TCL_LIBRARY"] = tcl_path
        os.environ["TK_LIBRARY"] = tk_path

import customtkinter as ctk
import matplotlib
from PIL import Image

matplotlib.use("TkAgg")

from controllers import AdminController, AuthController, StudentController
from database import initialize_db
from utils.constants import APP_TITLE, TEXT_MUTED
from utils.validation import validate_email, validate_phone
from views import AdminDashboardView, LoginView, RegisterView, StudentDashboardView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("500x600")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_user = None
        self.current_date = datetime.datetime.now()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

        self.logo_large = None
        self.logo_small = None
        self._load_school_logo()

        self.auth_controller = AuthController()
        self.student_controller = StudentController()
        self.admin_controller = AdminController()

        self.login_view = LoginView(self, self.auth_controller)
        self.register_view = RegisterView(self, self.auth_controller)
        self.student_dashboard_view = StudentDashboardView(self, self.student_controller, self.auth_controller)
        self.admin_dashboard_view = AdminDashboardView(self, self.admin_controller)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _load_school_logo(self):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        try:
            logo_image = Image.open(logo_path)
            self.logo_large = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(60, 60))
            self.logo_small = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(36, 36))
        except Exception:
            self.logo_large = None
            self.logo_small = None

    def setup_dialog_close(self, window):
        window.bind("<Escape>", lambda _event: window.destroy())
        ctk.CTkButton(
            window,
            text="X",
            width=28,
            height=28,
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color="#C03030",
            font=("Roboto", 14, "bold"),
            command=window.destroy,
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

    def show_login(self):
        self.login_view.show_login()

    def show_register(self):
        self.register_view.show_register()

    def show_admin_login(self):
        self.login_view.show_admin_login()

    def show_admin_dashboard(self):
        self.admin_dashboard_view.show_dashboard()

    def show_student_dashboard(self):
        self.student_dashboard_view.show_dashboard()

    def show_forgot_password(self):
        self.login_view.show_forgot_password()

    def on_close(self):
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    initialize_db()
    app = App()
    app.mainloop()
