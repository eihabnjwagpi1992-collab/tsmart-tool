
# device_data.py

# بيانات الرقائق المدعومة
CHIP_DATA = {
    "MT6765": {"name": "Helio P35/G35", "models": ["Redmi 9A", "Realme 3", "Oppo A9"]},
    "MT6768": {"name": "Helio P65/G85", "models": ["Redmi Note 9", "Realme 6i"]},
    "MT6785": {"name": "Helio G90T", "models": ["Redmi Note 8 Pro"]},
    "MT6761": {"name": "Helio A22", "models": ["Samsung A10s", "Realme C2"]},
    "MT6739": {"name": "Helio A22", "models": ["Samsung A01 Core", "Redmi 6A"]},
    "MT6833": {"name": "Dimensity 700", "models": ["Realme 8 5G", "Redmi Note 10 5G"]},
    "MT6877": {"name": "Dimensity 900", "models": ["Oppo Reno6 5G"]},
    "MT6893": {"name": "Dimensity 1200", "models": ["Realme GT Neo", "Redmi K40 Gaming"]},
    # أضف المزيد من الرقائق هنا بناءً على القائمة التي قدمتها
}

# بيانات العلامات التجارية والأجهزة المدعومة والعمليات
BRAND_DATA = {
    "SAMSUNG": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info", "Flash Firmware"]},
            "A10s (MT6761)": {"chip": "MT6761", "operations": ["FRP Bypass", "Factory Reset"]},
            "A01 Core (MT6739)": {"chip": "MT6739", "operations": ["FRP Bypass", "Factory Reset"]},
            # أضف المزيد من موديلات سامسونج هنا
        },
        "operations": {
            "FRP Bypass": "run_samsung_command(\"frp_adb\")",
            "Factory Reset": "run_samsung_command(\"factory_reset\")",
            "Read Info": "run_samsung_command(\"read_info\")",
            "Flash Firmware": "run_samsung_command(\"flash\")",
            "MTP Browser": "run_samsung_command(\"mtp_browser\")",
            "ADB Enable": "run_samsung_command(\"adb_enable\")",
            "Samsung Account Remove": "run_samsung_command(\"samsung_account_remove\")",
        }
    },
    "XIAOMI": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info", "Mi Cloud Bypass"]},
            "Redmi Note 8 Pro (MT6785)": {"chip": "MT6785", "operations": ["FRP Bypass", "Mi Cloud Bypass"]},
            "Redmi 9A/9C (MT6765)": {"chip": "MT6765", "operations": ["FRP Bypass", "Factory Reset"]},
            # أضف المزيد من موديلات شاومي هنا
        },
        "operations": {
            "FRP Bypass": "run_xiaomi_command(\"frp_bypass\")",
            "Factory Reset": "run_xiaomi_command(\"factory_reset\")",
            "Read Info": "run_xiaomi_command(\"read_info\")",
            "Mi Cloud Bypass": "run_xiaomi_command(\"mi_cloud_bypass\")",
            "Fastboot to EDL": "run_xiaomi_command(\"fastboot_to_edl\")",
            "Sideload Format": "run_xiaomi_command(\"sideload_format\")",
        }
    },
    "REALME": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info"]},
            "Realme 8 5G (MT6833)": {"chip": "MT6833", "operations": ["FRP Bypass", "Factory Reset"]},
            # أضف المزيد من موديلات ريلمي هنا
        },
        "operations": {
            "FRP Bypass": "run_mtk_command(\"frp_bypass\")",
            "Factory Reset": "run_mtk_command(\"factory_reset\")",
            "Read Info": "run_mtk_command(\"read_info\")",
        }
    },
    "OPPO": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info"]},
            "Oppo Reno6 5G (MT6877)": {"chip": "MT6877", "operations": ["FRP Bypass", "Factory Reset"]},
            # أضف المزيد من موديلات اوبو هنا
        },
        "operations": {
            "FRP Bypass": "run_mtk_command(\"frp_bypass\")",
            "Factory Reset": "run_mtk_command(\"factory_reset\")",
            "Read Info": "run_mtk_command(\"read_info\")",
        }
    },
    "VIVO": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info"]},
            # أضف المزيد من موديلات فيفو هنا
        },
        "operations": {
            "FRP Bypass": "run_mtk_command(\"frp_bypass\")",
            "Factory Reset": "run_mtk_command(\"factory_reset\")",
            "Read Info": "run_mtk_command(\"read_info\")",
        }
    },
    "V-SMART": {
        "models": {
            "Universal MTK": {"chip": "MTK Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Info"]},
            # أضف المزيد من موديلات في-سمارت هنا
        },
        "operations": {
            "FRP Bypass": "run_mtk_command(\"frp_bypass\")",
            "Factory Reset": "run_mtk_command(\"factory_reset\")",
            "Read Info": "run_mtk_command(\"read_info\")",
        }
    },
    "SPREADTRUM": {
        "models": {
            "Universal Unisoc": {"chip": "Unisoc Universal", "operations": ["FRP Bypass", "Factory Reset", "Read Flash", "Write Flash"]},
            # أضف المزيد من موديلات سبريدتروم هنا
        },
        "operations": {
            "FRP Bypass": "run_unisoc_command(\"frp_bypass\")",
            "Factory Reset": "run_unisoc_command(\"factory_reset\")",
            "Read Flash": "run_unisoc_command(\"read_flash\")",
            "Write Flash": "run_unisoc_command(\"write_flash\")",
        }
    },
    "MTK": {
        "models": {
            "Universal BROM": {"chip": "MTK Universal", "operations": ["BROM | ERASE FRP", "BROM | FACTORY RESET", "BROM | AUTH BYPASS", "BOOTLOADER | UNLOCK", "Read Info"]},
            # أضف المزيد من موديلات MTK هنا
        },
        "operations": {
            "BROM | ERASE FRP": "run_mtk_command(\"frp_bypass\")",
            "BROM | FACTORY RESET": "run_mtk_command(\"factory_reset\")",
            "BROM | AUTH BYPASS": "run_mtk_command(\"auth_bypass\")",
            "BOOTLOADER | UNLOCK": "run_mtk_command(\"unlock_bootloader\")",
            "Read Info": "run_mtk_command(\"read_info\")",
            "Format Data": "run_mtk_command(\"format_data\")",
            "Erase FRP": "run_mtk_command(\"erase_frp\")",
            "Unlock Bootloader": "run_mtk_command(\"unlock_bootloader\")",
            "Backup NVRAM": "run_mtk_command(\"backup_nvram\")",
        }
    },
    "ADB_FASTBOOT": {
        "models": {
            "Universal Android": {"chip": "Android Universal", "operations": ["Reboot to Recovery", "Reboot to Bootloader", "Reboot to EDL", "Remove Screen Lock", "Read Info"]},
        },
        "operations": {
            "Reboot to Recovery": "run_adb_command(\"reboot_recovery\")",
            "Reboot to Bootloader": "run_adb_command(\"reboot_bootloader\")",
            "Reboot to EDL": "run_adb_command(\"reboot_edl\")",
            "Remove Screen Lock": "run_adb_command(\"remove_screen_lock\")",
            "Read Info": "run_adb_command(\"read_info\")",
        }
    },
    "UTILITIES": {
        "models": {
            "General": {"chip": "N/A", "operations": ["Device Checker", "Partition Manager", "Update Tool"]},
        },
        "operations": {
            "Device Checker": "run_device_checker_command(\"check_device\")",
            "Partition Manager": "run_partition_command(\"read_partitions\")",
            "Update Tool": "check_for_updates()",
        }
    }
}

# قائمة الأقسام العلوية الجديدة
TOP_NAV_BRANDS = list(BRAND_DATA.keys())
