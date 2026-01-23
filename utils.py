import subprocess
import time
import random
import os
from config import KEYWORD_FILE

def clean_system():
    """Dọn dẹp sạch sẽ Edge và Driver"""
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

def human_type(element, text):
    """Gõ phím như người thật"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def smooth_scroll(driver):
    """Cuộn trang mượt mà"""
    try:
        total_scroll = random.randint(300, 1000)
        current_scroll = 0
        while current_scroll < total_scroll:
            step = random.randint(20, 60)
            driver.execute_script(f"window.scrollBy(0, {step});")
            current_scroll += step
            time.sleep(random.uniform(0.02, 0.05))
    except: pass