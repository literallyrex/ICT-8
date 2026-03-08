import threading
import time
import tkinter as tk
import tkinter.messagebox as messagebox

import customtkinter as ctk

from utils.constants import ACCENT, PRIMARY, SUCCESS, TEXT_MUTED

try:
    import tkintermapview

    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

try:
    from geopy.geocoders import Nominatim

    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


class BaseView:
    def __init__(self, app):
        self.app = app

    def __getattr__(self, name):
        return getattr(self.app, name)

    def fade_in_widget(self, widget, target_alpha=1.0, step=0.08, delay=15):
        try:
            widget._fade_step = getattr(widget, "_fade_step", 0.0) + step
            if widget._fade_step >= target_alpha:
                widget._fade_step = target_alpha
                return
            widget.after(delay, lambda: self.fade_in_widget(widget, target_alpha, step, delay))
        except Exception:
            pass

    def slide_in_frame(self, widget, start_y=20, step=3, delay=10):
        try:
            current = getattr(widget, "_slide_offset", start_y)
            if current <= 0:
                widget._slide_offset = 0
                return

            manager = widget.winfo_manager()
            if not manager:
                return

            widget._slide_offset = current - step

            if manager == "grid":
                info = widget.grid_info()
                original_pady = info.get("pady", (0, 0))
                if isinstance(original_pady, int):
                    original_pady = (original_pady, original_pady)
                widget.grid_configure(pady=(current - step, original_pady[1]))
            else:
                info = widget.pack_info()
                original_pady = info.get("pady", (0, 0))
                if isinstance(original_pady, int):
                    original_pady = (original_pady, original_pady)
                widget.pack_configure(pady=(current - step, original_pady[1]))

            widget.after(delay, lambda: self.slide_in_frame(widget, start_y, step, delay))
        except Exception:
            pass

    def animate_children(self, parent, delay_between=40):
        children = parent.winfo_children()
        for index, child in enumerate(children):
            child.after(index * delay_between, lambda widget=child: self.slide_in_frame(widget, start_y=15, step=5))

    def open_map_picker(self, target_entry):
        if not MAP_AVAILABLE:
            messagebox.showinfo("Info", "Map feature requires tkintermapview.\nInstall with: pip install tkintermapview")
            return

        map_window = ctk.CTkToplevel(self.app)
        map_window.title("Pick Your Address")
        map_window.geometry("700x550")
        map_window.grab_set()
        map_window.resizable(True, True)
        self.setup_dialog_close(map_window)

        top_frame = ctk.CTkFrame(map_window, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(10, 5))

        search_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Search place (e.g. Manila, Philippines)...",
            width=430,
            height=38,
            corner_radius=10,
        )
        search_entry.pack(side="left", padx=(0, 8))

        address_var = tk.StringVar(value="Click on the map or search a place to select address")
        ctk.CTkLabel(
            map_window,
            textvariable=address_var,
            font=("Roboto", 12),
            text_color=TEXT_MUTED,
            wraplength=650,
        ).pack(padx=15, pady=(0, 5))

        map_widget = tkintermapview.TkinterMapView(map_window, width=660, height=380, corner_radius=12)
        map_widget.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        map_widget.set_position(14.5995, 120.9842)
        map_widget.set_zoom(6)

        current_marker = [None]
        selected_address = [None]
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UnivRegSys/1.2"

        def update_address_label(text):
            try:
                if map_window.winfo_exists():
                    address_var.set(text)
            except Exception:
                pass

        def on_map_click(coords):
            latitude, longitude = coords
            try:
                if not map_window.winfo_exists():
                    return
            except Exception:
                return

            if current_marker[0]:
                try:
                    current_marker[0].delete()
                except Exception:
                    pass

            try:
                current_marker[0] = map_widget.set_marker(
                    latitude,
                    longitude,
                    text="Selected Location",
                    marker_color_circle="#D32F2F",
                    marker_color_outside="#B71C1C",
                    text_color="white",
                )
            except Exception:
                pass

            update_address_label("Searching address details...")
            selected_address[0] = f"{latitude:.6f}, {longitude:.6f}"

            def do_reverse_with_retry():
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        if GEOPY_AVAILABLE:
                            geolocator = Nominatim(user_agent=user_agent)
                            location = geolocator.reverse((latitude, longitude), timeout=15)
                            if location:
                                selected_address[0] = location.address
                                if map_window.winfo_exists():
                                    map_window.after(0, lambda: update_address_label(location.address))
                                return
                        break
                    except Exception:
                        if attempt < max_retries - 1:
                            if map_window.winfo_exists():
                                map_window.after(0, lambda: update_address_label("Slow connection... retrying"))
                            time.sleep(1.5)
                        else:
                            if map_window.winfo_exists():
                                map_window.after(0, lambda: update_address_label(selected_address[0]))

            self.executor.submit(do_reverse_with_retry)

        map_widget.add_left_click_map_command(on_map_click)

        def search_place():
            query = search_entry.get().strip()
            if not query:
                return

            update_address_label("Searching for location...")

            def do_search_with_retry():
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        if GEOPY_AVAILABLE:
                            geolocator = Nominatim(user_agent=user_agent)
                            location = geolocator.geocode(query, timeout=20)
                            if location and map_window.winfo_exists():
                                map_window.after(
                                    0,
                                    lambda: [
                                        map_widget.set_position(location.latitude, location.longitude),
                                        map_widget.set_zoom(15),
                                        on_map_click((location.latitude, location.longitude)),
                                    ],
                                )
                                return
                    except Exception:
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue

                if map_window.winfo_exists():
                    map_window.after(
                        0,
                        lambda: messagebox.showerror(
                            "Search Error",
                            "Could not find location or service busy.\nPlease try clicking manually or checking internet.",
                            parent=map_window,
                        ),
                    )
                    map_window.after(0, lambda: update_address_label("Search failed. Try manual click."))

            threading.Thread(target=do_search_with_retry, daemon=True).start()

        ctk.CTkButton(
            top_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=10,
            fg_color=PRIMARY,
            font=("Roboto", 12, "bold"),
            command=search_place,
        ).pack(side="left", padx=(0, 5))

        search_entry.bind("<Return>", lambda _event: search_place())

        button_frame = ctk.CTkFrame(map_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 12))

        def use_address():
            if selected_address[0]:
                target_entry.delete(0, "end")
                target_entry.insert(0, selected_address[0])
                map_window.destroy()
            else:
                messagebox.showwarning("No Selection", "Please click on the map to select a location first.", parent=map_window)

        ctk.CTkButton(
            button_frame,
            text="Use This Address",
            width=200,
            height=38,
            corner_radius=10,
            fg_color=SUCCESS,
            hover_color="#248A5E",
            font=("Roboto", 13, "bold"),
            command=use_address,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=ACCENT,
            font=("Roboto", 12),
            command=map_window.destroy,
        ).pack(side="left")
