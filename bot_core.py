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
        # === 1. DỌN DẸP TRÌNH DUYỆT NGẦM ===
        self.log("🧹 Đang dọn dẹp trình duyệt ngầm...")
        try:
            os.system("taskkill /F /IM msedge.exe /T >nul 2>&1")
            os.system("taskkill /F /IM msedgewebview2.exe /T >nul 2>&1")
            time.sleep(1.5)
        except: pass

        options = Options()
        
        # === 2. CÁCH LY HOÀN TOÀN KHỎI PROFILE CỦA WINDOWS ===
        # Tạo thư mục BingBot_Data ngay trong thư mục chứa tool để lưu data riêng biệt
        ISOLATED_DATA_DIR = os.path.join(os.getcwd(), "BingBot_Data")
        options.add_argument(f"--user-data-dir={ISOLATED_DATA_DIR}")
        options.add_argument(f"--profile-directory={profile_dir}")
        
        # Ép chuẩn đường dẫn Edge gốc (Tránh gọi nhầm WebView2)
        options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        
        # === 3. CHIẾN LƯỢC TẢI TRANG & FIX LỖI BẢO MẬT ===
        options.page_load_strategy = 'eager'
        
        options.add_argument("--remote-debugging-port=0") 
        options.add_argument("--remote-allow-origins=*")
        
        # Cấu hình chống Crash cho Edge v147+
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu") 
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-features=msEdgeEnhanceSecurity,RendererCodeIntegrity")
        
        options.add_argument("--log-level=3") 
        options.add_argument("--silent")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        
        if is_mobile:
            options.add_argument(f"user-agent={MOBILE_UA}")

        if not os.path.exists(DRIVER_PATH):
            self.log(f"[ERROR] Thiếu driver: {DRIVER_PATH}")
            return None

        service = Service(executable_path=DRIVER_PATH)
        service.creation_flags = subprocess.CREATE_NO_WINDOW
        return webdriver.Edge(options=options, service=service)

    # --- HÀM ĐỌC ĐIỂM CHỐNG NHẢY SỐ (STABILITY CHECK) ---
    def get_points_safe(self, driver, max_retries=5):
        last_value = None
        stable_count = 0 
        
        for _ in range(max_retries + 5):
            if not self.is_running: return "N/A"
            try:
                raw_text = ""
                try:
                    elm = driver.find_element(By.CLASS_NAME, "points-container")
                    raw_text = elm.text
                except: pass
                
                if not raw_text:
                    try: 
                        elm = driver.find_element(By.ID, "id_rc")
                        raw_text = elm.text
                    except: pass
                
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

                if raw_text and any(char.isdigit() for char in raw_text):
                    current_val = self.parse_points(raw_text)
                    
                    if current_val == last_value:
                        stable_count += 1
                    else:
                        stable_count = 0 
                        last_value = current_val
                    
                    if stable_count >= 1: 
                        return raw_text
            except:
                pass
            
            time.sleep(0.8) 
            
        return str(last_value) if last_value else "N/A"

    def check_points_final_round(self, profile_dir):
        if not self.is_running: return
        
        self.log(f"🕵️ Đang mở lại PC để chốt điểm cho [{profile_dir}]...")
        driver = None
        try:
            driver = self._create_driver(profile_dir, is_mobile=False)
            if not driver: return

            driver.get("https://www.bing.com")
            
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
            
            if not is_mobile:
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
            
            if is_mobile and self.is_running:
                delay = settings.get('delay_task', 5)
                self.log(f"⏳ Nghỉ {delay}s trước khi chốt điểm...")
                time.sleep(delay) 
                self.check_points_final_round(profile_dir)
            
            self.log(f"-> Đóng trình duyệt [{profile_dir}]")
            if self.stats: self.stats(profile_dir, status="Done")