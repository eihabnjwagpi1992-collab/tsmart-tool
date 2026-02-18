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
                    if line.strip():
                        current_devices.append(f"[ADB] {line.strip()}")
            except:
                pass

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
            except:
                pass

            # 3. Scan COM Ports (MTK, SPD, Qualcomm)
            ports = serial.tools.list_ports.comports()
            for port in ports:
                desc = port.description.upper()
                if "MEDIATEK" in desc or "MTK" in desc:
                    current_devices.append(
                        f"[MTK PORT] {port.device} ({port.description})"
                    )
                elif "SPRD" in desc or "SPREADTRUM" in desc or "UNISOC" in desc:
                    current_devices.append(
                        f"[SPD PORT] {port.device} ({port.description})"
                    )
                elif "QUALCOMM" in desc or "9008" in desc:
                    current_devices.append(
                        f"[EDL PORT] {port.device} ({port.description})"
                    )
                elif "SAMSUNG" in desc:
                    current_devices.append(
                        f"[SAMSUNG PORT] {port.device} ({port.description})"
                    )
                else:
                    current_devices.append(
                        f"[COM PORT] {port.device} ({port.description})"
                    )

            if current_devices != self.last_devices:
                self.last_devices = current_devices
                self.callback(current_devices)

            # Turbo Mode: Scan every 100ms for fast-switching devices (Samsung BROM)
            # Normal Mode: Scan every 2s to save CPU
            time.sleep(0.1 if self.turbo_mode else 2)


def get_device_info(adb_path, serial_number):
    """جلب معلومات تفصيلية عن الجهاز عبر ADB"""
    info = {}
    try:
        # مثال لجلب الموديل وإصدار الأندرويد
        cmds = {
            "Model": "ro.product.model",
            "Brand": "ro.product.brand",
            "Android": "ro.build.version.release",
            "Security Patch": "ro.build.version.security_patch",
            "CPU": "ro.board.platform",
        }
        for label, prop in cmds.items():
            res = subprocess.run(
                [adb_path, "-s", serial_number, "shell", "getprop", prop],
                capture_output=True,
                text=True,
            )
            info[label] = res.stdout.strip()
    except:
        pass
    return info
