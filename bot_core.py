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
    def __init__(self, log_callback, stats_callback=None):
        self.log = log_callback
        self.stats = stats_callback
        self.is_running = True
        
    def stop(self):
        self.is_running = False

    def parse_points(self, text):
        try:
            return int(''.join(filter(str.isdigit, text)))
        except:
            return -1

    def _create_driver(self, profile_dir, is_mobile=False):
        options = Options()
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        options.add_argument(f"--profile-directory={profile_dir}")
        
        options.add_argument("--disable-gpu") 
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3") 
        options.add_argument("--silent")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument("--start-maximized")
        
        if is_mobile:
            options.add_argument(f"user-agent={MOBILE_UA}")

        if not os.path.exists(DRIVER_PATH):
            self.log(f"[ERROR] Thiếu driver: {DRIVER_PATH}")
            return None

        service = Service(executable_path=DRIVER_PATH)
        service.creation_flags = subprocess.CREATE_NO_WINDOW
        return webdriver.Edge(options=options, service=service)

    # --- [UPDATE] HÀM ĐỌC ĐIỂM CHỐNG NHẢY SỐ (STABILITY CHECK) ---
    def get_points_safe(self, driver, max_retries=5):
        """
        Đọc điểm và đảm bảo con số đã dừng nhảy (animation finished).
        """
        last_value = None
        stable_count = 0 # Đếm số lần giá trị không đổi
        
        # Tăng số lần thử lên một chút để bù cho thời gian chờ animation
        for _ in range(max_retries + 5):
            if not self.is_running: return "N/A"
            try:
                raw_text = ""
                # Ưu tiên 1: Class points-container
                try:
                    elm = driver.find_element(By.CLASS_NAME, "points-container")
                    raw_text = elm.text
                except: pass
                
                # Ưu tiên 2: ID id_rc
                if not raw_text:
                    try: 
                        elm = driver.find_element(By.ID, "id_rc")
                        raw_text = elm.text
                    except: pass
                
                # Ưu tiên 3: Các selector khác...
                if not raw_text:
                    try:
                        elm = driver.find_element(By.XPATH, "//span[contains(@class, 'pointsValue')]")
                        raw_text = elm.text
                    except: pass
                
                if not raw_text:
                    try:
                        elm = driver.find_element(By.ID, "id_p")
                        raw_text = elm.text
                    except: pass

                # LOGIC KIỂM TRA ĐỘ ỔN ĐỊNH
                if raw_text and any(char.isdigit() for char in raw_text):
                    current_val = self.parse_points(raw_text)
                    
                    if current_val == last_value:
                        stable_count += 1
                    else:
                        stable_count = 0 # Reset nếu số thay đổi
                        last_value = current_val
                    
                    # Nếu số giữ nguyên trong 2 lần check liên tiếp (khoảng 1-1.5s) -> CHỐT
                    if stable_count >= 1: 
                        return raw_text
            except:
                pass
            
            # Thời gian chờ giữa các lần check
            time.sleep(0.8) 
            
        # Nếu hết thời gian mà vẫn chưa ổn định (hoặc ko tìm thấy), trả về giá trị cuối cùng đọc được
        return str(last_value) if last_value else "N/A"

    def check_points_final_round(self, profile_dir):
        if not self.is_running: return
        
        self.log(f"🕵️ Đang mở lại PC để chốt điểm cho [{profile_dir}]...")
        driver = None
        try:
            driver = self._create_driver(profile_dir, is_mobile=False)
            if not driver: return

            driver.get("https://www.bing.com")
            
            # Tăng retries lên để có thời gian cho animation chạy hết
            final_pts = self.get_points_safe(driver, max_retries=15)
            self.log(f"🏁 TỔNG KẾT ĐIỂM: {final_pts}")
            
            if final_pts != "N/A" and self.stats:
                self.stats(profile_dir, current_p=self.parse_points(final_pts))
                
        except Exception as e:
            self.log(f"[Lỗi Check Point] {str(e)}")
        finally:
            if driver:
                try: driver.quit()
                except: pass

    def run_browser(self, profile_dir, mode_name, max_count, keywords, is_mobile, settings, is_auto_mode):
        if not self.is_running: return

        self.log(f">>> START: [{profile_dir}] - Mode: {mode_name}")
        if self.stats: self.stats(profile_dir, status="Running")

        driver = None
        try:
            driver = self._create_driver(profile_dir, is_mobile)
            if not driver: return
            
            driver.get("https://www.bing.com")
            
            # PC: Đọc điểm đầu
            if not is_mobile:
                # Max retries cao hơn chút để chờ load trang
                start_pts_str = self.get_points_safe(driver, max_retries=10)
                if start_pts_str != "N/A" and self.stats:
                    self.stats(profile_dir, start_p=self.parse_points(start_pts_str))
                else:
                    self.log(f"⚠️ Chưa đọc được điểm đầu")

            time.sleep(2)

            if is_mobile:
                self.log(" -> [Mobile] Vào trang Rewards...")
                try:
                    driver.execute_script("window.open('https://rewards.bing.com/', '_blank');")
                    time.sleep(3)
                    driver.switch_to.window(driver.window_handles[0])
                except: pass

            last_points_int = -1
            no_increase_streak = 0
            
            min_type = settings.get('min_type', 0.1)
            max_type = settings.get('max_type', 0.4)
            thinking = settings.get('thinking', 3.0)
            interval = settings.get('interval', 3)
            min_read = settings.get('min_read', 5.0)
            max_read = settings.get('max_read', 10.0)

            for i in range(1, max_count + 1):
                if not self.is_running: break

                word1 = random.choice(keywords)
                word2 = random.choice(keywords)
                query = f"{word1} {word2}"
                
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    human_type(search_box, query, min_type, max_type)
                    time.sleep(thinking)
                    search_box.send_keys(Keys.ENTER)
                except:
                    driver.get(f"https://www.bing.com/search?q={query}&form=TSASDS")
                
                time.sleep(3)
                if random.choice([True, False]): smooth_scroll(driver)
                
                if not is_mobile:
                    should_check = (i % interval == 0) or (i == max_count)
                    if should_check:
                        # Check định kỳ thì chỉ cần retry ít thôi (2-3 lần) cho nhanh
                        points_str = self.get_points_safe(driver, max_retries=3)
                        self.log(f"[{profile_dir}][PC] {i}/{max_count}: '{query}' | Điểm: {points_str}")

                        if points_str != "N/A":
                            curr_p = self.parse_points(points_str)
                            if self.stats: self.stats(profile_dir, current_p=curr_p)

                            if is_auto_mode and curr_p > 0:
                                if curr_p > last_points_int:
                                    last_points_int = curr_p
                                    no_increase_streak = 0
                                else:
                                    no_increase_streak += 1
                                if no_increase_streak >= 3:
                                    self.log(f" [!] Điểm đứng yên {no_increase_streak} lần. Next!")
                                    break
                else:
                    self.log(f"[{profile_dir}][Mobile] {i}/{max_count}: '{query}'")

                time.sleep(random.uniform(min_read, max_read))

        except Exception as e:
            self.log(f"[LOI] {str(e)}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            
            # --- Chốt điểm Mobile ---
            if is_mobile and self.is_running:
                delay = settings.get('delay_task', 5)
                self.log(f"⏳ Nghỉ {delay}s trước khi chốt điểm...")
                time.sleep(delay) 
                self.check_points_final_round(profile_dir)
            
            self.log(f"-> Đóng trình duyệt [{profile_dir}]")
            if self.stats: self.stats(profile_dir, status="Done")