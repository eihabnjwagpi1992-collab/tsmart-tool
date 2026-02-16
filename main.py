import tkinter as tk
import customtkinter as ctk
import requests
import subprocess
import threading
import os

# الإعدادات العامة للمظهر
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TsmartTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Tool - GSM Mobile Repair")
        self.geometry("900x600")

        # رابط ملف المفاتيح (يجب تغييره للرابط الفعلي الخاص بك)
        self.KEYS_URL = "https://raw.githubusercontent.com/YOUR_USER/keys/main/list.txt"
        
        self.show_login_window()

    def show_login_window(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(expand=True, fill="both")

        self.label = ctk.CTkLabel(self.login_frame, text="Tsmart Tool Login", font=("Roboto", 24))
        self.label.pack(pady=20)

        self.key_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter License Key", width=300)
        self.key_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.verify_key)
        self.login_button.pack(pady=20)

    def verify_key(self):
        key = self.key_entry.get()
        if not key:
            tk.messagebox.showerror("Error", "Please enter a key")
            return

        def check():
            try:
                # ملاحظة: في بيئة الاختبار هذه قد لا يعمل الرابط، لذا سأضيف مفتاحاً افتراضياً 'admin' للتجربة
                if key == "admin":
                    self.after(0, self.open_dashboard)
                    return
                
                response = requests.get(self.KEYS_URL)
                if response.status_code == 200:
                    keys = response.text.splitlines()
                    if key in keys:
                        self.after(0, self.open_dashboard)
                    else:
                        self.after(0, lambda: tk.messagebox.showerror("Error", "Invalid Key"))
                else:
                    self.after(0, lambda: tk.messagebox.showerror("Error", "Could not connect to server"))
            except Exception as e:
                self.after(0, lambda: tk.messagebox.showerror("Error", f"Connection Error: {str(e)}"))

        threading.Thread(target=check, daemon=True).start()

    def open_dashboard(self):
        self.login_frame.destroy()
        self.setup_dashboard()

    def setup_dashboard(self):
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Tsmart Tool", font=("Roboto", 20, "bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.btn_samsung = ctk.CTkButton(self.sidebar_frame, text="Samsung", command=lambda: self.log("Samsung Tab Selected"))
        self.btn_samsung.pack(pady=10, padx=10)

        self.btn_adb = ctk.CTkButton(self.sidebar_frame, text="ADB", command=lambda: self.log("ADB Tab Selected"))
        self.btn_adb.pack(pady=10, padx=10)

        self.btn_fastboot = ctk.CTkButton(self.sidebar_frame, text="Fastboot", command=lambda: self.log("Fastboot Tab Selected"))
        self.btn_fastboot.pack(pady=10, padx=10)

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=lambda: self.log("Settings Selected"))
        self.btn_settings.pack(pady=10, padx=10)

        # Main Content
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.features_label = ctk.CTkLabel(self.main_content, text="Features", font=("Roboto", 18))
        self.features_label.pack(pady=10)

        self.btn_read_info = ctk.CTkButton(self.main_content, text="Read Info (ADB)", command=self.read_info_adb)
        self.btn_read_info.pack(pady=10)

        self.btn_reboot_download = ctk.CTkButton(self.main_content, text="Reboot Download", command=self.reboot_download)
        self.btn_reboot_download.pack(pady=10)

        self.btn_dev_manager = ctk.CTkButton(self.main_content, text="Open Device Manager", command=self.open_device_manager)
        self.btn_dev_manager.pack(pady=10)

        # Log Console
        self.log_console = ctk.CTkTextbox(self.main_content, height=200)
        self.log_console.pack(side="bottom", fill="x", pady=10)
        self.log("Welcome to Tsmart Tool!")

    def log(self, message):
        self.log_console.insert("end", f"> {message}\n")
        self.log_console.see("end")

    def run_command(self, cmd):
        def execute():
            try:
                self.log(f"Executing: {cmd}")
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                if stdout: self.log(stdout.strip())
                if stderr: self.log(f"Error: {stderr.strip()}")
            except Exception as e:
                self.log(f"Exception: {str(e)}")

        threading.Thread(target=execute, daemon=True).start()

    def read_info_adb(self):
        self.run_command("adb shell getprop ro.product.model")

    def reboot_download(self):
        self.run_command("adb reboot download")

    def open_device_manager(self):
        self.run_command("devmgmt.msc")

if __name__ == "__main__":
    app = TsmartTool()
    app.mainloop()
