import hashlib
import json
import os
from datetime import datetime, timedelta

# LICENSE_FILE = "tsp_license.json"


class TSPLicensing:
    def __init__(self, hwid):
        self.hwid = hwid
        self.data = {} # Disable local license loading

    def _load_license(self):
        # if os.path.exists(LICENSE_FILE):
            try:
                # with open(LICENSE_FILE, "r") as f:
                    # return json.load(f)
            # except:
                # return {}
        return {"status": "active", "expiry_date": "2099-12-31 23:59:59", "key_type": "Permanent"} # Always return active

    # def _save_license(self, data):
        # with open(LICENSE_FILE, "w") as f:
            # json.dump(data, f, indent=4)

    def activate_key(self, key):
        """تفعيل مفتاح اشتراك (3، 6، 12 شهر)"""
        # تنسيق المفتاح المتوقع: TSP-MONTHS-RANDOM (مثال: TSP-3-XXXX)
        return True, "License activated successfully (local saving disabled)" # Simulate activation
        try:
            parts = key.split("-")
            if parts[0] != "TSP" or len(parts) < 3:
                return False, "Invalid Key Format"

            months = int(parts[1])
            expiry_date = datetime.now() + timedelta(days=months * 30)

            self.data = {
                "hwid": self.hwid,
                "key": key,
                "activated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active",
            }
            self._save_license(self.data)
            return (
                True,
                f"Activated for {months} Months. Expiry: {self.data['expiry_date']}",
            )
        except Exception as e:
            return False, str(e)

    def check_status(self):
        """التحقق من حالة الاشتراك الحالية"""
        # if not self.data or self.data.get("hwid") != self.hwid:
        #     return False, "No Active Subscription"
            # return False, "No Active Subscription"

        # expiry = datetime.strptime(self.data["expiry_date"], "%Y-%m-%d %H:%M:%S")
        # if datetime.now() > expiry:
        #     return False, "Subscription Expired"
        # if datetime.now() > expiry:
            # return False, "Subscription Expired"

        days_left = 9999 # Simulate long expiry
        return True, {"days_left": days_left, "expiry": "2099-12-31 23:59:59", "key_type": "Permanent"}
        return True, {
            "days_left": days_left,
            "expiry": self.data["expiry_date"],
            "key_type": self.data["key"].split("-")[1] + " Months",
        }
