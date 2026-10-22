import customtkinter as ctk
import threading
import sys
import queue
import os
from datetime import datetime
from ui.theme import *
from ui.settings_window import SettingsWindow
from core.config_manager import ConfigManager
from core.coordinator import BotCoordinator
from utils import clean_system, load_daily_stats, save_daily_stats

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    """Giao diện chính Bing Rewards Bot v8.1 | Windows 11 Fluent Dark Mode"""
    def __init__(self):
        super().__init__()

        self.title("Bing Rewards Bot v8.1 | Edge Native Edition")
        self.geometry("1160x820")
        self.minsize(980, 720)
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except: pass

        self.cfg = ConfigManager.load()
        self.daily_stats = load_daily_stats()

        self.log_queue = queue.Queue()
        self.stats_queue = queue.Queue()

        self.coordinator = None
        self.is_running = False

        # =====================================================================
        # LAYOUT: 2 CỘT
        # =====================================================================
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # [CỘT 0] SIDEBAR NAV RAIL
        # ---------------------------------------------------------------------
        self.sidebar = ctk.CTkScrollableFrame(self, width=260, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Logo
        self.logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_box.pack(fill="x", padx=15, pady=(20, 15))
        ctk.CTkLabel(self.logo_box, text="BING BOT", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_ACCENT).pack(anchor="w")
        ctk.CTkLabel(self.logo_box, text="v8.1 Edge Native", font=(FONT_FAMILY, 11), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w")

        # 1. CHẾ ĐỘ HỒ SƠ (AUTO ALL vs CHẠY LẺ)
        ctk.CTkLabel(self.sidebar, text="🤖 CHẾ ĐỘ HỒ SƠ", font=(FONT_FAMILY, 11, "bold"), text_color="#bdc3c7").pack(anchor="w", padx=15, pady=(5, 3))
        
        self.radio_mode_var = ctk.IntVar(value=0) # 0: Auto All, 1: Single
        self.rb_auto = ctk.CTkRadioButton(
            self.sidebar, text="Chạy tất cả (Auto All)", variable=self.radio_mode_var, value=0,
            command=self.update_ui_profile_state, font=(FONT_FAMILY, 12), fg_color=COLOR_ACCENT
        )
        self.rb_auto.pack(anchor="w", padx=20, pady=4)

        self.rb_single = ctk.CTkRadioButton(
            self.sidebar, text="Chạy lẻ 1 hồ sơ", variable=self.radio_mode_var, value=1,
            command=self.update_ui_profile_state, font=(FONT_FAMILY, 12), fg_color=COLOR_ACCENT
        )
        self.rb_single.pack(anchor="w", padx=20, pady=4)

        profiles_list = self.cfg.get("pc", {}).get("profiles", ["Profile 1"])
        self.profile_menu = ctk.CTkOptionMenu(
            self.sidebar, values=profiles_list, width=220, height=32,
            fg_color="#2c3e50", button_color="#1a252f", font=(FONT_FAMILY, 12)
        )
        self.profile_menu.pack(padx=15, pady=(4, 15))

        # 2. CẦN GẠT LOẠI NHIỆM VỤ (SEGMENTED BUTTON: ALL / PC / MOBILE)
        ctk.CTkLabel(self.sidebar, text="🎯 LOẠI NHIỆM VỤ (NỀN TẢNG)", font=(FONT_FAMILY, 11, "bold"), text_color="#bdc3c7").pack(anchor="w", padx=15, pady=(5, 3))
        
        self.seg_mode = ctk.CTkSegmentedButton(
            self.sidebar, values=["Full Run", "PC Only", "Mobile Only"],
            selected_color=COLOR_ACCENT, selected_hover_color=COLOR_ACCENT_HOVER,
            unselected_color=COLOR_CARD, font=(FONT_FAMILY, 11, "bold")
        )
        self.seg_mode.set("Full Run")
        self.seg_mode.pack(fill="x", padx=15, pady=(2, 15))

        # 3. TÙY CHỌN CHI TIẾT (CHECKBOXES)
        ctk.CTkLabel(self.sidebar, text="⚙️ NHIỆM VỤ CHI TIẾT", font=(FONT_FAMILY, 11, "bold"), text_color="#3498db").pack(anchor="w", padx=15, pady=(5, 3))

        self.chk_pc_search = ctk.CTkCheckBox(self.sidebar, text="PC Search (Desktop)", font=(FONT_FAMILY, 12), fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        if self.cfg.get("pc", {}).get("do_search", True): self.chk_pc_search.select()
        self.chk_pc_search.pack(anchor="w", padx=20, pady=3)

        self.chk_pc_sets = ctk.CTkCheckBox(self.sidebar, text="PC Daily Sets & Quizzes", font=(FONT_FAMILY, 12), fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        if self.cfg.get("pc", {}).get("do_daily_sets", True): self.chk_pc_sets.select()
        self.chk_pc_sets.pack(anchor="w", padx=20, pady=3)

        self.chk_mob_search = ctk.CTkCheckBox(self.sidebar, text="Mobile Search (EdgA)", font=(FONT_FAMILY, 12), fg_color="#e67e22", hover_color="#d35400")
        if self.cfg.get("mobile", {}).get("do_search", True): self.chk_mob_search.select()
        self.chk_mob_search.pack(anchor="w", padx=20, pady=3)

        # 4. TÙY CHỌN HỆ THỐNG
        ctk.CTkLabel(self.sidebar, text="⚙️ HỆ THỐNG", font=(FONT_FAMILY, 11, "bold"), text_color="#bdc3c7").pack(anchor="w", padx=15, pady=(12, 3))
        
        self.switch_close = ctk.CTkSwitch(self.sidebar, text="Tự tắt bot khi xong", font=(FONT_FAMILY, 12), progress_color=COLOR_ACCENT)
        if self.cfg.get("general", {}).get("auto_close", False): self.switch_close.select()
        self.switch_close.pack(anchor="w", padx=20, pady=4)

        # NÚT BÁNH RĂNG CÀI ĐẶT
        self.btn_open_settings = ctk.CTkButton(
            self.sidebar, text="⚙️ Cài đặt chuyên sâu", height=38, corner_radius=8,
            fg_color=COLOR_CARD, hover_color=COLOR_CARD_HOVER, border_width=1, border_color=COLOR_BORDER,
            font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT, command=self.open_settings_dialog
        )
        self.btn_open_settings.pack(fill="x", padx=15, pady=(20, 15))

        # ---------------------------------------------------------------------
        # [CỘT 1] DASHBOARD CHÍNH
        # ---------------------------------------------------------------------
        self.content_view = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.content_view.grid(row=0, column=1, sticky="nsew", padx=25, pady=20)
        self.content_view.grid_rowconfigure(2, weight=1)
        self.content_view.grid_columnconfigure(0, weight=1)

        # 1. HERO ACTION CARD
        self.hero_card = ctk.CTkFrame(self.content_view, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.hero_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        hero_left = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_left.pack(side="left", padx=20, pady=15)
        self.lbl_main_status = ctk.CTkLabel(hero_left, text="🟢 Hệ thống sẵn sàng (Edge Native)", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_SUCCESS)
        self.lbl_main_status.pack(anchor="w")
        self.lbl_sub_status = ctk.CTkLabel(hero_left, text="Chọn chế độ rồi nhấn 'Bắt đầu chạy' để tiến hành", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SECONDARY)
        self.lbl_sub_status.pack(anchor="w", pady=(2, 0))

        hero_right = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_right.pack(side="right", padx=20, pady=15)

        self.btn_start = ctk.CTkButton(
            hero_right, text="▶  BẮT ĐẦU CHẠY", width=160, height=44, corner_radius=8,
            fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=(FONT_FAMILY, 14, "bold"),
            text_color="#000000", command=self.start_thread
        )
        self.btn_start.pack(side="left", padx=(0, 10))

        self.btn_stop = ctk.CTkButton(
            hero_right, text="⏹  DỪNG", width=100, height=44, corner_radius=8,
            fg_color=COLOR_CARD_SECONDARY, hover_color=COLOR_DANGER_BTN, state="disabled",
            font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT_SECONDARY, command=self.stop_bot
        )
        self.btn_stop.pack(side="left")

        # 2. SESSION SCOREBOARD (BẢNG ĐIỂM 6 CỘT CHI TIẾT)
        self.score_card = ctk.CTkFrame(self.content_view, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.score_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        score_header = ctk.CTkFrame(self.score_card, fg_color="transparent")
        score_header.pack(fill="x", padx=15, pady=(10, 6))
        ctk.CTkLabel(score_header, text="📊 BẢNG THEO DÕI ĐIỂM SỐ HỒ SƠ (SESSION STATS)", font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT).pack(side="left")

        # Header 6 cột
        self.grid_header = ctk.CTkFrame(self.score_card, fg_color=COLOR_CARD_SECONDARY, height=32, corner_radius=6)
        self.grid_header.pack(fill="x", padx=10, pady=(0, 6))
        cols = ["HỒ SƠ EDGE", "TRẠNG THÁI", "ĐIỂM ĐẦU", "+ ĐIỂM PC", "+ ĐIỂM MOBILE", "TỔNG ĐIỂM"]
        self.grid_header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        for idx, col_name in enumerate(cols):
            ctk.CTkLabel(self.grid_header, text=col_name, font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_ACCENT).grid(row=0, column=idx, pady=4)

        self.rows_frame = ctk.CTkScrollableFrame(self.score_card, height=130, fg_color="transparent")
        self.rows_frame.pack(fill="x", padx=5, pady=(0, 10))
        self.rows_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.row_widgets = {}
        self.render_scoreboard_rows()

        # 3. CONSOLE LOGS
        self.log_card = ctk.CTkFrame(self.content_view, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.log_card.grid(row=2, column=0, sticky="nsew")
        self.log_card.grid_rowconfigure(1, weight=1)
        self.log_card.grid_columnconfigure(0, weight=1)

        log_top = ctk.CTkFrame(self.log_card, fg_color="transparent")
        log_top.grid(row=0, column=0, sticky="ew", padx=15, pady=(8, 4))
        ctk.CTkLabel(log_top, text="💻 NHẬT KÝ HOẠT ĐỘNG THỜI GIAN THỰC (SYSTEM LOGS)", font=("Consolas", 11, "bold"), text_color=COLOR_TEXT_SECONDARY).pack(side="left")

        self.log_box = ctk.CTkTextbox(self.log_card, font=("Consolas", 11), text_color="#6ccb5f", fg_color="#181818", activate_scrollbars=True, corner_radius=6)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_box.configure(state="disabled")

        self.update_ui_profile_state()
        self.process_queue_updates()

    # =========================================================================
    # UI LOGIC
    # =========================================================================
    def update_ui_profile_state(self):
        """Khóa/mở menu chọn Profile theo chế độ Auto All / Single"""
        if self.radio_mode_var.get() == 0:
            self.profile_menu.configure(state="disabled", fg_color="#2c3e50")
        else:
            self.profile_menu.configure(state="normal", fg_color="#34495e")

    def render_scoreboard_rows(self):
        """Vẽ lại bảng điểm 6 cột chi tiết"""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        self.row_widgets.clear()

        profiles = self.cfg.get("pc", {}).get("profiles", ["Profile 1"])
        for idx, profile in enumerate(profiles):
            p_data = self.daily_stats["data"].get(profile, {})
            stat_txt = p_data.get("status", "Sẵn sàng")
            start_txt = str(p_data.get("start", "---"))
            
            # Điểm PC Gain
            pc_gain_val = p_data.get("pc_gain", None)
            pc_gain_txt = f"+{pc_gain_val}" if pc_gain_val is not None else "---"
            
            # Điểm Mobile Gain
            mob_gain_val = p_data.get("mobile_gain", None)
            mob_gain_txt = f"+{mob_gain_val}" if mob_gain_val is not None else "---"

            # Tổng điểm
            curr_txt = str(p_data.get("current", "---"))

            color = COLOR_TEXT_SECONDARY
            if stat_txt == "Running": color = COLOR_RUNNING
            elif stat_txt == "Done": color = COLOR_SUCCESS

            l_name = ctk.CTkLabel(self.rows_frame, text=profile, font=(FONT_FAMILY, 12, "bold"))
            l_stat = ctk.CTkLabel(self.rows_frame, text=stat_txt, text_color=color, font=(FONT_FAMILY, 11, "bold"))
            l_start = ctk.CTkLabel(self.rows_frame, text=start_txt, font=(FONT_FAMILY, 12))
            
            l_pc_gain = ctk.CTkLabel(
                self.rows_frame, text=pc_gain_txt, font=(FONT_FAMILY, 12, "bold"),
                text_color=COLOR_SUCCESS if (pc_gain_val and pc_gain_val > 0) else COLOR_TEXT_SECONDARY
            )
            l_mob_gain = ctk.CTkLabel(
                self.rows_frame, text=mob_gain_txt, font=(FONT_FAMILY, 12, "bold"),
                text_color="#e67e22" if (mob_gain_val and mob_gain_val > 0) else COLOR_TEXT_SECONDARY
            )
            l_curr = ctk.CTkLabel(
                self.rows_frame, text=curr_txt, font=(FONT_FAMILY, 12, "bold"),
                text_color=COLOR_ACCENT if curr_txt != "---" else COLOR_TEXT_SECONDARY
            )

            l_name.grid(row=idx, column=0, pady=4)
            l_stat.grid(row=idx, column=1, pady=4)
            l_start.grid(row=idx, column=2, pady=4)
            l_pc_gain.grid(row=idx, column=3, pady=4)
            l_mob_gain.grid(row=idx, column=4, pady=4)
            l_curr.grid(row=idx, column=5, pady=4)

            self.row_widgets[profile] = {
                "stat": l_stat, "start": l_start, "pc_gain": l_pc_gain, "mob_gain": l_mob_gain, "curr": l_curr
            }

    def open_settings_dialog(self):
        SettingsWindow(self, on_save_callback=self.on_settings_updated)

    def on_settings_updated(self, updated_cfg):
        self.cfg = updated_cfg
        profiles = self.cfg.get("pc", {}).get("profiles", ["Profile 1"])
        self.profile_menu.configure(values=profiles)
        if self.profile_menu.get() not in profiles and profiles:
            self.profile_menu.set(profiles[0])
        self.render_scoreboard_rows()
        self.log_message("⚙️ Đã lưu và áp dụng cài đặt mới!")

    def process_queue_updates(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                if len(self.log_box.get("1.0", "end")) > 5000:
                    self.log_box.delete("1.0", "50.0")
                self.log_box.insert("end", f"{msg}\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty: pass

        try:
            while True:
                data = self.stats_queue.get_nowait()
                self.update_stats_ui_implementation(**data)
        except queue.Empty: pass

        self.after(100, self.process_queue_updates)

    def log_message(self, message):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log_queue.put(f"{now} {message}")

    def update_stats_ui(self, profile, status=None, start_p=None, pc_gain=None, mob_gain=None, current_p=None):
        self.stats_queue.put({
            "profile": profile, "status": status, "start_p": start_p,
            "pc_gain": pc_gain, "mob_gain": mob_gain, "current_p": current_p
        })

    def update_stats_ui_implementation(self, profile, status=None, start_p=None, pc_gain=None, mob_gain=None, current_p=None):
        if profile not in self.row_widgets: return
        p_data = self.daily_stats["data"].setdefault(profile, {})

        if status:
            p_data["status"] = status
            color = COLOR_TEXT_SECONDARY
            if status == "Running": color = COLOR_RUNNING
            elif status == "Done": color = COLOR_SUCCESS
            self.row_widgets[profile]["stat"].configure(text=status, text_color=color)

        if start_p is not None:
            if "start" not in p_data:
                p_data["start"] = start_p
                self.row_widgets[profile]["start"].configure(text=str(start_p))

        if pc_gain is not None:
            p_data["pc_gain"] = pc_gain
            self.row_widgets[profile]["pc_gain"].configure(
                text=f"+{pc_gain}", text_color=COLOR_SUCCESS if pc_gain > 0 else COLOR_TEXT_SECONDARY
            )

        if mob_gain is not None:
            p_data["mobile_gain"] = mob_gain
            self.row_widgets[profile]["mob_gain"].configure(
                text=f"+{mob_gain}", text_color="#e67e22" if mob_gain > 0 else COLOR_TEXT_SECONDARY
            )

        if current_p is not None:
            p_data["current"] = current_p
            self.row_widgets[profile]["curr"].configure(text=str(current_p), text_color=COLOR_ACCENT)

        save_daily_stats(self.daily_stats)

    def sync_quick_toggles_to_cfg(self):
        self.cfg.setdefault("pc", {})["do_search"] = bool(self.chk_pc_search.get())
        self.cfg.setdefault("pc", {})["do_daily_sets"] = bool(self.chk_pc_sets.get())
        self.cfg.setdefault("mobile", {})["do_search"] = bool(self.chk_mob_search.get())
        self.cfg.setdefault("general", {})["auto_close"] = bool(self.switch_close.get())
        ConfigManager.save(self.cfg)

    def run_bot_process(self):
        self.sync_quick_toggles_to_cfg()
        self.coordinator = BotCoordinator(self.log_message, self.update_stats_ui)

        # Xác định target_profiles dựa trên lựa chọn Auto All hoặc Single Profile
        is_auto_all = (self.radio_mode_var.get() == 0)
        all_profiles = self.cfg.get("pc", {}).get("profiles", ["Profile 1"])
        
        if is_auto_all:
            target_profiles = all_profiles
            self.log_message(f"🚀 CHẾ ĐỘ: AUTO ALL ({len(target_profiles)} Profiles)")
        else:
            selected_p = self.profile_menu.get()
            target_profiles = [selected_p] if selected_p else all_profiles[:1]
            self.log_message(f"👤 CHẾ ĐỘ: CHẠY LẺ 1 HỒ SƠ [{target_profiles[0]}]")

        run_mode = self.seg_mode.get() # "Full Run", "PC Only", "Mobile Only"
        self.coordinator.run_all(self.cfg, target_profiles=target_profiles, run_mode=run_mode)

        if self.cfg.get("general", {}).get("auto_close", False) and self.is_running:
            self.log_message("👋 Tự động tắt Bot trong 3s...")
            self.after(3000, self.on_closing)
        else:
            self.stop_bot()

    def start_thread(self):
        if self.is_running: return
        self.is_running = True

        self.btn_start.configure(state="disabled", fg_color="#333333", text_color=COLOR_TEXT_SECONDARY)
        self.btn_stop.configure(state="normal", fg_color=COLOR_DANGER_BTN, text_color="#ffffff")
        self.lbl_main_status.configure(text="🟡 Đang thực thi chu trình tự động...", text_color=COLOR_RUNNING)

        self.rb_auto.configure(state="disabled")
        self.rb_single.configure(state="disabled")
        self.profile_menu.configure(state="disabled")
        self.seg_mode.configure(state="disabled")
        self.btn_open_settings.configure(state="disabled")

        threading.Thread(target=self.run_bot_process, daemon=True).start()

    def stop_bot(self):
        self.after(0, self._stop_bot_implementation)

    def _stop_bot_implementation(self):
        self.is_running = False
        if self.coordinator: self.coordinator.stop()

        self.btn_start.configure(state="normal", fg_color=COLOR_SUCCESS, text_color="#000000")
        self.btn_stop.configure(state="disabled", fg_color=COLOR_CARD_SECONDARY, text_color=COLOR_TEXT_SECONDARY)
        self.rb_auto.configure(state="normal")
        self.rb_single.configure(state="normal")
        self.seg_mode.configure(state="normal")
        self.btn_open_settings.configure(state="normal")
        self.update_ui_profile_state()
        self.lbl_main_status.configure(text="🟢 Hệ thống sẵn sàng (Edge Native)", text_color=COLOR_SUCCESS)

    def on_closing(self):
        self.stop_bot()
        self.sync_quick_toggles_to_cfg()
        clean_system()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()
