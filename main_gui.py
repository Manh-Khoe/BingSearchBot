import customtkinter as ctk
import threading
import sys
import random
from datetime import datetime
from config import *
from utils import clean_system, load_keywords
from bot_core import BingBotCore

# Cài đặt giao diện
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MS Rewards Bot v5.3 (Advanced Settings)")
        self.geometry("980x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text="Claim 🍟", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3498db")
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="CHẾ ĐỘ CHẠY:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.radio_var = ctk.IntVar(value=0)
        self.rb_1 = ctk.CTkRadioButton(self.sidebar, text="🚀 Auto All", variable=self.radio_var, value=0)
        self.rb_1.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.rb_2 = ctk.CTkRadioButton(self.sidebar, text="💻 PC Only", variable=self.radio_var, value=1)
        self.rb_2.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.btn_start = ctk.CTkButton(self.sidebar, text="▶ BẮT ĐẦU", height=40, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_thread)
        self.btn_start.grid(row=7, column=0, padx=20, pady=(10, 10))

        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹ DỪNG LẠI", height=40, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(size=14, weight="bold"), state="disabled", command=self.stop_bot)
        self.btn_stop.grid(row=8, column=0, padx=20, pady=(0, 30))

        # ================= MAIN AREA =================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # 1. LOG BOX
        self.log_box = ctk.CTkTextbox(self.main_frame, height=350, font=("Consolas", 13))
        self.log_box.pack(fill="both", expand=True, pady=(0, 15))
        self.log_box.configure(state="disabled")
        self.log_message("⚡ Sẵn sàng...")

        # 2. ADVANCED SETTINGS FRAME
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#212121", corner_radius=10)
        self.settings_frame.pack(fill="x", pady=5, ipady=10)

        self.lbl_config = ctk.CTkLabel(self.settings_frame, text="⚙️ CẤU HÌNH THAM SỐ (Để trống = Mặc định)", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_config.pack(pady=10)

        # Chia làm 3 cột cài đặt
        self.grid_inputs = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.grid_inputs.pack(fill="x", padx=20)
        self.grid_inputs.grid_columnconfigure(0, weight=1)
        self.grid_inputs.grid_columnconfigure(1, weight=1)
        self.grid_inputs.grid_columnconfigure(2, weight=1)

        # --- CỘT 1: SỐ LƯỢNG ---
        self.f1 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f1.grid(row=0, column=0, sticky="n")
        
        ctk.CTkLabel(self.f1, text="SỐ LƯỢNG SEARCH", text_color="#3498db", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.create_input(self.f1, "PC Count:", str(DEFAULT_PC_TURNS), "entry_pc")
        self.create_input(self.f1, "Mobile Count:", str(DEFAULT_MOBILE_TURNS), "entry_mob")
        self.create_input(self.f1, "Interval (Check):", str(DEFAULT_INTERVAL), "entry_int")

        # --- CỘT 2: TỐC ĐỘ GÕ ---
        self.f2 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f2.grid(row=0, column=1, sticky="n")

        ctk.CTkLabel(self.f2, text="TỐC ĐỘ GÕ (giây)", text_color="#f39c12", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.create_input(self.f2, "Min Type:", str(DEFAULT_MIN_TYPE), "entry_min_type")
        self.create_input(self.f2, "Max Type:", str(DEFAULT_MAX_TYPE), "entry_max_type")
        self.create_input(self.f2, "Thinking:", str(DEFAULT_THINKING), "entry_think")

        # --- CỘT 3: TỐC ĐỘ ĐỌC ---
        self.f3 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f3.grid(row=0, column=2, sticky="n")

        ctk.CTkLabel(self.f3, text="TỐC ĐỘ ĐỌC (giây)", text_color="#e74c3c", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.create_input(self.f3, "Min Read:", str(DEFAULT_MIN_READ), "entry_min_read")
        self.create_input(self.f3, "Max Read:", str(DEFAULT_MAX_READ), "entry_max_read")


        self.bot_core = None
        self.is_running = False

    def create_input(self, parent, label, placeholder, var_name):
        """Hàm hỗ trợ tạo ô nhập liệu nhanh"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2)
        ctk.CTkLabel(frame, text=label, width=100, anchor="e").pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=60, justify="center")
        entry.pack(side="left")
        setattr(self, var_name, entry) # Lưu biến vào class (self.entry_pc...)

    def log_message(self, message):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{now} {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def get_settings(self):
        """Lấy toàn bộ thông số từ giao diện"""
        def get_val(entry, default, is_float=False):
            try:
                val = entry.get().strip()
                if not val: return default
                return float(val) if is_float else int(val)
            except: return default

        return {
            "pc_turns": get_val(self.entry_pc, DEFAULT_PC_TURNS),
            "mob_turns": get_val(self.entry_mob, DEFAULT_MOBILE_TURNS),
            "interval": get_val(self.entry_int, DEFAULT_INTERVAL),
            "min_type": get_val(self.entry_min_type, DEFAULT_MIN_TYPE, True),
            "max_type": get_val(self.entry_max_type, DEFAULT_MAX_TYPE, True),
            "thinking": get_val(self.entry_think, DEFAULT_THINKING, True),
            "min_read": get_val(self.entry_min_read, DEFAULT_MIN_READ, True),
            "max_read": get_val(self.entry_max_read, DEFAULT_MAX_READ, True),
        }

    def run_bot_process(self):
        clean_system()
        all_keywords = load_keywords()
        settings = self.get_settings() # Lấy cục settings mới
        
        self.bot_core = BingBotCore(self.log_message)
        
        queue = []
        for profile in PROFILES_LIST:
            queue.append({"p": profile, "m": "PC", "c": settings['pc_turns'], "mob": False})
            if self.radio_var.get() == 0:
                 queue.append({"p": profile, "m": "MOBILE", "c": settings['mob_turns'], "mob": True})
        
        random.shuffle(queue)
        
        self.log_message(f"▶ BẮT ĐẦU VỚI CẤU HÌNH TÙY CHỈNH...")
        self.log_message(f"ℹ Type: {settings['min_type']}-{settings['max_type']}s | Think: {settings['thinking']}s")
        self.log_message("-" * 40)

        for task in queue:
            if not self.is_running: break
            
            # Truyền settings vào hàm run_browser
            self.bot_core.run_browser(
                profile_dir=task['p'],
                mode_name=task['m'],
                max_count=task['c'],
                keywords=all_keywords,
                is_mobile=task['mob'],
                settings=settings 
            )
            clean_system()
            if self.is_running:
                time.sleep(5)

        self.log_message("✅ HOÀN TẤT.")
        self.stop_bot()

    def start_thread(self):
        if self.is_running: return
        self.is_running = True
        self.btn_start.configure(state="disabled", fg_color="gray")
        self.btn_stop.configure(state="normal", fg_color="#e74c3c")
        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.is_running = False
        if self.bot_core: self.bot_core.stop()
        self.btn_start.configure(state="normal", fg_color="#2ecc71")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        self.log_message("⛔ ĐÃ DỪNG.")

    def on_closing(self):
        self.stop_bot()
        clean_system()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()