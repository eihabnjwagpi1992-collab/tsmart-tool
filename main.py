import os
import sys
import tkinter as tk
from datetime import datetime
import traceback
import subprocess
import threading
import ctypes

try:
    from subprocess import CREATE_NO_WINDOW
except ImportError:
    CREATE_NO_WINDOW = 0x08000000

import customtkinter as ctk

# --- WINDOWS 10 COMPATIBILITY PATCH ---
try:
    if os.name == 'nt':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from bridge_engine import BridgeEngine
from device_engine import DeviceMonitor, get_device_info
from updater import UpdateManager
from auth import AuthManager

# --- MODERN COLORS & STYLES ---
COLORS = {
    "bg_dark": "#121212",
    "sidebar_bg": "#1A1A1A",
    "card_bg": "#1E1E1E",
    "accent_blue": "#3498DB",
    "accent_orange": "#E67E22",
    "accent_red": "#E74C3C",
    "accent_purple": "#9B59B6",
    "accent_green": "#2ECC71",
    "text_main": "#FFFFFF",
    "text_dim": "#AAAAAA",
    "border": "#333333"
}

# --- RESOURCE PATH FUNCTION ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- BINARY PATHS ---
if os.name == 'nt':
    ADB_PATH = resource_path(os.path.join("bin", "adb.exe"))
    FASTBOOT_PATH = resource_path(os.path.join("bin", "fastboot.exe"))
else:
    ADB_PATH = resource_path(os.path.join("bin", "adb"))
    FASTBOOT_PATH = resource_path(os.path.join("bin", "fastboot"))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TSPToolPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.title("TSP TOOL PRO - Penumbra Powered Suite v3.1")
            self.geometry("1350x880")
            self.configure(fg_color=COLORS["bg_dark"])
            
            icon_file = resource_path(os.path.join("mtkclient", "icon.ico"))
            if os.path.exists(icon_file):
                self.iconbitmap(icon_file)

            self.bridge = BridgeEngine(self.log)
            self.update_manager = UpdateManager(self.log)
            self.auth_manager = AuthManager()
            self.current_view_frame = None
            self.update_window = None
            self.login_window = None

            self.show_login_screen()
            
        except Exception as e:
            error_msg = f"Critical Error: {str(e)}\n{traceback.format_exc()}"
            with open("crash_log.txt", "w") as f: f.write(error_msg)
            tk.messagebox.showerror("Error", f"Failed to start tool.\nCheck crash_log.txt")
            sys.exit(1)

    def show_login_screen(self):
        self.withdraw() # إخفاء النافذة الرئيسية
        self.login_window = ctk.CTkToplevel(self)
        self.login_window.title("Login")
        self.login_window.geometry("400x500")
        self.login_window.protocol("WM_DELETE_WINDOW", sys.exit)
        self.login_window.attributes("-topmost", True)

        ctk.CTkLabel(self.login_window, text="TSP TOOL PRO", font=("Impact", 34), text_color=COLORS["accent_red"]).pack(pady=30)
        ctk.CTkLabel(self.login_window, text="Email & Password Login", font=("Roboto", 16)).pack(pady=10)

        self.email_entry = ctk.CTkEntry(self.login_window, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.login_window, placeholder_text="Password", show="*", width=300, height=40)
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.login_window, text="Login", command=self.attempt_login, width=300, height=40).pack(pady=20)

    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        success, message = self.auth_manager.login(email, password)

        if success:
            self.login_window.destroy()
            self.deiconify() # إظهار النافذة الرئيسية
            self.setup_ui()
            self.log("System Ready | User Logged In", "success")
            self.monitor = DeviceMonitor(ADB_PATH, FASTBOOT_PATH, self.update_device_list)
            self.monitor.start()
            threading.Thread(target=self.check_for_updates_silent, daemon=True).start()
        else:
            tk.messagebox.showerror("Login Failed", message)

    def check_for_updates_silent(self):
        try:
            update_data = self.update_manager.check_for_updates()
            if update_data: self.after(0, lambda: self.show_update_dialog(update_data))
        except: pass

    def check_for_updates(self):
        self.log("Checking for updates...", "info")
        threading.Thread(target=self._check_updates_manual_thread, daemon=True).start()

    def _check_updates_manual_thread(self):
        update_data = self.update_manager.check_for_updates()
        if update_data: self.after(0, lambda: self.show_update_dialog(update_data))
        else: self.after(0, lambda: self.log("Latest version installed.", "success"))

    def show_update_dialog(self, data):
        if hasattr(self, 'update_window') and self.update_window and self.update_window.winfo_exists():
            self.update_window.lift()
            self.update_window.focus_force()
            return

        self.update_window = ctk.CTkToplevel(self)
        self.update_window.attributes("-topmost", True)
        self.update_window.title("Update Available")
        self.update_window.geometry("480x380")
        self.update_window.configure(fg_color=COLORS["card_bg"])
        
        ctk.CTkLabel(self.update_window, text="✨ New Update Available! ✨", font=("Roboto", 20, "bold"), text_color=COLORS["accent_green"]).pack(pady=20)
        ctk.CTkLabel(self.update_window, text=f"Version: {data['version']}", font=("Roboto", 14)).pack()
        
        changelog_frame = ctk.CTkFrame(self.update_window, corner_radius=12, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        changelog_frame.pack(pady=20, padx=25, fill="both", expand=True)
        
        changelog_text = tk.Text(changelog_frame, height=6, bg=COLORS["bg_dark"], fg=COLORS["text_main"], font=("Roboto", 11), borderwidth=0, padx=10, pady=10)
        changelog_text.insert("1.0", data.get("changelog", "Improvements and fixes."))
        changelog_text.config(state="disabled")
        changelog_text.pack(fill="both", expand=True)
        
        def start_update():
            self.update_window.destroy()
            self.log("🚀 Downloading update...", "warning")
            threading.Thread(target=lambda: self.update_manager.download_and_install(data['download_url']), daemon=True).start()

        ctk.CTkButton(self.update_window, text="Update Now", fg_color=COLORS["accent_green"], hover_color="#27AE60", font=("Roboto", 14, "bold"), command=start_update, height=45).pack(pady=10, padx=25, fill="x")
        ctk.CTkButton(self.update_window, text="Maybe Later", fg_color="transparent", border_width=1, border_color=COLORS["border"], command=self.update_window.destroy, height=35).pack(pady=5)

    def setup_ui(self):
        # New Odin Style Layout
        self.grid_columnconfigure(0, weight=0) # Sidebar column
        self.grid_columnconfigure(1, weight=1) # Main content column
        self.grid_columnconfigure(2, weight=0) # Monitor panel column
        self.grid_rowconfigure(0, weight=0) # Top bar row
        self.grid_rowconfigure(1, weight=1) # Main body row
        self.grid_rowconfigure(2, weight=0) # Log console row

        # 1. TOP BAR
        self.top_bar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.top_nav_buttons = {}
        top_nav_items = ["Samsung", "MTK", "Penumbra", "Unisoc", "Xiaomi", "ACB", "Settings"]
        for item in top_nav_items:
            btn = ctk.CTkButton(self.top_bar, text=item, height=40, corner_radius=8, fg_color="transparent", hover_color=COLORS["accent_orange"], font=("Roboto", 14, "bold"),
                                command=lambda i=item: self.show_view(i))
            btn.pack(side="left", padx=10, pady=10)
            self.top_nav_buttons[item] = btn

        # 2. MAIN BODY (contains sidebar, content area, and monitor panel)
        self.main_body = ctk.CTkFrame(self, fg_color="transparent")
        self.main_body.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.main_body.grid_columnconfigure(1, weight=1)
        self.main_body.grid_rowconfigure(0, weight=1)

        # 3. SIDEBAR (Left)
        self.sidebar = ctk.CTkFrame(self.main_body, width=220, corner_radius=10, fg_color=COLORS["card_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(self.sidebar, text="TSMART PRO", font=("Impact", 28), text_color=COLORS["accent_orange"]).pack(pady=20)

        nav_items = [
            ("Home", "home_icon.png"), # Placeholder for icons
            ("Samsung", "samsung_icon.png"),
            ("MTK & Scatter", "mtk_icon.png"),
            ("Partition Manager", "partition_icon.png"),
            ("Device Checker", "device_icon.png"),
            ("ADB", "adb_icon.png"),
            ("Settings", "settings_icon.png"),
            ("About", "about_icon.png"),
        ]

        self.nav_buttons = {}
        for item, icon in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=item, height=45, corner_radius=8, fg_color="transparent",
                text_color=COLORS["text_dim"], hover_color=COLORS["accent_orange"], anchor="w", font=("Roboto", 14, "bold"),
                command=lambda i=item: self.show_view(i)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[item] = btn

        # 4. MAIN CONTENT (Center)
        self.content_area = ctk.CTkFrame(self.main_body, corner_radius=10, fg_color=COLORS["card_bg"])
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # 5. RIGHT MONITOR
        self.monitor_panel = ctk.CTkFrame(self.main_body, width=280, corner_radius=10, fg_color=COLORS["card_bg"])
        self.monitor_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(self.monitor_panel, text="DEVICE MONITOR", font=("Roboto", 18, "bold"), text_color="#F1C40F").pack(pady=25)

        self.device_list_box = ctk.CTkTextbox(self.monitor_panel, height=320, fg_color="#000000", text_color="#F1C40F", font=("Consolas", 13), border_width=1, border_color=COLORS["border"])
        self.device_list_box.pack(padx=15, fill="x")

        # 6. LOG CONSOLE
        self.log_console = ctk.CTkTextbox(self, height=150, fg_color=COLORS["card_bg"], text_color=COLORS["text_main"], font=("Consolas", 12), border_width=1, border_color=COLORS["border"])
        self.log_console.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.show_view("Home") # Default view

    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        if level == "info":
            formatted_message = f"{timestamp} {message}\n"
            color = COLORS["text_main"]
        elif level == "warning":
            formatted_message = f"{timestamp} ⚠️ {message}\n"
            color = COLORS["accent_orange"]
        elif level == "error":
            formatted_message = f"{timestamp} ❌ {message}\n"
            color = COLORS["accent_red"]
        elif level == "success":
            formatted_message = f"{timestamp} ✅ {message}\n"
            color = COLORS["accent_green"]
        else:
            formatted_message = f"{timestamp} {message}\n"
            color = COLORS["text_main"]

        self.log_console.configure(state="normal")
        self.log_console.insert("end", formatted_message)
        self.log_console.configure(state="disabled")
        self.log_console.see("end")

    def update_device_list(self, devices):
        self.device_list_box.configure(state="normal")
        self.device_list_box.delete("1.0", "end")
        if devices:
            for device in devices:
                self.device_list_box.insert("end", f"[COM{device['port']}] {device['description']}\n")
        else:
            self.device_list_box.insert("end", "No Device Connected")
        self.device_list_box.configure(state="disabled")

    def show_view(self, view_name):
        if self.current_view_frame:
            for widget in self.current_view_frame.winfo_children():
                widget.destroy()
            self.current_view_frame.destroy()

        self.current_view_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.current_view_frame.pack(fill="both", expand=True)

        # Update active button styles
        for btn_dict in [self.nav_buttons, self.top_nav_buttons]:
            for item, btn in btn_dict.items():
                if item == view_name or (view_name == "MTK & Scatter" and item == "MTK") or \
                   (view_name == "Penumbra" and item == "Xiaomi") or \
                   (view_name == "Unisoc Pro" and item == "Unisoc") or \
                   (view_name == "ADB / Fastboot" and item == "ADB") or \
                   (view_name == "Partition Manager" and item == "Partition Manager") or \
                   (view_name == "Device Checker" and item == "Device Checker"):
                    btn.configure(fg_color=COLORS["accent_orange"], text_color=COLORS["text_main"])
                else:
                    btn.configure(fg_color="transparent", text_color=COLORS["text_dim"])

        if view_name == "Home": self.create_home_view()
        elif view_name == "Samsung": self.create_samsung_view(self.bridge)
        elif view_name == "MTK" or view_name == "MTK & Scatter": self.create_mtk_view(self.bridge)
        elif view_name == "Penumbra" or view_name == "Penumbra (Xiaomi)": self.create_xiaomi_view(self.bridge)
        elif view_name == "Unisoc" or view_name == "Unisoc Pro": self.create_unisoc_view(self.bridge)
        elif view_name == "Partition Manager": self.create_partition_manager_view(self.bridge)
        elif view_name == "Device Checker": self.create_device_checker_view(self.bridge)
        elif view_name == "ADB" or view_name == "ADB / Fastboot": self.create_adb_view(self.bridge)
        elif view_name == "Settings": self.create_settings_view()
        elif view_name == "About": self.create_about_view()
        else:
            self.create_placeholder_view(view_name)

    def create_home_view(self):
        ctk.CTkLabel(self.current_view_frame, text="Welcome to TSMART PRO", font=("Roboto", 24, "bold")).pack(pady=20)

    def create_partition_manager_view(self, bridge):
        partition_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        partition_frame.pack(fill="both", expand=True)

        # Partition Manager Services (Grid Layout)
        services_frame = ctk.CTkFrame(partition_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="Partition Manager Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "Read Partition Table", "Backup Partition", "Restore Partition", "Erase Partition",
            "Format Partition", "Resize Partition", "Mount Partition", "Unmount Partition"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_partition_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_device_checker_view(self, bridge):
        checker_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        checker_frame.pack(fill="both", expand=True)

        # Device Checker Services (Grid Layout)
        services_frame = ctk.CTkFrame(checker_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="Device Checker Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "Check ADB Status", "Check Fastboot Status", "Read Device Info", "Check Root Status",
            "Check Bootloader Status", "Check FRP Status", "Check Battery Health", "Check Storage Info"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_device_checker_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_samsung_view(self, bridge):
        samsung_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        samsung_frame.pack(fill="both", expand=True)

        # Odin Style Section
        odin_frame = ctk.CTkFrame(samsung_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        odin_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(odin_frame, text="Odin Style", font=("Roboto", 16, "bold")).pack(pady=10)

        file_types = ["BL File", "AP File", "CP File", "CSC File"]
        for file_type in file_types:
            file_row = ctk.CTkFrame(odin_frame, fg_color="transparent")
            file_row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(file_row, text=file_type, width=80, anchor="w").pack(side="left", padx=5)
            ctk.CTkEntry(file_row, placeholder_text=f"Select {file_type}", width=300).pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkButton(file_row, text="Browse", width=80).pack(side="left", padx=5)

            ctk.CTkButton(odin_frame, text="Service", fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 14, "bold"), height=40, command=lambda: bridge.run_samsung_command("flash")).pack(pady=10, padx=10, fill="x")

        # Other Samsung Services (Grid Layout)
        services_frame = ctk.CTkFrame(samsung_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="Services", font=("Roboto", 16, "bold")).pack(pady=10)

        # Example buttons, need to map to actual functions later
        buttons_data = [
            "FRP Service", "Read Codes", "Multi-Device", "DIP Service",
            "Read Cert", "PDS Service", "ADT Service", "USB Service",
            "Root Service", "MBN Service", "FRP Remove", "Test Service",
            "NVM Service", "EFS Service", "Reset Factory", "Reset FRP"
        ]

        # Create a grid for buttons
        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_samsung_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_mtk_view(self, bridge):
        mtk_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        mtk_frame.pack(fill="both", expand=True)

        # MTK Services (Grid Layout)
        services_frame = ctk.CTkFrame(mtk_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="MTK Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "Read Info", "FRP Bypass", "Format Data", "Backup NVRAM",
            "Restore NVRAM", "Unlock Bootloader", "Lock Bootloader", "Erase FRP",
            "Factory Reset", "Read Partition", "Write Partition", "Repair IMEI"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_mtk_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_xiaomi_view(self, bridge):
        xiaomi_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        xiaomi_frame.pack(fill="both", expand=True)

        # Xiaomi Services (Grid Layout)
        services_frame = ctk.CTkFrame(xiaomi_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="Xiaomi Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "Read Info", "FRP Bypass", "Flash Fastboot", "Flash Recovery",
            "Unlock Bootloader", "Lock Bootloader", "Erase FRP", "Factory Reset",
            "Disable Mi Account", "Enable Mi Account", "Read QCN", "Write QCN"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_xiaomi_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_unisoc_view(self, bridge):
        unisoc_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        unisoc_frame.pack(fill="both", expand=True)

        # Unisoc Services (Grid Layout)
        services_frame = ctk.CTkFrame(unisoc_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="Unisoc Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "Read Info", "FRP Bypass", "Format Data", "Backup NVRAM",
            "Restore NVRAM", "Unlock Bootloader", "Lock Bootloader", "Erase FRP",
            "Factory Reset", "Read Partition", "Write Partition", "Repair IMEI"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_unisoc_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_adb_view(self, bridge):
        adb_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        adb_frame.pack(fill="both", expand=True)

        # ADB/Fastboot Services (Grid Layout)
        services_frame = ctk.CTkFrame(adb_frame, corner_radius=10, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        services_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(services_frame, text="ADB/Fastboot Services", font=("Roboto", 16, "bold")).pack(pady=10)

        buttons_data = [
            "ADB Devices", "Fastboot Devices", "Reboot to Bootloader", "Reboot to Recovery",
            "Sideload", "Install APK", "Uninstall APK", "Pull File",
            "Push File", "Wipe Data", "Unlock Bootloader", "Lock Bootloader"
        ]

        button_grid_frame = ctk.CTkFrame(services_frame, fg_color="transparent")
        button_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = 4
        for i, btn_text in enumerate(buttons_data):
            row = i // cols
            col = i % cols
            btn = ctk.CTkButton(button_grid_frame, text=btn_text, fg_color=COLORS["accent_blue"], hover_color="#2980B9", font=("Roboto", 12, "bold"), height=35, command=lambda cmd=btn_text: bridge.run_adb_command(cmd.replace(" ", "_").lower()))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        for i in range(cols):
            button_grid_frame.grid_columnconfigure(i, weight=1)

    def create_settings_view(self):
        settings_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(settings_frame, text="Settings", font=("Roboto", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(settings_frame, text="Theme: Dark (Default)", font=("Roboto", 14)).pack(pady=5)
        ctk.CTkLabel(settings_frame, text="Language: English (Default)", font=("Roboto", 14)).pack(pady=5)
        ctk.CTkButton(settings_frame, text="Check for Updates", command=self.check_for_updates).pack(pady=10)

    def create_about_view(self):
        about_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        about_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(about_frame, text="About TSP TOOL PRO", font=("Roboto", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(about_frame, text="Version: 3.1", font=("Roboto", 14)).pack(pady=5)
        ctk.CTkLabel(about_frame, text="Developed by Penumbra Team", font=("Roboto", 14)).pack(pady=5)
        ctk.CTkLabel(about_frame, text="© 2023-2024 All Rights Reserved", font=("Roboto", 12)).pack(pady=5)

    def create_placeholder_view(self, view_name):
        placeholder_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        placeholder_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(placeholder_frame, text=f"Coming Soon: {view_name}", font=("Roboto", 24, "bold")).pack(pady=50)


if __name__ == "__main__":
    app = TSPToolPro()
    app.mainloop()
