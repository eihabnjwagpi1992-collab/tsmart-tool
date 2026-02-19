import os
import subprocess
import sys
import threading
import time

# إضافة مسارات المجلدات إلى sys.path لتمكين استيراد المكتبات مباشرة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# تصحيح المسارات لتشمل المجلدات الصحيحة
sys.path.append(os.path.join(BASE_DIR, "mtkclient"))
sys.path.append(os.path.join(BASE_DIR, "unisoc"))

class BridgeEngine:
    def __init__(self, logger_callback):
        self.logger = logger_callback
        self.current_process = None
        self.penumbra_dir = os.path.join(BASE_DIR, "penumbra")
        self.penumbra_payloads = os.path.join(self.penumbra_dir, "core", "payloads")
        self.penumbra_scripts = os.path.join(self.penumbra_dir, "scripts")
        self.usb_force_mode = True 

<<<<<<< HEAD
    def run_mtk_command(self, action, args=[]):
        """تشغيل أوامر MTK باستخدام مكتبة mtkclient المدمجة"""
        self.logger(f"Starting MTK Action: {action}", "info")
        # بدلاً من استدعاء EXE، سنستخدم python لتشغيل المكتبة كـ module
        cmd = [sys.executable, "-m", "mtk", action] + args
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=[]):
        """تشغيل أوامر Unisoc باستخدام مكتبة unisoc المدمجة"""
        self.logger(f"Starting Unisoc Action: {action}", "info")
        
        if action == "frp_diag":
            # محاكاة تشغيل FRP عبر Diag Mode (غالباً عبر بروتوكول AT أو Diag)
            self.logger("Connecting to Unisoc Diag Port...", "warning")
            cmd = [sys.executable, "-m", "mtk", "erase", "frp"] # استخدام محرك mtk كمحرك بديل لعمليات المسح حالياً
        elif action == "frp_flash":
            # محاكاة تشغيل FRP عبر Flash Mode (غالباً عبر بروتوكول Spreadtrum Flash)
            self.logger("Connecting to Unisoc Flash Port...", "warning")
            cmd = [sys.executable, "-m", "mtk", "erase", "frp"]
        else:
            # تشغيل ملف cli.py الموجود في مجلد unisoc (لعمليات Unlock/Lock)
            cli_path = os.path.join(BASE_DIR, "unisoc", "cli.py")
            cmd = [sys.executable, cli_path, action] + args
            
        self._execute_async(cmd)

    def run_xiaomi_command(self, action, args=[]):
        """تشغيل أوامر Xiaomi/Penumbra"""
        self.logger(f"Starting Xiaomi Action: {action}", "info")
        # Penumbra مكتوبة بـ Rust، لذا سنحاول تشغيلها كـ binary إذا كانت مبنية
        # أو استخدام سكريبتات الـ python المساعدة في مجلد penumbra/scripts
        script_path = os.path.join(BASE_DIR, "penumbra", "scripts", f"{action}.py")
        if os.path.exists(script_path):
            cmd = [sys.executable, script_path] + args
=======
    def get_tool_path(self, tool_name):
        """الحصول على المسار الصحيح للأداة (ADB/Fastboot/Heimdall)"""
        if os.name == 'nt':
            path = os.path.join(BASE_DIR, "bin", f"{tool_name}.exe")
>>>>>>> 83948c17ad36592085fb39a94329b80a405abf10
        else:
            path = os.path.join(BASE_DIR, "bin", tool_name)
        
        if not os.path.exists(path):
            return tool_name
        return path

    def run_mtk_command(self, action, args=None):
        """تشغيل أوامر MTK باستخدام mtkclient الحقيقي"""
        if args is None: args = []
        self.logger(f"🔥 MTK Engine: {action}", "warning")
        
        # استخدام mtk_main.py الموجود داخل Library كمدخل للمحرك
        mtk_main = os.path.join(BASE_DIR, "mtkclient", "Library", "mtk_main.py")
        if not os.path.exists(mtk_main):
            # محاولة البحث عن أي مدخل آخر إذا لم يوجد
            mtk_main = os.path.join(BASE_DIR, "mtkclient", "mtk.py")

        cmd = [sys.executable, mtk_main, action] + args
        self._execute_async(cmd)

    def run_samsung_command(self, action, files=None):
        """تفعيل عمليات سامسونج الحقيقية"""
        self.logger(f"🔥 Samsung Engine: {action}", "warning")
        adb_path = self.get_tool_path("adb")
        heimdall_path = self.get_tool_path("heimdall")
        
        if action == "flash":
            if not files:
                self.logger("❌ No files selected for flashing!", "error")
                return
            
            self.logger("🚀 Starting Real Flash via Heimdall...", "success")
            # بناء أمر التفليش الحقيقي (مثال مبسط لـ Heimdall)
            cmd = [heimdall_path, "flash"]
            for part, path in files.items():
                if path: cmd.extend([f"--{part}", path])
            self._execute_async(cmd)

        elif action == "frp_brom":
            self.logger("🔓 Attempting BROM FRP Bypass...", "warning")
            # استدعاء penumbra_engine للقيام بالمهمة الصعبة
            penumbra_path = self.get_tool_path("penumbra_engine")
            da_path = os.path.join(BASE_DIR, "bin", "da_samsung.bin")
            cmd = [penumbra_path, "erase", "--da", da_path, "frp"]
            self._execute_async(cmd)
            
        elif action == "frp_adb":
            self.logger("🔓 Clearing FRP via ADB...", "info")
            cmd = [adb_path, "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"]
            self._execute_async(cmd)

    def run_unisoc_command(self, action, args=None):
        """تشغيل أوامر Unisoc الحقيقية"""
        if args is None: args = []
        self.logger(f"🚀 Unisoc Action: {action}", "warning")
        # Unisoc موديول مدمج، نستخدم __main__.py أو cli.py
        unisoc_main = os.path.join(BASE_DIR, "unisoc", "__main__.py")
        if not os.path.exists(unisoc_main):
            unisoc_main = os.path.join(BASE_DIR, "unisoc", "cli.py")
            
        cmd = [sys.executable, unisoc_main, action] + args
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
