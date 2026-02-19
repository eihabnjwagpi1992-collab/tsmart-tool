import os
import sys
import json
import requests
import zipfile
import shutil
import subprocess
import time
from packaging import version

# تعريف الإصدار الحالي
CURRENT_VERSION = "2.6.0"
# رابط ملف الإصدار على GitHub
VERSION_URL = "https://raw.githubusercontent.com/eihabnjwagpi1992-collab/tsmart-tool/main/version.json"

class UpdateManager:
    def __init__(self, logger_callback=None):
        self.logger = logger_callback or print

    def check_for_updates(self):
        """التحقق من وجود تحديث جديد"""
        try:
            response = requests.get(VERSION_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("version", "1.0.0")
                
                if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                    return data
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    def download_and_install(self, update_url):
        """تحميل التحديث وتثبيته في الخلفية"""
        try:
            temp_zip = "update_package.zip"
            self.logger(f"📥 Downloading update...", "info")
            
            response = requests.get(update_url, stream=True, timeout=30)
            with open(temp_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger("📦 Extracting update...", "info")
            if os.path.exists("update_temp"):
                shutil.rmtree("update_temp")
            
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall("update_temp")
            
            os.remove(temp_zip)
            
            self.logger("🛠️ Applying update... The tool will restart.", "warning")
            self._apply_and_restart()
            return True
        except Exception as e:
            self.logger(f"❌ Installation failed: {str(e)}", "error")
            return False

    def _apply_and_restart(self):
        """إنشاء سكريبت باتش لاستبدال الملفات وإعادة التشغيل"""
        updater_script = "finish_update.bat"
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])
            
        exe_dir = os.path.dirname(exe_path)
        
        with open(updater_script, "w", encoding="utf-8") as f:
            f.write(f"""@echo off
timeout /t 2 /nobreak > nul
xcopy /s /y /i "update_temp\\*" "{exe_dir}"
rd /s /q "update_temp"
start "" "{exe_path}"
del "%~f0"
            """)
        
        subprocess.Popen([updater_script], shell=True)
        os._exit(0) # استخدام خروج قسري لضمان إغلاق كافة الخيوط
