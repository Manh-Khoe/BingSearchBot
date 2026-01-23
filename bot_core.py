import time
import random
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import *
from utils import human_type, smooth_scroll

class BingBotCore:
    def __init__(self, log_callback):
        self.log = log_callback # Hàm để gửi log về GUI
        self.is_running = True
        
    def stop(self):
        self.is_running = False

    def run_browser(self, profile_dir, mode_name, max_count, keywords, is_mobile):
        if not self.is_running: return

        self.log(f">>> START: [{profile_dir}] - Mode: {mode_name}")
        
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
        options.add_argument("--start-maximized") # Luôn full màn hình
        
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

            # --- SEARCH LOOP ---
            for i in range(1, max_count + 1):
                if not self.is_running: break # Kiểm tra nút dừng

                word1 = random.choice(keywords)
                word2 = random.choice(keywords)
                query = f"{word1} {word2}"
                
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    human_type(search_box, query)
                    time.sleep(random.uniform(1, 2))
                    search_box.send_keys(Keys.ENTER)
                except:
                    driver.get(f"https://www.bing.com/search?q={query}&form=TSASDS")
                
                time.sleep(3)

                if random.choice([True, False]): 
                    smooth_scroll(driver)
                
                # In log ra màn hình GUI
                self.log(f"[{profile_dir}][{mode_name}] {i}/{max_count}: '{query}'")

                # Tạm thời bỏ qua check điểm mobile để tránh lỗi như bạn yêu cầu
                
                wait_time = random.randint(3, 6)
                time.sleep(wait_time) 
                
        except Exception as e:
            self.log(f"[LOI] {str(e)}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            self.log(f"-> Đóng trình duyệt [{profile_dir}]")