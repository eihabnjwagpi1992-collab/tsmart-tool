import hashlib
import subprocess
import os
import sys

def get_hwid():
    """توليد رقم تعريف فريد للجهاز بناءً على بصمة الهاردوير"""
    try:
        # استخدام رقم لوحة الأم أو UUID النظام
        if os.name == 'nt':
            cmd = "wmic csproduct get uuid"
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
        else:
            # للينكس (لأغراض الاختبار في الساندبوكس)
            uuid = os.popen('cat /etc/machine-id').read().strip()
        
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
            f.write(current_hwid) # تفعيل تلقائي لأول مرة
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
