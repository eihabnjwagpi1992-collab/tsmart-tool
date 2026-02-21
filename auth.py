
from datetime import datetime
from database_manager import DatabaseManager
from hwid_utils import generate_hwid

class AuthManager:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def login(self, email, password):
        user = self.db_manager.get_user_by_email(email)

        if not user or not user.check_password(password):
            return False, "Invalid email or password."

        if not user.is_active:
            return False, "User account is inactive. Please contact support."

        # Generate the HWID for the current machine
        current_hwid = generate_hwid()

        # Check for an active license and validate HWID
        valid_license = None
        for license in user.licenses:
            if license.is_active and license.expires_at > datetime.utcnow():
                # First time activation for this license
                if not license.hwid:
                    self.db_manager.bind_hwid_to_license(license.key, current_hwid)
                    valid_license = license
                    break
                # HWID matches, allow login
                elif license.hwid == current_hwid:
                    valid_license = license
                    break
                # HWID does not match
                else:
                    return False, f"License is already in use on another device.\nHWID: {license.hwid[:16]}..."
        
        if not valid_license:
            return False, "No active and valid license found for this account. Please purchase a license."

        return True, f"Login successful! Welcome, {user.email}."
