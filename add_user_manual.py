
import sys
from database_manager import DatabaseManager
from datetime import datetime, timedelta

def add_user_manually(email, password, duration_months=12):
    db_manager = DatabaseManager()
    
    # 1. التحقق مما إذا كان المستخدم موجوداً بالفعل
    existing_user = db_manager.get_user_by_email(email)
    if existing_user:
        print(f"⚠️ المستخدم {email} موجود بالفعل في قاعدة البيانات.")
        user = existing_user
    else:
        # 2. إنشاء مستخدم جديد
        user, msg = db_manager.create_user(email, password)
        if user:
            print(f"✅ تم إنشاء المستخدم بنجاح: {email}")
        else:
            print(f"❌ فشل إنشاء المستخدم: {msg}")
            return

    # 3. إضافة ترخيص فعال للمستخدم
    try:
        new_license = db_manager.create_license_for_user(user.id, duration_months)
        print(f"✅ تم توليد ترخيص جديد:")
        print(f"   - المفتاح: {new_license.key}")
        print(f"   - المدة: {duration_months} أشهر")
        print(f"   - تاريخ الانتهاء: {new_license.expires_at.strftime('%Y-%m-%d')}")
        print(f"\n🚀 يمكنك الآن تسجيل الدخول باستخدام:")
        print(f"   - البريد الإلكتروني: {email}")
        print(f"   - كلمة المرور: {password}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء إضافة الترخيص: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("استخدام السكريبت: python add_user_manual.py <email> <password>")
        print("مثال: python add_user_manual.py test@example.com 123456")
    else:
        email = sys.argv[1]
        password = sys.argv[2]
        add_user_manually(email, password)
