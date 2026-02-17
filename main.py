import tkinter as tk
import customtkinter as ctk
import requests
import subprocess
import threading
import os
import json
import sys
import time
from datetime import datetime

# --- RESOURCE PATH FUNCTION ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- BINARY PATHS ---
ADB_PATH = resource_path(os.path.join("bin", "adb.exe"))
FASTBOOT_PATH = resource_path(os.path.join("bin", "fastboot.exe"))

# --- GLOBAL SETTINGS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TsmartToolPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Pro Tool - Advanced GSM Suite v2.0")
        self.geometry("1300x850")
        
        self.current_user = "Admin"
        self.is_activated = True # Default for development
        
        self.setup_ui()
        self.start_device_monitor()

    def setup_ui(self):
        # Main Grid Configuration
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Content
        self.grid_columnconfigure(2, weight=0) # Right Monitor
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDE NAVIGATION (Vertical Menu)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1E1E1E")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TSMART PRO", font=("Impact", 32), text_color="#3498DB").pack(pady=30)
        
        self.nav_buttons = {}
        nav_items = [
            ("Samsung", "#0057B7"),
            ("MTK & Scatter", "#E67E22"),
            ("Penumbra (Xiaomi)", "#E74C3C"),
            ("Unisoc Pro", "#9B59B6"),
            ("ADB / Fastboot", "#2C3E50"),
            ("Settings", "#7F8C8D")
        ]
        
        for item, color in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=item, height=50, corner_radius=0, 
                               fg_color="transparent", text_color="white", hover_color=color,
                               anchor="w", font=("Roboto", 15, "bold"),
                               command=lambda i=item: self.show_view(i))
            btn.pack(fill="x", pady=2)
            self.nav_buttons[item] = btn

        # 2. MAIN CONTENT AREA
        self.content_area = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 3. RIGHT DEVICE MONITOR PANEL
        self.monitor_panel = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#1E1E1E")
        self.monitor_panel.grid(row=0, column=2, sticky="nsew")
        
        ctk.CTkLabel(self.monitor_panel, text="DEVICE MONITOR", font=("Roboto", 18, "bold"), text_color="#F1C40F").pack(pady=20)
        
        self.device_list = ctk.CTkTextbox(self.monitor_panel, height=300, fg_color="#000", text_color="#F1C40F", font=("Consolas", 12))
        self.device_list.pack(padx=10, fill="x")
        
        self.info_panel = ctk.CTkFrame(self.monitor_panel, fg_color="#262626", corner_radius=10)
        self.info_panel.pack(pady=20, padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.info_panel, text="Device Info", font=("Roboto", 14, "bold")).pack(pady=5)
        self.info_text = ctk.CTkLabel(self.info_panel, text="No Device Connected", font=("Roboto", 11), text_color="#AAA")
        self.info_text.pack(pady=10)

        # 4. BOTTOM LOG CONSOLE (Global)
        self.log_frame = ctk.CTkFrame(self.content_area, height=180, fg_color="#111", corner_radius=10)
        self.log_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.log_console = ctk.CTkTextbox(self.log_frame, fg_color="transparent", text_color="#0F0", font=("Consolas", 12))
        self.log_console.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.log_frame, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)

        self.show_view("Samsung")

    # --- VIEW RENDERING ---
    def show_view(self, name):
        for widget in self.content_area.winfo_children():
            if widget != self.log_frame:
                widget.destroy()
        
        if name == "Samsung": self.render_samsung()
        elif name == "MTK & Scatter": self.render_mtk()
        elif name == "Penumbra (Xiaomi)": self.render_penumbra()
        elif name == "ADB / Fastboot": self.render_adb()

    # 1. SAMSUNG TAB
    def render_samsung(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Column 1: Flashing (LabelFrame style)
        flash_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        flash_frame.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(flash_frame, text="FLASHING", font=("Roboto", 16, "bold"), text_color="#3498DB").pack(pady=10)
        
        for part in ["BL", "AP", "CP", "CSC"]:
            f = ctk.CTkFrame(flash_frame, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=part, width=40, anchor="w").pack(side="left")
            ctk.CTkEntry(f, placeholder_text=f"Select {part} file...", height=35).pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(f, text="📁", width=40, height=35, fg_color="#333").pack(side="right")
            
        ctk.CTkButton(flash_frame, text="FLASH FIRMWARE", height=50, fg_color="#0057B7", font=("Roboto", 16, "bold"), command=self.mock_flash).pack(pady=30, padx=20, fill="x")

        # Column 2: Services
        service_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        service_frame.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(service_frame, text="SECURITY & SERVICES", font=("Roboto", 16, "bold"), text_color="#F1C40F").pack(pady=10)
        
        btn_grid = ctk.CTkFrame(service_frame, fg_color="transparent")
        btn_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        services = [
            ("FRP (MTP)", "#27AE60"), ("FRP (ADB)", "#27AE60"),
            ("FRP (BROM)", "#E67E22"), ("CSC Change", "#3498DB"),
            ("IMEI Repair", "#E74C3C"), ("Patch Cert", "#E74C3C"),
            ("Soft Brick Fix", "#2C3E50"), ("Exit Download", "#2C3E50")
        ]
        
        for i, (text, color) in enumerate(services):
            btn = ctk.CTkButton(btn_grid, text=text, fg_color=color, height=45, command=lambda t=text: self.log(f"Starting {t}...", "warning"))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
        btn_grid.grid_columnconfigure((0,1), weight=1)

    # 2. MTK & SCATTER TAB
    def render_mtk(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top: Scatter Selection
        top_frame = ctk.CTkFrame(container, height=100, corner_radius=10)
        top_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top_frame, text="Scatter File:", width=100).pack(side="left", padx=10)
        ctk.CTkEntry(top_frame, placeholder_text="Select MTK Scatter File...", height=35).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(top_frame, text="Load Scatter", width=120, fg_color="#E67E22").pack(side="right", padx=10)

        # Middle: Partition Manager
        list_frame = ctk.CTkFrame(container, corner_radius=10, border_width=1)
        list_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(list_frame, text="Partition Manager", font=("Roboto", 14, "bold")).pack(pady=5)
        
        self.part_list = ctk.CTkTextbox(list_frame, fg_color="#111", text_color="#EEE")
        self.part_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.part_list.insert("1.0", " [X] preloader\n [X] recovery\n [X] boot\n [X] system\n [X] vendor\n [ ] userdata")

        # Bottom: Operations
        bot_frame = ctk.CTkFrame(container, height=120, fg_color="transparent")
        bot_frame.pack(fill="x", pady=(10, 0))
        ops = [("Erase FRP", "#E67E22"), ("Unlock BL", "#C0392B"), ("Format FS", "#2C3E50"), ("Safe Format", "#27AE60")]
        for i, (text, color) in enumerate(ops):
            ctk.CTkButton(bot_frame, text=text, fg_color=color, height=45, command=lambda t=text: self.log(f"MTK Operation: {t}")).grid(row=0, column=i, padx=5, sticky="nsew")
        bot_frame.grid_columnconfigure((0,1,2,3), weight=1)

    # 3. PENUMBRA (XIAOMI)
    def render_penumbra(self):
        ctk.CTkLabel(self.content_area, text="PENUMBRA XIAOMI ENGINE", font=("Roboto", 24, "bold"), text_color="#E74C3C").pack(pady=20)
        grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid.pack(expand=True, fill="both", padx=50)
        
        ops = ["Bypass Mi Cloud", "Remove FRP (Xiaomi)", "Fix System Update", "Disable Find Device", "Auth Flash (EDL)"]
        for op in ops:
            ctk.CTkButton(grid, text=op, height=50, fg_color="#E74C3C", font=("Roboto", 15, "bold"), command=lambda o=op: self.log(f"Penumbra executing {o}...")).pack(pady=5, fill="x")

    # --- CORE ENGINE FUNCTIONS ---
    def log(self, msg, level="info"):
        color = "#0F0" # Green
        if level == "error": color = "#F00" # Red
        elif level == "warning": color = "#F1C40F" # Yellow
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert("end", f"[{timestamp}] {msg}\n")
        self.log_console.see("end")
        # Note: True colored text in Textbox requires tags, simplified for now

    def mock_flash(self):
        self.log("Initializing Flash Engine...", "warning")
        def run():
            for i in range(101):
                time.sleep(0.05)
                self.progress_bar.set(i/100)
                if i % 20 == 0: self.log(f"Writing block {i}%...")
            self.log("FLASH COMPLETED SUCCESSFULLY!", "success")
            tk.messagebox.showinfo("Success", "Firmware Flashed Successfully!")
        threading.Thread(target=run).start()

    def start_device_monitor(self):
        def monitor():
            while True:
                try:
                    # Mock monitoring - in real tool, this calls ADB/Fastboot/COM list
                    self.device_list.delete("1.0", "end")
                    self.device_list.insert("end", ">>> COM3: Samsung Mobile USB\n>>> ADB: SM-G973F Connected\n>>> FASTBOOT: Waiting...")
                except: pass
                time.sleep(3)
        threading.Thread(target=monitor, daemon=True).start()

    def render_adb(self):
        ctk.CTkLabel(self.content_area, text="Global ADB & Fastboot Tools", font=("Roboto", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self.content_area, text="Reboot to Download", command=lambda: self.log("Rebooting to Download Mode...")).pack(pady=10)
        ctk.CTkButton(self.content_area, text="Reboot to Recovery", command=lambda: self.log("Rebooting to Recovery...")).pack(pady=10)
        ctk.CTkButton(self.content_area, text="Open Device Manager", fg_color="#333", command=lambda: os.system("devmgmt.msc")).pack(pady=10)

if __name__ == "__main__":
    app = TsmartToolPro()
    app.mainloop()
