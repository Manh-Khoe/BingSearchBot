import os

# --- ĐƯỜNG DẪN HỆ THỐNG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_PATH = os.path.join(BASE_DIR, "msedgedriver.exe")
KEYWORD_FILE = os.path.join(BASE_DIR, "keywords.txt")
USER_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data')

# --- CẤU HÌNH MẶC ĐỊNH (SỐ LƯỢNG) ---
DEFAULT_PC_TURNS = 30
DEFAULT_MOBILE_TURNS = 20
DEFAULT_MOB_NEWS_COUNT = 10
DEFAULT_INTERVAL = 3

# --- CẤU HÌNH MẶC ĐỊNH (THỜI GIAN - GIÂY) ---
DEFAULT_MIN_TYPE = 0.1
DEFAULT_MAX_TYPE = 0.4
DEFAULT_THINKING = 3.5
DEFAULT_MIN_READ = 5.0
DEFAULT_MAX_READ = 10.0

DEFAULT_MOB_DELAY_MIN = 8.0
DEFAULT_MOB_DELAY_MAX = 15.0

# Thời gian nghỉ giữa các nhiệm vụ (chuyển PC->Mobile hoặc Acc->Acc)
DEFAULT_TASK_DELAY = 15 

# BẬT/TẮT TÁC VỤ MẶC ĐỊNH
DEFAULT_DO_PC_SEARCH = True
DEFAULT_DO_PC_SETS = True
DEFAULT_DO_MOB_SEARCH = True
DEFAULT_DO_MOB_NEWS = True
DEFAULT_DO_MOB_CHECKIN = True

# DANH SÁCH PROFILE PC
PROFILES_LIST = ["Profile 1", "Profile 2"]

# USER AGENT BACKUP
MOBILE_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 EdgA/126.0.2592.113"
