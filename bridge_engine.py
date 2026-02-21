
import os
import subprocess
import sys
import threading
import time

# دالة لجلب المسار الصحيح للموارد في بيئة PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# استخدام المسار الصحيح للمجلد الرئيسي
BASE_DIR = resource_path(".")
sys.path.append(os.path.join(BASE_DIR, "mtkclient"))
sys.path.append(os.path.join(BASE_DIR, "unisoc"))

class BridgeEngine:
    def __init__(self, logger_callback):
        self.logger = logger_callback
        self.current_process = None

    def get_tool_path(self, tool_name):
        """الحصول على المسار الصحيح للأداة (ADB/Fastboot/Heimdall)"""
        if os.name == 'nt':
            return os.path.join(BASE_DIR, "bin", f"{tool_name}.exe")
        else:
            return os.path.join(BASE_DIR, "bin", tool_name)

    def _get_penumbra_args(self):
        """جلب وسائط Penumbra لحقن DA و Auth Bypass"""
        injection_args = []
        penumbra_payloads = os.path.join(BASE_DIR, "penumbra", "core", "payloads")
        best_da = os.path.join(penumbra_payloads, "extloader_v6.bin")
        best_payload = os.path.join(penumbra_payloads, "hakujoudai.bin")

        if os.path.exists(best_da):
            self.logger(f"💉 Penumbra Engine: Injecting Smart DA ({os.path.basename(best_da)})", "success")
            injection_args.extend(["--da", best_da])
        
        if os.path.exists(best_payload):
            self.logger(f"🔓 Penumbra Engine: Injecting Auth Bypass Payload ({os.path.basename(best_payload)})", "success")
            injection_args.extend(["--payload", best_payload])
        
        if not injection_args:
            self.logger("⚠️ Penumbra assets not found, using default MTK loader", "info")
        
        return injection_args

    def run_mtk_command(self, action, args=None, wait_for_device=False):
        """تشغيل أوامر MTK مع حقن Penumbra آلياً للأجهزة الحديثة"""
        if args is None:
            args = []
        
        self.logger(f"🚀 Starting MTK Action: {action}", "warning")
        
        # استخدام Penumbra دائماً للأجهزة الحديثة
        injection_args = self._get_penumbra_args()

        if wait_for_device:
            self.logger("⏳ Turbo Mode Active: Waiting for BROM Port...", "info")

        # محاولة تشغيل mtkclient عبر المكتبة المدمجة
        python_exe = sys.executable if not sys.executable.endswith(".exe") else "python"
        # تعديل الاستدعاء ليكون عبر mtkclient.Library.mtk_main إذا كان mtk.py مفقوداً
        base_cmd = [python_exe, "-m", "mtkclient.Library.mtk_main"] + injection_args

        if action in ["frp_bypass", "BROM | ERASE FRP", "erase_frp"]:
            cmd = base_cmd + ["frp", "--disable-boot-auth"]
        elif action in ["factory_reset", "BROM | FACTORY RESET", "format_data"]:
            cmd = base_cmd + ["reset", "--factory-reset"]
        elif action in ["auth_bypass", "BROM | AUTH BYPASS"]:
            cmd = base_cmd + ["auth", "bypass"]
        elif action in ["unlock_bootloader", "BOOTLOADER | UNLOCK"]:
            cmd = base_cmd + ["bootloader", "unlock"]
        elif action == "read_info":
            cmd = base_cmd + ["info"]
        else:
            self.logger(f"❌ MTK action {action} not recognized.", "error")
            return

        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تشغيل أوامر سامسونج مع دعم Penumbra لمعالجات MTK"""
        self.logger(f"🚀 Starting Samsung Action: {action}", "warning")
        adb_path = self.get_tool_path("adb")
        mtp_tool = os.path.join(BASE_DIR, "bin", "samsung_mtp.exe") 

        # إذا كانت العملية تخص سامسونج MTK (مثل FRP BROM)
        if action == "samsung_mtk_frp":
            self.logger("📱 Samsung MTK detected! Using Penumbra for FRP Bypass...", "success")
            self.run_mtk_command("frp_bypass", wait_for_device=True)
            return

        if action == "mtp_browser":
            self.logger("🌐 Sending MTP Command to open Browser...", "info")
            cmd = [mtp_tool, "-open", "https://www.youtube.com"]
        
        elif action == "adb_enable":
            self.logger("📲 Step 1: Dial *#0*# on emergency call", "warning")
            cmd = [mtp_tool, "-at", "AT+KSTRNG=0,*#0*#", "-enable_adb"]
            
        elif action == "frp_adb":
            self.logger("🔓 Bypassing FRP via ADB...", "warning")
            cmds = [
                [adb_path, "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"],
                [adb_path, "shell", "am", "start", "-n", "com.google.android.gsf.login/"],
                [adb_path, "shell", "am", "start", "-n", "com.android.settings/.Settings"]
            ]
            for c in cmds:
                self._execute_async(c)
            return
        
        elif action == "read_info":
            cmd = [adb_path, "shell", "getprop"]

        else:
            self.logger(f"❌ Samsung action {action} not fully implemented.", "error")
            return

        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=None):
        """تشغيل أوامر Xiaomi باستخدام Penumbra Engine"""
        if args is None: args = []
        self.logger(f"🔥 Xiaomi Engine: {action}", "warning")
        
        # استخدام Penumbra دائماً لشاومي MTK
        self.run_mtk_command(action, args, wait_for_device=True)

    def run_adb_command(self, action, args=None):
        """تشغيل أوامر ADB/Fastboot"""
        if args is None: args = []
        self.logger(f"🔥 ADB/Fastboot Action: {action}", "warning")
        
        adb_path = self.get_tool_path("adb")
        fastboot_path = self.get_tool_path("fastboot")

        if action == "reboot_recovery":
            cmd = [adb_path, "reboot", "recovery"]
        elif action == "reboot_bootloader":
            cmd = [adb_path, "reboot", "bootloader"]
        elif action == "read_info":
            cmd = [adb_path, "shell", "getprop"]
        else:
            self.logger(f"❌ Unknown ADB/Fastboot action: {action}", "error")
            return
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=None):
        """تشغيل أوامر Unisoc"""
        if args is None: args = []
        self.logger(f"🚀 Unisoc Action: {action}", "warning")
        unisoc_main = os.path.join(BASE_DIR, "unisoc", "__main__.py")
        if not os.path.exists(unisoc_main):
            unisoc_main = os.path.join(BASE_DIR, "unisoc", "cli.py")
            
        if action == "frp_bypass":
            cmd = [sys.executable, "-u", unisoc_main, "frp"] + args
        elif action == "factory_reset":
            cmd = [sys.executable, "-u", unisoc_main, "reset"] + args
        else:
            self.logger(f"❌ Unisoc action {action} not recognized.", "error")
            return

        self._execute_async(cmd)

    def _execute_async(self, cmd):
        """تنفيذ الأوامر في الخلفية"""
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

                if self.current_process.stdout:
                    for line in self.current_process.stdout:
                        if line.strip():
                            self.logger(line.strip(), "info")

                self.current_process.wait()
                if self.current_process.returncode == 0:
                    self.logger("✅ SUCCESS: Operation completed.", "success")
                else:
                    self.logger(f"❌ FAILED: Exit code {self.current_process.returncode}", "error")
            except Exception as e:
                self.logger(f"🛑 CRITICAL ERROR: {str(e)}", "error")
            finally:
                self.current_process = None

        if self.current_process and self.current_process.poll() is None:
            self.logger("⚠️ Another operation is already running. Please wait.", "error")
            return

        threading.Thread(target=task, daemon=True).start()
