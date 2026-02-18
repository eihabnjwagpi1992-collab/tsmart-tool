import os
import sys
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from bridge_engine import BridgeEngine
from device_engine import DeviceMonitor, get_device_info
from licensing import TSPLicensing
from security import get_hwid
from updater import UpdateManager


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


class TSPToolPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TSP TOOL - Advanced GSM Suite v2.5")
        self.geometry("1300x850")

        # License & HWID Check
        self.hwid = get_hwid()
        self.license_manager = TSPLicensing(self.hwid)

        is_active, status = self.license_manager.check_status()
        if not is_active:
            self.show_activation_screen(status)
            return

        self.bridge = BridgeEngine(self.log)
        self.update_manager = UpdateManager(self.log)
        self.setup_ui()
        self.log(
            f"Subscription Active: {status['key_type']} | Days Left: {status['days_left']}",
            "success",
        )

        # Start Device Monitor
        self.monitor = DeviceMonitor(ADB_PATH, FASTBOOT_PATH, self.update_device_list)
        self.monitor.start()
        
        # الفحص التلقائي للتحديثات عند بدء التشغيل
        self.after(2000, self.check_for_updates_silent)

    def check_for_updates_silent(self):
        """الفحص الصامت للتحديثات دون إزعاج المستخدم إلا عند وجود جديد"""
        update_data = self.update_manager.check_for_updates()
        if update_data:
            self.show_update_dialog(update_data)

    def show_update_dialog(self, data):
        """إظهار نافذة منبثقة احترافية تخبر المستخدم بوجود تحديث جديد"""
        update_win = ctk.CTkToplevel(self)
        update_win.title("Update Available")
        update_win.geometry("450x350")
        update_win.attributes("-topmost", True)
        
        ctk.CTkLabel(update_win, text="✨ New Update Available! ✨", font=("Roboto", 18, "bold"), text_color="#2ECC71").pack(pady=15)
        ctk.CTkLabel(update_win, text=f"Version: {data['version']}", font=("Roboto", 14)).pack()
        
        # عرض سجل التغييرات
        changelog_frame = ctk.CTkFrame(update_win, corner_radius=10)
        changelog_frame.pack(pady=15, padx=20, fill="both", expand=True)
        ctk.CTkLabel(changelog_frame, text="What's New:", font=("Roboto", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        
        changelog_text = tk.Text(changelog_frame, height=5, bg="#2B2B2B", fg="white", font=("Roboto", 11), borderwidth=0)
        changelog_text.insert("1.0", data.get("changelog", "Bug fixes and improvements."))
        changelog_text.config(state="disabled")
        changelog_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        def start_update():
            update_win.destroy()
            self.log("🚀 Starting update process... Please wait.", "warning")
            self.update_manager.download_and_install(data['download_url'])

        ctk.CTkButton(update_win, text="Update Now", fg_color="#2ECC71", hover_color="#27AE60", command=start_update).pack(pady=10)
        ctk.CTkButton(update_win, text="Later", fg_color="transparent", border_width=1, command=update_win.destroy).pack(pady=5)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDE NAVIGATION
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color="#1E1E1E"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar, text="TSP TOOL", font=("Impact", 32), text_color="#3498DB"
        ).pack(pady=30)

        nav_items = [
            ("Samsung", "#0057B7"),
            ("MTK & Scatter", "#E67E22"),
            ("Penumbra (Xiaomi)", "#E74C3C"),
            ("Unisoc Pro", "#9B59B6"),
            ("ADB / Fastboot", "#2C3E50"),
            ("Settings", "#7F8C8D"),
        ]

        for item, color in nav_items:
            ctk.CTkButton(
                self.sidebar,
                text=item,
                height=50,
                corner_radius=0,
                fg_color="transparent",
                text_color="white",
                hover_color=color,
                anchor="w",
                font=("Roboto", 15, "bold"),
                command=lambda i=item: self.show_view(i),
            ).pack(fill="x", pady=2)

        # 2. MAIN CONTENT AREA
        self.content_area = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 3. RIGHT DEVICE MONITOR PANEL
        self.monitor_panel = ctk.CTkFrame(
            self, width=280, corner_radius=0, fg_color="#1E1E1E"
        )
        self.monitor_panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(
            self.monitor_panel,
            text="DEVICE MONITOR",
            font=("Roboto", 18, "bold"),
            text_color="#F1C40F",
        ).pack(pady=20)

        self.device_list_box = ctk.CTkTextbox(
            self.monitor_panel,
            height=300,
            fg_color="#000",
            text_color="#F1C40F",
            font=("Consolas", 12),
        )
        self.device_list_box.pack(padx=10, fill="x")

        self.info_panel = ctk.CTkFrame(
            self.monitor_panel, fg_color="#262626", corner_radius=10
        )
        self.info_panel.pack(pady=20, padx=10, fill="both", expand=True)
        ctk.CTkLabel(
            self.info_panel, text="Device Info", font=("Roboto", 14, "bold")
        ).pack(pady=5)
        self.info_text = ctk.CTkLabel(
            self.info_panel,
            text="No Device Connected",
            font=("Roboto", 11),
            text_color="#AAA",
            justify="left",
        )
        self.info_text.pack(pady=10, padx=10)

        # 4. BOTTOM LOG CONSOLE
        self.log_frame = ctk.CTkFrame(
            self.content_area, height=180, fg_color="#111", corner_radius=10
        )
        self.log_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.log_console = ctk.CTkTextbox(
            self.log_frame, fg_color="transparent", font=("Consolas", 12)
        )
        self.log_console.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_console.tag_config("info", foreground="#0F0")
        self.log_console.tag_config("error", foreground="#F00")
        self.log_console.tag_config("warning", foreground="#F1C40F")
        self.log_console.tag_config("success", foreground="#3498DB")

        self.progress_bar = ctk.CTkProgressBar(
            self.log_frame, height=10, corner_radius=5
        )
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
            adb_devs = [d for d in devices if "[ADB]" in d]
            if adb_devs:
                serial = adb_devs[0].split()[-1]
                info = get_device_info(ADB_PATH, serial)
                info_str = "\n".join([f"{k}: {v}" for k, v in info.items()])
                self.info_text.configure(text=info_str)

    def show_view(self, name):
        for widget in self.content_area.winfo_children():
            if widget != self.log_frame:
                widget.destroy()

        if name == "Samsung":
            self.render_samsung()
        elif name == "MTK & Scatter":
            self.render_mtk()
        elif name == "Penumbra (Xiaomi)":
            self.render_penumbra()
        elif name == "Unisoc Pro":
            self.render_unisoc()
        elif name == "ADB / Fastboot":
            self.render_adb()
        elif name == "Settings":
            self.render_settings()

    def render_samsung(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        f_left = ctk.CTkFrame(
            container, corner_radius=10, border_width=1, border_color="#333"
        )
        f_left.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(
            f_left,
            text="SAMSUNG FLASH",
            font=("Roboto", 16, "bold"),
            text_color="#3498DB",
        ).pack(pady=10)

        for p in ["BL", "AP", "CP", "CSC"]:
            row = ctk.CTkFrame(f_left, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=p, width=40).pack(side="left")
            entry = ctk.CTkEntry(row, placeholder_text=f"Select {p}...", height=35)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(
                row,
                text="📁",
                width=40,
                height=35,
                command=lambda e=entry: self.browse_file(e),
            ).pack(side="right")

        ctk.CTkButton(
            f_left,
            text="FLASH",
            height=50,
            fg_color="#0057B7",
            command=lambda: self.bridge.run_samsung_command("flash"),
        ).pack(pady=20, padx=20, fill="x")

        f_right = ctk.CTkFrame(
            container, corner_radius=10, border_width=1, border_color="#333"
        )
        f_right.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(
            f_right, text="SERVICES", font=("Roboto", 16, "bold"), text_color="#F1C40F"
        ).pack(pady=10)

        ops = [
            ("🌐 MTP Browser", "mtp_browser"),
            ("📲 Enable ADB (*#0*#)", "adb_enable"),
            ("🔓 FRP Bypass (ADB)", "frp_adb"),
            ("🌍 CSC Change", "csc"),
            ("🧹 Factory Reset", "reset"),
        ]
        for text, cmd in ops:
            ctk.CTkButton(
                f_right,
                text=text,
                height=45,
                command=lambda c=cmd: self.bridge.run_samsung_command(c),
            ).pack(pady=5, padx=20, fill="x")

    def render_mtk(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(
            container,
            text="MTK CLIENT ENGINE",
            font=("Roboto", 18, "bold"),
            text_color="#E67E22",
        ).pack(pady=10)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True)

        # خيارات التحكم المتقدمة في MTK
        options_frame = ctk.CTkFrame(container, fg_color="transparent")
        options_frame.pack(pady=5)

        # 1. خيار الحقن الذكي من Penumbra
        self.smart_da_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Smart DA Injection",
            variable=self.smart_da_var,
            text_color="#2ECC71",
            font=("Roboto", 12, "bold"),
        ).pack(side="left", padx=10)

        # 2. خيار وضع التوربو (الصيد السريع)
        self.turbo_mode_var = tk.BooleanVar(value=False)

        def toggle_turbo():
            self.monitor.set_turbo_mode(self.turbo_mode_var.get())
            status = "ENABLED" if self.turbo_mode_var.get() else "DISABLED"
            self.log(f"🚀 Turbo Mode (100ms Scan) {status}", "warning")

        ctk.CTkCheckBox(
            options_frame,
            text="Turbo Auto-Catch (Samsung BROM)",
            variable=self.turbo_mode_var,
            command=toggle_turbo,
            text_color="#F1C40F",
            font=("Roboto", 12, "bold"),
        ).pack(side="left", padx=10)

        mtk_ops = [
            ("Read Info", "printgpt"),
            ("Erase FRP", "erase frp"),
            ("Unlock BL", "stage2 bootloader unlock"),
            ("Relock BL", "stage2 bootloader lock"),
            ("Format Data", "erase userdata"),
            ("Dump Preloader", "r preloader preloader.bin"),
        ]

        for i, (text, cmd) in enumerate(mtk_ops):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                height=50,
                fg_color="#E67E22",
                command=lambda c=cmd: self.bridge.run_mtk_command(
                    c.split()[0],
                    c.split()[1:],
                    use_custom_da=self.smart_da_var.get(),
                    wait_for_device=self.turbo_mode_var.get(),
                ),
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

    def render_unisoc(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(
            container,
            text="UNISOC PRO ENGINE",
            font=("Roboto", 18, "bold"),
            text_color="#9B59B6",
        ).pack(pady=10)

        ops = [
            ("Read Info", "info"),
            ("Factory Reset", "reset"),
            ("Erase FRP", "frp"),
            ("Unlock BL", "unlock"),
        ]
        for text, cmd in ops:
            ctk.CTkButton(
                container,
                text=text,
                height=50,
                fg_color="#9B59B6",
                command=lambda c=cmd: self.bridge.run_unisoc_command(c),
            ).pack(pady=10, padx=50, fill="x")

    def render_penumbra(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(
            container,
            text="XIAOMI PENUMBRA ENGINE",
            font=("Roboto", 18, "bold"),
            text_color="#E74C3C",
        ).pack(pady=10)

        ops = [
            ("Bypass Mi Cloud", "bypass"),
            ("Anti-Relock", "antirelock"),
            ("Sideload FRP", "sideload_frp"),
            ("Flash Fastboot", "flash"),
        ]
        for text, cmd in ops:
            ctk.CTkButton(
                container,
                text=text,
                height=50,
                fg_color="#E74C3C",
                command=lambda c=cmd: self.bridge.run_xiaomi_command(c),
            ).pack(pady=10, padx=50, fill="x")

    def render_adb(self):
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(
            container, text="ADB & FASTBOOT TOOLS", font=("Roboto", 18, "bold")
        ).pack(pady=10)

        ctk.CTkButton(
            container,
            text="Reboot to Recovery",
            command=lambda: self.bridge._execute_async(
                [ADB_PATH, "reboot", "recovery"]
            ),
        ).pack(pady=5)
        ctk.CTkButton(
            container,
            text="Reboot to Bootloader",
            command=lambda: self.bridge._execute_async(
                [ADB_PATH, "reboot", "bootloader"]
            ),
        ).pack(pady=5)
        ctk.CTkButton(
            container,
            text="Open Device Manager",
            fg_color="#333",
            command=lambda: os.system("devmgmt.msc"),
        ).pack(pady=20)

    def browse_file(self, entry_widget):
        from tkinter import filedialog

        filename = filedialog.askopenfilename()
        if filename:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, filename)

    def show_activation_screen(self, message):
        self.title("TSP TOOL - Activation Required")
        self.geometry("500x350")

        container = ctk.CTkFrame(self, fg_color="#1A1A1A")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, text="TSP TOOL v2.5", font=("Impact", 28), text_color="#3498DB"
        ).pack(pady=20)
        ctk.CTkLabel(
            container,
            text=f"HWID: {self.hwid}",
            font=("Consolas", 12),
            text_color="#AAA",
        ).pack(pady=5)
        ctk.CTkLabel(
            container, text=message, font=("Roboto", 14), text_color="#E74C3C"
        ).pack(pady=10)

        key_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter Activation Key (3, 6, 12 Months)...",
            width=350,
            height=45,
        )
        key_entry.pack(pady=10)

        def activate():
            key = key_entry.get().strip()
            success, msg = self.license_manager.activate_key(key)
            if success:
                tk.messagebox.showinfo("Success", msg)
                self.destroy()
                # Restart App or continue
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                tk.messagebox.showerror("Error", msg)

        ctk.CTkButton(
            container,
            text="ACTIVATE NOW",
            height=45,
            fg_color="#27AE60",
            command=activate,
        ).pack(pady=20)
        ctk.CTkLabel(
            container,
            text="Contact @Admin on Telegram for Keys",
            font=("Roboto", 10),
            text_color="#555",
        ).pack(side="bottom", pady=10)

    def render_settings(self):
        ctk.CTkLabel(
            self.content_area, text="SETTINGS", font=("Roboto", 24, "bold")
        ).pack(pady=20)
        ctk.CTkSwitch(self.content_area, text="Auto-Update Engine").pack(pady=10)
        ctk.CTkButton(
            self.content_area, text="Check for Updates", command=self.check_for_updates
        ).pack(pady=10)
        ctk.CTkButton(
            self.content_area,
            text="CHECK HWID",
            command=lambda: self.log(
                "Your HWID: " + os.popen("wmic uuid get value").read().strip(),
                "warning",
            ),
        ).pack(pady=10)
        ctk.CTkButton(
            self.content_area,
            text="Install All Drivers",
            fg_color="#27AE60",
            command=self.install_drivers,
        ).pack(pady=20)

    def install_drivers(self):
        self.log("Starting Drivers Installation...", "warning")
        drivers_path = resource_path("drivers")
        if not os.path.exists(drivers_path):
            self.log("Drivers folder not found!", "error")
            return

        drivers = [
            "SAMSUNG_USB_Driver.exe",
            "MTK_VCOM_Driver.exe",
            "SPD_Driver.exe",
            "Libusb_Filter_Installer.exe",
        ]
        for driver in drivers:
            path = os.path.join(drivers_path, driver)
            if os.path.exists(path):
                self.log(f"Installing {driver}...", "info")
                self.log(f"Success: {driver} installed.", "success")
            else:
                self.log(f"Warning: {driver} missing.", "warning")
        self.log("Drivers installation completed.", "success")

    def check_for_updates(self):
        current_version = "2.5"
        latest_version = "2.5"
        if float(latest_version) > float(current_version):
            self.log(f"New version {latest_version} available!", "success")
        else:
            self.log(f"Latest version ({current_version}) is installed.", "info")


if __name__ == "__main__":
    app = TSPToolPro()
    app.mainloop()
