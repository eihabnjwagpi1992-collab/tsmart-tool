import tkinter as tk
import customtkinter as ctk
import requests
import subprocess
import threading
import os
import json
import sys
from datetime import datetime

# الإعدادات العامة للمظهر
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

USER_DB_FILE = "users_db.json"

class TsmartTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Tool Pro - Ultimate GSM Repair Suite")
        self.geometry("1200x800")
        
        self.current_user = None
        self.is_activated = False
        self.load_user_db()
        
        # عرض شاشة الدخول عند البدء
        self.show_auth_screen()

    def load_user_db(self):
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, "r") as f:
                self.users = json.load(f)
        else:
            self.users = {}

    def save_user_db(self):
        with open(USER_DB_FILE, "w") as f:
            json.dump(self.users, f)

    def show_auth_screen(self):
        self.auth_frame = ctk.CTkFrame(self)
        self.auth_frame.pack(expand=True, fill="both")

        self.tab_view = ctk.CTkTabview(self.auth_frame, width=450, height=550)
        self.tab_view.pack(pady=50)

        self.tab_view.add("Login")
        self.tab_view.add("Register")

        # --- Login Tab ---
        ctk.CTkLabel(self.tab_view.tab("Login"), text="Tsmart Tool Access", font=("Roboto", 26, "bold"), text_color="#3498DB").pack(pady=30)
        self.login_email = ctk.CTkEntry(self.tab_view.tab("Login"), placeholder_text="Email", width=300, height=45)
        self.login_email.pack(pady=10)
        self.login_password = ctk.CTkEntry(self.tab_view.tab("Login"), placeholder_text="Password", show="*", width=300, height=45)
        self.login_password.pack(pady=10)
        ctk.CTkButton(self.tab_view.tab("Login"), text="Login", command=self.handle_login, width=200, height=45, font=("Roboto", 16, "bold")).pack(pady=30)

        # --- Register Tab ---
        ctk.CTkLabel(self.tab_view.tab("Register"), text="Create New Account", font=("Roboto", 26, "bold")).pack(pady=30)
        self.reg_email = ctk.CTkEntry(self.tab_view.tab("Register"), placeholder_text="Email", width=300, height=45)
        self.reg_email.pack(pady=10)
        self.reg_password = ctk.CTkEntry(self.tab_view.tab("Register"), placeholder_text="Password", show="*", width=300, height=45)
        self.reg_password.pack(pady=10)
        ctk.CTkButton(self.tab_view.tab("Register"), text="Register", command=self.handle_signup, width=200, height=45).pack(pady=30)

    def handle_login(self):
        email = self.login_email.get()
        password = self.login_password.get()

        if email in self.users and self.users[email]["password"] == password:
            self.current_user = email
            # فحص الاشتراك السنوي
            expiry = self.users[email].get("expiry", "")
            if expiry:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                if datetime.now() < expiry_date:
                    self.is_activated = True
            
            self.auth_frame.destroy()
            self.setup_dashboard()
        else:
            tk.messagebox.showerror("Auth Error", "Invalid credentials or No Internet Connection.")

    def handle_signup(self):
        email = self.reg_email.get()
        password = self.reg_password.get()
        if email and password:
            if email in self.users:
                tk.messagebox.showerror("Error", "User already exists.")
            else:
                self.users[email] = {"password": password, "credits": 0, "expiry": None}
                self.save_user_db()
                tk.messagebox.showinfo("Success", "Account created. Please login.")
                self.tab_view.set("Login")

    def setup_dashboard(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#1A1A1A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TSMART PRO", font=("Roboto", 28, "bold"), text_color="#3498DB").pack(pady=30)
        
        # Status Card
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="#262626", corner_radius=10)
        status_frame.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(status_frame, text=f"User: {self.current_user[:15]}...", font=("Roboto", 11)).pack(pady=2)
        status_text = "ACTIVE ✅" if self.is_activated else "INACTIVE ❌"
        self.status_label = ctk.CTkLabel(status_frame, text=status_text, font=("Roboto", 14, "bold"), text_color="#2ECC71" if self.is_activated else "#E74C3C")
        self.status_label.pack(pady=5)

        # Navigation
        self.btn_mtk = ctk.CTkButton(self.sidebar, text="MTK Pro (Bypass/FRP)", command=lambda: self.show_view("MTK"), height=45, fg_color="#E67E22" if self.is_activated else "#555")
        self.btn_mtk.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="Xiaomi Pro", command=lambda: self.show_view("Xiaomi"), height=40, fg_color="transparent", border_width=1).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="ADB / Fastboot", command=lambda: self.show_view("ADB"), height=40, fg_color="transparent", border_width=1).pack(pady=5, padx=20, fill="x")
        
        if not self.is_activated:
            ctk.CTkButton(self.sidebar, text="Activate License", fg_color="#2ECC71", command=self.show_activation).pack(pady=20, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#C0392B", command=self.logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # Main View
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        self.log_console = ctk.CTkTextbox(self.main_view, height=200, fg_color="#000", text_color="#0F0")
        self.log_console.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.show_view("MTK")

    def show_view(self, name):
        if not self.is_activated and name == "MTK":
            tk.messagebox.showwarning("Subscription Required", "This module requires an active annual subscription.")
            return

        for widget in self.main_view.winfo_children():
            if widget != self.log_console:
                widget.destroy()
            
        if name == "MTK": self.render_mtk()
        elif name == "Xiaomi": self.render_xiaomi()
        elif name == "ADB": self.render_adb()

    def render_mtk(self):
        ctk.CTkLabel(self.main_view, text="MediaTek Professional Module (mtkclient)", font=("Roboto", 24, "bold"), text_color="#E67E22").pack(pady=20)
        
        grid = ctk.CTkFrame(self.main_view, fg_color="transparent")
        grid.pack(expand=True, fill="both", padx=50)
        
        # أزرار mtkclient
        ctk.CTkButton(grid, text="Bypass Auth (Brom)", width=250, height=50, command=lambda: self.run_mtk("python3 mtkclient/mtk payload-bypass")).pack(pady=10)
        ctk.CTkButton(grid, text="Erase FRP (MTK)", width=250, height=50, command=lambda: self.run_mtk("python3 mtkclient/mtk e frp")).pack(pady=10)
        ctk.CTkButton(grid, text="Unlock Bootloader", width=250, height=50, fg_color="#C0392B", command=lambda: self.run_mtk("python3 mtkclient/mtk stage2 unlock")).pack(pady=10)
        ctk.CTkButton(grid, text="Read Full Flash", width=250, height=50, command=lambda: self.run_mtk("python3 mtkclient/mtk rf flash.bin")).pack(pady=10)

    def show_activation(self):
        dialog = ctk.CTkInputDialog(text="Enter 1-Year Activation Key:", title="License Activation")
        key = dialog.get_input()
        if key and key.startswith("TSMART-PRO-"):
            # محاكاة تفعيل سنوي
            self.users[self.current_user]["expiry"] = "2027-02-17"
            self.save_user_db()
            tk.messagebox.showinfo("Success", "Account activated for 1 Year!")
            self.logout() # إعادة دخول لتحديث الحالة
        else:
            tk.messagebox.showerror("Invalid Key", "Please contact admin for a valid subscription key.")

    def run_mtk(self, cmd):
        self.log(f"Initializing MTK Port...")
        self.log(f"Running: {cmd}")
        # هنا يتم استدعاء ملفات mtkclient التي تم دمجها
        threading.Thread(target=lambda: self.execute_cmd(cmd), daemon=True).start()

    def execute_cmd(self, cmd):
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
        except Exception as e:
            self.log(f"Error: {str(e)}")

    def log(self, msg):
        self.log_console.insert("end", f">>> {msg}\n")
        self.log_console.see("end")

    def render_xiaomi(self):
        ctk.CTkLabel(self.main_view, text="Xiaomi Pro Services", font=("Roboto", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self.main_view, text="Fastboot to EDL", width=200).pack(pady=10)

    def render_adb(self):
        ctk.CTkLabel(self.main_view, text="ADB/Fastboot Tools", font=("Roboto", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self.main_view, text="Check Devices", command=lambda: self.execute_cmd("adb devices")).pack(pady=10)

    def logout(self):
        self.current_user = None
        for widget in self.winfo_children():
            widget.destroy()
        self.show_auth_screen()

if __name__ == "__main__":
    app = TsmartTool()
    app.mainloop()
