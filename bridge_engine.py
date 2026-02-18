import os
import subprocess
import sys
import threading


# إضافة مسارات المجلدات إلى sys.path لتمكين استيراد المكتبات مباشرة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "mtkclient"))
sys.path.append(os.path.join(BASE_DIR, "unisoc"))


class BridgeEngine:
    def __init__(self, logger_callback):
        self.logger = logger_callback
        self.current_process = None

    def run_mtk_command(self, action, args=None, use_custom_da=True, wait_for_device=False):
        """تشغيل أوامر MTK باستخدام مكتبة mtkclient مع حقن ملفات DA من Penumbra آلياً"""
        if args is None:
            args = []
        
        self.logger(f"🚀 Starting MTK Action: {action}", "warning")
        
        # إعداد بارامترات الحقن الذكي من Penumbra
        injection_args = []
        if wait_for_device:
            self.logger("⏳ Turbo Mode Active: Waiting for BROM Port...", "info")
            # mtkclient يدعم الانتظار تلقائياً إذا لم يجد المنفذ فوراً، لكننا سنضيف التنبيه
        
        if use_custom_da:
            penumbra_payloads = os.path.join(BASE_DIR, "penumbra", "core", "payloads")
            # اختيار أفضل ملف DA متاح (مثل extloader_v6.bin للأجهزة الحديثة)
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

        # بناء الأمر النهائي مع الحقن
        cmd = [sys.executable, "-m", "mtk"] + injection_args + [action] + args
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=None):
        """تشغيل أوامر Unisoc باستخدام مكتبة unisoc المدمجة"""
        if args is None:
            args = []
        self.logger(f"🚀 Starting Unisoc Action: {action}", "warning")
        cli_path = os.path.join(BASE_DIR, "unisoc", "cli.py")
        cmd = [sys.executable, cli_path, action] + args
        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=None):
        """تشغيل أوامر Xiaomi/Penumbra"""
        if args is None:
            args = []
        self.logger(f"🚀 Starting Xiaomi/Penumbra Action: {action}", "warning")

        # محاولة تشغيل سكريبتات Penumbra المساعدة
        script_path = os.path.join(BASE_DIR, "penumbra", "scripts", f"{action}.py")
        if os.path.exists(script_path):
            cmd = [sys.executable, script_path] + args
        else:
            # إذا لم يوجد سكريبت، نحاول استخدام mtkclient كبديل لعمليات Xiaomi المشتركة
            self.logger(f"⚠️ Penumbra script not found, falling back to MTK Engine for {action}", "info")
            if action == "bypass":
                cmd = [sys.executable, "-m", "mtk", "erase", "config"] # مثال لتجاوز Mi Cloud عبر مسح الـ config
            else:
                bin_path = os.path.join(BASE_DIR, "bin", "penumbra.exe")
                if os.path.exists(bin_path):
                    cmd = [bin_path, action] + args
                else:
                    self.logger(f"❌ Error: {action} module not integrated correctly.", "error")
                    return

        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تشغيل أوامر سامسونج (FRP, MTP, ADB)"""
        self.logger(f"🚀 Starting Samsung Action: {action}", "warning")
        adb_path = os.path.join(BASE_DIR, "bin", "adb.exe")
        mtp_tool = os.path.join(BASE_DIR, "bin", "samsung_mtp.exe") # أداة MTP افتراضية

        if action == "mtp_browser":
            self.logger("🌐 Sending MTP Command to open Browser...", "info")
            # استخدام أداة MTP لإرسال رابط يفتح اليوتيوب أو المتصفح
            cmd = [mtp_tool, "-open", "https://www.youtube.com"]
        
        elif action == "adb_enable":
            self.logger("📲 Step 1: Dial *#0*# on emergency call", "warning")
            self.logger("📲 Step 2: Waiting for ADB authorization prompt...", "info")
            # محاولة تفعيل ADB عبر ثغرة AT Commands
            cmd = [mtp_tool, "-at", "AT+KSTRNG=0,*#0*#", "-enable_adb"]
            
        elif action == "frp_adb":
            self.logger("🔓 Bypassing FRP via ADB...", "warning")
            # سلسلة أوامر ADB لتخطي FRP بشكل نهائي
            cmds = [
                [adb_path, "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"],
                [adb_path, "shell", "am", "start", "-n", "com.google.android.gsf.login/"],
                [adb_path, "shell", "am", "start", "-n", "com.android.settings/.Settings"]
            ]
            # تنفيذ سلسلة الأوامر
            for c in cmds:
                self._execute_async(c)
            return

        elif action == "flash" and files:
            # قسم Odin Mode - لم يتم المساس به
            self.logger("⚡ Entering Odin Mode Flash...", "info")
            fastboot_path = os.path.join(BASE_DIR, "bin", "fastboot.exe")
            cmd = [fastboot_path, "flash", "all"] 
        else:
            self.logger(f"❌ Samsung action {action} not fully implemented.", "error")
            return

        self._execute_async(cmd)

    def _execute_async(self, cmd):
        """تنفيذ الأوامر في الخلفية مع توجيه المخرجات للواجهة ومنع النوافذ المنبثقة"""
        def task():
            try:
                # التأكد من أن جميع عناصر cmd هي نصوص
                cmd_str = [str(c) for c in cmd]
                self.logger(f"Executing: {' '.join(cmd_str)}", "info")

                # إعدادات لمنع ظهور نافذة CMD سوداء على ويندوز
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

        # منع تشغيل أكثر من عملية في نفس الوقت
        if self.current_process and self.current_process.poll() is None:
            self.logger("⚠️ Another operation is already running. Please wait.", "error")
            return

        threading.Thread(target=task, daemon=True).start()
