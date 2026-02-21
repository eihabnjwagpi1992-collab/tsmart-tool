
from auth import AuthManager
import sys

def test_login(email, password):
    auth = AuthManager()
    print(f"🔍 محاولة تسجيل الدخول لـ: {email}")
    success, message = auth.login(email, password)
    if success:
        print(f"✅ نجاح: {message}")
    else:
        print(f"❌ فشل: {message}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("الاستخدام: python test_auth_logic.py <email> <password>")
    else:
        test_login(sys.argv[1], sys.argv[2])
