import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import human_type, smooth_scroll
from core.browser_factory import BrowserFactory

class PCEngine:
    """Tự động hóa tìm kiếm và làm nhiệm vụ Microsoft Rewards trên PC"""
    def __init__(self, log_callback=None, stats_callback=None, stop_checker=None):
        self.log = log_callback or (lambda msg: print(f"[PC] {msg}"))
        self.stats = stats_callback
        self.should_stop = stop_checker or (lambda: False)

    def parse_points(self, text):
        try:
            return int(''.join(filter(str.isdigit, str(text))))
        except Exception:
            return -1

    def create_driver(self, profile_dir, is_mobile=False):
        return BrowserFactory.create_driver(profile_dir, is_mobile=is_mobile, log_callback=self.log)

    def get_points_safe(self, driver, max_retries=6):
        """Đọc điểm số thông minh hỗ trợ cả giao diện cũ và mới (Dashboard 2026)"""
        last_val = None
        stable_count = 0

        for _ in range(max_retries + 3):
            if self.should_stop(): return "N/A"
            try:
                # 1. Thử các selector truyền thống
                for selector in [
                    (By.CLASS_NAME, "points-container"),
                    (By.ID, "id_rc"),
                    (By.XPATH, "//span[contains(@class, 'pointsValue')]"),
                    (By.ID, "id_p"),
                    (By.CSS_SELECTOR, "a[aria-label*='points'], div[aria-label*='points']")
                ]:
                    try:
                        elm = driver.find_element(*selector)
                        if elm and elm.text and any(c.isdigit() for c in elm.text):
                            pts = self.parse_points(elm.text)
                            if pts > 0:
                                if pts == last_val:
                                    stable_count += 1
                                    if stable_count >= 1:
                                        return str(pts)
                                else:
                                    stable_count = 0
                                    last_val = pts
                    except Exception: pass

                # 2. Thử tìm trên giao diện Rewards Dashboard mới (React Aria)
                # Tìm các thẻ button hoặc span có định dạng số điểm (ví dụ: '10,911' hoặc '9,714')
                elements = driver.find_elements(By.CSS_SELECTOR, "button, p, span")
                for elm in elements:
                    try:
                        txt = elm.text.strip()
                        # Kiểm tra định dạng số điểm: có dấu phẩy hoặc từ 3-6 chữ số thuần
                        if txt and re.match(r"^\d{1,3}(,\d{3})+$|^\d{3,6}$", txt):
                            pts = self.parse_points(txt)
                            if pts > 100:  # Điểm Rewards thông thường lớn hơn 100
                                if pts == last_val:
                                    stable_count += 1
                                    if stable_count >= 1:
                                        return str(pts)
                                else:
                                    stable_count = 0
                                    last_val = pts
                    except Exception: pass

            except Exception: pass
            time.sleep(0.7)

        return str(last_val) if last_val else "N/A"

    def fetch_points_via_rewards_page(self, driver):
        """Truy cập trực tiếp trang Rewards Dashboard để chốt điểm chính xác 100%"""
        try:
            curr_url = driver.current_url
            driver.get("https://rewards.bing.com")
            time.sleep(3.5)
            pts_str = self.get_points_safe(driver, max_retries=5)
            # Quay lại trang trước nếu cần
            if curr_url and "bing.com/search" in curr_url:
                driver.get(curr_url)
            return pts_str
        except Exception:
            return "N/A"

    def run_pc_search(self, driver, profile_dir, max_count, keywords, settings, is_auto_mode=True):
        self.log(f"💻 [PC Search] Bắt đầu tìm kiếm {max_count} lượt cho [{profile_dir}]...")
        
        try:
            driver.get("https://www.bing.com")
            time.sleep(2.5)
        except Exception: pass

        last_points_int = -1
        no_increase_streak = 0
        
        min_type = settings.get('min_type', 0.1)
        max_type = settings.get('max_type', 0.4)
        thinking = settings.get('thinking', 3.0)
        interval = settings.get('interval_check', 3)
        min_read = settings.get('min_read', 5.0)
        max_read = settings.get('max_read', 10.0)

        for i in range(1, max_count + 1):
            if self.should_stop(): break

            word1 = random.choice(keywords)
            word2 = random.choice(keywords)
            query = f"{word1} {word2}"
            
            try:
                search_box = driver.find_element(By.ID, "sb_form_q")
                search_box.clear()
                human_type(search_box, query, min_type, max_type)
                time.sleep(thinking)
                search_box.send_keys(Keys.ENTER)
            except Exception:
                driver.get(f"https://www.bing.com/search?q={query}&form=TSASDS")
            
            time.sleep(2.5)
            if random.choice([True, False]): smooth_scroll(driver)
            
            should_check = (i % interval == 0) or (i == max_count)
            if should_check:
                points_str = self.get_points_safe(driver, max_retries=2)
                self.log(f"[{profile_dir}][PC] {i}/{max_count}: '{query}' | Điểm: {points_str}")

                if points_str != "N/A":
                    curr_p = self.parse_points(points_str)
                    if is_auto_mode and curr_p > 0:
                        if curr_p > last_points_int:
                            last_points_int = curr_p
                            no_increase_streak = 0
                        else:
                            no_increase_streak += 1
                        if no_increase_streak >= 3:
                            self.log(f" [!] Điểm đứng yên {no_increase_streak} lần. Chuyển task!")
                            break

            time.sleep(random.uniform(min_read, max_read))

        self.log(f"✅ [PC Search] Hoàn tất tìm kiếm PC cho [{profile_dir}]")

    def run_daily_sets(self, driver, profile_dir):
        """Tự động làm nhiệm vụ hàng ngày Daily Sets trên rewards.bing.com"""
        if self.should_stop(): return

        self.log(f"🎯 [Daily Sets] Bắt đầu kiểm tra nhiệm vụ hàng ngày cho [{profile_dir}]...")
        try:
            driver.get("https://rewards.bing.com/")
            time.sleep(4)

            cards = driver.find_elements(By.CSS_SELECTOR, "c-card-content, .card-content, [data-bi-id*='daily-set']")
            if not cards:
                cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'c-card') or contains(@class, 'promo-card')]")

            self.log(f"Tìm thấy {len(cards)} thẻ nhiệm vụ tiềm năng.")
            main_window = driver.current_window_handle

            for idx, card in enumerate(cards[:3]):
                if self.should_stop(): break
                try:
                    self.log(f" -> Đang thực hiện nhiệm vụ Daily Card #{idx+1}...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    time.sleep(1)
                    card.click()
                    time.sleep(4)

                    windows = driver.window_handles
                    if len(windows) > 1:
                        for w in windows:
                            if w != main_window:
                                driver.switch_to.window(w)
                                time.sleep(3)
                                try:
                                    poll_options = driver.find_elements(By.CSS_SELECTOR, ".btOption, .wk_option, input[type='radio']")
                                    if poll_options:
                                        random.choice(poll_options).click()
                                        time.sleep(2)
                                except Exception: pass
                                driver.close()
                        driver.switch_to.window(main_window)
                        time.sleep(2)
                except Exception as e:
                    self.log(f"Bỏ qua thẻ #{idx+1}: {e}")

            self.log(f"✅ [Daily Sets] Hoàn tất nhiệm vụ hàng ngày cho [{profile_dir}]")
        except Exception as e:
            self.log(f"Lỗi khi làm Daily Sets: {e}")
