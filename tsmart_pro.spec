# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# --- Dependency Collection ---
def get_all_from(package_name):
    try:
        datas, binaries, hiddenimports = collect_all(package_name)
    except:
        datas, binaries, hiddenimports = [], [], []
    return datas, binaries, hiddenimports

# Collect Critical UI and System Libraries
ctk_datas, ctk_binaries, ctk_hidden = get_all_from('customtkinter')
pil_datas, pil_binaries, pil_hidden = get_all_from('Pillow')
wmi_datas, wmi_binaries, wmi_hidden = get_all_from('wmi')

# Resource Bundling
all_datas = ctk_datas + pil_datas + wmi_datas + [
    ('mtkclient', 'mtkclient'),
    ('unisoc', 'unisoc'),
    ('penumbra', 'penumbra'),
    ('bin', 'bin'),
    ('drivers', 'drivers'),
    ('version.json', '.'),
    ('logo.png', '.')
]

# Hidden Imports for Runtime Stability
all_hidden = ctk_hidden + pil_hidden + wmi_hidden + [
    'usb.backend.libusb1',
    'serial',
    'packaging',
    'packaging.version',
    'PIL._tkinter_finder',
    'win32timezone',
    'requests',
    'jsonrpc',
    'pyusb',
    'pyserial',
    'pywin32',
    'cryptography',
    'pycryptodome',
    'bridge_engine',
    'device_engine',
    'licensing',
    'security',
    'updater'
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=ctk_binaries + pil_binaries + wmi_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['keystone-engine', 'capstone'],
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
    icon=\'logo.png\',