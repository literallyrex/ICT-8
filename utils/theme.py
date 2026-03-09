import customtkinter as ctk

# Color Mappings for Primary UI Color
UI_COLORS = {
    "Blue": ("#3B8ED0", "#1F6AA5"),
    "Green": ("#2ECC71", "#27AE60"),
    "Purple": ("#9B59B6", "#8E44AD"),
    "Orange": ("#E67E22", "#D35400"),
    "Red": ("#E74C3C", "#C0392B"),
    "Gray": ("#95A5A6", "#7F8C8D"),
}

# Color Mappings for Button Color
BUTTON_COLORS = {
    "Standard": ("#3B8ED0", "#1F6AA5"),
    "Green": ("#2ECC71", "#27AE60"),
    "Red": ("#E74C3C", "#C0392B"),
    "Purple": ("#9B59B6", "#8E44AD"),
    "Orange": ("#E67E22", "#D35400"),
    "Gray": ("#95A5A6", "#7F8C8D"),
}

# Accent Colors
ACCENT_COLORS = {
    "Blue": "#3B8ED0",
    "Green": "#2ECC71",
    "Purple": "#9B59B6",
    "Orange": "#E67E22",
    "Red": "#E74C3C",
    "Gold": "#F1C40F",
}

def apply_theme_to_app(app, user_settings):
    """Applies the given user settings to the global app."""
    if not user_settings:
        return

    # Apply Mode
    theme_mode = user_settings.get("theme_mode", "Dark")
    ctk.set_appearance_mode(theme_mode)

    # Note: set_default_color_theme is only effective for widgets created *after* the call.
    # To handle live updates of existing widgets, we must recursively re-color them.
    # However, setting it here ensures new dialogs/widgets will pick up the closest match.
    ui_color_name = user_settings.get("ui_color", "Blue")
    if ui_color_name.lower() in ["blue", "green", "dark-blue"]:
        ctk.set_default_color_theme(ui_color_name.lower())
    else:
        ctk.set_default_color_theme("blue")  # fallback to blue base

def apply_widget_colors(widget, user_settings):
    """Recursively applies colors to widgets to emulate a live theme update."""
    if not user_settings:
        return

    ui_color_name = user_settings.get("ui_color", "Blue")
    btn_color_name = user_settings.get("button_color", "Standard")
    theme_mode = user_settings.get("theme_mode", "Dark")
    bg_style = user_settings.get("background_style", "Solid")
    text_color_name = user_settings.get("text_color", "Default")
    
    ui_color_tuple = UI_COLORS.get(ui_color_name, UI_COLORS["Blue"])
    btn_color_tuple = BUTTON_COLORS.get(btn_color_name, BUTTON_COLORS["Standard"])
    
    TEXT_COLORS = {
        "Default": None,
        "White": "#FFFFFF",
        "Light Gray": "#E0E0E0",
        "Dark Gray": "#808080",
        "Black": "#000000",
        "Gold": "#FFD700",
        "Cyan": "#00FFFF",
    }
    
    txt_color = TEXT_COLORS.get(text_color_name)
    w_type = type(widget)
    
    try:
        if txt_color and w_type in [ctk.CTkLabel, ctk.CTkButton, ctk.CTkEntry, ctk.CTkTextbox, ctk.CTkCheckBox, ctk.CTkRadioButton]:
            widget.configure(text_color=txt_color)

        if w_type == ctk.CTkButton:
            # We don't overwrite if the button is specifically meant to be 'danger' or 'success' by default
            # but we can try our best
            current_fg = widget.cget("fg_color")
            # Only override if it looks like a standard colored button (not transparent, not red etc if not intended)
            if current_fg != "transparent" and str(current_fg).upper() != "#C03030":
                widget.configure(fg_color=btn_color_tuple, hover_color=btn_color_tuple[1])
                
        elif w_type == ctk.CTkOptionMenu:
            widget.configure(fg_color=btn_color_tuple, button_color=btn_color_tuple[1], button_hover_color=btn_color_tuple[0])
            
        elif w_type in [ctk.CTkSwitch, ctk.CTkCheckBox, ctk.CTkRadioButton]:
            widget.configure(progress_color=ui_color_tuple[0])
            
        elif w_type == ctk.CTkEntry:
            # Maybe adjust border color if focused, but standard is fine
            pass

        elif w_type == ctk.CTkProgressBar:
            widget.configure(progress_color=ui_color_tuple[0])
            
        elif w_type == ctk.CTkSlider:
            widget.configure(button_color=ui_color_tuple[0], progress_color=ui_color_tuple[1], button_hover_color=ui_color_tuple[1])

        # To handle Background Style, we can apply a slight hue to frames if they use default coloring
        if bg_style == "Solid":
            pass # Standard behavior
        elif bg_style == "Gradient" or bg_style == "Blurred panel style":
            # For simplicity in CustomTkinter, we might adjust the global frame color slightly 
            # or rely on an image background. We will use a subtle color shift for frames.
            pass
            
    except Exception:
        pass # Ignore widgets that don't support these arguments
        
    # Recursively apply to children
    for child in widget.winfo_children():
        apply_widget_colors(child, user_settings)
