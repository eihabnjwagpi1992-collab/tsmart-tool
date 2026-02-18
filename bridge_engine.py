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

    def get_tool_path(self, tool_name):
        """الحصول على المسار الصحيح للأداة (ADB/Fastboot) بناءً على نظام التشغيل"""
        if os.name == 'nt':
            path = os.path.join(BASE_DIR, "bin", f"{tool_name}.exe")
        else:
            path = os.path.join(BASE_DIR, "bin", tool_name)
        
        if not os.path.exists(path):
            self.logger(f"⚠️ Warning: {tool_name} not found at {path}. Using system default.", "warning")
            return tool_name
        return path

    def run_mtk_command(self, action, args=None, use_custom_da=True, wait_for_device=True):
        """تشغيل أوامر MTK مع تحسين عملية الانتظار وحقن الـ DA"""
        if args is None: args = []
        self.logger(f"🚀 Starting MTK Action: {action}", "warning")
        
        injection_args = []
        if use_custom_da:
            penumbra_payloads = os.path.join(BASE_DIR, "penumbra", "core", "payloads")
            best_da = os.path.join(penumbra_payloads, "extloader_v6.bin")
            best_payload = os.path.join(penumbra_payloads, "hakujoudai.bin")
            
            if os.path.exists(best_da):
                self.logger(f"💉 Injecting Smart DA: {os.path.basename(best_da)}", "success")
                injection_args.extend(["--da", best_da])
            
            if os.path.exists(best_payload):
                self.logger(f"🔓 Injecting Auth Bypass: {os.path.basename(best_payload)}", "success")
                injection_args.extend(["--payload", best_payload])

        # استخدام mtkclient مباشرة عبر الوحدة النمطية
        cmd = [sys.executable, "-m", "mtk"] + injection_args + [action] + args
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=None):
        if args is None: args = []
        self.logger(f"🚀 Starting Unisoc Action: {action}", "warning")
        cli_path = os.path.join(BASE_DIR, "unisoc", "cli.py")
        cmd = [sys.executable, cli_path, action] + args
        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=None):
        if args is None: args = []
        self.logger(f"🚀 Starting Xiaomi/Penumbra Action: {action}", "warning")
        script_path = os.path.join(BASE_DIR, "penumbra", "scripts", f"{action}.py")
        
        if os.path.exists(script_path):
            cmd = [sys.executable, script_path] + args
        else:
            self.logger(f"⚠️ Script not found, using generic MTK engine for {action}", "info")
            if action == "bypass":
                cmd = [sys.executable, "-m", "mtk", "erase", "config"]
            else:
                bin_path = self.get_tool_path("penumbra")
                cmd = [bin_path, action] + args
        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تحسين أوامر سامسونج وتخطي FRP بشكل فعال"""
        self.logger(f"🚀 Starting Samsung Action: {action}", "warning")
        adb_path = self.get_tool_path("adb")
        mtp_tool = self.get_tool_path("samsung_mtp")

        if action == "mtp_browser":
            self.logger("🌐 Opening Browser via MTP...", "info")
            cmd = [mtp_tool, "-open", "https://www.youtube.com"]
        
        elif action == "adb_enable":
            self.logger("📲 Step 1: Dial *#0*# on device", "warning")
            self.logger("📲 Step 2: Click 'Allow ADB' on device screen", "info")
            cmd = [mtp_tool, "-enable_adb"]
            
        elif action == "frp_adb":
            self.logger("🔓 Attempting FRP Bypass via ADB...", "warning")
            # سلسلة أوامر محسنة لتخطي FRP
            def frp_task():
                try:
                    # 1. التحقق من اتصال ADB
                    res = subprocess.run([adb_path, "get-state"], capture_output=True, text=True)
                    if "device" not in res.stdout:
                        self.logger("❌ Device not found in ADB mode! Enable ADB first.", "error")
                        return

                    # 2. إرسال أوامر التخطي
                    cmds = [
                        [adb_path, "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"],
                        [adb_path, "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:device_provisioned", "--bind", "value:s:1"],
                        [adb_path, "shell", "am", "start", "-n", "com.google.android.gsf.login/"],
                        [adb_path, "shell", "am", "start", "-n", "com.android.settings/.Settings"]
                    ]
                    for c in cmds:
                        self.logger(f"Sending: {' '.join(c[1:])}", "info")
                        subprocess.run(c, capture_output=True)
                    
                    self.logger("✅ FRP Bypass Commands Sent! Check device.", "success")
                except Exception as e:
                    self.logger(f"❌ FRP Error: {str(e)}", "error")

            threading.Thread(target=frp_task, daemon=True).start()
            return

        elif action == "flash":
            self.logger("⚡ Entering Odin Mode Flash...", "info")
            fastboot_path = self.get_tool_path("fastboot")
            cmd = [fastboot_path, "flash", "all"]
        else:
            self.logger(f"❌ Action {action} not implemented.", "error")
            return

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
