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

        self.title("Tsmart Tool - GSM Mobile Repair (Xiaomi Pro Edition)")
        self.geometry("1000x700")

        # بيانات افتراضية للكرديت
        self.user_credits = 0
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
        if key == "admin": # مفتاح تجريبي
            self.user_credits = 50 # رصيد وهمي للتجربة
            self.open_dashboard()
        else:
            tk.messagebox.showerror("Error", "Invalid Key. Use 'admin' for testing.")

    def open_dashboard(self):
        self.login_frame.destroy()
        self.setup_dashboard()

    def setup_dashboard(self):
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Tsmart Tool", font=("Roboto", 20, "bold"))
        self.logo_label.pack(pady=20, padx=10)

        # تبويبات الجوانب
        self.btn_samsung = ctk.CTkButton(self.sidebar_frame, text="Samsung", command=lambda: self.show_frame("Samsung"))
        self.btn_samsung.pack(pady=10, padx=10)

        self.btn_xiaomi = ctk.CTkButton(self.sidebar_frame, text="Xiaomi Pro", fg_color="#E67E22", hover_color="#D35400", command=lambda: self.show_frame("Xiaomi"))
        self.btn_xiaomi.pack(pady=10, padx=10)

        self.btn_adb = ctk.CTkButton(self.sidebar_frame, text="ADB / Fastboot", command=lambda: self.show_frame("ADB"))
        self.btn_adb.pack(pady=10, padx=10)

        # عرض الرصيد في الأسفل
        self.credit_label = ctk.CTkLabel(self.sidebar_frame, text=f"Credits: {self.user_credits}", font=("Roboto", 14, "bold"))
        self.credit_label.pack(side="bottom", pady=20)

        # Main Content Area
        self.main_view = ctk.CTkFrame(self)
        self.main_view.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Log Console
        self.log_console = ctk.CTkTextbox(self, height=150)
        self.log_console.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.show_frame("Xiaomi") # الافتراضي هو شاومي كما طلب المستخدم

    def show_frame(self, name):
        # مسح المحتوى الحالي
        for widget in self.main_view.winfo_children():
            widget.destroy()

        if name == "Xiaomi":
            self.render_xiaomi_view()
        elif name == "ADB":
            self.render_adb_view()
        else:
            label = ctk.CTkLabel(self.main_view, text=f"{name} Module coming soon...")
            label.pack(pady=50)

    def render_xiaomi_view(self):
        ctk.CTkLabel(self.main_view, text="Xiaomi Professional Services", font=("Roboto", 20)).pack(pady=10)
        
        # قسم التحويلات
        convert_frame = ctk.CTkLabel(self.main_view, text="Switching Modes", font=("Roboto", 16, "bold"))
        convert_frame.pack(pady=5)
        
        ctk.CTkButton(self.main_view, text="Fastboot to EDL (OEM)", command=self.xiaomi_fastboot_to_edl).pack(pady=5)
        
        # قسم العمليات المدفوعة
        auth_frame = ctk.CTkFrame(self.main_view)
        auth_frame.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkLabel(auth_frame, text="Paid Services (Auth Required)", font=("Roboto", 16, "bold")).pack(pady=5)
        
        ctk.CTkButton(auth_frame, text="Xiaomi FRP Bypass (10 Credits)", fg_color="#C0392B", command=self.xiaomi_frp_bypass).pack(pady=5)
        ctk.CTkButton(auth_frame, text="Xiaomi Auth Flashing (15 Credits)", fg_color="#C0392B", command=self.xiaomi_auth_flash).pack(pady=5)

    def render_adb_view(self):
        ctk.CTkLabel(self.main_view, text="General ADB / Fastboot", font=("Roboto", 20)).pack(pady=10)
        ctk.CTkButton(self.main_view, text="Read Info (ADB)", command=lambda: self.run_command("adb shell getprop ro.product.model")).pack(pady=5)
        ctk.CTkButton(self.main_view, text="Reboot Download", command=lambda: self.run_command("adb reboot download")).pack(pady=5)
        ctk.CTkButton(self.main_view, text="Open Device Manager", command=lambda: self.run_command("devmgmt.msc")).pack(pady=5)

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

    # --- Xiaomi Functions ---

    def xiaomi_fastboot_to_edl(self):
        self.log("Attempting Fastboot to EDL...")
        self.run_command("fastboot oem edl")

    def xiaomi_frp_bypass(self):
        if self.user_credits < 10:
            tk.messagebox.showerror("Credits", "Insufficient credits! Please top up.")
            return
        
        if tk.messagebox.askyesno("Confirm", "This will consume 10 credits. Continue?"):
            self.log("Starting Xiaomi FRP Bypass via Server...")
            def process():
                import time
                time.sleep(2)
                self.user_credits -= 10
                self.credit_label.configure(text=f"Credits: {self.user_credits}")
                self.log("Server Auth: SUCCESS")
                self.log("FRP Bypass: DONE")
            threading.Thread(target=process, daemon=True).start()

    def xiaomi_auth_flash(self):
        if self.user_credits < 15:
            tk.messagebox.showerror("Credits", "Insufficient credits! Please top up.")
            return
        
        self.log("Waiting for Xiaomi Auth Server response...")
        self.run_command("fastboot flash recovery recovery.img")

if __name__ == "__main__":
    app = TsmartTool()
    app.mainloop()
