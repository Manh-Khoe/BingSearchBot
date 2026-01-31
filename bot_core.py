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
        self.log = log_callback
        self.is_running = True
        
    def stop(self):
        self.is_running = False

    def parse_points(self, text):
        try:
            return int(text.replace(",", "").replace(".", "").strip())
        except:
            return -1

    def get_pc_points(self, driver):
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            try:
                elm = driver.find_element(By.CLASS_NAME, "points-container")
                return elm.text
            except:
                return driver.find_element(By.ID, "id_rc").text
        except:
            return "N/A"

    def run_browser(self, profile_dir, mode_name, max_count, keywords, is_mobile, settings, is_auto_mode):
        if not self.is_running: return

        self.log(f">>> START: [{profile_dir}] - Mode: {mode_name}")
        
        # Lấy tham số
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
            
            # [ĐÃ XÓA] Dòng lệnh driver.minimize_window() gây lỗi đen màn hình và rung lắc
            # Bot sẽ mở cửa sổ Full màn hình bình thường.

            time.sleep(3)

            # Mobile setup
            if is_mobile:
                self.log(" -> [Mobile] Chuẩn bị Tab Rewards...")
                driver.execute_script("window.open('https://rewards.bing.com/', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[0])

            last_points_int = -1
            no_increase_streak = 0

            # --- SEARCH LOOP ---
            for i in range(1, max_count + 1):
                if not self.is_running: break

                word1 = random.choice(keywords)
                word2 = random.choice(keywords)
                query = f"{word1} {word2}"
                
                # 1. SEARCH
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    human_type(search_box, query, min_type, max_type)
                    time.sleep(thinking)
                    search_box.send_keys(Keys.ENTER)
                except:
                    driver.get(f"https://www.bing.com/search?q={query}&form=TSASDS")
                
                time.sleep(3)

                # 2. SCROLL
                if random.choice([True, False]): 
                    smooth_scroll(driver)
                
                # 3. CHECK POINTS
                points_str = ""
                should_check = (i % interval == 0) or (i == max_count)

                if not is_mobile and should_check:
                    points_str = self.get_pc_points(driver)
                    self.log(f"[{profile_dir}][PC] {i}/{max_count}: '{query}' | Điểm: {points_str}")

                    # STOP LOGIC (AUTO ALL ONLY)
                    if is_auto_mode and points_str != "N/A":
                        curr = self.parse_points(points_str)
                        if curr > 0:
                            if curr > last_points_int:
                                last_points_int = curr
                                no_increase_streak = 0
                            else:
                                no_increase_streak += 1
                            
                            if no_increase_streak >= 2:
                                self.log(f" [!] Điểm đứng yên ({last_points_int}). Next!")
                                break
                else:
                    self.log(f"[{profile_dir}][{mode_name}] {i}/{max_count}: '{query}'")

                # 4. READ TIME
                wait_time = random.uniform(min_read, max_read)
                time.sleep(wait_time) 
                
        except Exception as e:
            self.log(f"[LOI] {str(e)}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            self.log(f"-> Đóng trình duyệt [{profile_dir}]")