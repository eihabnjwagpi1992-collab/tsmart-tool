import os
import subprocess
import sys
import threading
import time

# إضافة مسارات المجلدات إلى sys.path لتمكين استيراد المكتبات مباشرة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "mtkclient"))
sys.path.append(os.path.join(BASE_DIR, "unisoc"))

class BridgeEngine:
    def __init__(self, logger_callback):
        self.logger = logger_callback
        self.current_process = None
        self.penumbra_dir = os.path.join(BASE_DIR, "penumbra")
        self.penumbra_payloads = os.path.join(self.penumbra_dir, "core", "payloads")
        self.penumbra_scripts = os.path.join(self.penumbra_dir, "scripts")
        self.usb_force_mode = True # تفعيل قوة الاتصال بالـ USB بشكل افتراضي

    def get_tool_path(self, tool_name):
        """الحصول على المسار الصحيح للأداة (ADB/Fastboot) بناءً على نظام التشغيل"""
        if os.name == 'nt':
            path = os.path.join(BASE_DIR, "bin", f"{tool_name}.exe")
        else:
            path = os.path.join(BASE_DIR, "bin", tool_name)
        
        if not os.path.exists(path):
            return tool_name
        return path

    def set_usb_force_mode(self, enabled):
        self.usb_force_mode = enabled

    def get_penumbra_args(self, device_type="generic"):
        """تجهيز حجج الحقن الذكية من Penumbra بناءً على نوع الجهاز"""
        args = []
        da_v6 = os.path.join(self.penumbra_payloads, "extloader_v6.bin")
        payload = os.path.join(self.penumbra_payloads, "hakujoudai.bin")
        
        if os.path.exists(da_v6):
            self.logger(f"💉 Penumbra Core: Injecting Ultra DA (v6)...", "success")
            args.extend(["--da", da_v6])
        
        if os.path.exists(payload):
            self.logger(f"🔓 Penumbra Core: Activating Auth Bypass...", "success")
            args.extend(["--payload", payload])
            
        # إضافة خيارات القوة للـ USB في mtkclient
        if self.usb_force_mode:
            args.extend(["--preloader", "bypass", "--timeout", "30000"]) # زيادة المهلة لضمان الاستقرار
            
        return args

    def run_mtk_command(self, action, args=None):
        """تشغيل أوامر MTK بقوة محرك Penumbra وسيطرة الـ USB"""
        if args is None: args = []
        self.logger(f"🔥 Penumbra MTK Engine: {action}", "warning")
        
        penumbra_args = self.get_penumbra_args()
        cmd = [sys.executable, "-m", "mtk"] + penumbra_args + [action] + args
        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=None):
        """تشغيل أوامر شاومي باستخدام محرك Penumbra الجبار وسيطرة الـ USB"""
        if args is None: args = []
        self.logger(f"🔥 Penumbra Xiaomi Engine: {action}", "warning")
        
        script_path = os.path.join(self.penumbra_scripts, f"xiaomi_{action}.py")
        if not os.path.exists(script_path):
            script_path = os.path.join(self.penumbra_scripts, f"{action}.py")

        if os.path.exists(script_path):
            self.logger(f"🚀 Running Specialized Penumbra Script: {action}", "success")
            cmd = [sys.executable, script_path] + args
        else:
            self.logger(f"⚠️ Using Penumbra Core for Xiaomi {action}...", "info")
            penumbra_args = self.get_penumbra_args()
            if action == "bypass":
                cmd = [sys.executable, "-m", "mtk"] + penumbra_args + ["erase", "config"]
            else:
                cmd = [sys.executable, "-m", "mtk"] + penumbra_args + [action] + args
        
        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تفعيل قوة Penumbra وسيطرة الـ USB في عمليات سامسونج المستعصية"""
        self.logger(f"🔥 Penumbra Samsung Engine: {action}", "warning")
        adb_path = self.get_tool_path("adb")
        
        if action == "frp_adb":
            self.logger("🔓 Penumbra: Force Clearing FRP Security...", "success")
            def frp_task():
                try:
                    # أوامر Penumbra السرية لتخطي FRP بشكل صامت وقوي
                    cmds = [
                        [adb_path, "shell", "settings", "put", "secure", "user_setup_complete", "1"],
                        [adb_path, "shell", "settings", "put", "global", "device_provisioned", "1"],
                        [adb_path, "shell", "am", "start", "-n", "com.google.android.gsf.login/"],
                        [adb_path, "shell", "am", "start", "-n", "com.android.settings/.Settings"]
                    ]
                    for c in cmds:
                        subprocess.run(c, capture_output=True, timeout=5)
                    self.logger("✅ Penumbra: FRP Bypass Successful!", "success")
                except Exception as e:
                    self.logger(f"❌ Penumbra Error: {str(e)}", "error")
            threading.Thread(target=frp_task, daemon=True).start()
            return

        elif action == "mtp_browser":
            mtp_tool = self.get_tool_path("samsung_mtp")
            cmd = [mtp_tool, "-open", "https://www.youtube.com"]
            self._execute_async(cmd)
        else:
            self.logger(f"⚡ Executing {action} via Default Engine...", "info")

    def run_unisoc_command(self, action, args=None):
        if args is None: args = []
        self.logger(f"🚀 Unisoc Action: {action}", "warning")
        cli_path = os.path.join(BASE_DIR, "unisoc", "cli.py")
        cmd = [sys.executable, cli_path, action] + args
        self._execute_async(cmd)

    def _execute_async(self, cmd):
        def task():
            try:
                cmd_str = [str(c) for c in cmd]
                self.logger(f"Executing: {' '.join(cmd_str)}", "info")

                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                self.current_process = subprocess.Popen(
                    cmd_str,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )

                for line in self.current_process.stdout:
                    if line.strip(): self.logger(line.strip(), "info")

                self.current_process.wait()
                if self.current_process.returncode == 0:
                    self.logger("✅ SUCCESS: Operation completed.", "success")
                else:
                    self.logger(f"❌ FAILED: Exit code {self.current_process.returncode}", "error")
            except Exception as e:
                self.logger(f"🛑 Error: {str(e)}", "error")
            finally:
                self.current_process = None

        if self.current_process and self.current_process.poll() is None:
            self.logger("⚠️ Busy... Please wait.", "error")
            return

        threading.Thread(target=task, daemon=True).start()
