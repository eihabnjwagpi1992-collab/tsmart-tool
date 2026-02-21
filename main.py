
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

import customtkinter
import security_utils
from device_data import BRAND_DATA, CHIP_DATA, TOP_NAV_BRANDS # استيراد البيانات الجديدة

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

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class TSPToolPro(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.title(security_utils.deobfuscate_string("VFNCIFRPT0wgUFJPIC0gUGVudW1icmEgUG93ZXJlZCBTdWl0ZSB2My4x"))
            if security_utils.check_debugger():
                print("Debugger detected! Exiting.")
                self.destroy()
                return
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
        self.login_window = customtkinter.CTkToplevel(self)
        self.login_window.title("Login")
        self.login_window.geometry("400x500")
        self.login_window.protocol("WM_DELETE_WINDOW", sys.exit)
        self.login_window.attributes("-topmost", True)

        customtkinter.CTkLabel(self.login_window, text=security_utils.deobfuscate_string("VFNCIFRPT0wgUFJP"), font=("Impact", 34), text_color=COLORS["accent_red"]).pack(pady=30)
        customtkinter.CTkLabel(self.login_window, text=security_utils.deobfuscate_string("RW1haWwgJiBQYXNzd29yZCBMb2dpbg=="), font=("Roboto", 16)).pack(pady=10)

        self.email_entry = customtkinter.CTkEntry(self.login_window, placeholder_text=security_utils.deobfuscate_string("RW1haWw="), width=300, height=40)
        self.email_entry.pack(pady=10)

        self.password_entry = customtkinter.CTkEntry(self.login_window, placeholder_text=security_utils.deobfuscate_string("UGFzc3dvcmQ="), show="*", width=300, height=40)
        self.password_entry.pack(pady=10)

        customtkinter.CTkButton(self.login_window, text=security_utils.deobfuscate_string("TG9naW4="), command=self.attempt_login, width=300, height=40).pack(pady=20)

    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        success, message = self.auth_manager.login(email, password)

        if success:
            self.login_window.destroy()
            self.deiconify() # إظهار النافذة الرئيسية
            self.setup_ui()
            self.log(security_utils.deobfuscate_string("U3lzdGVtIFJlYWR5IHwgVXNlciBMb2dnZWQgSW4="), "success")
            self.monitor = DeviceMonitor(ADB_PATH, FASTBOOT_PATH, self.update_device_list)
            self.monitor.start()
            threading.Thread(target=self.check_for_updates_silent, daemon=True).start()
        else:
            tk.messagebox.showerror(security_utils.deobfuscate_string("TG9naW4gRmFpbGVk"), message)

    def check_for_updates_silent(self):
        try:
            update_data = self.update_manager.check_for_updates()
            if update_data: self.after(0, lambda: self.show_update_dialog(update_data))
        except: pass

    def check_for_updates(self):
        self.log(security_utils.deobfuscate_string("Q2hlY2tpbmcgZm9yIHVwZGF0ZXMuLi4="), "info")
        threading.Thread(target=self._check_updates_manual_thread, daemon=True).start()

    def _check_updates_manual_thread(self):
        update_data = self.update_manager.check_for_updates()
        if update_data: self.after(0, lambda: self.show_update_dialog(update_data))
        else: self.after(0, lambda: self.log(security_utils.deobfuscate_string("TGF0ZXN0IHZlcnNpb24gaW5zdGFsbGVkLg=="), "success"))

    def show_update_dialog(self, data):
        if hasattr(self, 'update_window') and self.update_window and self.update_window.winfo_exists():
            self.update_window.lift()
            self.update_window.focus_force()
            return

        self.update_window = customtkinter.CTkToplevel(self)
        self.update_window.attributes("-topmost", True)
        self.update_window.title(security_utils.deobfuscate_string("VXBkYXRlIEF2YWlsYWJsZQ=="))
        self.update_window.geometry("480x380")
        self.update_window.configure(fg_color=COLORS["card_bg"])
        
        customtkinter.CTkLabel(self.update_window, text=security_utils.deobfuscate_string("4oCcIE5ldyBVcGRhdGUgQXZhaWxhYmxlISDigJwg"), font=("Roboto", 20, "bold"), text_color=COLORS["accent_green"]).pack(pady=20)
        customtkinter.CTkLabel(self.update_window, text=f"Version: {data['version']}", font=("Roboto", 14)).pack()
        
        changelog_frame = customtkinter.CTkFrame(self.update_window, corner_radius=12, fg_color=COLORS["bg_dark"], border_width=1, border_color=COLORS["border"])
        changelog_frame.pack(pady=20, padx=25, fill="both", expand=True)
        
        changelog_text = tk.Text(changelog_frame, height=6, bg=COLORS["bg_dark"], fg=COLORS["text_main"], font=("Roboto", 11), borderwidth=0, padx=10, pady=10)
        changelog_text.insert("1.0", data.get("changelog", security_utils.deobfuscate_string("SW1wcm92ZW1lbnRzIGFuZCBmaXhlcy4=")))
        changelog_text.config(state="disabled")
        changelog_text.pack(fill="both", expand=True)
        
        def start_update():
            self.update_window.destroy()
            self.log(security_utils.deobfuscate_string("8J+YgyBEb3dubG9hZGluZyB1cGRhdGUuLi4="), "warning")
            threading.Thread(target=lambda: self.update_manager.download_and_install(data['download_url']), daemon=True).start()

        customtkinter.CTkButton(self.update_window, text=security_utils.deobfuscate_string("VXBkYXRlIE5vdw=="), fg_color=COLORS["accent_green"], hover_color="#27AE60", font=("Roboto", 14, "bold"), command=start_update, height=45).pack(pady=10, padx=25, fill="x")
        customtkinter.CTkButton(self.update_window, text=security_utils.deobfuscate_string("TWF5YmUgTGF0ZXI="), fg_color="transparent", border_width=1, border_color=COLORS["border"], command=self.update_window.destroy, height=35).pack(pady=5)

    def setup_ui(self):
        # New Odin Style Layout
        self.grid_columnconfigure(0, weight=0) # Sidebar column
        self.grid_columnconfigure(1, weight=1) # Main content column
        self.grid_columnconfigure(2, weight=0) # Monitor panel column
        self.grid_rowconfigure(0, weight=0) # Top bar row
        self.grid_rowconfigure(1, weight=1) # Main body row
        self.grid_rowconfigure(2, weight=0) # Log console row

        # 1. TOP BAR (Brands as Tabs)
        self.top_bar = customtkinter.CTkFrame(self, height=60, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.top_nav_buttons = {}
        for item in TOP_NAV_BRANDS:
            btn = customtkinter.CTkButton(self.top_bar, text=item, height=40, corner_radius=8, fg_color="transparent", hover_color=COLORS["accent_orange"], font=("Roboto", 14, "bold"),
                                command=lambda i=item: self.show_view(i))
            btn.pack(side="left", padx=10, pady=10)
            self.top_nav_buttons[item] = btn
        
        # 2. MAIN BODY (contains sidebar, content area, and monitor panel)
        self.main_body = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_body.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.main_body.grid_columnconfigure(1, weight=1)
        self.main_body.grid_rowconfigure(0, weight=1)

        # 3. SIDEBAR (Left) - Not used in this new layout, but keeping for potential future use or other elements
        # self.sidebar = customtkinter.CTkFrame(self.main_body, width=220, corner_radius=10, fg_color=COLORS["card_bg"])
        # self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        # customtkinter.CTkLabel(self.sidebar, text=security_utils.deobfuscate_string("VFNCIFRPT0wgUFJP"), font=("Impact", 28), text_color=COLORS["accent_orange"]).pack(pady=20)

        # 4. MAIN CONTENT (Center) - This will hold the dynamic views for each brand
        self.content_area = customtkinter.CTkFrame(self.main_body, corner_radius=10, fg_color=COLORS["card_bg"])
        self.content_area.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(0, 10)) # Adjusted to take more space
        self.main_body.grid_columnconfigure(0, weight=1) # Give content area more weight

        # 5. RIGHT MONITOR
        self.monitor_panel = customtkinter.CTkFrame(self.main_body, width=280, corner_radius=10, fg_color=COLORS["card_bg"])
        self.monitor_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        self.device_list_box = customtkinter.CTkTextbox(self.monitor_panel, height=320, fg_color="#000000", text_color="#F1C40F", font=("Consolas", 13), border_width=1, border_color=COLORS["border"])
        self.device_list_box.pack(padx=15, fill="x", pady=10)
        customtkinter.CTkLabel(self.monitor_panel, text="Device Monitor", font=("Roboto", 16, "bold")).pack(pady=(0,5))

        # 6. LOG CONSOLE
        self.log_console = customtkinter.CTkTextbox(self, height=150, fg_color="#000000", text_color="#00FF00", font=("Consolas", 12), border_width=1, border_color=COLORS["border"])
        self.log_console.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(10, 0))

        self.show_view(TOP_NAV_BRANDS[0]) # Show the first brand by default

    def show_view(self, brand_name):
        if self.current_view_frame:
            self.current_view_frame.destroy()

        self.current_view_frame = customtkinter.CTkFrame(self.content_area, fg_color="transparent")
        self.current_view_frame.pack(fill="both", expand=True)

        brand_data = BRAND_DATA.get(brand_name)
        if not brand_data:
            customtkinter.CTkLabel(self.current_view_frame, text=f"No data found for {brand_name}", font=("Roboto", 24, "bold")).pack(pady=50)
            return

        # Top section for Model/Chip selection
        top_frame = customtkinter.CTkFrame(self.current_view_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        # Model Selection
        customtkinter.CTkLabel(top_frame, text="Select Model:", font=("Roboto", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        model_options = list(brand_data["models"].keys())
        self.model_dropdown = customtkinter.CTkOptionMenu(top_frame, values=model_options, command=self.on_model_selected)
        self.model_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.model_dropdown.set(model_options[0]) # Set default selected model

        # Chip Info Display
        customtkinter.CTkLabel(top_frame, text="Chip:", font=("Roboto", 14, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.chip_label = customtkinter.CTkLabel(top_frame, text="N/A", font=("Roboto", 14))
        self.chip_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Operations Section
        operations_frame = customtkinter.CTkFrame(self.current_view_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        operations_frame.pack(fill="both", expand=True, padx=10, pady=10)
        customtkinter.CTkLabel(operations_frame, text="Operations:", font=("Roboto", 16, "bold")).pack(pady=10)

        self.operations_buttons_frame = customtkinter.CTkFrame(operations_frame, fg_color="transparent")
        self.operations_buttons_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.operations_buttons_frame.grid_columnconfigure(0, weight=1)
        self.operations_buttons_frame.grid_columnconfigure(1, weight=1)
        self.operations_buttons_frame.grid_columnconfigure(2, weight=1)

        # Instructions Section
        self.instructions_frame = customtkinter.CTkFrame(operations_frame, fg_color=COLORS["bg_dark"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.instructions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.instructions_label = customtkinter.CTkLabel(self.instructions_frame, text="Select an operation to see instructions", font=("Roboto", 12, "italic"), text_color=COLORS["text_dim"], wraplength=600)
        self.instructions_label.pack(pady=10, padx=10)

        self.current_brand_name = brand_name
        self.on_model_selected(model_options[0]) # Trigger initial display of operations

    def on_model_selected(self, selected_model):
        brand_data = BRAND_DATA.get(self.current_brand_name)
        model_info = brand_data["models"].get(selected_model)

        if model_info:
            self.chip_label.configure(text=model_info["chip"])
            operations_list = model_info["operations"]
            self.update_operations_buttons(operations_list, brand_data["operations"])
        else:
            self.chip_label.configure(text="N/A")
            self.update_operations_buttons([], {})

    def update_operations_buttons(self, operations_list, brand_operations_map):
        # Clear existing buttons
        for widget in self.operations_buttons_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        for op_name in operations_list:
            command_str = brand_operations_map.get(op_name)
            if command_str:
                btn = customtkinter.CTkButton(self.operations_buttons_frame, text=op_name, height=40, corner_radius=8, font=("Roboto", 12, "bold"),
                                        command=lambda cmd=command_str, name=op_name: self.on_operation_click(cmd, name))
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                col += 1
                if col > 2: # 3 buttons per row
                    col = 0
                    row += 1

    def on_operation_click(self, command_str, op_name):
        # Update instructions based on operation
        instructions = {
            "FRP Bypass": "1. Power off device\n2. Hold Vol Up + Vol Down\n3. Connect USB Cable",
            "Factory Reset": "1. Power off device\n2. Hold Vol Down + Power (or Vol Up + Vol Down)\n3. Connect USB Cable",
            "BROM | ERASE FRP": "1. Power off device\n2. Connect USB Cable (Auto-detection active)",
            "BROM | AUTH BYPASS": "1. Power off device\n2. Connect USB Cable for BROM injection",
            "Mi Cloud Bypass": "1. Enter Sideload Mode (Vol Up + Power)\n2. Connect USB Cable",
            "MTP Browser": "1. Power on device\n2. Connect to Wi-Fi\n3. Connect USB Cable",
            "ADB Enable": "1. Go to Emergency Call\n2. Dial *#0*#\n3. Connect USB Cable"
        }
        
        msg = instructions.get(op_name, "Follow the on-screen prompts in the log console.")
        self.instructions_label.configure(text=f"INSTRUCTIONS for {op_name}:\n{msg}", text_color=COLORS["accent_orange"], font=("Roboto", 12, "bold"))
        
        # Execute command
        try:
            eval(f"self.bridge.{command_str}")
        except Exception as e:
            self.log(f"Error executing {op_name}: {str(e)}", "error")

    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_console.see(tk.END)

    def update_device_list(self, devices):
        self.device_list_box.delete("1.0", tk.END)
        if devices:
            for device in devices:
                self.device_list_box.insert(tk.END, f"{device}\n")
        else:
            self.device_list_box.insert(tk.END, security_utils.deobfuscate_string("Tm8gZGV2aWNlcyBmb3VuZC4="))

if __name__ == "__main__":
    app = TSPToolPro()
    app.mainloop()
