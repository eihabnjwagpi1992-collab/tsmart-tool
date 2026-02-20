# -*- mode: python ; coding: utf-8 -*-
# TSmart Pro Tool - Ultimate Stable Spec (v3.2.5)
import os
import sys
import customtkinter

block_cipher = None
BASE_PATH = os.getcwd()
ctk_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    ['main.py'],
    pathex=[BASE_PATH],
    binaries=[],
    datas=[
        (ctk_path, 'customtkinter'),
        ('mtkclient', 'mtkclient'),
        ('unisoc', 'unisoc'),
        ('penumbra', 'penumbra'),
        ('bin', 'bin'),
        ('drivers', 'drivers'),
        ('version.json', '.'),
        ('bridge_engine.py', '.'),
        ('device_engine.py', '.'),
        ('updater.py', '.'),
        ('security.py', '.'),
        ('licensing.py', '.')
    ],
    hiddenimports=[
        'bridge_engine',
        'device_engine',
        'updater',
        'security',
        'licensing',
        'customtkinter',
        'PIL._tkinter_finder',
        'usb.backend.libusb1',
        'serial',
        'packaging',
        'packaging.version',
        'wmi',
        'pywin32',
        'win32timezone'
    ],
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
    icon=os.path.join('mtkclient', 'icon.ico') if os.path.exists(os.path.join('mtkclient', 'icon.ico')) else None,
)
