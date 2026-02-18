# -*- mode: python ; coding: utf-8 -*-
# TSmart Pro Tool - Hardened Build Spec (v3.2.2)
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# --- Smart Dependency Collection ---
def get_all_from(package_name):
    datas, binaries, hiddenimports = collect_all(package_name)
    return datas, binaries, hiddenimports

# تجميع المكتبات الحرجة
ctk_datas, ctk_binaries, ctk_hidden = get_all_from('customtkinter')
pil_datas, pil_binaries, pil_hidden = get_all_from('Pillow')
wmi_datas, wmi_binaries, wmi_hidden = get_all_from('wmi')

# دمج الموارد الأصلية
all_datas = ctk_datas + pil_datas + wmi_datas + [
    ('mtkclient', 'mtkclient'),
    ('unisoc', 'unisoc'),
    ('penumbra', 'penumbra'),
    ('bin', 'bin'),
    ('drivers', 'drivers'),
    ('version.json', '.')
]

# دمج الاستيرادات المخفية
all_hidden = ctk_hidden + pil_hidden + wmi_hidden + [
    'usb.backend.libusb1',
    'serial',
    'packaging',
    'packaging.version',
    'PIL._tkinter_finder',
    'win32timezone'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=ctk_binaries + pil_binaries + wmi_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['keystone-engine', 'capstone'], # استبعاد المسببات المحتملة للفشل إذا كانت غير موجودة
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tsmart_Pro_Tool_v3.2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('mtkclient', 'icon.ico') if os.path.exists(os.path.join('mtkclient', 'icon.ico')) else None,
)
