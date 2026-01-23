import os

# --- ĐƯỜNG DẪN HỆ THỐNG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_PATH = os.path.join(BASE_DIR, "msedgedriver.exe")
KEYWORD_FILE = os.path.join(BASE_DIR, "keywords.txt")
USER_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')

# --- CẤU HÌNH MẶC ĐỊNH ---
DEFAULT_PC_TURNS = 30
DEFAULT_MOBILE_TURNS = 20

# DANH SÁCH PROFILE
PROFILES_LIST = ["Default", "Profile 4", "Profile 8"]

# USER AGENT
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"