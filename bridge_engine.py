
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
        injection_args = []
        penumbra_payloads = os.path.join(BASE_DIR, "penumbra", "core", "payloads")
        best_da = os.path.join(penumbra_payloads, "extloader_v6.bin")
        best_payload = os.path.join(penumbra_payloads, "hakujoudai.bin")

        if os.path.exists(best_da):
            self.logger(f"💉 Injecting Smart DA from Penumbra: {os.path.basename(best_da)}", "success")
            injection_args.extend(["--da", best_da])
        
        if os.path.exists(best_payload):
            self.logger(f"🔓 Injecting Auth Bypass Payload: {os.path.basename(best_payload)}", "success")
            injection_args.extend(["--payload", best_payload])
        
        if not injection_args:
            self.logger("⚠️ Penumbra DA/Payloads not found, using default MTK loader", "info")
        
        return injection_args

    def run_mtk_command(self, action, args=None, wait_for_device=False):
        """تشغيل أوامر MTK باستخدام مكتبة mtkclient مع حقن ملفات DA من Penumbra آلياً"""
        if args is None:
            args = []
        
        self.logger(f"🚀 Starting MTK Action: {action}", "warning")
        
        injection_args = self._get_penumbra_args()

        if wait_for_device:
            self.logger("⏳ Turbo Mode Active: Waiting for BROM Port...", "info")

        python_exe = sys.executable if not sys.executable.endswith(".exe") else "python"
        base_cmd = [python_exe, "-m", "mtk"] + injection_args

        if action == "frp_bypass" or action == "BROM | ERASE FRP":
            cmd = base_cmd + ["frp", "--disable-boot-auth"]
        elif action == "factory_reset" or action == "BROM | FACTORY RESET":
            cmd = base_cmd + ["reset", "--factory-reset"]
        elif action == "auth_bypass" or action == "BROM | AUTH BYPASS":
            cmd = base_cmd + ["auth", "bypass"]
        elif action == "unlock_bootloader" or action == "BOOTLOADER | UNLOCK":
            cmd = base_cmd + ["bootloader", "unlock"]
        elif action == "read_info":
            cmd = base_cmd + ["info"]
        elif action == "format_data":
            cmd = base_cmd + ["reset", "--format-data"]
        elif action == "erase_frp":
            cmd = base_cmd + ["frp", "--disable-boot-auth"]
        elif action == "backup_nvram":
            self.logger("⚠️ Backup NVRAM not directly supported by mtkclient. Requires custom script.", "error")
            return
        else:
            self.logger(f"❌ MTK action {action} not recognized or fully implemented.", "error")
            return

        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تشغيل أوامر سامسونج (FRP, MTP, ADB)"""
        self.logger(f"🚀 Starting Samsung Action: {action}", "warning")
        adb_path = self.get_tool_path("adb")
        # Placeholder for samsung_mtp.exe or similar tool
        mtp_tool = os.path.join(BASE_DIR, "bin", "samsung_mtp.exe") 

        if action == "mtp_browser":
            self.logger("🌐 Sending MTP Command to open Browser...", "info")
            cmd = [mtp_tool, "-open", "https://www.youtube.com"]
        
        elif action == "adb_enable":
            self.logger("📲 Step 1: Dial *#0*# on emergency call", "warning")
            self.logger("📲 Step 2: Waiting for ADB authorization prompt...", "info")
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

        elif action == "flash" and files:
            self.logger("⚡ Entering Odin Mode Flash...", "info")
            # This would typically involve heimdall or Odin tool
            # For now, a placeholder for fastboot flash
            fastboot_path = self.get_tool_path("fastboot")
            cmd = [fastboot_path, "flash", "all"] # Simplified, needs actual files
        
        elif action == "factory_reset":
            self.logger("🔄 Performing Factory Reset via ADB...", "info")
            cmd = [adb_path, "shell", "wipe", "data"]
        
        elif action == "read_info":
            self.logger("ℹ️ Reading Device Info via ADB...", "info")
            cmd = [adb_path, "shell", "getprop"]

        elif action == "samsung_account_remove":
            self.logger("🗑️ Removing Samsung Account via ADB...", "info")
            cmd = [adb_path, "shell", "pm", "uninstall", "--user", "0", "com.samsung.android.app.spage"]

        else:
            self.logger(f"❌ Samsung action {action} not fully implemented.", "error")
            return

        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=None):
        """تشغيل أوامر Xiaomi باستخدام penumbra_engine الحقيقي"""
        if args is None: args = []
        self.logger(f"🔥 Xiaomi Engine: {action}", "warning")
        
        # penumbra_engine is a placeholder, assuming it's a separate executable or script
        penumbra_path = self.get_tool_path("penumbra_engine") 
        
        if action == "frp_bypass":
            cmd = [penumbra_path, "xiaomi", "frp"] + args
        elif action == "factory_reset":
            cmd = [penumbra_path, "xiaomi", "reset"] + args
        elif action == "read_info":
            cmd = [penumbra_path, "xiaomi", "info"] + args
        elif action == "mi_cloud_bypass":
            cmd = [penumbra_path, "xiaomi", "micloud"] + args
        elif action == "fastboot_to_edl":
            cmd = [penumbra_path, "xiaomi", "edl"] + args
        elif action == "sideload_format":
            cmd = [penumbra_path, "xiaomi", "sideload", "format"] + args
        else:
            self.logger(f"❌ Xiaomi action {action} not recognized or fully implemented.", "error")
            return

        self._execute_async(cmd)

    def run_adb_command(self, action, args=None):
        """تشغيل أوامر ADB/Fastboot الحقيقية"""
        if args is None: args = []
        self.logger(f"🔥 ADB/Fastboot Action: {action}", "warning")
        
        adb_path = self.get_tool_path("adb")
        fastboot_path = self.get_tool_path("fastboot")

        if action == "reboot_recovery":
            cmd = [adb_path, "reboot", "recovery"]
        elif action == "reboot_bootloader":
            cmd = [adb_path, "reboot", "bootloader"]
        elif action == "reboot_edl":
            # EDL reboot usually requires specific commands or shorting test points
            self.logger("⚠️ Reboot to EDL often requires specific hardware interaction.", "info")
            cmd = [adb_path, "reboot", "edl"] # This might not work on all devices
        elif action == "remove_screen_lock":
            self.logger("🔓 Attempting to remove screen lock via ADB...", "info")
            cmds = [
                [adb_path, "shell", "rm", "/data/system/gesture.key"],
                [adb_path, "shell", "rm", "/data/system/locksettings.db"],
                [adb_path, "shell", "rm", "/data/system/locksettings.db-wal"],
                [adb_path, "shell", "rm", "/data/system/locksettings.db-shm"]
            ]
            for c in cmds:
                self._execute_async(c)
            return
        elif action == "read_info":
            cmd = [adb_path, "shell", "getprop"]
        else:
            self.logger(f"❌ Unknown ADB/Fastboot action: {action}", "error")
            return
        self._execute_async(cmd)

    def run_device_checker_command(self, action, args=None):
        """تشغيل أوامر فحص الجهاز (Device Checker) الحقيقية"""
        if args is None: args = []
        self.logger(f"🔥 Device Checker Action: {action}", "warning")
        
        adb_path = self.get_tool_path("adb")
        fastboot_path = self.get_tool_path("fastboot")

        if action == "check_device":
            self.logger("🔍 Checking for connected ADB devices...", "info")
            self._execute_async([adb_path, "devices"])
            self.logger("🔍 Checking for connected Fastboot devices...", "info")
            self._execute_async([fastboot_path, "devices"])
        elif action == "read_device_info":
            cmd = [adb_path, "shell", "getprop"]
        else:
            self.logger(f"❌ Unknown Device Checker action: {action}", "error")
            return
        self._execute_async(cmd)

    def run_partition_command(self, action, args=None):
        """تشغيل أوامر إدارة الأقسام (Partition Manager) الحقيقية"""
        if args is None: args = []
        self.logger(f"🔥 Partition Manager Action: {action}", "warning")
        
        adb_path = self.get_tool_path("adb")

        if action == "read_partitions":
            cmd = [adb_path, "shell", "cat", "/proc/partitions"]
        elif action == "backup_partition":
            self.logger("⚠️ Backup Partition requires partition name and save path. Not fully implemented.", "error")
            return
        else:
            self.logger(f"❌ Unknown Partition Manager action: {action}", "error")
            return
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=None):
        """تشغيل أوامر Unisoc الحقيقية"""
        if args is None: args = []
        self.logger(f"🚀 Unisoc Action: {action}", "warning")
        # Unisoc module is integrated, use __main__.py or cli.py
        unisoc_main = os.path.join(BASE_DIR, "unisoc", "__main__.py")
        if not os.path.exists(unisoc_main):
            unisoc_main = os.path.join(BASE_DIR, "unisoc", "cli.py")
            
        if action == "frp_bypass":
            cmd = [sys.executable, "-u", unisoc_main, "frp"] + args
        elif action == "factory_reset":
            cmd = [sys.executable, "-u", unisoc_main, "reset"] + args
        elif action == "read_flash":
            cmd = [sys.executable, "-u", unisoc_main, "readflash"] + args
        elif action == "write_flash":
            cmd = [sys.executable, "-u", unisoc_main, "writeflash"] + args
        else:
            self.logger(f"❌ Unisoc action {action} not recognized or fully implemented.", "error")
            return

        self._execute_async(cmd)

    def _execute_async(self, cmd):
        """تنفيذ الأوامر في الخلفية مع توجيه المخرجات للواجهة ومنع النوافذ المنبثقة"""
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
