
class AuthManager:
    def __init__(self):
        pass

    def login(self, email, password):
        # هذا مجرد منطق وهمي لتسجيل الدخول.
        # في التطبيق الحقيقي، ستقوم بالتحقق من قاعدة بيانات أو خدمة مصادقة.
        if email == "test@example.com" and password == "password":
            return True, "Login successful!"
        else:
            return False, "Invalid email or password."
