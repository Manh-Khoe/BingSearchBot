import customtkinter as ctk
import threading
import sys
import random
import time
import queue  # <--- THÊM THƯ VIỆN NÀY
from datetime import datetime
from config import *
from utils import clean_system, load_keywords, save_settings_to_file, load_settings_from_file, load_daily_stats, save_daily_stats
from bot_core import BingBotCore

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MS Rewards Bot v6.1 (No-Lag Edition)")
        self.geometry("1000x780")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- 1. KHỞI TẠO QUEUE (HỘP THƯ) ---
        self.log_queue = queue.Queue()
        self.stats_queue = queue.Queue()

        # Load Settings & Stats
        saved_data = load_settings_from_file()
        self.daily_stats = load_daily_stats()
        
        self.cfg = {
            "pc": saved_data.get("pc_turns", DEFAULT_PC_TURNS) if saved_data else DEFAULT_PC_TURNS,
            "mob": saved_data.get("mob_turns", DEFAULT_MOBILE_TURNS) if saved_data else DEFAULT_MOBILE_TURNS,
            "int": saved_data.get("interval", DEFAULT_INTERVAL) if saved_data else DEFAULT_INTERVAL,
            "delay_task": saved_data.get("delay_task", DEFAULT_TASK_DELAY) if saved_data else DEFAULT_TASK_DELAY,
            
            "min_t": saved_data.get("min_type", DEFAULT_MIN_TYPE) if saved_data else DEFAULT_MIN_TYPE,
            "max_t": saved_data.get("max_type", DEFAULT_MAX_TYPE) if saved_data else DEFAULT_MAX_TYPE,
            "think": saved_data.get("thinking", DEFAULT_THINKING) if saved_data else DEFAULT_THINKING,
            "min_r": saved_data.get("min_read", DEFAULT_MIN_READ) if saved_data else DEFAULT_MIN_READ,
            "max_r": saved_data.get("max_read", DEFAULT_MAX_READ) if saved_data else DEFAULT_MAX_READ,
            
            "run_mode": saved_data.get("run_mode", "Full Run") if saved_data else "Full Run",
            "mode_auto": saved_data.get("mode_auto", True) if saved_data else True
        }

        # --- LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text="Claim 🍟", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3498db")
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="QUY MÔ CHẠY:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        init_mode = 0 if self.cfg["mode_auto"] else 1
        self.radio_var = ctk.IntVar(value=init_mode) 
        self.rb_auto = ctk.CTkRadioButton(self.sidebar, text=f"Auto All ({len(PROFILES_LIST)} Acc)", variable=self.radio_var, value=0, command=self.update_ui_state)
        self.rb_auto.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.rb_single = ctk.CTkRadioButton(self.sidebar, text="Single Profile", variable=self.radio_var, value=1, command=self.update_ui_state)
        self.rb_single.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.profile_menu = ctk.CTkOptionMenu(self.sidebar, values=PROFILES_LIST, width=180)
        self.profile_menu.grid(row=4, column=0, padx=20, pady=(5, 10))

        self.lbl_type = ctk.CTkLabel(self.sidebar, text="LOẠI NHIỆM VỤ:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_type.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

        self.seg_mode = ctk.CTkSegmentedButton(self.sidebar, values=["Full Run", "PC Only", "Mobile Only"])
        self.seg_mode.set(self.cfg["run_mode"]) 
        self.seg_mode.grid(row=6, column=0, padx=20, pady=5)

        self.btn_start = ctk.CTkButton(self.sidebar, text="▶ BẮT ĐẦU", height=40, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_thread)
        self.btn_start.grid(row=9, column=0, padx=20, pady=(10, 10))
        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹ DỪNG LẠI", height=40, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(size=14, weight="bold"), state="disabled", command=self.stop_bot)
        self.btn_stop.grid(row=10, column=0, padx=20, pady=(0, 30))

        # === MAIN AREA ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- SCOREBOARD ---
        self.score_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a", corner_radius=10)
        self.score_frame.pack(fill="x", pady=(0, 15))

        headers = ["TÀI KHOẢN", "TRẠNG THÁI", "ĐIỂM ĐẦU", "ĐIỂM CUỐI", "KIẾM ĐƯỢC"]
        self.score_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        for idx, h in enumerate(headers):
            ctk.CTkLabel(self.score_frame, text=h, font=("Arial", 12, "bold"), text_color="#bdc3c7").grid(row=0, column=idx, pady=10)

        self.row_widgets = {} 
        for idx, profile in enumerate(PROFILES_LIST):
            r = idx + 1
            p_data = self.daily_stats["data"].get(profile, {})
            stat_txt = p_data.get("status", "Chờ chạy")
            start_txt = str(p_data.get("start", "---"))
            curr_txt = str(p_data.get("current", "---"))
            gain_txt = f"+{p_data.get('current', 0) - p_data.get('start', 0)}" if p_data.get("start") else "---"
            
            color = "#bdc3c7"
            if stat_txt == "Running": color = "#f1c40f"
            elif stat_txt == "Done": color = "#2ecc71"

            l_name = ctk.CTkLabel(self.score_frame, text=profile, font=("Arial", 13))
            l_stat = ctk.CTkLabel(self.score_frame, text=stat_txt, text_color=color, font=("Arial", 13, "bold"))
            l_start = ctk.CTkLabel(self.score_frame, text=start_txt)
            l_curr = ctk.CTkLabel(self.score_frame, text=curr_txt)
            l_gain = ctk.CTkLabel(self.score_frame, text=gain_txt, text_color="#2ecc71")

            l_name.grid(row=r, column=0, pady=5)
            l_stat.grid(row=r, column=1, pady=5)
            l_start.grid(row=r, column=2, pady=5)
            l_curr.grid(row=r, column=3, pady=5)
            l_gain.grid(row=r, column=4, pady=5)

            self.row_widgets[profile] = {
                "stat": l_stat, "start": l_start, "curr": l_curr, "gain": l_gain
            }

        # --- LOG BOX ---
        self.log_box = ctk.CTkTextbox(self.main_frame, height=250, font=("Consolas", 12))
        self.log_box.pack(fill="both", expand=True, pady=(0, 15))
        self.log_box.configure(state="disabled")

        # --- SETTINGS ---
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#212121", corner_radius=10)
        self.settings_frame.pack(fill="x", pady=5, ipady=5)

        self.grid_inputs = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.grid_inputs.pack(fill="x", padx=20, pady=5)
        self.grid_inputs.grid_columnconfigure((0,1,2), weight=1)

        # Cột 1
        self.f1 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f1.grid(row=0, column=0, sticky="n")
        ctk.CTkLabel(self.f1, text="SỐ LƯỢNG", text_color="#3498db", font=("Arial", 11, "bold")).pack(pady=2)
        self.create_input(self.f1, "PC Count:", str(self.cfg["pc"]), "entry_pc")
        self.create_input(self.f1, "Mob Count:", str(self.cfg["mob"]), "entry_mob")
        self.create_input(self.f1, "Delay Task:", str(self.cfg["delay_task"]), "entry_delay")

        # Cột 2
        self.f2 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f2.grid(row=0, column=1, sticky="n")
        ctk.CTkLabel(self.f2, text="TỐC ĐỘ GÕ", text_color="#f39c12", font=("Arial", 11, "bold")).pack(pady=2)
        self.create_input(self.f2, "Min Type:", str(self.cfg["min_t"]), "entry_min_type")
        self.create_input(self.f2, "Max Type:", str(self.cfg["max_t"]), "entry_max_type")
        self.create_input(self.f2, "Thinking:", str(self.cfg["think"]), "entry_think")

        # Cột 3
        self.f3 = ctk.CTkFrame(self.grid_inputs, fg_color="transparent")
        self.f3.grid(row=0, column=2, sticky="n")
        ctk.CTkLabel(self.f3, text="TỐC ĐỘ ĐỌC", text_color="#e74c3c", font=("Arial", 11, "bold")).pack(pady=2)
        self.create_input(self.f3, "Min Read:", str(self.cfg["min_r"]), "entry_min_read")
        self.create_input(self.f3, "Max Read:", str(self.cfg["max_r"]), "entry_max_read")
        self.create_input(self.f3, "Interval:", str(self.cfg["int"]), "entry_int")

        self.bot_core = None
        self.is_running = False
        self.all_entries = [] 
        self.collect_entries()
        self.update_ui_state()

        # --- BẮT ĐẦU VÒNG LẶP CHECK QUEUE ---
        self.process_queue_updates()

    # --- HÀM MỚI: XỬ LÝ QUEUE ĐỂ CẬP NHẬT UI ---
    def process_queue_updates(self):
        # 1. Xử lý Log
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                self.log_box.insert("end", f"{msg}\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty:
            pass

        # 2. Xử lý Stats
        try:
            while True:
                data = self.stats_queue.get_nowait()
                self.update_stats_ui_implementation(**data)
        except queue.Empty:
            pass

        # Gọi lại hàm này sau 100ms
        self.after(100, self.process_queue_updates)

    # --- HÀM GỌI TỪ BOT (CHỈ PUT VÀO QUEUE) ---
    def log_message(self, message):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log_queue.put(f"{now} {message}")

    def update_stats_ui(self, profile, status=None, start_p=None, current_p=None):
        # Đóng gói dữ liệu và gửi vào Queue
        data = {
            "profile": profile,
            "status": status,
            "start_p": start_p,
            "current_p": current_p
        }
        self.stats_queue.put(data)

    # --- HÀM THỰC THI UI (CHẠY Ở MAIN THREAD) ---
    def update_stats_ui_implementation(self, profile, status=None, start_p=None, current_p=None):
        if profile not in self.row_widgets: return

        p_data = self.daily_stats["data"].setdefault(profile, {})
        
        if status:
            p_data["status"] = status
            color = "#bdc3c7"
            if status == "Running": color = "#f1c40f"
            elif status == "Done": color = "#2ecc71"
            self.row_widgets[profile]["stat"].configure(text=status, text_color=color)
        
        if start_p is not None:
            if "start" not in p_data:
                p_data["start"] = start_p
                self.row_widgets[profile]["start"].configure(text=str(start_p))
        
        if current_p is not None:
            p_data["current"] = current_p
            self.row_widgets[profile]["curr"].configure(text=str(current_p))
            if "start" in p_data:
                gain = current_p - p_data["start"]
                self.row_widgets[profile]["gain"].configure(text=f"+{gain}")
        
        save_daily_stats(self.daily_stats)

    def create_input(self, parent, label, placeholder, var_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2)
        ctk.CTkLabel(frame, text=label, width=80, anchor="e").pack(side="left", padx=(0, 5))
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
            "delay_task": get_val(self.entry_delay, DEFAULT_TASK_DELAY),
            
            "min_type": get_val(self.entry_min_type, DEFAULT_MIN_TYPE, True),
            "max_type": get_val(self.entry_max_type, DEFAULT_MAX_TYPE, True),
            "thinking": get_val(self.entry_think, DEFAULT_THINKING, True),
            "min_read": get_val(self.entry_min_read, DEFAULT_MIN_READ, True),
            "max_read": get_val(self.entry_max_read, DEFAULT_MAX_READ, True),
            "run_mode": self.seg_mode.get(),
            "mode_auto": (self.radio_var.get() == 0)
        }

    def run_bot_process(self):
        # ... (Code phần này giữ nguyên như cũ, chỉ gọi bot core) ...
        clean_system()
        all_keywords = load_keywords()
        settings = self.get_settings()
        
        self.bot_core = BingBotCore(self.log_message, self.update_stats_ui)
        
        is_auto_mode = settings["mode_auto"]
        target_profiles = PROFILES_LIST if is_auto_mode else [self.profile_menu.get()]
        
        if is_auto_mode: self.log_message(f"🚀 CHẾ ĐỘ: AUTO ALL")
        else: self.log_message(f"👤 CHẾ ĐỘ: SINGLE [{target_profiles[0]}]")

        run_mode = settings["run_mode"]
        queue_tasks = []
        for profile in target_profiles:
            if run_mode in ["Full Run", "PC Only"]:
                queue_tasks.append({"p": profile, "m": "PC", "c": settings['pc_turns'], "mob": False})
            if run_mode in ["Full Run", "Mobile Only"]:
                queue_tasks.append({"p": profile, "m": "MOBILE", "c": settings['mob_turns'], "mob": True})
        
        if len(target_profiles) > 1: random.shuffle(queue_tasks)
        
        self.log_message("-" * 40)

        for idx, task in enumerate(queue_tasks):
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
            
            if self.is_running and idx < len(queue_tasks) - 1:
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
        
        self.rb_auto.configure(state="disabled")
        self.rb_single.configure(state="disabled")
        self.profile_menu.configure(state="disabled")
        self.seg_mode.configure(state="disabled")
        self.toggle_inputs("disabled")

        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        # Hàm này phải chạy ở Main Thread để update UI nút bấm
        # Nếu gọi từ thread bot, ta phải dùng .after để đẩy về Main Thread
        self.after(0, self._stop_bot_implementation)

    def _stop_bot_implementation(self):
        self.is_running = False
        if self.bot_core: self.bot_core.stop()
        
        self.btn_start.configure(state="normal", fg_color="#2ecc71")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        
        self.rb_auto.configure(state="normal")
        self.rb_single.configure(state="normal")
        self.seg_mode.configure(state="normal")
        self.toggle_inputs("normal")
        self.update_ui_state()
        
        # Không cần log ở đây nữa vì bot_process sẽ log "HOÀN TẤT"
        
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