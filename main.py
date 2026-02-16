import tkinter as tk
import customtkinter as ctk
import requests
import subprocess
import threading
import os
import time

# الإعدادات العامة للمظهر
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TsmartTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tsmart Tool - GSM Mobile Repair (Pro Edition)")
        self.geometry("1200x750")
        self.minsize(900, 600)

        # بيانات افتراضية للكرديت
        self.user_credits = 100 # رصيد افتراضي
        self.KEYS_URL = "https://raw.githubusercontent.com/YOUR_USER/keys/main/list.txt"
        
        self.show_login_window()

    def show_login_window(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(expand=True, fill="both")

        self.label = ctk.CTkLabel(self.login_frame, text="Tsmart Tool Login", font=("Roboto", 30, "bold"))
        self.label.pack(pady=40)

        self.key_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter License Key", width=350, height=40, font=("Roboto", 16))
        self.key_entry.pack(pady=20)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.verify_key, width=200, height=40, font=("Roboto", 16, "bold"))
        self.login_button.pack(pady=30)

    def verify_key(self):
        key = self.key_entry.get()
        if key == "admin": # مفتاح تجريبي
            self.open_dashboard()
        else:
            tk.messagebox.showerror("Error", "Invalid Key. Use 'admin' for testing.")

    def open_dashboard(self):
        self.login_frame.destroy()
        self.setup_dashboard()

    def setup_dashboard(self):
        # Configure grid layout for main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=("#2B2B2B", "#202020"))
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Tsmart Tool", font=("Roboto", 28, "bold"), text_color="#3498DB")
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation Buttons
        self.btn_samsung = ctk.CTkButton(self.sidebar_frame, text="Samsung", command=lambda: self.show_frame("Samsung"),
                                         height=40, font=("Roboto", 16), fg_color="transparent", hover_color="#34495E")
        self.btn_samsung.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_xiaomi = ctk.CTkButton(self.sidebar_frame, text="Xiaomi Pro", command=lambda: self.show_frame("Xiaomi"),
                                        height=40, font=("Roboto", 16), fg_color="#E67E22", hover_color="#D35400")
        self.btn_xiaomi.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_adb = ctk.CTkButton(self.sidebar_frame, text="ADB / Fastboot", command=lambda: self.show_frame("ADB"),
                                     height=40, font=("Roboto", 16), fg_color="transparent", hover_color="#34495E")
        self.btn_adb.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Credit Display
        self.credit_label = ctk.CTkLabel(self.sidebar_frame, text=f"Credits: {self.user_credits}", font=("Roboto", 18, "bold"), text_color="#2ECC71")
        self.credit_label.grid(row=5, column=0, padx=20, pady=20, sticky="s")

        # Main Content Area
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Log Console
        self.log_console = ctk.CTkTextbox(self, height=180, corner_radius=10, fg_color=("#34495E", "#2C3E50"), text_color="#ECF0F1")
        self.log_console.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.log("Welcome to Tsmart Tool Pro Edition!")

        self.show_frame("Xiaomi") # Default view

    def show_frame(self, name):
        # Clear current content
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        if name == "Xiaomi":
            self.render_xiaomi_view()
        elif name == "ADB":
            self.render_adb_view()
        else:
            coming_soon_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
            coming_soon_frame.pack(expand=True)
            ctk.CTkLabel(coming_soon_frame, text=f"{name} Module coming soon...", font=("Roboto", 24, "bold"), text_color="#BDC3C7").pack(pady=50)

    def render_xiaomi_view(self):
        xiaomi_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        xiaomi_frame.pack(expand=True, fill="both")
        xiaomi_frame.grid_columnconfigure(0, weight=1)
        xiaomi_frame.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(xiaomi_frame, text="Xiaomi Professional Services", font=("Roboto", 26, "bold"), text_color="#E67E22").grid(row=0, column=0, pady=20)
        
        # Switching Modes Section
        switch_mode_frame = ctk.CTkFrame(xiaomi_frame, fg_color=("#34495E", "#2C3E50"), corner_radius=10)
        switch_mode_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(switch_mode_frame, text="Device Mode Switching", font=("Roboto", 18, "bold"), text_color="#ECF0F1").pack(pady=10)
        ctk.CTkButton(switch_mode_frame, text="Fastboot to EDL (OEM)", command=self.xiaomi_fastboot_to_edl,
                      height=45, font=("Roboto", 16), fg_color="#3498DB", hover_color="#2980B9").pack(pady=10, padx=20, fill="x")

        # Paid Services Section
        paid_services_frame = ctk.CTkFrame(xiaomi_frame, fg_color=("#34495E", "#2C3E50"), corner_radius=10)
        paid_services_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(paid_services_frame, text="Paid Services (Credits Required)", font=("Roboto", 18, "bold"), text_color="#ECF0F1").pack(pady=10)
        
        ctk.CTkButton(paid_services_frame, text="Xiaomi FRP Bypass (10 Credits)", command=self.xiaomi_frp_bypass,
                      height=45, font=("Roboto", 16), fg_color="#C0392B", hover_color="#A93226").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(paid_services_frame, text="Xiaomi Auth Flashing (15 Credits)", command=self.xiaomi_auth_flash,
                      height=45, font=("Roboto", 16), fg_color="#C0392B", hover_color="#A93226").pack(pady=10, padx=20, fill="x")

    def render_adb_view(self):
        adb_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        adb_frame.pack(expand=True, fill="both")
        adb_frame.grid_columnconfigure(0, weight=1)
        adb_frame.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(adb_frame, text="General ADB / Fastboot Operations", font=("Roboto", 26, "bold"), text_color="#3498DB").grid(row=0, column=0, pady=20)

        adb_buttons_frame = ctk.CTkFrame(adb_frame, fg_color=("#34495E", "#2C3E50"), corner_radius=10)
        adb_buttons_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(adb_buttons_frame, text="ADB & Fastboot Commands", font=("Roboto", 18, "bold"), text_color="#ECF0F1").pack(pady=10)

        ctk.CTkButton(adb_buttons_frame, text="Read Info (ADB)", command=lambda: self.run_command("adb shell getprop ro.product.model"),
                      height=45, font=("Roboto", 16), fg_color="#3498DB", hover_color="#2980B9").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(adb_buttons_frame, text="Reboot Download", command=lambda: self.run_command("adb reboot download"),
                      height=45, font=("Roboto", 16), fg_color="#3498DB", hover_color="#2980B9").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(adb_buttons_frame, text="Open Device Manager", command=lambda: self.run_command("devmgmt.msc"),
                      height=45, font=("Roboto", 16), fg_color="#3498DB", hover_color="#2980B9").pack(pady=10, padx=20, fill="x")

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
            self.log("Connecting to FRP Bypass Server...")
            threading.Thread(target=self._simulate_api_call, args=("frp_bypass", 10), daemon=True).start()

    def xiaomi_auth_flash(self):
        if self.user_credits < 15:
            tk.messagebox.showerror("Credits", "Insufficient credits! Please top up.")
            return
        
        if tk.messagebox.askyesno("Confirm", "This will consume 15 credits. Continue?"):
            self.log("Connecting to Xiaomi Auth Flashing Server...")
            threading.Thread(target=self._simulate_api_call, args=("auth_flash", 15), daemon=True).start()

    def _simulate_api_call(self, service_type, cost):
        # Simulate API call to an external server
        try:
            # In a real scenario, this would be an actual API endpoint
            # response = requests.post("https://api.your-credit-service.com/deduct_credits", json={'user_key': 'YOUR_KEY', 'service': service_type, 'cost': cost})
            # if response.status_code == 200 and response.json().get('success'):
            
            # Simulate network delay and success
            time.sleep(3) 
            self.user_credits -= cost
            self.after(0, lambda: self.credit_label.configure(text=f"Credits: {self.user_credits}"))
            self.log(f"Server Auth for {service_type.replace('_', ' ').upper()}: SUCCESS")
            self.log(f"{service_type.replace('_', ' ').upper()} operation: DONE")
            # else:
            #     self.log(f"Server Auth for {service_type.replace('_', ' ').upper()}: FAILED - {response.json().get('message', 'Unknown error')}")
        except Exception as e:
            self.log(f"API Connection Error for {service_type.replace('_', ' ').upper()}: {str(e)}")

if __name__ == "__main__":
    app = TsmartTool()
    app.mainloop()
