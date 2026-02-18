import tkinter as tk
import customtkinter as ctk
import os
import sys
from datetime import datetime
from device_engine import DeviceMonitor, get_device_info
from bridge_engine import BridgeEngine
from security import verify_license, get_hwid

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

        self.title("TSMART PRO TOOL - Advanced GSM Suite v2.5")
        self.geometry("1300x850")
        
        # License Verification
        is_valid, hwid = verify_license()
        if not is_valid:
            tk.messagebox.showerror("License Error", f"HWID Not Authorized: {hwid}")
            self.destroy()
            return

        self.bridge = BridgeEngine(self.log)
        self.setup_ui()
        
        # Start Device Monitor
        self.monitor = DeviceMonitor(ADB_PATH, FASTBOOT_PATH, self.update_device_list)
        self.monitor.start()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDE NAVIGATION
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1E1E1E")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TSMART PRO", font=("Impact", 32), text_color="#3498DB").pack(pady=30)
        
        nav_items = [
            ("Samsung", "#0057B7"),
            ("MTK & Scatter", "#E67E22"),
            ("Penumbra (Xiaomi)", "#E74C3C"),
            ("Unisoc Pro", "#9B59B6"),
            ("ADB / Fastboot", "#2C3E50"),
            ("Settings", "#7F8C8D")
        ]
        
        for item, color in nav_items:
            ctk.CTkButton(self.sidebar, text=item, height=50, corner_radius=0, 
                               fg_color="transparent", text_color="white", hover_color=color,
                               anchor="w", font=("Roboto", 15, "bold"),
                               command=lambda i=item: self.show_view(i)).pack(fill="x", pady=2)

        # 2. MAIN CONTENT AREA
        self.content_area = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 3. RIGHT DEVICE MONITOR PANEL
        self.monitor_panel = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#1E1E1E")
        self.monitor_panel.grid(row=0, column=2, sticky="nsew")
        
        ctk.CTkLabel(self.monitor_panel, text="DEVICE MONITOR", font=("Roboto", 18, "bold"), text_color="#F1C40F").pack(pady=20)
        
        self.device_list_box = ctk.CTkTextbox(self.monitor_panel, height=300, fg_color="#000", text_color="#F1C40F", font=("Consolas", 12))
        self.device_list_box.pack(padx=10, fill="x")
        
        self.info_panel = ctk.CTkFrame(self.monitor_panel, fg_color="#262626", corner_radius=10)
        self.info_panel.pack(pady=20, padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.info_panel, text="Device Info", font=("Roboto", 14, "bold")).pack(pady=5)
        self.info_text = ctk.CTkLabel(self.info_panel, text="No Device Connected", font=("Roboto", 11), text_color="#AAA", justify="left")
        self.info_text.pack(pady=10, padx=10)

        # 4. BOTTOM LOG CONSOLE
        self.log_frame = ctk.CTkFrame(self.content_area, height=180, fg_color="#111", corner_radius=10)
        self.log_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.log_console = ctk.CTkTextbox(self.log_frame, fg_color="transparent", font=("Consolas", 12))
        self.log_console.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_console.tag_config("info", foreground="#0F0")
        self.log_console.tag_config("error", foreground="#F00")
        self.log_console.tag_config("warning", foreground="#F1C40F")
        self.log_console.tag_config("success", foreground="#3498DB")
        
        self.progress_bar = ctk.CTkProgressBar(self.log_frame, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)

        self.show_view("Samsung")

    def log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert("end", f"[{timestamp}] {msg}\n", level)
        self.log_console.see("end")

    def update_device_list(self, devices):
        self.device_list_box.delete("1.0", "end")
        if not devices:
            self.device_list_box.insert("end", "Waiting for device...")
            self.info_text.configure(text="No Device Connected")
        else:
            for dev in devices:
                self.device_list_box.insert("end", f"{dev}\n")
            # تحديث معلومات أول جهاز ADB إذا وجد
            adb_devs = [d for d in devices if "[ADB]" in d]
            if adb_devs:
                serial = adb_devs[0].split()[-1]
                info = get_device_info(ADB_PATH, serial)
                info_str = "\n".join([f"{k}: {v}" for k, v in info.items()])
                self.info_text.configure(text=info_str)

    def show_view(self, name):
        for widget in self.content_area.winfo_children():
            if widget != self.log_frame: widget.destroy()
        
        if name == "Samsung": self.render_samsung()
        elif name == "MTK & Scatter": self.render_mtk()
        elif name == "Penumbra (Xiaomi)": self.render_penumbra()
        elif name == "Unisoc Pro": self.render_unisoc()
        elif name == "ADB / Fastboot": self.render_adb()
        elif name == "Settings": self.render_settings()

    def render_samsung(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        f_left = ctk.CTkFrame(container, corner_radius=10, border_width=1, border_color="#333")
        f_left.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(f_left, text="SAMSUNG FLASH", font=("Roboto", 16, "bold"), text_color="#3498DB").pack(pady=10)
        
        for p in ["BL", "AP", "CP", "CSC"]:
            row = ctk.CTkFrame(f_left, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=p, width=40).pack(side="left")
            ctk.CTkEntry(row, placeholder_text=f"Select {p}...", height=35).pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(row, text="📁", width=40, height=35).pack(side="right")
            
        ctk.CTkButton(f_left, text="FLASH", height=50, fg_color="#0057B7", command=lambda: self.bridge.run_mtk_command("flash")).pack(pady=20, padx=20, fill="x")

        f_right = ctk.CTkFrame(container, corner_radius=10, border_width=1, border_color="#333")
        f_right.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(f_right, text="SERVICES", font=("Roboto", 16, "bold"), text_color="#F1C40F").pack(pady=10)
        
        ops = [("FRP MTP", "frp_mtp"), ("FRP ADB", "frp_adb"), ("CSC Change", "csc"), ("Factory Reset", "reset")]
        for text, cmd in ops:
            ctk.CTkButton(f_right, text=text, height=45, command=lambda c=cmd: self.bridge.run_mtk_command(c)).pack(pady=5, padx=20, fill="x")

    def render_mtk(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text="MTK CLIENT ENGINE", font=("Roboto", 18, "bold"), text_color="#E67E22").pack(pady=10)
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True)
        
        mtk_ops = [
            ("Read Info", "printgpt"), ("Erase FRP", "erase frp"), 
            ("Unlock BL", "stage2 bootloader unlock"), ("Relock BL", "stage2 bootloader lock"),
            ("Format Data", "erase userdata"), ("Dump Preloader", "r preloader preloader.bin")
        ]
        
        for i, (text, cmd) in enumerate(mtk_ops):
            btn = ctk.CTkButton(btn_frame, text=text, height=50, fg_color="#E67E22", 
                                 command=lambda c=cmd: self.bridge.run_mtk_command(c.split()[0], c.split()[1:]))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
        btn_frame.grid_columnconfigure((0,1), weight=1)

    def render_unisoc(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="UNISOC PRO ENGINE", font=("Roboto", 18, "bold"), text_color="#9B59B6").pack(pady=10)
        
        ops = [("Read Info", "info"), ("Factory Reset", "reset"), ("Erase FRP", "frp"), ("Unlock BL", "unlock")]
        for text, cmd in ops:
            ctk.CTkButton(container, text=text, height=50, fg_color="#9B59B6", 
                           command=lambda c=cmd: self.bridge.run_unisoc_command(c)).pack(pady=10, padx=50, fill="x")

    def render_penumbra(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="XIAOMI PENUMBRA ENGINE", font=("Roboto", 18, "bold"), text_color="#E74C3C").pack(pady=10)
        
        ops = [("Bypass Mi Cloud", "bypass"), ("Anti-Relock", "antirelock"), ("Sideload FRP", "sideload_frp")]
        for text, cmd in ops:
            ctk.CTkButton(container, text=text, height=50, fg_color="#E74C3C", 
                           command=lambda c=cmd: self.bridge.run_xiaomi_command(c)).pack(pady=10, padx=50, fill="x")

    def render_adb(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="ADB & FASTBOOT TOOLS", font=("Roboto", 18, "bold")).pack(pady=10)
        
        ctk.CTkButton(container, text="Reboot to Recovery", command=lambda: self.bridge._execute_async([ADB_PATH, "reboot", "recovery"])).pack(pady=5)
        ctk.CTkButton(container, text="Reboot to Bootloader", command=lambda: self.bridge._execute_async([ADB_PATH, "reboot", "bootloader"])).pack(pady=5)
        ctk.CTkButton(container, text="Open Device Manager", fg_color="#333", command=lambda: os.system("devmgmt.msc")).pack(pady=20)

    def render_settings(self):
        ctk.CTkLabel(self.content_area, text="SETTINGS", font=("Roboto", 24, "bold")).pack(pady=20)
        ctk.CTkSwitch(self.content_area, text="Auto-Update Engine").pack(pady=10)
        ctk.CTkButton(self.content_area, text="CHECK HWID", command=lambda: self.log(f"Your HWID: {os.popen('wmic uuid get value').read().strip()}", "warning")).pack(pady=20)

if __name__ == "__main__":
    app = TsmartToolPro()
    app.mainloop()
