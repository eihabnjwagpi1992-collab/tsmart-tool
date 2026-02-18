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
        self.last_devices = []

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def set_turbo_mode(self, enabled):
        self.turbo_mode = enabled

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

            # 3. Scan COM Ports
            ports = serial.tools.list_ports.comports()
            for port in ports:
                desc = port.description.upper()
                if any(x in desc for x in ["MEDIATEK", "MTK", "VCOM"]):
                    current_devices.append(f"[MTK PORT] {port.device}")
                elif any(x in desc for x in ["SPRD", "SPREADTRUM", "UNISOC", "SCI"]):
                    current_devices.append(f"[SPD PORT] {port.device}")
                elif any(x in desc for x in ["QUALCOMM", "9008", "QDLOADER"]):
                    current_devices.append(f"[EDL PORT] {port.device}")
                elif "SAMSUNG" in desc:
                    current_devices.append(f"[SAMSUNG PORT] {port.device}")
                else:
                    current_devices.append(f"[COM PORT] {port.device}")

            if current_devices != self.last_devices:
                self.last_devices = current_devices
                self.callback(current_devices)

            time.sleep(0.2 if self.turbo_mode else 2)

def get_device_info(adb_path, serial_number):
    """جلب معلومات تفصيلية عن الجهاز عبر ADB مع معالجة أفضل للأخطاء"""
    info = {}
    try:
        # التحقق من أن الجهاز ما زال متصلاً
        res = subprocess.run([adb_path, "-s", serial_number, "get-state"], capture_output=True, text=True)
        if "device" not in res.stdout:
            return {"Error": "Device Offline"}

        props = {
            "Model": "ro.product.model",
            "Brand": "ro.product.brand",
            "Android": "ro.build.version.release",
            "Security": "ro.build.version.security_patch",
            "CPU": "ro.board.platform",
            "Carrier": "ro.carrier",
            "IMEI": "gsm.serial"
        }
        
        for label, prop in props.items():
            res = subprocess.run(
                [adb_path, "-s", serial_number, "shell", "getprop", prop],
                capture_output=True,
                text=True,
                timeout=5
            )
            val = res.stdout.strip()
            if val: info[label] = val
        
        if not info: info["Status"] = "Online (No info available)"
    except Exception as e:
        info["Error"] = str(e)
    return info
