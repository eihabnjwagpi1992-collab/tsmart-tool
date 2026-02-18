import os
import sys
import json
import requests
import zipfile
import shutil
import subprocess
import time
from packaging import version

# تعريف الإصدار الحالي (يتم تحديثه في كل نسخة جديدة)
CURRENT_VERSION = "2.6.0"
# رابط ملف الإصدار على GitHub (يجب تغييره لرابطك المباشر)
VERSION_URL = "https://raw.githubusercontent.com/eihabnjwagpi1992-collab/tsmart-tool/main/version.json"

class UpdateManager:
    def __init__(self, logger_callback=None):
        self.logger = logger_callback or print

    def check_for_updates(self):
        """التحقق من وجود تحديث جديد عبر مقارنة الإصدار الحالي مع السيرفر"""
        try:
            self.logger("🔍 Checking for updates...", "info")
            response = requests.get(VERSION_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("version", "1.0.0")
                
                # استخدام packaging.version للمقارنة الصحيحة
                if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                    self.logger(f"✨ New version available: {latest_version}", "success")
                    return data # إرجاع بيانات التحديث (رابط، سجل التغييرات)
                else:
                    self.logger("✅ You are using the latest version.", "success")
                    return None
            else:
                self.logger(f"⚠️ Could not check for updates (Status: {response.status_code})", "error")
                return None
        except Exception as e:
            self.logger(f"❌ Update check failed: {str(e)}", "error")
            return None

    def download_and_install(self, update_url):
        """تحميل التحديث وفك ضغطه واستبدال الملفات القديمة"""
        try:
            temp_zip = "update_package.zip"
            self.logger(f"📥 Downloading update from: {update_url}", "info")
            
            # تحميل الملف مع شريط تقدم (تبسيط)
            response = requests.get(update_url, stream=True)
            with open(temp_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger("📦 Extracting update package...", "info")
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall("update_temp")
            
            # حذف الملف المضغوط بعد الفك
            os.remove(temp_zip)
            
            self.logger("🛠️ Preparing to restart and apply update...", "warning")
            self._apply_and_restart()
            return True
        except Exception as e:
            self.logger(f"❌ Installation failed: {str(e)}", "error")
            return False

    def _apply_and_restart(self):
        """إنشاء سكريبت باتش (Windows) لاستبدال الملفات وإعادة التشغيل"""
        updater_script = "finish_update.bat"
        
        # الحصول على المسار الكامل للملف التنفيذي
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])
            
        exe_name = os.path.basename(exe_path)
        exe_dir = os.path.dirname(exe_path)
        
        # سكريبت الباتش يقوم بـ:
        # 1. الانتظار حتى يغلق البرنامج الحالي
        # 2. نسخ الملفات الجديدة من المجلد المؤقت للمجلد الرئيسي
        # 3. حذف المجلد المؤقت
        # 4. إعادة تشغيل البرنامج
        with open(updater_script, "w", encoding="utf-8") as f:
            f.write(f"""@echo off
timeout /t 2 /nobreak > nul
xcopy /s /y /i "update_temp\\*" "{exe_dir}"
rd /s /q "update_temp"
start "" "{exe_path}"
del "%~f0"
            """)
        
        # تشغيل السكريبت وإغلاق البرنامج الحالي فوراً
        subprocess.Popen([updater_script], shell=True)
        sys.exit(0)

if __name__ == "__main__":
    # للاختبار فقط
    mgr = UpdateManager()
    mgr.check_for_updates()
