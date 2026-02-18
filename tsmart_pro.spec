# -*- mode: python ; coding: utf-8 -*-
# TSmart Pro Tool - Ultra Build Spec (v3.2.1)
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# التحقق من وجود الأيقونة (استخدام المسار النسبي لضمان التوافق مع GitHub Actions)
icon_name = "icon.ico"
icon_source = os.path.join("mtkclient", icon_name)
if not os.path.exists(icon_source):
    icon_source = None

# جمع بيانات customtkinter بشكل آلي وشامل
datas, binaries, hiddenimports = collect_all('customtkinter')

# إضافة الموارد الأساسية للمشروع
all_datas = datas + [
    ('mtkclient', 'mtkclient'),
    ('unisoc', 'unisoc'),
    ('penumbra', 'penumbra'),
    ('bin', 'bin'),
    ('drivers', 'drivers'),
    ('version.json', '.')
]

all_hiddenimports = hiddenimports + [
    'usb.backend.libusb1',
    'serial',
    'packaging',
    'packaging.version',
    'PIL._tkinter_finder',
    'wmi'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon=icon_source if icon_source else None,
)
