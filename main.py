import os
import sys
import tkinter as tk
from datetime import datetime
import traceback
import subprocess
import threading
import ctypes # لإضافة التوافق مع ويندوز 10

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
            self.title("TSP TOOL PRO - Penumbra Powered Suite v3.1")
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
        if self.update_window and self.update_window.winfo_exists():
            self.update_window.focus(); return

        self.update_window = ctk.CTkToplevel(self)
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
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="TSP TOOL PRO", font=("Impact", 34), text_color=COLORS["accent_red"]).pack(pady=40)
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
                command=lambda i=item: self.show_view(i)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[item] = btn

        # 2. MAIN CONTENT
        self.main_container = ctk.CTkFrame(self, corner_radius=20, fg_color=COLORS["bg_dark"])
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=COLORS["card_bg"], border_width=1, border_color=COLORS["border"])
        self.content_area.pack(fill="both", expand=True, padx=5, pady=5)

        # 3. RIGHT MONITOR
        self.monitor_panel = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.monitor_panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(self.monitor_panel, text="DEVICE MONITOR", font=("Roboto", 18, "bold"), text_color="#F1C40F").pack(pady=25)

        self.device_list_box = ctk.CTkTextbox(self.monitor_panel, height=320, fg_color="#000000", text_color="#F1C40F", font=("Consolas", 13), border_width=1, border_color=COLORS["border"])
        self.device_list_box.pack(padx=15, fill="x")

        self.info_panel = ctk.CTkFrame(self.monitor_panel, fg_color=COLORS["card_bg"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.info_panel.pack(pady=25, padx=15, fill="both", expand=True)
        ctk.CTkLabel(self.info_panel, text="Device Information", font=("Roboto", 15, "bold")).pack(pady=10)
        self.info_text = ctk.CTkLabel(self.info_panel, text="Waiting for device...", font=("Roboto", 12), text_color=COLORS["text_dim"], justify="left")
        self.info_text.pack(pady=15, padx=15)

        # 4. LOG CONSOLE
        self.log_frame = ctk.CTkFrame(self.content_area, height=200, fg_color="#080808", corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.log_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.log_console = ctk.CTkTextbox(self.log_frame, fg_color="transparent", font=("Consolas", 12), text_color="#00FF00")
        self.log_console.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_console.tag_config("info", foreground="#00FF00")
        self.log_console.tag_config("error", foreground="#FF4444")
        self.log_console.tag_config("warning", foreground="#FFBB00")
        self.log_console.tag_config("success", foreground="#00AAFF")

        self.progress_bar = ctk.CTkProgressBar(self.log_frame, height=8, corner_radius=4, progress_color=COLORS["accent_blue"])
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        self.show_view("Samsung")

    def log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert("end", f"[{timestamp}] {msg}\n", level)
        self.log_console.see("end")

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
        # Reset nav buttons
        for btn_name, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=COLORS["text_dim"])
        self.nav_buttons[name].configure(fg_color=self.nav_buttons[name].cget("hover_color"), text_color="white")

        if self.current_view_frame: self.current_view_frame.destroy()
        self.current_view_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.current_view_frame.pack(fill="both", expand=True, padx=30, pady=30) # زيادة المسافة لتبدو احترافية

        if name == "Samsung": self.render_samsung(self.current_view_frame)
        elif name == "MTK & Scatter": self.render_mtk(self.current_view_frame)
        elif name == "Penumbra (Xiaomi)": self.render_penumbra(self.current_view_frame)
        elif name == "Unisoc Pro": self.render_unisoc(self.current_view_frame)
        elif name == "ADB / Fastboot": self.render_adb(self.current_view_frame)
        elif name == "Settings": self.render_settings(self.current_view_frame)

    def create_card(self, parent, title, color):
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color=COLORS["sidebar_bg"], border_width=1, border_color=COLORS["border"])
        ctk.CTkLabel(card, text=title, font=("Roboto", 18, "bold"), text_color=color).pack(pady=15)
        return card

    def render_samsung(self, parent):
        parent.grid_columnconfigure((0, 1), weight=1)
        
        f_left = self.create_card(parent, "PENUMBRA FLASH ENGINE", COLORS["accent_blue"])
        f_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for p in ["BL", "AP", "CP", "CSC"]:
            row = ctk.CTkFrame(f_left, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=p, width=45, font=("Roboto", 13, "bold")).pack(side="left")
            entry = ctk.CTkEntry(row, placeholder_text=f"Select {p} file...", height=40, corner_radius=8, border_color=COLORS["border"])
            entry.pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkButton(row, text="📁", width=45, height=40, corner_radius=8, fg_color=COLORS["accent_blue"], command=lambda e=entry: self.browse_file(e)).pack(side="right")

        ctk.CTkButton(f_left, text="START FLASHING", height=55, corner_radius=10, fg_color=COLORS["accent_blue"], font=("Roboto", 16, "bold"), command=lambda: self.bridge.run_samsung_command("flash")).pack(pady=25, padx=20, fill="x")

        f_right = self.create_card(parent, "PENUMBRA SAMSUNG TOOLS", "#F1C40F")
        f_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        btns = [("Open MTP Browser", "mtp_browser"), ("Enable ADB (*#0*#)", "adb_enable"), ("Remove FRP (ADB)", "frp_adb"), ("Factory Reset", "reset")]
        for txt, cmd in btns:
            ctk.CTkButton(f_right, text=txt, height=50, corner_radius=10, fg_color="#2C3E50", hover_color=COLORS["accent_blue"], font=("Roboto", 14), command=lambda c=cmd: self.bridge.run_samsung_command(c)).pack(pady=8, padx=25, fill="x")

    def render_mtk(self, parent):
        card = self.create_card(parent, "PENUMBRA MTK ENGINE", COLORS["accent_orange"])
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        btns = [("Auth Bypass (BROM)", "bypass"), ("Erase FRP (Samsung/MTK)", "erase_frp"), ("Unlock Bootloader", "unlock_bl"), ("Format Userdata", "format")]
        for txt, cmd in btns:
            ctk.CTkButton(card, text=txt, height=55, corner_radius=12, fg_color=COLORS["accent_orange"], hover_color="#D35400", font=("Roboto", 16, "bold"), command=lambda c=cmd: self.bridge.run_mtk_command(c)).pack(pady=12, padx=100, fill="x")

    def render_penumbra(self, parent):
        card = self.create_card(parent, "PENUMBRA XIAOMI ENGINE", COLORS["accent_red"])
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        btns = [("Mi Cloud Bypass (Anti-Relock)", "bypass"), ("Sideload FRP Remove", "sideload_frp"), ("Enable Diag Mode", "diag")]
        for txt, cmd in btns:
            ctk.CTkButton(card, text=txt, height=55, corner_radius=12, fg_color=COLORS["accent_red"], hover_color="#C0392B", font=("Roboto", 16, "bold"), command=lambda c=cmd: self.bridge.run_xiaomi_command(c)).pack(pady=12, padx=100, fill="x")

    def render_unisoc(self, parent):
        card = self.create_card(parent, "UNISOC PRO SERVICE", COLORS["accent_purple"])
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        btns = [("Read System Info", "info"), ("Erase FRP (Fastboot)", "erase_frp"), ("Factory Reset (Diag)", "reset")]
        for txt, cmd in btns:
            ctk.CTkButton(card, text=txt, height=55, corner_radius=12, fg_color=COLORS["accent_purple"], hover_color="#8E44AD", font=("Roboto", 16, "bold"), command=lambda c=cmd: self.bridge.run_unisoc_command(c)).pack(pady=12, padx=100, fill="x")

    def render_adb(self, parent):
        card = self.create_card(parent, "ADB & FASTBOOT UTILS", "#2C3E50")
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        btns = [("Reboot to Recovery", "adb_recovery"), ("Reboot to Bootloader", "adb_bl"), ("Get Fastboot Vars", "fb_vars"), ("Exit Fastboot", "fb_reboot")]
        for txt, cmd in btns:
            ctk.CTkButton(card, text=txt, height=55, corner_radius=12, fg_color="#34495E", hover_color="#2C3E50", font=("Roboto", 16, "bold"), command=lambda c=cmd: self.bridge.run_adb_command(c)).pack(pady=12, padx=100, fill="x")

    def render_settings(self, parent):
        card = self.create_card(parent, "TOOL CONFIGURATION", "#7F8C8D")
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        ctk.CTkButton(card, text="Check for Updates", height=50, corner_radius=10, fg_color="#2980B9", command=self.check_for_updates).pack(pady=15, padx=100, fill="x")
        ctk.CTkButton(card, text="Copy HWID", height=50, corner_radius=10, fg_color="#16A085", command=lambda: self.log("HWID Copied: " + self.hwid, "success")).pack(pady=15, padx=100, fill="x")
        ctk.CTkButton(card, text="Install Drivers Pack", height=50, corner_radius=10, fg_color=COLORS["accent_green"], command=self.install_drivers).pack(pady=15, padx=100, fill="x")
        
        ctk.CTkLabel(card, text=f"HWID: {self.hwid}", font=("Consolas", 12), text_color=COLORS["text_dim"]).pack(side="bottom", pady=20)

    def browse_file(self, entry):
        from tkinter import filedialog
        path = filedialog.askopenfilename()
        if path: entry.delete(0, "end"); entry.insert(0, path)

    def install_drivers(self):
        self.log("Starting Drivers Installation...", "warning")
        drivers_path = resource_path("drivers")
        if not os.path.exists(drivers_path): self.log("Drivers folder not found!", "error"); return
        
        drivers = ["SAMSUNG_USB_Driver.exe", "MTK_VCOM_Driver.exe", "SPD_Driver.exe", "Libusb_Filter_Installer.exe"]
        for d in drivers:
            p = os.path.join(drivers_path, d)
            if os.path.exists(p): self.log(f"Installing {d}...", "info"); subprocess.Popen(p, shell=True)
            else: self.log(f"Warning: {d} missing.", "warning")

    def show_activation_screen(self, status):
        if self.activation_window and self.activation_window.winfo_exists():
            self.activation_window.focus(); return

        self.withdraw()
        self.activation_window = ctk.CTkToplevel(self)
        self.activation_window.title("TSP TOOL PRO - Activation")
        self.activation_window.geometry("550x450")
        self.activation_window.configure(fg_color=COLORS["bg_dark"])
        self.activation_window.protocol("WM_DELETE_WINDOW", sys.exit)
        
        win = self.activation_window
        ctk.CTkLabel(win, text="TSP TOOL PRO", font=("Impact", 38), text_color=COLORS["accent_red"]).pack(pady=30)
        ctk.CTkLabel(win, text="License Activation Required", font=("Roboto", 18, "bold")).pack(pady=10)
        
        hw_card = ctk.CTkFrame(win, corner_radius=12, fg_color=COLORS["sidebar_bg"], border_width=1, border_color=COLORS["border"])
        hw_card.pack(pady=20, padx=40, fill="x")
        ctk.CTkLabel(hw_card, text=f"HWID: {self.hwid}", font=("Consolas", 12), text_color=COLORS["accent_orange"]).pack(pady=10)
        
        key_entry = ctk.CTkEntry(win, placeholder_text="Paste your activation key here...", width=380, height=45, corner_radius=10, border_color=COLORS["border"])
        key_entry.pack(pady=20)
        
        def activate():
            k = key_entry.get()
            s, m = self.license_manager.activate_key(k)
            if s: tk.messagebox.showinfo("Success", m); self.activation_window.destroy(); restart_application()
            else: tk.messagebox.showerror("Error", m)

        ctk.CTkButton(win, text="ACTIVATE TOOL", fg_color=COLORS["accent_red"], hover_color="#C0392B", font=("Roboto", 16, "bold"), command=activate, height=50, width=380, corner_radius=10).pack(pady=10)
        ctk.CTkLabel(win, text=f"Status: {status}", text_color=COLORS["text_dim"]).pack(pady=15)


if __name__ == "__main__":
    app = TSPToolPro()
    app.mainloop()
