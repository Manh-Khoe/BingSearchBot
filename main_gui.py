import customtkinter as ctk
import threading
import sys
import random
import time
from datetime import datetime
from config import *
from utils import clean_system, load_keywords, save_settings_to_file, load_settings_from_file
from bot_core import BingBotCore

# Cài đặt giao diện
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MS Rewards Bot v5.7 (Auto Minimize & Delay)")
        self.geometry("980x750")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Load Settings
        saved_data = load_settings_from_file()
        self.cfg = {
            "pc": saved_data.get("pc_turns", DEFAULT_PC_TURNS) if saved_data else DEFAULT_PC_TURNS,
            "mob": saved_data.get("mob_turns", DEFAULT_MOBILE_TURNS) if saved_data else DEFAULT_MOBILE_TURNS,
            "int": saved_data.get("interval", DEFAULT_INTERVAL) if saved_data else DEFAULT_INTERVAL,
            "delay_task": saved_data.get("delay_task", DEFAULT_TASK_DELAY) if saved_data else DEFAULT_TASK_DELAY, # [MỚI]
            
            "min_t": saved_data.get("min_type", DEFAULT_MIN_TYPE) if saved_data else DEFAULT_MIN_TYPE,
            "max_t": saved_data.get("max_type", DEFAULT_MAX_TYPE) if saved_data else DEFAULT_MAX_TYPE,
            "think": saved_data.get("thinking", DEFAULT_THINKING) if saved_data else DEFAULT_THINKING,
            "min_r": saved_data.get("min_read", DEFAULT_MIN_READ) if saved_data else DEFAULT_MIN_READ,
            "max_r": saved_data.get("max_read", DEFAULT_MAX_READ) if saved_data else DEFAULT_MAX_READ,
            
            # Lưu chế độ chạy (Full/PC/Mobile) dưới dạng string
            "run_mode": saved_data.get("run_mode", "Full Run") if saved_data else "Full Run",
            "mode_auto": saved_data.get("mode_auto", True) if saved_data else True
        }

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text="Claim 🍟", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3498db")
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        # 1. Chế độ (Auto/Single)
        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="QUY MÔ CHẠY:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        init_mode = 0 if self.cfg["mode_auto"] else 1
        self.radio_var = ctk.IntVar(value=init_mode) 
        self.rb_auto = ctk.CTkRadioButton(self.sidebar, text=f"Auto All ({len(PROFILES_LIST)} Acc)", variable=self.radio_var, value=0, command=self.update_ui_state)
        self.rb_auto.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.rb_single = ctk.CTkRadioButton(self.sidebar, text="Single Profile", variable=self.radio_var, value=1, command=self.update_ui_state)
        self.rb_single.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # 2. Dropdown Tài khoản
        self.profile_menu = ctk.CTkOptionMenu(self.sidebar, values=PROFILES_LIST, width=180)
        self.profile_menu.grid(row=4, column=0, padx=20, pady=(5, 10))

        # 3. [MỚI] Thanh chọn chế độ (Full - PC - Mobile)
        self.lbl_type = ctk.CTkLabel(self.sidebar, text="LOẠI NHIỆM VỤ:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_type.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

        self.seg_mode = ctk.CTkSegmentedButton(self.sidebar, values=["Full Run", "PC Only", "Mobile Only"])
        self.seg_mode.set(self.cfg["run_mode"]) # Set giá trị mặc định/đã lưu
        self.seg_mode.grid(row=6, column=0, padx=20, pady=5)

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
        self.log_message("⚡ Sẵn sàng. (Auto Minimize bật)")

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#212121", corner_radius=10)
        self.settings_frame.pack(fill="x", pady=5, ipady=10)

        self.lbl_config = ctk.CTkLabel(self.settings_frame, text="⚙️ CẤU HÌNH THAM SỐ", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_config.pack(pady=10)

        self.grid_inputs = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.grid_inputs.pack(fill="x", padx=20)
        self.grid_inputs.grid_columnconfigure(0, weight=1)
        self.grid_inputs.grid_columnconfigure(1, weight=1)
        self.grid_inputs.grid_columnconfigure(2, weight=1)

        # Cột 1: Số lượng & Delay
        self.f1 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f1.grid(row=0, column=0, sticky="n")
        ctk.CTkLabel(self.f1, text="SỐ LƯỢNG", text_color="#3498db", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f1, "PC Count:", str(self.cfg["pc"]), "entry_pc")
        self.create_input(self.f1, "Mob Count:", str(self.cfg["mob"]), "entry_mob")
        self.create_input(self.f1, "Delay Task:", str(self.cfg["delay_task"]), "entry_delay") # [MỚI]

        # Cột 2
        self.f2 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f2.grid(row=0, column=1, sticky="n")
        ctk.CTkLabel(self.f2, text="TỐC ĐỘ GÕ (s)", text_color="#f39c12", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f2, "Min Type:", str(self.cfg["min_t"]), "entry_min_type")
        self.create_input(self.f2, "Max Type:", str(self.cfg["max_t"]), "entry_max_type")
        self.create_input(self.f2, "Thinking:", str(self.cfg["think"]), "entry_think")

        # Cột 3
        self.f3 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f3.grid(row=0, column=2, sticky="n")
        ctk.CTkLabel(self.f3, text="TỐC ĐỘ ĐỌC (s)", text_color="#e74c3c", font=("Arial", 12, "bold")).pack(pady=5)
        self.create_input(self.f3, "Min Read:", str(self.cfg["min_r"]), "entry_min_read")
        self.create_input(self.f3, "Max Read:", str(self.cfg["max_r"]), "entry_max_read")
        self.create_input(self.f3, "Interval:", str(self.cfg["int"]), "entry_int")

        self.bot_core = None
        self.is_running = False
        self.all_entries = [] 
        
        self.collect_entries()
        self.update_ui_state()

    def create_input(self, parent, label, placeholder, var_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2)
        ctk.CTkLabel(frame, text=label, width=90, anchor="e").pack(side="left", padx=(0, 5))
        entry = ctk.CTkEntry(frame, width=50, justify="center")
        entry.insert(0, placeholder)
        entry.pack(side="left")
        setattr(self, var_name, entry)

    def collect_entries(self):
        self.all_entries = [
            self.entry_pc, self.entry_mob, self.entry_int, self.entry_delay,
            self.entry_min_type, self.entry_max_type, self.entry_think,
            self.entry_min_read, self.entry_max_read
        ]

    def update_ui_state(self):
        if self.radio_var.get() == 0: 
            self.profile_menu.configure(state="disabled", fg_color="gray")
        else: 
            self.profile_menu.configure(state="normal", fg_color="#1f6aa5")

    def toggle_inputs(self, state):
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
            "delay_task": get_val(self.entry_delay, DEFAULT_TASK_DELAY), # [MỚI]
            
            "min_type": get_val(self.entry_min_type, DEFAULT_MIN_TYPE, True),
            "max_type": get_val(self.entry_max_type, DEFAULT_MAX_TYPE, True),
            "thinking": get_val(self.entry_think, DEFAULT_THINKING, True),
            "min_read": get_val(self.entry_min_read, DEFAULT_MIN_READ, True),
            "max_read": get_val(self.entry_max_read, DEFAULT_MAX_READ, True),
            
            "run_mode": self.seg_mode.get(), # Lấy giá trị từ thanh chọn (Full/PC/Mobile)
            "mode_auto": (self.radio_var.get() == 0)
        }

    def run_bot_process(self):
        clean_system()
        all_keywords = load_keywords()
        settings = self.get_settings()
        
        self.bot_core = BingBotCore(self.log_message)
        
        is_auto_mode = settings["mode_auto"]
        
        # 1. Chọn Profile
        target_profiles = []
        if is_auto_mode:
            target_profiles = PROFILES_LIST
            self.log_message(f"🚀 CHẾ ĐỘ: AUTO ALL ({len(target_profiles)} Acc)")
        else:
            selected = self.profile_menu.get()
            target_profiles = [selected]
            self.log_message(f"👤 CHẾ ĐỘ: SINGLE PROFILE [{selected}]")

        # 2. Xử lý Chế độ (Full / PC Only / Mobile Only)
        run_mode = settings["run_mode"] # "Full Run", "PC Only", "Mobile Only"
        self.log_message(f"🎯 LOẠI NHIỆM VỤ: {run_mode.upper()}")
        
        # 3. Tạo Hàng Đợi (Queue)
        queue = []
        for profile in target_profiles:
            # Nếu chế độ là Full hoặc PC Only -> Thêm PC
            if run_mode in ["Full Run", "PC Only"]:
                queue.append({"p": profile, "m": "PC", "c": settings['pc_turns'], "mob": False})
            
            # Nếu chế độ là Full hoặc Mobile Only -> Thêm Mobile
            if run_mode in ["Full Run", "Mobile Only"]:
                queue.append({"p": profile, "m": "MOBILE", "c": settings['mob_turns'], "mob": True})
        
        # Logic xáo trộn: Nếu chạy Auto All thì xáo trộn, Single thì theo thứ tự
        if len(target_profiles) > 1:
            random.shuffle(queue)
        
        self.log_message("-" * 40)

        # 4. CHẠY TASK
        for idx, task in enumerate(queue):
            if not self.is_running: break
            
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
            
            # [MỚI] Sử dụng Delay tùy chỉnh từ Settings
            if self.is_running and idx < len(queue) - 1:
                wait_sec = settings['delay_task']
                self.log_message(f"⏳ Nghỉ {wait_sec}s chuyển task...")
                time.sleep(wait_sec)

        self.log_message("✅ HOÀN TẤT.")
        self.stop_bot()

    def start_thread(self):
        if self.is_running: return
        self.is_running = True
        
        self.btn_start.configure(state="disabled", fg_color="gray")
        self.btn_stop.configure(state="normal", fg_color="#e74c3c")
        
        # Khóa inputs
        self.rb_auto.configure(state="disabled")
        self.rb_single.configure(state="disabled")
        self.profile_menu.configure(state="disabled")
        self.seg_mode.configure(state="disabled") # Khóa thanh chọn mode
        self.toggle_inputs("disabled")

        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.is_running = False
        if self.bot_core: self.bot_core.stop()
        
        self.btn_start.configure(state="normal", fg_color="#2ecc71")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        
        self.rb_auto.configure(state="normal")
        self.rb_single.configure(state="normal")
        self.seg_mode.configure(state="normal")
        self.toggle_inputs("normal")
        self.update_ui_state()
        
        self.log_message("⛔ ĐÃ DỪNG.")

    def on_closing(self):
        self.stop_bot()
        current_settings = self.get_settings()
        save_settings_to_file(current_settings)
        clean_system()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()