import subprocess
import time
import random
import os
from config import KEYWORD_FILE

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

# [CẬP NHẬT] Thêm tham số min/max speed
def human_type(element, text, min_delay=0.1, max_delay=0.4):
    """Gõ phím với tốc độ tùy chỉnh"""
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