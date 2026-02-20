# -*- mode: python ; coding: utf-8 -*-
# TSP TOOL PRO - Ultimate Suite Spec (v2.5.2)
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
        ('logo.png', '.'),
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
        'win32timezone',
        'requests',
        'dotenv',
        'PIL',
        'PIL.Image',
        'serial.tools',
        'serial.tools.list_ports'
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
    [],
    exclude_binaries=True,
    name='TSP_TOOL_PRO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TSP_TOOL_PRO_SUITE',
)
