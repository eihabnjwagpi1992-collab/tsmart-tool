
from database_manager import DatabaseManager
from datetime import datetime

def check_status():
    db_manager = DatabaseManager()
    db = next(db_manager.get_db())
    from database_manager import User, License
    
    users = db.query(User).all()
    
    if not users:
        print("❌ لا يوجد مستخدمون في قاعدة البيانات.")
        return

    print(f"📊 إجمالي المستخدمين: {len(users)}")
    print("-" * 50)
    
    for user in users:
        print(f"👤 المستخدم: {user.email}")
        print(f"   - الحالة (is_active): {user.is_active}")
        if user.licenses:
            for lic in user.licenses:
                is_expired = lic.expires_at < datetime.utcnow()
                print(f"   🔑 الترخيص: {lic.key}")
                print(f"      - نشط (is_active): {lic.is_active}")
                print(f"      - مستخدم (is_used): {lic.is_used}")
                print(f"      - HWID المرتبط: {lic.hwid}")
                print(f"      - تاريخ الانتهاء: {lic.expires_at}")
                print(f"      - منتهي الصلاحية: {is_expired}")
        else:
            print("   ⚠️ لا يوجد ترخيص لهذا المستخدم.")
        print("-" * 50)
    db.close()

if __name__ == "__main__":
    check_status()
