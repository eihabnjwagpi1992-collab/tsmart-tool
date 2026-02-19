import hashlib
import os
import subprocess
import sys


def get_hwid():
    """توليد رقم تعريف فريد للجهاز بناءً على بصمة الهاردوير"""
    try:
        # استخدام رقم لوحة الأم أو UUID النظام
        if os.name == "nt":
            # استخدام PowerShell بدلاً من wmic المهمل في Windows 11
            try:
                cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
                uuid = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
            except:
                # خطة احتياطية باستخدام wmic
                try:
                    cmd = "wmic csproduct get uuid"
                    uuid = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().split("\n")[1].strip()
                except:
                    # خطة أخيرة باستخدام اسم الجهاز
                    uuid = os.environ.get('COMPUTERNAME', 'UNKNOWN') + os.environ.get('USERNAME', 'USER')
        else:
            # للينكس والماك
            try:
                uuid = open("/etc/machine-id").read().strip()
            except:
                uuid = subprocess.check_output(["hostname"]).decode().strip()

        return hashlib.sha256(uuid.encode()).hexdigest().upper()[:16]
    except:
        return "UNKNOWN-HWID-0000"


def verify_license():
    """التحقق من ترخيص الأداة (محاكاة لنظام حقيقي)"""
    current_hwid = get_hwid()
    # في نظام حقيقي، يتم التحقق من السيرفر هنا
    # سنقوم بإنشاء ملف محلي للترخيص لأغراض العرض
    license_file = "license.key"
    if not os.path.exists(license_file):
        with open(license_file, "w") as f:
            f.write(current_hwid)  # تفعيل تلقائي لأول مرة
        return True, current_hwid

    with open(license_file, "r") as f:
        saved_hwid = f.read().strip()

    if saved_hwid == current_hwid:
        return True, current_hwid
    else:
        return False, current_hwid


def protect_code():
    """تعليمات لاستخدام PyArmor لتشفير الكود"""
    # هذا التابع يوضح كيفية التشفير برمجياً
    # pyarmor gen main.py
    pass
