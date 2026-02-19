import os
import sys
import tkinter as tk
from datetime import datetime
import traceback
import subprocess
import threading
import ctypes # لإضافة التوافق مع ويندوز 10
try:
    from subprocess import CREATE_NO_WINDOW
except ImportError:
    CREATE_NO_WINDOW = 0x08000000  # Default Windows Flag for no window

import customtkinter as ctk

# --- WINDOWS 10 COMPATIBILITY PATCH ---
try:
    if os.name == 'nt':
        # تفعيل الـ High DPI لضمان وضوح الأداة على ويندوز 10 و 11
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from bridge_engine import BridgeEngine
from device_engine import DeviceMonitor, get_device_info
from licensing import TSPLicensing
from security import get_hwid
from updater import UpdateManager


# --- MODERN COLORS & STYLES ---
COLORS = {
    "bg_dark": "#121212",        # خلفية البرنامج الأساسية
    "sidebar_bg": "#1A1A1A",     # خلفية القائمة الجانبية
    "card_bg": "#1E1E1E",        # خلفية الإطارات (Cards)
    "accent_blue": "#3498DB",    # لون أزرق سامسونج
    "accent_orange": "#E67E22",  # لون برتقالي MTK
    "accent_red": "#E74C3C",     # لون أحمر شاومي
    "accent_purple": "#9B59B6",  # لون بنفسجي Unisoc
    "accent_green": "#2ECC71",   # لون أخضر النجاح
    "text_main": "#FFFFFF",      # نص رئيسي
    "text_dim": "#AAAAAA",       # نص خافت
    "border": "#333333"          # لون الحدود
}


# --- RESOURCE PATH FUNCTION ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def restart_application():
    app.log("Attempting to restart application...", "warning")
    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable] + sys.argv)
    else:
        subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)


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
            self.title("TSP TOOL - T SMART PRO")
            self.geometry("1350x880")
            self.configure(fg_color=COLORS["bg_dark"])
            
            # تعيين أيقونة البرنامج في شريط المهام والنافذة
            icon_file = resource_path(os.path.join("mtkclient", "icon.ico"))
            if os.path.exists(icon_file):
                self.iconbitmap(icon_file)

            self.hwid = get_hwid()
            self.license_manager = TSPLicensing(self.hwid)
            is_active, status = self.license_manager.check_status()
            
            self.bridge = BridgeEngine(self.log)
            self.update_manager = UpdateManager(self.log)
            self.current_view_frame = None
            self.update_window = None
            self.activation_window = None

            if not is_active:
                self.show_activation_screen(status)
            else:
                self.setup_ui()
                self.log(f"System Ready | License: {status['key_type']} | Days: {status['days_left']}", "success")
                self.monitor = DeviceMonitor(ADB_PATH, FASTBOOT_PATH, self.update_device_list)
                self.monitor.start()
                threading.Thread(target=self.check_for_updates_silent, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Critical Error: {str(e)}\n{traceback.format_exc()}"
            with open("crash_log.txt", "w") as f: f.write(error_msg)
            tk.messagebox.showerror("Error", f"Failed to start tool.\nCheck crash_log.txt")
            sys.exit(1)

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
        self.update_window.attributes("-topmost", True)
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
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0) # Monitor panel fixed width
        self.grid_rowconfigure(0, weight=0) # Top tabs fixed height
        self.grid_rowconfigure(1, weight=1) # Main content area

        # 1. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew") # Sidebar spans two rows

        ctk.CTkLabel(self.sidebar, text="TSMART PRO", font=("Impact", 34), text_color=COLORS["accent_orange"]).pack(pady=40)
        ctk.CTkLabel(self.sidebar, text="PENUMBRA CORE ACTIVE", font=("Roboto", 10, "bold"), text_color=COLORS["accent_green"]).pack(pady=(0, 10))

        nav_items = [
            ("Samsung", COLORS["accent_blue"]),
            ("MTK & Scatter", COLORS["accent_orange"]),
            ("Penumbra (Xiaomi)", COLORS["accent_red"]),
            ("Unisoc Pro", COLORS["accent_purple"]),
            ("ADB / Fastboot", "#2C3E50"),
            ("Settings", "#555555"),
        ]

        self.nav_buttons = {}
        for item, color in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=item, height=55, corner_radius=0, fg_color="transparent",
                text_color=COLORS["text_dim"], hover_color=color, anchor="w", font=("Roboto", 16, "bold"),
                padx=20, # مسافة داخلية للنص عن الحافة
                command=lambda i=item: self.show_view(i)
            )
            btn.pack(fill="x", pady=2, padx=10) # مسافة خارجية للزر عن الحافة
            self.nav_buttons[item] = btn

        # 2. TOP TABS FRAME
        self.top_tabs_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLORS["card_bg"])
        self.top_tabs_frame.grid(row=0, column=1, sticky="new", padx=15, pady=(15, 0))
        self.top_tabs_frame.grid_columnconfigure(0, weight=1) # Allow tabs to expand

        self.top_tab_buttons = {}
        top_tab_items = ["Samsung", "MTK", "Penumbra", "Unisoc", "Xiaomi", "ACB", "Settings"]
        for i, item in enumerate(top_tab_items):
            btn = ctk.CTkButton(
                self.top_tabs_frame, text=item, height=40, corner_radius=8, fg_color="transparent",
                text_color=COLORS["text_main"], hover_color=COLORS["border"], font=("Roboto", 14, "bold"),
                command=lambda i=item: self.show_view(i)
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.top_tab_buttons[item] = btn

        # Add a placeholder for the right side of the top bar (e.g., user info, minimize/close buttons)
        self.top_right_placeholder = ctk.CTkFrame(self.top_tabs_frame, fg_color="transparent")
        self.top_right_placeholder.grid(row=0, column=len(top_tab_items), padx=5, pady=5, sticky="e")
        self.top_tabs_frame.grid_columnconfigure(len(top_tab_items), weight=1) # Allow placeholder to expand

        # 3. CENTRAL CONTENT AREA
        self.central_content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=COLORS["card_bg"], border_width=1, border_color=COLORS["border"])
        self.central_content_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=(0, 15))
        self.central_content_frame.grid_rowconfigure(0, weight=1) # Content area inside central frame
        self.central_content_frame.grid_columnconfigure(0, weight=1)

        # 4. RIGHT MONITOR
        self.monitor_panel = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.monitor_panel.grid(row=0, column=2, rowspan=2, sticky="nsew") # Monitor panel spans two rows

        ctk.CTkLabel(self.monitor_panel, text="DEVICE MONITOR", font=("Roboto", 18, "bold"), text_color="#F1C40F").pack(pady=25)

        self.device_list_box = ctk.CTkTextbox(self.monitor_panel, height=320, fg_color="#000000", text_color="#F1C40F", font=("Consolas", 13), border_width=1, border_color=COLORS["border"])
        self.device_list_box.pack(padx=15, fill="x")

        self.info_panel = ctk.CTkFrame(self.monitor_panel, fg_color=COLORS["card_bg"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.info_panel.pack(pady=25, padx=15, fill="both", expand=True)
        ctk.CTkLabel(self.info_panel, text="Device Information", font=("Roboto", 15, "bold")).pack(pady=10)
        self.info_text = ctk.CTkLabel(self.info_panel, text="Waiting for device...", font=("Roboto", 12), text_color=COLORS["text_dim"], justify="left")
        self.info_text.pack(pady=15, padx=15)

        # 5. LOG CONSOLE
        self.log_frame = ctk.CTkFrame(self.central_content_frame, height=200, fg_color="#080808", corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.log_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.log_console = ctk.CTkTextbox(self.log_frame, fg_color="transparent", font=("Consolas", 12), text_color="#00FF00")
        self.log_console.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_console.configure(state="disabled") # Make log console read-only

        self.log_console.tag_config("info", foreground="#00AAFF") # Blue for info
        self.log_console.tag_config("success", foreground="#2ECC71") # Green for success
        self.log_console.tag_config("warning", foreground="#F1C40F") # Yellow for warning
        self.log_console.tag_config("error", foreground="#E74C3C") # Red for error

        self.progress_bar = ctk.CTkProgressBar(self.log_frame, height=8, corner_radius=4, progress_color=COLORS["accent_blue"])
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        # Create a frame for the actual tab content within central_content_frame
        self.tab_content_frame = ctk.CTkFrame(self.central_content_frame, corner_radius=15, fg_color=COLORS["card_bg"], border_width=1, border_color=COLORS["border"])
        self.tab_content_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0)) # Pack at top of central content frame

        # Initial view setup
        self.current_view_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")
        self.current_view_frame.pack(fill="both", expand=True)
        self.current_view_frame.grid_columnconfigure(0, weight=1)
        self.current_view_frame.grid_rowconfigure(0, weight=1)

        # Initialize with Samsung view
        self.show_view("Samsung")

    # --- VIEW LOADERS (PLACEHOLDERS FOR NOW) ---
    def load_samsung_view(self):
        # Odin Style Interface
        samsung_frame = ctk.CTkFrame(self.current_view_frame, fg_color="transparent")
        samsung_frame.pack(fill="both", expand=True, padx=10, pady=10)
        samsung_frame.grid_columnconfigure(0, weight=1)
        samsung_frame.grid_rowconfigure(0, weight=0)
        samsung_frame.grid_rowconfigure(1, weight=1)

        # Top section for Odin Style label
        odin_style_label = ctk.CTkLabel(samsung_frame, text="Odin Style", font=("Roboto", 24, "bold"), text_color=COLORS["text_main"])
        odin_style_label.grid(row=0, column=0, pady=10, sticky="w")

        # Main Odin Style content frame
        odin_content_frame = ctk.CTkFrame(samsung_frame, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        odin_content_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        odin_content_frame.grid_columnconfigure(1, weight=1) # Entry fields column

        # File selection rows
        file_labels = ["BL File:", "AP File:", "CP File:", "CSC File:", "PIT File:", "IMG File:"]
        for i, label_text in enumerate(file_labels):
            ctk.CTkLabel(odin_content_frame, text=label_text, font=("Roboto", 14), text_color=COLORS["text_dim"], anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkEntry(odin_content_frame, placeholder_text="Select file...", width=300, fg_color=COLORS["bg_dark"], border_color=COLORS["border"], text_color=COLORS["text_main"])
.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            ctk.CTkButton(odin_content_frame, text="Browse", width=80, fg_color=COLORS["accent_blue"], hover_color="#2980B9").grid(row=i, column=2, padx=10, pady=5)

        # Device/Operation buttons
        buttons_frame = ctk.CTkFrame(samsung_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=10)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        buttons_frame.grid_columnconfigure(3, weight=1)

        # Example buttons (as seen in image, roughly)
        button_texts = [
            "Device", "Read EFS", "Multi-Device", "DL-Port",
            "FRP Service", "PID Service", "ADT Service", "SNP Service",
            "Read Cert", "MTP Service", "Read Factory", "TDP Service",
            "Raw Service", "NVM Service", "FSP Service", "Full Format"
        ]

        for i, text in enumerate(button_texts):
            row = i // 4
            col = i % 4
            ctk.CTkButton(buttons_frame, text=text, fg_color=COLORS["card_bg"], text_color=COLORS["text_main"], hover_color=COLORS["border"], border_color=COLORS["border"], border_width=1, height=40)
.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # Service button at the bottom
        service_button = ctk.CTkButton(samsung_frame, text="Service", fg_color=COLORS["accent_blue"], hover_color="#2980B9", height=50, font=("Roboto", 16, "bold"))
        service_button.grid(row=3, column=0, sticky="ew", pady=10)

    def load_mtk_view(self):
        ctk.CTkLabel(self.current_view_frame, text="MTK View Content", font=("Roboto", 20)).pack(pady=50)

    def load_penumbra_view(self):
        ctk.CTkLabel(self.current_view_frame, text="Penumbra (Xiaomi) View Content", font=("Roboto", 20)).pack(pady=50)

    def load_unisoc_view(self):
        ctk.CTkLabel(self.current_view_frame, text="Unisoc View Content", font=("Roboto", 20)).pack(pady=50)

    def load_adb_fastboot_view(self):
        ctk.CTkLabel(self.current_view_frame, text="ADB / Fastboot View Content", font=("Roboto", 20)).pack(pady=50)

    def load_settings_view(self):
        ctk.CTkLabel(self.current_view_frame, text="Settings View Content", font=("Roboto", 20)).pack(pady=50)

    def log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.configure(state="normal") # Enable writing
        self.log_console.insert("end", f"[{timestamp}] {msg}\n", level)
        self.log_console.see("end")
        self.log_console.configure(state="disabled") # Disable writing

    def update_device_list(self, devices):
        self.device_list_box.delete("1.0", "end")
        if not devices:
            self.device_list_box.insert("end", "No devices found...")
            self.info_text.configure(text="Waiting for device...")
        else:
            for dev in devices: self.device_list_box.insert("end", f"▶ {dev}\n")
            adb_devs = [d for d in devices if "[ADB]" in d]
            if adb_devs:
                serial = adb_devs[0].split()[-1]
                info = get_device_info(ADB_PATH, serial)
                info_str = "\n".join([f"• {k}: {v}" for k, v in info.items()])
                self.info_text.configure(text=info_str)

    def show_view(self, name):
        # Destroy current view
        if self.current_view_frame:
            for widget in self.current_view_frame.winfo_children():
                widget.destroy()
            self.current_view_frame.destroy()

        # Create new view frame
        self.current_view_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")
        self.current_view_frame.pack(fill="both", expand=True)
        self.current_view_frame.grid_columnconfigure(0, weight=1)
        self.current_view_frame.grid_rowconfigure(0, weight=1)

        # Highlight selected sidebar button
        for btn_name, btn_widget in self.nav_buttons.items():
            if btn_name == name:
                btn_widget.configure(fg_color=COLORS["card_bg"], text_color=COLORS["text_main"])
            else:
                btn_widget.configure(fg_color="transparent", text_color=COLORS["text_dim"])

        # Highlight selected top tab button
        for btn_name, btn_widget in self.top_tab_buttons.items():
            if btn_name == name:
                btn_widget.configure(fg_color=COLORS["accent_blue"], text_color=COLORS["text_main"])
            else:
                btn_widget.configure(fg_color="transparent", text_color=COLORS["text_dim"])

        # Load content based on view name
        if name == "Samsung":
            self.load_samsung_view()
        elif name == "MTK":
            self.load_mtk_view()
        elif name == "Penumbra":
            self.load_penumbra_view()
        elif name == "Unisoc":
            self.load_unisoc_view()
        elif name == "ADB / Fastboot":
            self.load_adb_fastboot_view()
        elif name == "Settings":
            self.load_settings_view()
        else:
            ctk.CTkLabel(self.current_view_frame, text=f"View for {name} not implemented yet.", font=("Roboto", 20)).pack(pady=50)


if __name__ == "__main__":
    app = TSPToolPro()
    app.mainloop()
