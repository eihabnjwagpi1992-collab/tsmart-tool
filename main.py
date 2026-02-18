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
MTK_EXE_PATH = resource_path(os.path.join("bin", "mtk.exe")) # Standalone MTK Binary
SAMSUNG_EXE_PATH = resource_path(os.path.join("bin", "samsung_tool.exe")) # Standalone Samsung Binary

# --- BINARY PATHS (إضافة المسارات الجديدة) ---
UNISOC_EXE_PATH = resource_path(os.path.join("bin", "unisoc_tool.exe"))
XIAOMI_EXE_PATH = resource_path(os.path.join("bin", "xiaomi_tool.exe"))

# --- GLOBAL SETTINGS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TsmartToolPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Pro Tool - Advanced GSM Suite v2.1")
        self.geometry("1300x850")
        
        self.current_user = "Admin"
        self.is_activated = True 
        
        self.setup_ui()
        self.start_device_monitor()

    def setup_ui(self):
        # Main Grid Configuration
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Content
        self.grid_columnconfigure(2, weight=0) # Right Monitor
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDE NAVIGATION
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
        
        self.log_console = ctk.CTkTextbox(self.log_frame, fg_color="transparent", font=("Consolas", 12))
        self.log_console.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure tags for colored logging
        self.log_console.tag_config("info", foreground="#0F0")    # Green
        self.log_console.tag_config("error", foreground="#F00")   # Red
        self.log_console.tag_config("warning", foreground="#F1C40F") # Yellow
        self.log_console.tag_config("success", foreground="#3498DB") # Blue
        
        self.progress_bar = ctk.CTkProgressBar(self.log_frame, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)

        self.show_view("Samsung")

    # --- VIEW RENDERING (تعديل دالة التنقل لتشمل التبويبات الجديدة) ---
    def show_view(self, name):
        for widget in self.content_area.winfo_children():
            if widget != self.log_frame:
                widget.destroy()
        
        if name == "Samsung": self.render_samsung()
        elif name == "MTK & Scatter": self.render_mtk()
        elif name == "Penumbra (Xiaomi)": self.render_penumbra()
        elif name == "Unisoc Pro": self.render_unisoc() # <--- إضافة Unisoc
        elif name == "ADB / Fastboot": self.render_adb()
        elif name == "Settings": self.render_settings()

    # 1. SAMSUNG TAB
    def render_samsung(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        flash_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        flash_frame.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(flash_frame, text="FLASHING", font=("Roboto", 16, "bold"), text_color="#3498DB").pack(pady=10)
        
        for part in ["BL", "AP", "CP", "CSC"]:
            f = ctk.CTkFrame(flash_frame, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=part, width=40, anchor="w").pack(side="left")
            ctk.CTkEntry(f, placeholder_text=f"Select {part} file...", height=35).pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(f, text="📁", width=40, height=35, fg_color="#333").pack(side="right")
            
        ctk.CTkButton(flash_frame, text="FLASH FIRMWARE", height=50, fg_color="#0057B7", font=("Roboto", 16, "bold"), 
                       command=lambda: self.run_binary_task(SAMSUNG_EXE_PATH, ["--flash"])).pack(pady=30, padx=20, fill="x")

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
            btn = ctk.CTkButton(btn_grid, text=text, fg_color=color, height=45, 
                                 command=lambda t=text: self.run_binary_task(SAMSUNG_EXE_PATH, [f"--{t.lower().replace(' ', '_')}"]))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
        btn_grid.grid_columnconfigure((0,1), weight=1)

    # 2. MTK & SCATTER TAB
    def render_mtk(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        top_frame = ctk.CTkFrame(container, height=100, corner_radius=10)
        top_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top_frame, text="Scatter File:", width=100).pack(side="left", padx=10)
        ctk.CTkEntry(top_frame, placeholder_text="Select MTK Scatter File...", height=35).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(top_frame, text="Load Scatter", width=120, fg_color="#E67E22").pack(side="right", padx=10)

        list_frame = ctk.CTkFrame(container, corner_radius=10, border_width=1)
        list_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(list_frame, text="Partition Manager", font=("Roboto", 14, "bold")).pack(pady=5)
        
        self.part_list = ctk.CTkTextbox(list_frame, fg_color="#111", text_color="#EEE")
        self.part_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.part_list.insert("1.0", " [X] preloader\n [X] recovery\n [X] boot\n [X] system\n [X] vendor\n [ ] userdata")

        bot_frame = ctk.CTkFrame(container, height=120, fg_color="transparent")
        bot_frame.pack(fill="x", pady=(10, 0))
        ops = [("Erase FRP", "#E67E22"), ("Unlock BL", "#C0392B"), ("Format FS", "#2C3E50"), ("Safe Format", "#27AE60")]
        for i, (text, color) in enumerate(ops):
            ctk.CTkButton(bot_frame, text=text, fg_color=color, height=45, 
                           command=lambda t=text: self.run_binary_task(MTK_EXE_PATH, [f"--{t.lower().replace(' ', '_')}"])).grid(row=0, column=i, padx=5, sticky="nsew")
        bot_frame.grid_columnconfigure((0,1,2,3), weight=1)

    # 3. UNISOC PRO TAB (تبويب اليونيسوك الجديد)
    def render_unisoc(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # قسم التفليش (Flash PAC)
        flash_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        flash_frame.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(flash_frame, text="UNISOC FLASHER (PAC)", font=("Roboto", 16, "bold"), text_color="#9B59B6").pack(pady=10)
        
        f = ctk.CTkFrame(flash_frame, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=20)
        ctk.CTkEntry(f, placeholder_text="Select .PAC Firmware...", height=35).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(f, text="📁", width=40, height=35, fg_color="#333").pack(side="right")
            
        ctk.CTkButton(flash_frame, text="START FLASHING", height=50, fg_color="#9B59B6", font=("Roboto", 16, "bold"), 
                       command=lambda: self.run_binary_task(UNISOC_EXE_PATH, ["--flash_pac"])).pack(pady=30, padx=20, fill="x")

        # قسم الخدمات (Security)
        service_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        service_frame.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(service_frame, text="SPD/UNISOC SERVICES", font=("Roboto", 16, "bold"), text_color="#F1C40F").pack(pady=10)
        
        btn_grid = ctk.CTkFrame(service_frame, fg_color="transparent")
        btn_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        services = [
            ("Read Info (Diag)", "#2C3E50"), ("Factory Reset", "#E74C3C"),
            ("Erase FRP", "#E67E22"), ("Remove Privacy ID", "#3498DB"),
            ("Unlock Bootloader", "#C0392B"), ("Relock Bootloader", "#27AE60"),
            ("IMEI Repair (Diag)", "#8E44AD"), ("Write NVRAM", "#2980B9")
        ]
        
        for i, (text, color) in enumerate(services):
            btn = ctk.CTkButton(btn_grid, text=text, fg_color=color, height=45, 
                                 command=lambda t=text: self.run_binary_task(UNISOC_EXE_PATH, [f"--{t.lower().replace(' ', '_')}"]))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
        btn_grid.grid_columnconfigure((0,1), weight=1)

    # 4. PENUMBRA XIAOMI TAB (تطوير تبويب شاومي ليصبح احترافياً)
    def render_penumbra(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # قسم الـ EDL & BROM
        left_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(left_frame, text="XIAOMI EDL / BROM", font=("Roboto", 16, "bold"), text_color="#E74C3C").pack(pady=10)
        
        ops_left = [
            ("Bypass Mi Cloud", "#C0392B"), ("Erase FRP (EDL)", "#E67E22"),
            ("Anti-Relock Fix", "#D35400"), ("Factory Reset (BROM)", "#7F8C8D"),
            ("Auth Flash", "#2980B9"), ("Partition Manager", "#34495E")
        ]
        
        for text, color in ops_left:
            ctk.CTkButton(left_frame, text=text, fg_color=color, height=45, 
                           command=lambda t=text: self.run_binary_task(XIAOMI_EXE_PATH, [f"--{t.lower().replace(' ', '_')}"])).pack(pady=5, padx=20, fill="x")

        # قسم الـ Fastboot & Sideload
        right_frame = ctk.CTkFrame(container, width=400, corner_radius=10, border_width=1, border_color="#333")
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(right_frame, text="FASTBOOT / SIDELOAD", font=("Roboto", 16, "bold"), text_color="#3498DB").pack(pady=10)
        
        ops_right = [
            ("Read Info (FB)", "#2C3E50"), ("Exit Fastboot", "#2C3E50"),
            ("Unlock BL (Instant)", "#E74C3C"), ("Sideload FRP", "#27AE60"),
            ("Cloud Bypass (Assistant)", "#2980B9"), ("Fix System Destroyed", "#C0392B")
        ]
        
        for text, color in ops_right:
            ctk.CTkButton(right_frame, text=text, fg_color=color, height=45, 
                           command=lambda t=text: self.run_binary_task(XIAOMI_EXE_PATH, [f"--{t.lower().replace(' ', '_')}"])).pack(pady=5, padx=20, fill="x")

    # تبويب الإعدادات (Settings) - لإكمال الواجهة
    def render_settings(self):
        ctk.CTkLabel(self.content_area, text="TOOL SETTINGS", font=("Roboto", 24, "bold")).pack(pady=20)
        frame = ctk.CTkFrame(self.content_area, fg_color="#1E1E1E", width=600, height=400)
        frame.pack(pady=20, padx=20)
        
        ctk.CTkSwitch(frame, text="Enable Auto-Update").pack(pady=10, padx=20)
        ctk.CTkSwitch(frame, text="Save Logs Automatically").pack(pady=10, padx=20)
        ctk.CTkButton(frame, text="Install USB Drivers", fg_color="#333").pack(pady=20, padx=20)
        ctk.CTkLabel(frame, text="Developed by: Tsmart GSM Pro Team", text_color="#555").pack(pady=20)

    # --- CORE ENGINE FUNCTIONS ---
    def log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {msg}\n"
        self.log_console.insert("end", formatted_msg, level)
        self.log_console.see("end")

    def run_binary_task(self, binary_path, args):
        self.log(f"Executing: {os.path.basename(binary_path)} {' '.join(args)}", "warning")
        self.progress_bar.set(0)
        
        def run():
            try:
                # Use subprocess.Popen for real-time output if needed
                process = subprocess.Popen([binary_path] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                
                for line in process.stdout:
                    self.log(line.strip())
                    # Mock progress update based on log output
                    if "%" in line:
                        try:
                            p = int(line.split("%")[0].split()[-1]) / 100
                            self.progress_bar.set(p)
                        except: pass
                
                process.wait()
                if process.returncode == 0:
                    self.log("OPERATION SUCCESSFUL!", "success")
                    self.progress_bar.set(1.0)
                else:
                    self.log(f"OPERATION FAILED! (Code: {process.returncode})", "error")
            except Exception as e:
                self.log(f"CRITICAL ERROR: {str(e)}", "error")
                
        threading.Thread(target=run, daemon=True).start()

    def start_device_monitor(self):
        def monitor():
            while True:
                try:
                    # In real tool, this would call ADB/Fastboot/COM list
                    self.device_list.delete("1.0", "end")
                    self.device_list.insert("end", ">>> SCANNING PORTS...\n")
                    # Example of calling adb.exe
                    res = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    self.device_list.insert("end", res.stdout)
                except: pass
                time.sleep(3)
        threading.Thread(target=monitor, daemon=True).start()

    def render_adb(self):
        ctk.CTkLabel(self.content_area, text="Global ADB & Fastboot Tools", font=("Roboto", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self.content_area, text="Reboot to Download", command=lambda: self.run_binary_task(ADB_PATH, ["reboot", "download"])).pack(pady=10)
        ctk.CTkButton(self.content_area, text="Reboot to Recovery", command=lambda: self.run_binary_task(ADB_PATH, ["reboot", "recovery"])).pack(pady=10)
        ctk.CTkButton(self.content_area, text="Open Device Manager", fg_color="#333", command=lambda: os.system("devmgmt.msc")).pack(pady=10)

if __name__ == "__main__":
    app = TsmartToolPro()
    app.mainloop()
