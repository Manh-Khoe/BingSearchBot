import subprocess
import time
import random
import os
import json
from datetime import datetime
from config import KEYWORD_FILE

SETTINGS_FILE = "user_settings.json"
STATS_FILE = "daily_stats.json"

def clean_system():
    try:
        subprocess.call("taskkill /f /im msedge.exe /t", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.call("taskkill /f /im msedgedriver.exe /t", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except: pass
    time.sleep(1)

def load_keywords():
    try:
        with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines if lines else ["bing", "rewards", "weather", "news", "finance"]
    except: return ["news", "tech", "bitcoin", "weather", "youtube"]

def human_type(element, text, min_delay=0.1, max_delay=0.4):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def smooth_scroll(driver):
    try:
        total_scroll = random.randint(300, 1000)
        current_scroll = 0
        while current_scroll < total_scroll:
            step = random.randint(20, 60)
            driver.execute_script(f"window.scrollBy(0, {step});")
            current_scroll += step
            time.sleep(random.uniform(0.02, 0.05))
    except: pass

# --- CÀI ĐẶT NGƯỜI DÙNG ---
def save_settings_to_file(data):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except: pass

def load_settings_from_file():
    if not os.path.exists(SETTINGS_FILE): return None
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

# --- [MỚI] THỐNG KÊ HÀNG NGÀY ---
def load_daily_stats():
    """Load thống kê, nếu qua ngày mới thì reset"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    default_data = {"date": today_str, "data": {}}
    
    if not os.path.exists(STATS_FILE):
        return default_data

    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            saved_stats = json.load(f)
            
        # Kiểm tra nếu là ngày cũ thì Reset
        if saved_stats.get("date") != today_str:
            return default_data # Trả về data mới tinh
        
        return saved_stats
    except:
        return default_data

def save_daily_stats(stats_data):
    """Lưu thống kê hiện tại"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=4)
    except: pass