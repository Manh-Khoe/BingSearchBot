import json
import os

SETTINGS_FILE = "user_settings.json"

DEFAULT_SETTINGS = {
    "general": {
        "auto_close": False,
        "delay_between_accounts": 15
    },
    "ui_state": {
        "profile_mode": 0,
        "selected_profile": "Profile 1",
        "run_mode": "Full Run"
    },
    "pc": {
        "enabled": True,
        "do_search": True,
        "do_daily_sets": True,
        "search_count": 30,
        "interval_check": 3,
        "min_type": 0.1,
        "max_type": 0.4,
        "min_read": 5.0,
        "max_read": 10.0,
        "profiles": ["Profile 1", "Profile 2"]
    },
    "mobile": {
        "enabled": True,
        "do_search": True,
        "search_count": 20,
        "min_search_delay": 8.0,
        "max_search_delay": 15.0
    },
    "appearance": {
        "theme": "Dark",
        "accent": "Windows 11 Blue"
    }
}

class ConfigManager:
    """Quản lý toàn bộ cấu hình ứng dụng không cần sửa code"""
    @staticmethod
    def load():
        if not os.path.exists(SETTINGS_FILE):
            ConfigManager.save(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            for key, val in data.items():
                if isinstance(val, dict) and key in merged:
                    merged[key].update(val)
                else:
                    merged[key] = val
            return merged
        except Exception:
            return DEFAULT_SETTINGS.copy()

    @staticmethod
    def save(settings_data):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
