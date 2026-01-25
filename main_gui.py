import customtkinter as ctk
import threading
import sys
import random
import time
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

        self.title("MS Rewards Bot v5.5 (Final Control)")
        self.geometry("980x720")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Logo
        self.logo = ctk.CTkLabel(self.sidebar, text="Claim 🍟", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3498db")
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Chế độ chạy
        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="CHẾ ĐỘ CHẠY:", anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.radio_var = ctk.IntVar(value=0) # 0 = Auto All, 1 = Single
        self.rb_auto = ctk.CTkRadioButton(self.sidebar, text=f"Auto All ({len(PROFILES_LIST)} Acc)", variable=self.radio_var, value=0, command=self.update_ui_state)
        self.rb_auto.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.rb_single = ctk.CTkRadioButton(self.sidebar, text="Single Profile", variable=self.radio_var, value=1, command=self.update_ui_state)
        self.rb_single.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Dropdown Tài khoản
        self.lbl_acc = ctk.CTkLabel(self.sidebar, text="TÀI KHOẢN:", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_acc.grid(row=4, column=0, padx=25, pady=(10, 0), sticky="w")

        self.profile_menu = ctk.CTkOptionMenu(self.sidebar, values=PROFILES_LIST, width=180)
        self.profile_menu.grid(row=5, column=0, padx=20, pady=(5, 10))

        # Switch Mobile Only
        self.switch_mobile_var = ctk.BooleanVar(value=False)
        self.switch_mobile = ctk.CTkSwitch(self.sidebar, text="Chỉ chạy Mobile", variable=self.switch_mobile_var, font=ctk.CTkFont(size=13))
        self.switch_mobile.grid(row=6, column=0, padx=20, pady=20, sticky="w")

        # Nút Start/Stop
        self.btn_start = ctk.CTkButton(self.sidebar, text="▶ BẮT ĐẦU", height=40, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_thread)
        self.btn_start.grid(row=9, column=0, padx=20, pady=(10, 10))

        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹ DỪNG LẠI", height=40, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(size=14, weight="bold"), state="disabled", command=self.stop_bot)
        self.btn_stop.grid(row=10, column=0, padx=20, pady=(0, 30))

        # ================= MAIN AREA =================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Log
        self.log_box = ctk.CTkTextbox(self.main_frame, height=380, font=("Consolas", 13))
        self.log_box.pack(fill="both", expand=True, pady=(0, 15))
        self.log_box.configure(state="disabled")
        self.log_message("⚡ Sẵn sàng...")

        # Settings
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#212121", corner_radius=10)
        self.settings_frame.pack(fill="x", pady=5, ipady=10)

        self.lbl_config = ctk.CTkLabel(self.settings_frame, text="⚙️ CẤU HÌNH THAM SỐ (Để trống = Mặc định)", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_config.pack(pady=10)

        self.grid_inputs = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.grid_inputs.pack(fill="x", padx=20)
        self.grid_inputs.grid_columnconfigure(0, weight=1)
        self.grid_inputs.grid_columnconfigure(1, weight=1)
        self.grid_inputs.grid_columnconfigure(2, weight=1)

        # Cột 1
        self.f1 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f1.grid(row=0, column=0, sticky="n")
        ctk.CTkLabel(self.f1, text="SỐ LƯỢNG", text_color="#3498db", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f1, "PC Count:", str(DEFAULT_PC_TURNS), "entry_pc")
        self.create_input(self.f1, "Mobile Count:", str(DEFAULT_MOBILE_TURNS), "entry_mob")
        self.create_input(self.f1, "Interval:", str(DEFAULT_INTERVAL), "entry_int")

        # Cột 2
        self.f2 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f2.grid(row=0, column=1, sticky="n")
        ctk.CTkLabel(self.f2, text="TỐC ĐỘ GÕ (s)", text_color="#f39c12", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f2, "Min Type:", str(DEFAULT_MIN_TYPE), "entry_min_type")
        self.create_input(self.f2, "Max Type:", str(DEFAULT_MAX_TYPE), "entry_max_type")
        self.create_input(self.f2, "Thinking:", str(DEFAULT_THINKING), "entry_think")

        # Cột 3
        self.f3 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f3.grid(row=0, column=2, sticky="n")
        ctk.CTkLabel(self.f3, text="TỐC ĐỘ ĐỌC (s)", text_color="#e74c3c", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f3, "Min Read:", str(DEFAULT_MIN_READ), "entry_min_read")
        self.create_input(self.f3, "Max Read:", str(DEFAULT_MAX_READ), "entry_max_read")

        self.bot_core = None
        self.is_running = False
        self.all_entries = [] # Danh sách chứa tất cả ô nhập để khóa/mở
        
        # Gom các entry vào list để dễ quản lý
        self.collect_entries()
        self.update_ui_state()

    def create_input(self, parent, label, placeholder, var_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2)
        ctk.CTkLabel(frame, text=label, width=100, anchor="e").pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=60, justify="center")
        entry.pack(side="left")
        setattr(self, var_name, entry)

    def collect_entries(self):
        """Gom hết các ô nhập vào 1 list"""
        self.all_entries = [
            self.entry_pc, self.entry_mob, self.entry_int,
            self.entry_min_type, self.entry_max_type, self.entry_think,
            self.entry_min_read, self.entry_max_read
        ]

    def update_ui_state(self):
        """Khóa/Mở Dropdown Profile"""
        if self.radio_var.get() == 0: # Auto All
            self.profile_menu.configure(state="disabled", fg_color="gray")
        else: # Single Profile
            self.profile_menu.configure(state="normal", fg_color="#1f6aa5")

    def toggle_inputs(self, state):
        """Khóa hoặc Mở toàn bộ ô nhập liệu tham số"""
        # state là "normal" hoặc "disabled"
        for entry in self.all_entries:
            entry.configure(state=state)

    def log_message(self, message):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{now} {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def get_settings(self):
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
        settings = self.get_settings()
        
        self.bot_core = BingBotCore(self.log_message)
        
        is_auto_mode = (self.radio_var.get() == 0) # True nếu là Auto All
        
        target_profiles = []
        if is_auto_mode:
            target_profiles = PROFILES_LIST
            self.log_message(f"🚀 CHẾ ĐỘ: AUTO ALL ({len(target_profiles)} Acc)")
        else:
            selected = self.profile_menu.get()
            target_profiles = [selected]
            self.log_message(f"👤 CHẾ ĐỘ: SINGLE PROFILE [{selected}]")

        mobile_only = self.switch_mobile_var.get()
        if mobile_only: self.log_message("📱 TÙY CHỌN: CHỈ CHẠY MOBILE")
        
        queue = []
        for profile in target_profiles:
            if not mobile_only:
                queue.append({"p": profile, "m": "PC", "c": settings['pc_turns'], "mob": False})
            queue.append({"p": profile, "m": "MOBILE", "c": settings['mob_turns'], "mob": True})
        
        if len(target_profiles) > 1:
            random.shuffle(queue)
        
        self.log_message("-" * 40)

        for task in queue:
            if not self.is_running: break
            
            # Truyền thêm biến is_auto_mode vào core
            self.bot_core.run_browser(
                profile_dir=task['p'],
                mode_name=task['m'],
                max_count=task['c'],
                keywords=all_keywords,
                is_mobile=task['mob'],
                settings=settings,
                is_auto_mode=is_auto_mode 
            )
            clean_system()
            
            if self.is_running:
                self.log_message("⏳ Nghỉ 5s chuyển task tiếp theo...")
                time.sleep(5)

        self.log_message("✅ HOÀN TẤT.")
        self.stop_bot()

    def start_thread(self):
        if self.is_running: return
        self.is_running = True
        
        # Khóa nút Start, Mở Stop
        self.btn_start.configure(state="disabled", fg_color="gray")
        self.btn_stop.configure(state="normal", fg_color="#e74c3c")
        
        # Khóa toàn bộ Controls và Inputs
        self.rb_auto.configure(state="disabled")
        self.rb_single.configure(state="disabled")
        self.profile_menu.configure(state="disabled")
        self.switch_mobile.configure(state="disabled")
        self.toggle_inputs("disabled") # KHÓA NHẬP LIỆU

        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.is_running = False
        if self.bot_core: self.bot_core.stop()
        
        self.btn_start.configure(state="normal", fg_color="#2ecc71")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        
        # Mở khóa lại Controls và Inputs
        self.rb_auto.configure(state="normal")
        self.rb_single.configure(state="normal")
        self.switch_mobile.configure(state="normal")
        self.toggle_inputs("normal") # MỞ KHÓA NHẬP LIỆU
        self.update_ui_state()
        
        self.log_message("⛔ ĐÃ DỪNG.")

    def on_closing(self):
        self.stop_bot()
        clean_system()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()