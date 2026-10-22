import os
import subprocess
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from config import DRIVER_PATH

# User-Agent Edge Mobile trên Android phiên bản mới nhất
EDGE_ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36 EdgA/128.0.2708.88"
)

class BrowserFactory:
    """Khởi tạo trình duyệt Edge tối ưu với cơ chế TỰ ĐỘNG CẬP NHẬT DRIVER"""
    @staticmethod
    def create_driver(profile_dir, is_mobile=False, log_callback=None):
        log = log_callback or (lambda msg: None)
        options = Options()

        # 1. Cách ly Profile hoàn toàn khỏi Edge của Windows
        ISOLATED_DATA_DIR = os.path.join(os.getcwd(), "BingBot_Data")
        options.add_argument(f"--user-data-dir={ISOLATED_DATA_DIR}")
        options.add_argument(f"--profile-directory={profile_dir}")
        options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

        # 2. Hiệu năng & Ổn định
        options.page_load_strategy = 'eager'
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-features=msEdgeEnhanceSecurity,RendererCodeIntegrity")

        # 3. Anti-Detection (Che giấu tự động hóa)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        # 4. CHẾ ĐỘ GIẢ LẬP DI ĐỘNG CHUẨN CHROMIUM (MOBILE EMULATION)
        if is_mobile:
            mobile_emulation = {
                "deviceMetrics": {
                    "width": 412,
                    "height": 915,
                    "pixelRatio": 2.625,
                    "touch": True,
                    "mobile": True
                },
                "userAgent": EDGE_ANDROID_UA
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)

        # 5. TỰ ĐỘNG CẬP NHẬT VÀ QUẢN LÝ DRIVER THÔNG MINH
        driver = None
        
        # Cách 1: Dùng Selenium Manager tích hợp (Tự động tải & khớp 100% phiên bản Edge hiện tại)
        try:
            service = Service()
            service.creation_flags = subprocess.CREATE_NO_WINDOW
            driver = webdriver.Edge(options=options, service=service)
        except Exception as e:
            log(f"⚠️ Selenium Manager tải driver tự động gặp sự cố: {e}. Đang thử cách dự phòng...")

        # Cách 2: Nếu cách 1 gặp sự cố, thử webdriver-manager
        if not driver:
            try:
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                auto_driver_path = EdgeChromiumDriverManager().install()
                service = Service(executable_path=auto_driver_path)
                service.creation_flags = subprocess.CREATE_NO_WINDOW
                driver = webdriver.Edge(options=options, service=service)
            except Exception: pass

        # Cách 3: Fallback dùng file msedgedriver.exe cục bộ nếu có sẵn trong thư mục
        if not driver and os.path.exists(DRIVER_PATH):
            try:
                service = Service(executable_path=DRIVER_PATH)
                service.creation_flags = subprocess.CREATE_NO_WINDOW
                driver = webdriver.Edge(options=options, service=service)
            except Exception as e:
                log(f"[ERROR] Không thể khởi tạo Edge Driver: {e}")
                return None

        if not driver:
            log("[ERROR] Không thể khởi tạo Edge Driver bằng mọi phương thức!")
            return None

        # 6. Xóa cờ navigator.webdriver qua CDP
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            if is_mobile:
                driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {
                    "enabled": True,
                    "maxTouchPoints": 5
                })
        except Exception: pass

        return driver
