import customtkinter as ctk
import threading
import sys
import random
import time
import queue
import os
from datetime import datetime
from config import *
from utils import clean_system, load_keywords, save_settings_to_file, load_settings_from_file, load_daily_stats, save_daily_stats
from bot_core import BingBotCore

# --- CẤU HÌNH GIAO DIỆN CHUNG ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Bảng màu Cyberpunk/Modern
COLOR_BG = "#121212"          # Nền chính siêu tối
COLOR_SIDEBAR = "#1e1e1e"     # Nền sidebar
COLOR_CARD = "#252526"        # Nền các khung (Card)
COLOR_ACCENT = "#00e5ff"      # Màu xanh Neon (Cyan) cho điểm nhấn
COLOR_TEXT = "#ffffff"        # Màu chữ trắng
COLOR_SUCCESS = "#00b894"     # Màu xanh lá (Start/Done)
COLOR_DANGER = "#d63031"      # Màu đỏ (Stop/Error)
COLOR_WARNING = "#fab1a0"     # Màu cam nhạt (Running)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bing Rewards Bot v7.0 | Ultimate Edition")
        self.geometry("1100x800")
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Thử load icon nếu có file .ico bên cạnh
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except: pass

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

        # --- LAYOUT CHÍNH (GRID 1x2) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===================================================
        # [CỘT 0] SIDEBAR - ĐIỀU KHIỂN
        # ===================================================
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20))
        ctk.CTkLabel(self.logo_frame, text="BING BOT", font=("Impact", 32), text_color=COLOR_ACCENT).pack()
        ctk.CTkLabel(self.logo_frame, text="v7.0 Cyberpunk", font=("Arial", 10), text_color="gray").pack()

        # Mode Selection
        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="🤖 CHẾ ĐỘ CHẠY", anchor="w", font=("Roboto", 12, "bold"), text_color="#bdc3c7")
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        init_mode = 0 if self.cfg["mode_auto"] else 1
        self.radio_var = ctk.IntVar(value=init_mode) 
        
        self.rb_auto = ctk.CTkRadioButton(self.sidebar, text=f"Auto All ({len(PROFILES_LIST)} acc)", variable=self.radio_var, value=0, 
                                          command=self.update_ui_state, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT)
        self.rb_auto.grid(row=2, column=0, padx=20, pady=8, sticky="w")
        
        self.rb_single = ctk.CTkRadioButton(self.sidebar, text="Chạy lẻ (Single)", variable=self.radio_var, value=1, 
                                            command=self.update_ui_state, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT)
        self.rb_single.grid(row=3, column=0, padx=20, pady=8, sticky="w")

        self.profile_menu = ctk.CTkOptionMenu(self.sidebar, values=PROFILES_LIST, width=200, fg_color="#34495e", button_color="#2c3e50")
        self.profile_menu.grid(row=4, column=0, padx=20, pady=(0, 15))

        # Task Type
        self.lbl_type = ctk.CTkLabel(self.sidebar, text="🎯 LOẠI NHIỆM VỤ", anchor="w", font=("Roboto", 12, "bold"), text_color="#bdc3c7")
        self.lbl_type.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")

        self.seg_mode = ctk.CTkSegmentedButton(self.sidebar, values=["Full Run", "PC Only", "Mobile Only"], 
                                               selected_color=COLOR_ACCENT, selected_hover_color="#00cec9")
        self.seg_mode.set(self.cfg["run_mode"]) 
        self.seg_mode.grid(row=6, column=0, padx=20, pady=5)

        # Buttons
        self.btn_start = ctk.CTkButton(self.sidebar, text="▶  BẮT ĐẦU CHẠY", height=50, corner_radius=8,
                                       fg_color=COLOR_SUCCESS, hover_color="#00a884", 
                                       font=("Roboto", 16, "bold"), command=self.start_thread)
        self.btn_start.grid(row=8, column=0, padx=20, pady=(40, 10))
        
        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹  DỪNG KHẨN CẤP", height=40, corner_radius=8,
                                      fg_color=COLOR_DANGER, hover_color="#c0392b", state="disabled", 
                                      font=("Roboto", 14, "bold"), command=self.stop_bot)
        self.btn_stop.grid(row=9, column=0, padx=20, pady=(0, 20))

        # Footer
        ctk.CTkLabel(self.sidebar, text="Designed by You", font=("Arial", 10), text_color="#555").grid(row=11, column=0, pady=10)


        # ===================================================
        # [CỘT 1] MAIN AREA - HIỂN THỊ
        # ===================================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- 1. BẢNG THỐNG KÊ (SCOREBOARD) ---
        self.score_card = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color="#333")
        self.score_card.pack(fill="x", pady=(0, 15))
        
        # Title Card
        ctk.CTkLabel(self.score_card, text=" BẢNG THÀNH TÍCH (SESSION STATS)", font=("Roboto", 13, "bold"), text_color="gray").pack(pady=(10,5))
        
        # Grid Header
        self.grid_header = ctk.CTkFrame(self.score_card, fg_color="transparent")
        self.grid_header.pack(fill="x", padx=10)
        headers = ["TÀI KHOẢN", "TRẠNG THÁI", "ĐIỂM ĐẦU", "ĐIỂM CUỐI", "KIẾM ĐƯỢC"]
        self.grid_header.grid_columnconfigure((0,1,2,3,4), weight=1)
        for idx, h in enumerate(headers):
            ctk.CTkLabel(self.grid_header, text=h, font=("Arial", 11, "bold"), text_color=COLOR_ACCENT).grid(row=0, column=idx, pady=5)

        # Scrollable Rows (Nếu có nhiều acc)
        self.rows_frame = ctk.CTkScrollableFrame(self.score_card, height=180, fg_color="transparent")
        self.rows_frame.pack(fill="x", padx=5, pady=(0, 10))
        self.rows_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        self.row_widgets = {} 
        self.render_scoreboard_rows() # Vẽ hàng

        # --- 2. LOG CONSOLE (TERMINAL STYLE) ---
        self.log_frame = ctk.CTkFrame(self.main_frame, fg_color="#000000", corner_radius=10, border_width=1, border_color="#333")
        self.log_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(self.log_frame, text=" SYSTEM LOGS", font=("Consolas", 12, "bold"), text_color="#555", anchor="w").pack(fill="x", padx=10, pady=(5,0))
        
        self.log_box = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12), text_color="#00ff00", fg_color="transparent", activate_scrollbars=True)
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box.configure(state="disabled")

        # --- 3. SETTINGS PANEL (THẺ CẤU HÌNH) ---
        self.settings_card = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color="#333")
        self.settings_card.pack(fill="x", pady=5)

        # Chia 3 cột settings
        self.grid_inputs = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.grid_inputs.pack(fill="x", padx=20, pady=15)
        self.grid_inputs.grid_columnconfigure((0,1,2), weight=1)

        # Cột 1: Số lượng
        self.f1 = self.create_setting_group(self.grid_inputs, 0, "⚙️ SỐ LƯỢNG (Limit)", "#3498db")
        self.create_input(self.f1, "PC Search:", str(self.cfg["pc"]), "entry_pc")
        self.create_input(self.f1, "Mob Search:", str(self.cfg["mob"]), "entry_mob")
        self.create_input(self.f1, "Nghỉ giữa acc:", str(self.cfg["delay_task"]), "entry_delay")

        # Cột 2: Tốc độ gõ
        self.f2 = self.create_setting_group(self.grid_inputs, 1, "⌨️ TỐC ĐỘ GÕ (Typing)", "#f39c12")
        self.create_input(self.f2, "Min Speed (s):", str(self.cfg["min_t"]), "entry_min_type")
        self.create_input(self.f2, "Max Speed (s):", str(self.cfg["max_t"]), "entry_max_type")
        self.create_input(self.f2, "Suy nghĩ (s):", str(self.cfg["think"]), "entry_think")

        # Cột 3: Tốc độ đọc
        self.f3 = self.create_setting_group(self.grid_inputs, 2, "👀 TỐC ĐỘ ĐỌC (Reading)", "#e74c3c")
        self.create_input(self.f3, "Min Read (s):", str(self.cfg["min_r"]), "entry_min_read")
        self.create_input(self.f3, "Max Read (s):", str(self.cfg["max_r"]), "entry_max_read")
        self.create_input(self.f3, "Check mỗi:", str(self.cfg["int"]), "entry_int")

        self.bot_core = None
        self.is_running = False
        self.all_entries = [] 
        self.collect_entries()
        self.update_ui_state()

        # --- BẮT ĐẦU VÒNG LẶP CHECK QUEUE ---
        self.process_queue_updates()

    # ================= UI HELPER FUNCTIONS =================
    def render_scoreboard_rows(self):
        # Xóa cũ (nếu có) nhưng ở đây ta init 1 lần, update text thôi
        for idx, profile in enumerate(PROFILES_LIST):
            r = idx
            p_data = self.daily_stats["data"].get(profile, {})
            stat_txt = p_data.get("status", "Sẵn sàng")
            start_txt = str(p_data.get("start", "---"))
            curr_txt = str(p_data.get("current", "---"))
            gain_val = p_data.get('current', 0) - p_data.get('start', 0) if p_data.get("start") else 0
            gain_txt = f"+{gain_val}" if p_data.get("start") else "---"

            color = "gray"
            if stat_txt == "Running": color = COLOR_WARNING
            elif stat_txt == "Done": color = COLOR_SUCCESS

            l_name = ctk.CTkLabel(self.rows_frame, text=profile, font=("Arial", 13))
            l_stat = ctk.CTkLabel(self.rows_frame, text=stat_txt, text_color=color, font=("Arial", 12, "bold"))
            l_start = ctk.CTkLabel(self.rows_frame, text=start_txt)
            l_curr = ctk.CTkLabel(self.rows_frame, text=curr_txt)
            l_gain = ctk.CTkLabel(self.rows_frame, text=gain_txt, text_color=COLOR_ACCENT if gain_val > 0 else "gray")

            l_name.grid(row=r, column=0, pady=5)
            l_stat.grid(row=r, column=1, pady=5)
            l_start.grid(row=r, column=2, pady=5)
            l_curr.grid(row=r, column=3, pady=5)
            l_gain.grid(row=r, column=4, pady=5)

            self.row_widgets[profile] = {
                "stat": l_stat, "start": l_start, "curr": l_curr, "gain": l_gain
            }

    def create_setting_group(self, parent, col, title, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="n", padx=10)
        ctk.CTkLabel(frame, text=title, text_color=color, font=("Arial", 12, "bold")).pack(pady=(0, 10))
        return frame

    def create_input(self, parent, label, placeholder, var_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2, fill="x")
        ctk.CTkLabel(frame, text=label, width=90, anchor="w", text_color="#bdc3c7").pack(side="left")
        entry = ctk.CTkEntry(frame, width=60, justify="center", fg_color="#121212", border_color="#444")
        entry.insert(0, placeholder)
        entry.pack(side="right")
        setattr(self, var_name, entry)

    # ================= LOGIC FUNCTIONS (NO CHANGE IN LOGIC) =================
    def process_queue_updates(self):
        # 1. Log
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                
                # Auto clear log if too long (Memory optimization)
                if len(self.log_box.get("1.0", "end")) > 5000: 
                    self.log_box.delete("1.0", "50.0")

                self.log_box.insert("end", f"{msg}\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty:
            pass

        # 2. Stats
        try:
            while True:
                data = self.stats_queue.get_nowait()
                self.update_stats_ui_implementation(**data)
        except queue.Empty:
            pass

        self.after(100, self.process_queue_updates)

    def log_message(self, message):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log_queue.put(f"{now} {message}")

    def update_stats_ui(self, profile, status=None, start_p=None, current_p=None):
        data = {"profile": profile, "status": status, "start_p": start_p, "current_p": current_p}
        self.stats_queue.put(data)

    def update_stats_ui_implementation(self, profile, status=None, start_p=None, current_p=None):
        if profile not in self.row_widgets: return

        p_data = self.daily_stats["data"].setdefault(profile, {})
        
        if status:
            p_data["status"] = status
            color = "gray"
            if status == "Running": color = COLOR_WARNING
            elif status == "Done": color = COLOR_SUCCESS
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
                self.row_widgets[profile]["gain"].configure(text=f"+{gain}", text_color=COLOR_ACCENT)
        
        save_daily_stats(self.daily_stats)

    def collect_entries(self):
        self.all_entries = [
            self.entry_pc, self.entry_mob, self.entry_int, self.entry_delay,
            self.entry_min_type, self.entry_max_type, self.entry_think,
            self.entry_min_read, self.entry_max_read
        ]

    def update_ui_state(self):
        if self.radio_var.get() == 0: 
            self.profile_menu.configure(state="disabled", fg_color="#2c3e50")
        else: 
            self.profile_menu.configure(state="normal", fg_color="#34495e")

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
        
        self.btn_start.configure(state="disabled", fg_color="#2d3436")
        self.btn_stop.configure(state="normal", fg_color=COLOR_DANGER)
        
        self.rb_auto.configure(state="disabled")
        self.rb_single.configure(state="disabled")
        self.profile_menu.configure(state="disabled")
        self.seg_mode.configure(state="disabled")
        self.toggle_inputs("disabled")

        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.after(0, self._stop_bot_implementation)

    def _stop_bot_implementation(self):
        self.is_running = False
        if self.bot_core: self.bot_core.stop()
        
        self.btn_start.configure(state="normal", fg_color=COLOR_SUCCESS)
        self.btn_stop.configure(state="disabled", fg_color="#2d3436")
        
        self.rb_auto.configure(state="normal")
        self.rb_single.configure(state="normal")
        self.seg_mode.configure(state="normal")
        self.toggle_inputs("normal")
        self.update_ui_state()

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