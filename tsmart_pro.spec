# -*- mode: python ; coding: utf-8 -*-
# TSmart Pro Tool - PyInstaller Spec File (v3.1.0)
# هذا الملف يحل مشاكل البناء مع customtkinter والأيقونات

import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# تحديد مسار الأيقونة الصحيح
icon_path = os.path.join('mtkclient', 'icon.ico')

# جمع جميع ملفات customtkinter
customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all('customtkinter')

# جمع ملفات الموارد الأصلية
all_datas = [
    ('mtkclient', 'mtkclient'),
    ('unisoc', 'unisoc'),
    ('penumbra', 'penumbra'),
    ('bin', 'bin'),
    ('drivers', 'drivers'),
    ('version.json', '.'),
    (icon_path, '.') # دمج الأيقونة في المجلد الرئيسي للـ EXE
]
all_datas += customtkinter_datas

all_hiddenimports = [
    'customtkinter',
    'PIL._tkinter_finder',
    'usb.backend.libusb1',
    'serial',
    'packaging',
    'packaging.version',
]
all_hiddenimports += customtkinter_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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
    name='Tsmart_Pro_Tool_v3.1',
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
    icon=icon_path, # تعيين الأيقونة للملف التنفيذي
)
