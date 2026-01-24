import time
import random
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
from utils import human_type, smooth_scroll

class BingBotCore:
    def __init__(self, log_callback):
        self.log = log_callback
        self.is_running = True
        
    def stop(self):
        self.is_running = False

    # [CẬP NHẬT] Nhận thêm biến settings
    def run_browser(self, profile_dir, mode_name, max_count, keywords, is_mobile, settings):
        if not self.is_running: return

        self.log(f">>> START: [{profile_dir}] - Mode: {mode_name}")
        
        # --- LẤY THÔNG SỐ TỪ SETTINGS ---
        min_type = settings.get('min_type', 0.1)
        max_type = settings.get('max_type', 0.4)
        thinking = settings.get('thinking', 3.0)
        min_read = settings.get('min_read', 5.0)
        max_read = settings.get('max_read', 10.0)
        interval = settings.get('interval', 3)
        
        options = Options()
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        options.add_argument(f"--profile-directory={profile_dir}")
        options.add_argument("--log-level=3") 
        options.add_argument("--silent")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222") 
        options.add_argument("--start-maximized")
        
        if is_mobile:
            options.add_argument(f"user-agent={MOBILE_UA}")

        driver = None
        try:
            if not os.path.exists(DRIVER_PATH):
                self.log(f"[ERROR] Thiếu driver: {DRIVER_PATH}")
                return

            service = Service(executable_path=DRIVER_PATH)
            service.creation_flags = subprocess.CREATE_NO_WINDOW
            driver = webdriver.Edge(options=options, service=service)
            
            driver.get("https://www.bing.com")
            time.sleep(3)

            # Mobile: Mở sẵn Tab 2 để check điểm
            if is_mobile:
                self.log(" -> [Mobile] Chuẩn bị Tab Rewards...")
                driver.execute_script("window.open('https://rewards.bing.com/', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[0])

            # --- SEARCH LOOP ---
            for i in range(1, max_count + 1):
                if not self.is_running: break

                word1 = random.choice(keywords)
                word2 = random.choice(keywords)
                query = f"{word1} {word2}"
                
                # 1. SEARCHING
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    
                    # [CẬP NHẬT] Dùng tốc độ gõ từ cài đặt
                    human_type(search_box, query, min_type, max_type)
                    
                    # [CẬP NHẬT] Thời gian suy nghĩ trước khi Enter
                    time.sleep(thinking)
                    
                    search_box.send_keys(Keys.ENTER)
                except:
                    driver.get(f"https://www.bing.com/search?q={query}&form=TSASDS")
                
                time.sleep(3)

                # 2. SCROLLING
                if random.choice([True, False]): 
                    smooth_scroll(driver)
                
                self.log(f"[{profile_dir}][{mode_name}] {i}/{max_count}: '{query}'")

                # 3. CHECK POINTS (Đơn giản hóa để chạy mượt)
                # Chỉ check nếu là PC hoặc (Mobile và đúng nhịp Interval)
                check_now = False
                if not is_mobile: check_now = True
                elif i % interval == 0 or i == max_count: check_now = True
                
                if check_now:
                    # (Code check điểm cũ của bạn sẽ nằm ở đây - Tạm thời in log giả lập)
                    pass # Để bot chạy trơn tru trước khi lắp lại phần check điểm phức tạp

                # [CẬP NHẬT] Thời gian đọc bài (Nghỉ sau khi search)
                wait_time = random.uniform(min_read, max_read)
                time.sleep(wait_time) 
                
        except Exception as e:
            self.log(f"[LOI] {str(e)}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            self.log(f"-> Đóng trình duyệt [{profile_dir}]")