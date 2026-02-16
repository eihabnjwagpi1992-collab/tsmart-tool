import tkinter as tk
import customtkinter as ctk
import requests
import subprocess
import threading
import os
import time
import json

# الإعدادات العامة للمظهر
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# محاكاة قاعدة بيانات المستخدمين (في الواقع يفضل استخدام Firebase أو MySQL)
USER_DB_FILE = "users_db.json"

class TsmartTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Tool - Professional GSM Suite")
        self.geometry("1100x700")
        
        self.current_user = None
        self.load_user_db()
        
        # عرض شاشة الدخول عند البدء
        self.show_auth_screen()

    def load_user_db(self):
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, "r") as f:
                self.users = json.load(f)
        else:
            self.users = {} # {email: {"password": pwd, "credits": 0}}

    def save_user_db(self):
        with open(USER_DB_FILE, "w") as f:
            json.dump(self.users, f)

    def show_auth_screen(self):
        self.auth_frame = ctk.CTkFrame(self)
        self.auth_frame.pack(expand=True, fill="both")

        self.tab_view = ctk.CTkTabview(self.auth_frame, width=400, height=500)
        self.tab_view.pack(pady=50)

        self.tab_view.add("Login")
        self.tab_view.add("Sign Up")

        # --- Login Tab ---
        ctk.CTkLabel(self.tab_view.tab("Login"), text="Welcome Back", font=("Roboto", 24, "bold")).pack(pady=20)
        self.login_email = ctk.CTkEntry(self.tab_view.tab("Login"), placeholder_text="Email Address", width=300, height=40)
        self.login_email.pack(pady=10)
        self.login_password = ctk.CTkEntry(self.tab_view.tab("Login"), placeholder_text="Password", show="*", width=300, height=40)
        self.login_password.pack(pady=10)
        ctk.CTkButton(self.tab_view.tab("Login"), text="Login", command=self.handle_login, width=200, height=40).pack(pady=20)

        # --- Sign Up Tab ---
        ctk.CTkLabel(self.tab_view.tab("Sign Up"), text="Create Account", font=("Roboto", 24, "bold")).pack(pady=20)
        self.signup_email = ctk.CTkEntry(self.tab_view.tab("Sign Up"), placeholder_text="Email Address", width=300, height=40)
        self.signup_email.pack(pady=10)
        self.signup_password = ctk.CTkEntry(self.tab_view.tab("Sign Up"), placeholder_text="Password", show="*", width=300, height=40)
        self.signup_password.pack(pady=10)
        ctk.CTkButton(self.tab_view.tab("Sign Up"), text="Register", command=self.handle_signup, width=200, height=40).pack(pady=20)

    def handle_login(self):
        email = self.login_email.get()
        password = self.login_password.get()

        if email in self.users and self.users[email]["password"] == password:
            self.current_user = email
            self.auth_frame.destroy()
            self.setup_dashboard()
        else:
            tk.messagebox.showerror("Error", "Invalid Email or Password")

    def handle_signup(self):
        email = self.signup_email.get()
        password = self.signup_password.get()

        if not email or not password:
            tk.messagebox.showerror("Error", "Please fill all fields")
            return

        if email in self.users:
            tk.messagebox.showerror("Error", "Email already exists")
        else:
            self.users[email] = {"password": password, "credits": 0}
            self.save_user_db()
            tk.messagebox.showinfo("Success", "Account created! Please login.")
            self.tab_view.set("Login")

    def setup_dashboard(self):
        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="Tsmart Tool", font=("Roboto", 24, "bold"), text_color="#3498DB").pack(pady=30)
        
        # User Info Section
        user_info = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_info.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(user_info, text=f"👤 {self.current_user}", font=("Roboto", 12), wraplength=200).pack()
        self.credit_display = ctk.CTkLabel(user_info, text=f"💰 Credits: {self.users[self.current_user]['credits']}", font=("Roboto", 16, "bold"), text_color="#2ECC71")
        self.credit_display.pack(pady=5)

        # Navigation
        ctk.CTkButton(self.sidebar, text="Xiaomi Pro", command=lambda: self.show_view("Xiaomi")).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="ADB / Fastboot", command=lambda: self.show_view("ADB")).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Top Up Credits", fg_color="#E67E22", command=self.show_topup).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#C0392B", command=self.logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # Main View
        self.main_view = ctk.CTkFrame(self, corner_radius=10)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.show_view("Xiaomi")

    def show_view(self, name):
        for widget in self.main_view.winfo_children():
            widget.destroy()
            
        if name == "Xiaomi":
            self.render_xiaomi()
        elif name == "ADB":
            self.render_adb()

    def render_xiaomi(self):
        ctk.CTkLabel(self.main_view, text="Xiaomi Professional Services", font=("Roboto", 22, "bold")).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_frame.pack(expand=True)
        
        ctk.CTkButton(btn_frame, text="Fastboot to EDL", width=300, height=50, command=self.fb_to_edl).pack(pady=10)
        ctk.CTkButton(btn_frame, text="FRP Bypass (10 Credits)", width=300, height=50, fg_color="#C0392B", command=lambda: self.consume_credits(10, "FRP Bypass")).pack(pady=10)
        ctk.CTkButton(btn_frame, text="Auth Flashing (15 Credits)", width=300, height=50, fg_color="#C0392B", command=lambda: self.consume_credits(15, "Auth Flashing")).pack(pady=10)

    def render_adb(self):
        ctk.CTkLabel(self.main_view, text="ADB & Fastboot Tools", font=("Roboto", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self.main_view, text="Read Device Info", width=250, command=lambda: self.run_cmd("adb shell getprop ro.product.model")).pack(pady=10)
        ctk.CTkButton(self.main_view, text="Reboot to Download", width=250, command=lambda: self.run_cmd("adb reboot download")).pack(pady=10)

    def show_topup(self):
        dialog = ctk.CTkInputDialog(text="Enter Top-up Code or Amount (Simulation):", title="Charge Credits")
        value = dialog.get_input()
        if value:
            try:
                amount = int(value)
                self.users[self.current_user]["credits"] += amount
                self.save_user_db()
                self.credit_display.configure(text=f"💰 Credits: {self.users[self.current_user]['credits']}")
                tk.messagebox.showinfo("Success", f"Added {amount} credits to your account!")
            except:
                tk.messagebox.showerror("Error", "Invalid Input")

    def consume_credits(self, amount, service):
        if self.users[self.current_user]["credits"] < amount:
            tk.messagebox.showerror("Credits", "Insufficient credits! Please top up.")
            return
        
        if tk.messagebox.askyesno("Confirm", f"Consume {amount} credits for {service}?"):
            self.users[self.current_user]["credits"] -= amount
            self.save_user_db()
            self.credit_display.configure(text=f"💰 Credits: {self.users[self.current_user]['credits']}")
            tk.messagebox.showinfo("Success", f"{service} started successfully!")

    def fb_to_edl(self):
        tk.messagebox.showinfo("Action", "Executing Fastboot to EDL...")

    def run_cmd(self, cmd):
        tk.messagebox.showinfo("ADB", f"Running: {cmd}")

    def logout(self):
        self.current_user = None
        for widget in self.winfo_children():
            widget.destroy()
        self.show_auth_screen()

if __name__ == "__main__":
    app = TsmartTool()
    app.mainloop()
