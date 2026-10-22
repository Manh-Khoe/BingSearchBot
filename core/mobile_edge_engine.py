import time
import random
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import human_type

class MobileEdgeEngine:
    """Tự động hóa tìm kiếm di động thông qua Edge Mobile Emulation (EdgA)"""
    def __init__(self, log_callback=None, stop_checker=None):
        self.log = log_callback or (lambda msg: print(f"[Mobile] {msg}"))
        self.should_stop = stop_checker or (lambda: False)

    def smooth_scroll_mobile(self, driver):
        """Giả lập cuộn trang cảm ứng mượt mà trên di động"""
        try:
            total_scroll = random.randint(400, 900)
            cur = 0
            while cur < total_scroll:
                if self.should_stop(): break
                step = random.randint(30, 80)
                driver.execute_script(f"window.scrollBy({{top: {step}, behavior: 'smooth'}});")
                cur += step
                time.sleep(random.uniform(0.04, 0.08))
        except Exception: pass

    def run_mobile_search(self, driver, profile_dir, max_count, keywords, settings):
        """Thực hiện chu trình tìm kiếm di động với định danh Edge Android"""
        self.log(f"📱 [Mobile Search] Bắt đầu tìm kiếm {max_count} lượt cho [{profile_dir}] (Edge Android)...")

        # Truy cập Bing Mobile
        try:
            driver.get("https://www.bing.com")
            time.sleep(3)
        except Exception as e:
            self.log(f"Lỗi tải trang Bing Mobile: {e}")

        min_del = settings.get("min_search_delay", 8.0)
        max_del = settings.get("max_search_delay", 15.0)

        for i in range(1, max_count + 1):
            if self.should_stop():
                self.log("⏹ Đã dừng Mobile Search theo yêu cầu.")
                break

            word1 = random.choice(keywords)
            word2 = random.choice(keywords)
            query = f"{word1} {word2}"
            encoded = urllib.parse.quote(query)

            self.log(f"🔍 [{profile_dir}][Mobile {i}/{max_count}]: '{query}'")

            # Trên Mobile Bing, tìm kiếm bằng URL form QBLH là cách ổn định và chuẩn nhất
            try:
                driver.get(f"https://www.bing.com/search?q={encoded}&form=QBLH")
            except Exception:
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    human_type(search_box, query, 0.1, 0.3)
                    search_box.send_keys(Keys.ENTER)
                except Exception: pass

            time.sleep(3.0)

            # Cuộn lướt xem kết quả như người dùng điện thoại
            if random.choice([True, True, False]):
                self.smooth_scroll_mobile(driver)

            # Nghỉ ngẫu nhiên giữa các lượt search chống phạt Cooldown 15 phút
            wait_time = random.uniform(min_del, max_del)
            if i < max_count:
                self.log(f"⏳ Nghỉ {wait_time:.1f}s trước lượt kế tiếp...")
                step = 0.5
                elapsed = 0.0
                while elapsed < wait_time:
                    if self.should_stop(): break
                    time.sleep(step)
                    elapsed += step

        self.log(f"✅ [Mobile Search] Hoàn tất {max_count} lượt tìm kiếm di động cho [{profile_dir}]")

