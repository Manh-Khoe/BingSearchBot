import customtkinter as ctk
import threading
import sys
import random
from config import PROFILES_LIST, DEFAULT_PC_TURNS, DEFAULT_MOBILE_TURNS
from utils import clean_system, load_keywords
from bot_core import BingBotCore

# Cài đặt giao diện
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MS Rewards Bot v5.1")
        self.geometry("900x600")
        
        # [CẬP NHẬT 1] Bắt sự kiện bấm nút X để tắt sạch chương trình
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR (Bên trái)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Claim 🍟", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3498db")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.lbl_mode = ctk.CTkLabel(self.sidebar_frame, text="Chế độ chạy:", anchor="w")
        self.lbl_mode.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.radio_var = ctk.IntVar(value=0)
        self.radio_button_1 = ctk.CTkRadioButton(self.sidebar_frame, text="Auto All (PC + Mobile)", variable=self.radio_var, value=0)
        self.radio_button_1.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.radio_button_2 = ctk.CTkRadioButton(self.sidebar_frame, text="PC Only", variable=self.radio_var, value=1)
        self.radio_button_2.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Nút Start / Stop
        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="BẮT ĐẦU", fg_color="#2ecc71", hover_color="#27ae60", command=self.start_thread)
        self.btn_start.grid(row=5, column=0, padx=20, pady=10)

        self.btn_stop = ctk.CTkButton(self.sidebar_frame, text="DỪNG LẠI", fg_color="#e74c3c", hover_color="#c0392b", state="disabled", command=self.stop_bot)
        self.btn_stop.grid(row=6, column=0, padx=20, pady=(0, 20))

        # 2. MAIN AREA (Bên phải - Log & Setting)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Màn hình Log (Console giả lập)
        self.log_box = ctk.CTkTextbox(self.main_frame, height=350, font=("Consolas", 13))
        self.log_box.pack(fill="x", pady=(0, 20))
        self.log_box.configure(state="disabled")
        self.log_message("--- Sẵn sàng chạy ---")

        # Khu vực Cấu hình tham số (Bên dưới)
        self.setting_frame = ctk.CTkFrame(self.main_frame)
        self.setting_frame.pack(fill="both", expand=True)
        
        self.lbl_set = ctk.CTkLabel(self.setting_frame, text="CẤU HÌNH THAM SỐ (Để trống = Mặc định)", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_set.pack(pady=10)
        
        # Grid input
        self.grid_inputs = ctk.CTkFrame(self.setting_frame, fg_color="transparent")
        self.grid_inputs.pack(pady=5)
        
        ctk.CTkLabel(self.grid_inputs, text="PC Turns:").grid(row=0, column=0, padx=10)
        self.entry_pc = ctk.CTkEntry(self.grid_inputs, placeholder_text=str(DEFAULT_PC_TURNS), width=60)
        self.entry_pc.grid(row=0, column=1)

        ctk.CTkLabel(self.grid_inputs, text="Mobile Turns:").grid(row=0, column=2, padx=10)
        self.entry_mob = ctk.CTkEntry(self.grid_inputs, placeholder_text=str(DEFAULT_MOBILE_TURNS), width=60)
        self.entry_mob.grid(row=0, column=3)

        # Logic Bot
        self.bot_core = None
        self.is_running = False

    def log_message(self, message):
        """Hàm nhận text và in vào ô đen"""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def get_config_values(self):
        try: pc = int(self.entry_pc.get())
        except: pc = DEFAULT_PC_TURNS
        
        try: mob = int(self.entry_mob.get())
        except: mob = DEFAULT_MOBILE_TURNS
        return pc, mob

    def run_bot_process(self):
        # Dọn dẹp trước khi bắt đầu để tránh lỗi driver cũ
        clean_system()
        
        all_keywords = load_keywords()
        pc_turns, mob_turns = self.get_config_values()
        
        self.bot_core = BingBotCore(self.log_message)
        
        queue = []
        for profile in PROFILES_LIST:
            # Luôn thêm PC
            queue.append({"p": profile, "m": "PC", "c": pc_turns, "mob": False})
            # Nếu chọn mode Auto All thì thêm Mobile
            if self.radio_var.get() == 0:
                 queue.append({"p": profile, "m": "MOBILE", "c": mob_turns, "mob": True})
        
        random.shuffle(queue)
        
        self.log_message(f"=== BẮT ĐẦU CHẠY {len(queue)} NHIỆM VỤ ===")

        for task in queue:
            if not self.is_running: break
            
            self.bot_core.run_browser(
                profile_dir=task['p'],
                mode_name=task['m'],
                max_count=task['c'],
                keywords=all_keywords,
                is_mobile=task['mob']
            )
            # Dọn dẹp sau mỗi task
            clean_system()
            
            if self.is_running:
                self.log_message("--> Nghỉ 5s chuyển task...")
                time.sleep(5)

        self.log_message("=== HOÀN THÀNH TẤT CẢ ===")
        self.stop_bot()

    def start_thread(self):
        if self.is_running: return
        self.is_running = True
        self.btn_start.configure(state="disabled", fg_color="gray")
        self.btn_stop.configure(state="normal", fg_color="#e74c3c")
        
        # Chạy bot ở luồng riêng để không đơ giao diện
        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.is_running = False
        if self.bot_core:
            self.bot_core.stop()
        
        self.btn_start.configure(state="normal", fg_color="#2ecc71")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        self.log_message("!!! ĐÃ DỪNG !!!")

    # [CẬP NHẬT 2] Hàm xử lý khi bấm nút X
    def on_closing(self):
        """Hàm này chạy khi bấm nút X tắt chương trình"""
        self.stop_bot() # Dừng bot
        clean_system()  # Diệt sạch tiến trình Edge/Driver
        self.destroy()  # Tắt giao diện
        sys.exit()      # Thoát Python

if __name__ == "__main__":
    app = App()
    app.mainloop()