import os
import subprocess
import threading
import time
import serial.tools.list_ports

class DeviceMonitor:
    def __init__(self, adb_path, fastboot_path, callback):
        self.adb_path = adb_path
        self.fastboot_path = fastboot_path
        self.callback = callback
        self.running = False
        self.turbo_mode = False
        self.usb_filter_enabled = True # تفعيل فلترة الـ USB بشكل افتراضي
        self.last_devices = []

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def set_turbo_mode(self, enabled):
        self.turbo_mode = enabled

    def set_usb_filter(self, enabled):
        self.usb_filter_enabled = enabled

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            current_devices = []

            # 1. Scan ADB Devices
            try:
                res = subprocess.run(
                    [self.adb_path, "devices"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                lines = res.stdout.strip().split("\n")[1:]
                for line in lines:
                    if "device" in line:
                        serial = line.split()[0]
                        current_devices.append(f"[ADB] {serial}")
            except: pass

            # 2. Scan Fastboot Devices
            try:
                res = subprocess.run(
                    [self.fastboot_path, "devices"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                lines = res.stdout.strip().split("\n")
                for line in lines:
                    if line.strip():
                        current_devices.append(f"[FASTBOOT] {line.strip()}")
            except: pass

            # 3. Smart COM Port Filtering (قوة الفلترة والسيطرة)
            ports = serial.tools.list_ports.comports()
            for port in ports:
                desc = port.description.upper()
                hwid = port.hwid.upper()
                
                # فلترة المنافذ غير الضرورية (مثل منافذ البلوتوث أو المنافذ الوهمية)
                if self.usb_filter_enabled:
                    if any(x in desc for x in ["BLUETOOTH", "STANDARD SERIAL", "LPT"]):
                        continue

                # التعرف الذكي على المنافذ بناءً على الـ HWID والـ Description
                if any(x in desc for x in ["MEDIATEK", "MTK", "VCOM", "PRELOADER"]) or "VID_0E8D" in hwid:
                    current_devices.append(f"[MTK PORT] {port.device} (Ready)")
                elif any(x in desc for x in ["SPRD", "SPREADTRUM", "UNISOC", "SCI", "DIAG"]) or "VID_1782" in hwid:
                    current_devices.append(f"[SPD PORT] {port.device} (Active)")
                elif any(x in desc for x in ["QUALCOMM", "9008", "QDLOADER", "HS-USB"]) or "VID_05C6" in hwid:
                    current_devices.append(f"[EDL PORT] {port.device} (Force Mode)")
                elif "SAMSUNG" in desc or "VID_04E8" in hwid:
                    current_devices.append(f"[SAMSUNG PORT] {port.device} (Connected)")
                elif "VID_18D1" in hwid: # Google/Android generic
                    current_devices.append(f"[USB DEBUG] {port.device}")
                else:
                    current_devices.append(f"[COM PORT] {port.device}")

            if current_devices != self.last_devices:
                self.last_devices = current_devices
                self.callback(current_devices)

            # سرعة المسح في الـ Turbo Mode (للسيطرة اللحظية على المداخل)
            time.sleep(0.1 if self.turbo_mode else 1.5)

def get_device_info(adb_path, serial_number):
    """جلب معلومات تفصيلية عن الجهاز عبر ADB مع السيطرة على الاستجابة"""
    info = {}
    try:
        res = subprocess.run([adb_path, "-s", serial_number, "get-state"], capture_output=True, text=True, timeout=2)
        if "device" not in res.stdout: return {"Status": "Offline"}

        props = {
            "Model": "ro.product.model",
            "Brand": "ro.product.brand",
            "Android": "ro.build.version.release",
            "Security": "ro.build.version.security_patch",
            "CPU": "ro.board.platform",
            "Serial": "ro.serialno"
        }
        
        for label, prop in props.items():
            res = subprocess.run([adb_path, "-s", serial_number, "shell", "getprop", prop], capture_output=True, text=True, timeout=3)
            val = res.stdout.strip()
            if val: info[label] = val
            
    except Exception: pass
    return info
