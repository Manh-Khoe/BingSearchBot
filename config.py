import os

# --- ĐƯỜNG DẪN HỆ THỐNG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_PATH = os.path.join(BASE_DIR, "msedgedriver.exe")
KEYWORD_FILE = os.path.join(BASE_DIR, "keywords.txt")
USER_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')

# --- CẤU HÌNH MẶC ĐỊNH (SỐ LƯỢNG) ---
DEFAULT_PC_TURNS = 30
DEFAULT_MOBILE_TURNS = 20
DEFAULT_INTERVAL = 3  # Số lượt search thì check điểm 1 lần (Mobile)

# --- CẤU HÌNH MẶC ĐỊNH (THỜI GIAN - GIÂY) ---
# Tốc độ gõ (giây cho mỗi ký tự)
DEFAULT_MIN_TYPE = 0.1
DEFAULT_MAX_TYPE = 0.4

# Thời gian suy nghĩ trước khi nhấn Enter
DEFAULT_THINKING = 3.5

# Tốc độ đọc (nghỉ sau khi search xong)
DEFAULT_MIN_READ = 5.0
DEFAULT_MAX_READ = 10.0

# DANH SÁCH PROFILE
PROFILES_LIST = ["Default", "Profile 4", "Profile 8"]

# USER AGENT
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"