import sys
import os
import subprocess
import threading

# إضافة مسارات المجلدات إلى sys.path لتمكين استيراد المكتبات مباشرة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "mtkclient"))
sys.path.append(os.path.join(BASE_DIR, "unisoc"))

class BridgeEngine:
    def __init__(self, logger_callback):
        self.logger = logger_callback

    def run_mtk_command(self, action, args=[]):
        """تشغيل أوامر MTK باستخدام مكتبة mtkclient المدمجة"""
        self.logger(f"Starting MTK Action: {action}", "info")
        # بدلاً من استدعاء EXE، سنستخدم python لتشغيل المكتبة كـ module
        cmd = [sys.executable, "-m", "mtk", action] + args
        self._execute_async(cmd)

    def run_unisoc_command(self, action, args=[]):
        """تشغيل أوامر Unisoc باستخدام مكتبة unisoc المدمجة"""
        self.logger(f"Starting Unisoc Action: {action}", "info")
        # تشغيل ملف cli.py الموجود في مجلد unisoc
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
        else:
            # افتراضياً، سنحاول البحث عن ملف ثنائي في مجلد bin
            bin_path = os.path.join(BASE_DIR, "bin", "penumbra.exe")
            cmd = [bin_path, action] + args
        
        self._execute_async(cmd)

    def _execute_async(self, cmd):
        def task():
            try:
                self.logger(f"Executing: {' '.join(cmd)}", "warning")
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    bufsize=1, 
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                for line in process.stdout:
                    if line.strip():
                        self.logger(line.strip(), "info")
                
                process.wait()
                if process.returncode == 0:
                    self.logger("SUCCESS: Operation completed.", "success")
                else:
                    self.logger(f"FAILED: Exit code {process.returncode}", "error")
            except Exception as e:
                self.logger(f"CRITICAL ERROR: {str(e)}", "error")

        threading.Thread(target=task, daemon=True).start()
