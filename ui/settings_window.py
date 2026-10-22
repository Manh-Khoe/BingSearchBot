import customtkinter as ctk
from ui.theme import *
from core.config_manager import ConfigManager

class SettingsWindow(ctk.CTkToplevel):
    """Cửa sổ Cài đặt Edge Native phong cách Windows 11 Fluent Dark Mode - Tab Frame-based"""
    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)

        self.title("Cài đặt hệ thống | Bing Bot Settings")
        self.geometry("820x600")
        self.minsize(760, 520)
        self.configure(fg_color=COLOR_BG)
        self.transient(parent)
        self.grab_set()

        self.on_save_callback = on_save_callback
        self.cfg = ConfigManager.load()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # [CỘT 0] SIDEBAR TABS
        # ---------------------------------------------------------------------
        self.nav_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.nav_frame, text="⚙️ CÀI ĐẶT", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(20, 15))

        self.tabs = [
            ("profiles", "👥 Hồ sơ Edge (Profiles)"),
            ("pc", "💻 Nhiệm vụ PC"),
            ("mobile", "📱 Nhiệm vụ Mobile"),
            ("general", "⚙️ Chung"),
            ("about", "ℹ️ Giới thiệu")
        ]

        self.nav_buttons = {}
        for tab_id, tab_label in self.tabs:
            btn = ctk.CTkButton(
                self.nav_frame, text=tab_label, anchor="w", height=40,
                fg_color="transparent", text_color=COLOR_TEXT_SECONDARY,
                hover_color=COLOR_CARD, font=(FONT_FAMILY, 13),
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[tab_id] = btn

        # Nút Lưu ở chân sidebar kèm nhãn thông báo trạng thái
        self.lbl_save_status = ctk.CTkLabel(self.nav_frame, text="", font=(FONT_FAMILY, 11), text_color=COLOR_SUCCESS)
        self.lbl_save_status.pack(side="bottom", padx=15, pady=(0, 10))

        self.btn_save = ctk.CTkButton(
            self.nav_frame, text="💾 Lưu & Áp dụng", height=40,
            fg_color=COLOR_ACCENT, text_color="#000000", hover_color=COLOR_ACCENT_HOVER,
            font=(FONT_FAMILY, 13, "bold"), command=self.save_and_close
        )
        self.btn_save.pack(side="bottom", fill="x", padx=15, pady=(0, 6))

        # ---------------------------------------------------------------------
        # [CỘT 1] CONTENT CONTAINER (CHỨA CÁC TAB FRAME TỒN TẠI VĨNH VIỄN)
        # ---------------------------------------------------------------------
        self.content_container = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Xây dựng trước toàn bộ 5 Tab Frame (Không bao giờ destroy khi đổi tab)
        self.tab_frames = {}
        self.tab_frames["profiles"] = self.build_tab_profiles(self.content_container)
        self.tab_frames["pc"] = self.build_tab_pc(self.content_container)
        self.tab_frames["mobile"] = self.build_tab_mobile(self.content_container)
        self.tab_frames["general"] = self.build_tab_general(self.content_container)
        self.tab_frames["about"] = self.build_tab_about(self.content_container)

        self.current_tab = None
        self.switch_tab("profiles")

    def switch_tab(self, tab_id):
        """Chuyển đổi tab bằng pack / pack_forget để giữ nguyên 100% dữ liệu đã gõ"""
        self.current_tab = tab_id

        # Cập nhật màu highlight nút sidebar
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=COLOR_CARD, text_color=COLOR_ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SECONDARY)

        # Ẩn tất cả tab frame và chỉ hiện tab được chọn
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # =========================================================================
    # BUILD TABS (TẤT CẢ WIDGETS ĐƯỢC GIỮ NGUYÊN VẸN KHÔNG BỊ DESTROY)
    # =========================================================================
    def build_tab_profiles(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.create_header(frame, "Quản lý Hồ sơ Edge", "Thêm, xóa danh sách Profile Edge độc lập để cày tự động nhiều tài khoản.")

        card = self.create_card(frame, "👥 Danh sách Profiles")
        ctk.CTkLabel(card, text="Nhập các tên Profile cách nhau bằng dấu phẩy (,):", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(5, 5))
        
        profiles_str = ", ".join(self.cfg.get("pc", {}).get("profiles", ["Profile 1"]))
        self.entry_pc_profiles = ctk.CTkEntry(card, height=36, font=(FONT_FAMILY, 12), fg_color=COLOR_INPUT_BG, border_color=COLOR_INPUT_BORDER)
        self.entry_pc_profiles.insert(0, profiles_str)
        self.entry_pc_profiles.pack(fill="x", padx=15, pady=(0, 10))

        help_txt = (
            "💡 Hướng dẫn lấy tên Profile:\n"
            "1. Chạy file 'Setup_Acc.bat' để mở trình duyệt Edge.\n"
            "2. Gõ 'edge://version' trên thanh địa chỉ ➔ Nhìn dòng 'Profile path'.\n"
            "3. Phần cuối đường dẫn chính là tên Profile (ví dụ: 'Default', 'Profile 1', 'Profile 2')."
        )
        ctk.CTkLabel(card, text=help_txt, font=(FONT_FAMILY, 11), text_color=COLOR_TEXT_MUTED, justify="left").pack(anchor="w", padx=15, pady=(0, 12))
        return frame

    def build_tab_pc(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.create_header(frame, "Nhiệm vụ PC (Desktop Mode)", "Tùy chỉnh số lượt tìm kiếm và tốc độ gõ phím ngẫu nhiên trên máy tính.")

        card = self.create_card(frame, "⚙️ Giới hạn & Tốc độ PC")
        pc = self.cfg.get("pc", {})
        self.entry_pc_search = self.create_setting_row(card, "Số lượt tìm kiếm PC (lượt):", str(pc.get("search_count", 30)))
        self.entry_pc_interval = self.create_setting_row(card, "Kiểm tra điểm mỗi (lượt):", str(pc.get("interval_check", 3)))
        self.entry_pc_min_t = self.create_setting_row(card, "Tốc độ gõ tối thiểu (giây/ký tự):", str(pc.get("min_type", 0.1)))
        self.entry_pc_max_t = self.create_setting_row(card, "Tốc độ gõ tối đa (giây/ký tự):", str(pc.get("max_type", 0.4)))
        self.entry_pc_min_r = self.create_setting_row(card, "Thời gian xem trang tối thiểu (giây):", str(pc.get("min_read", 5.0)))
        self.entry_pc_max_r = self.create_setting_row(card, "Thời gian xem trang tối đa (giây):", str(pc.get("max_read", 10.0)))
        return frame

    def build_tab_mobile(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.create_header(frame, "Nhiệm vụ Mobile (Edge Android EdgA)", "Cấu hình số lượt tìm kiếm di động và thời gian nghỉ chống phạt Cooldown 15 phút.")

        card = self.create_card(frame, "⚙️ Giới hạn & Độ trễ Mobile")
        mob = self.cfg.get("mobile", {})
        self.entry_mob_search = self.create_setting_row(card, "Số lượt tìm kiếm di động (lượt):", str(mob.get("search_count", 20)))
        self.entry_mob_del_min = self.create_setting_row(card, "Độ trễ tối thiểu giữa 2 lượt (giây):", str(mob.get("min_search_delay", 8.0)))
        self.entry_mob_del_max = self.create_setting_row(card, "Độ trễ tối đa giữa 2 lượt (giây):", str(mob.get("max_search_delay", 15.0)))
        return frame

    def build_tab_general(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.create_header(frame, "Cài đặt Chung", "Tùy chỉnh hành vi hệ thống và thời gian nghỉ chuyển tài khoản.")

        card = self.create_card(frame, "⏱️ Thời gian nghỉ")
        gen = self.cfg.get("general", {})
        self.entry_delay_accs = self.create_setting_row(card, "Nghỉ giữa các Profile (giây):", str(gen.get("delay_between_accounts", 15)))

        card_behavior = self.create_card(frame, "⚙️ Tự động hóa")
        self.switch_auto_close = ctk.CTkSwitch(card_behavior, text="Tự động tắt bot khi hoàn thành", font=(FONT_FAMILY, 12), progress_color=COLOR_ACCENT)
        if gen.get("auto_close", False): self.switch_auto_close.select()
        self.switch_auto_close.pack(anchor="w", padx=15, pady=15)
        return frame

    def build_tab_about(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.create_header(frame, "Về Bing Rewards Bot", "Kiến trúc Edge Native v8.1.")

        card = self.create_card(frame, "🌟 Bing Rewards Bot v8.1 | Edge Native Edition")
        txt = (
            "• Kiến trúc: Edge Native Dual-Engine (PC & Mobile Emulation)\n"
            "• Không dùng giả lập Android: Bảo vệ 100% tài khoản khỏi bị Verify OTP / Checkpoint\n"
            "• Tự động cập nhật Driver: Tích hợp Selenium Manager & Webdriver Manager\n"
            "• Định danh di động: Chromium Mobile Emulation (EdgA) + Touch Screen + Viewport 412x915\n"
            "• Đa tài khoản: Quản lý theo Profile Edge độc lập, lưu session vĩnh viễn\n\n"
            "Mọi thiết lập lưu tự động trong file 'user_settings.json'."
        )
        ctk.CTkLabel(card, text=txt, font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=15, pady=15)
        return frame

    # =========================================================================
    # HELPERS
    # =========================================================================
    def create_header(self, parent, title, subtitle):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text=title, font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkLabel(frame, text=subtitle, font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

    def create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(card, text=title, font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(12, 6))
        return card

    def create_setting_row(self, parent, label_text, default_value):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(frame, text=label_text, font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SECONDARY).pack(side="left")
        entry = ctk.CTkEntry(frame, width=100, height=28, font=(FONT_FAMILY, 12), fg_color=COLOR_INPUT_BG, border_color=COLOR_INPUT_BORDER, justify="center")
        entry.insert(0, default_value)
        entry.pack(side="right")
        return entry

    # =========================================================================
    # LƯU VÀ ÁP DỤNG CÀI ĐẶT
    # =========================================================================
    def save_and_close(self):
        """Lưu toàn bộ cài đặt từ các tab và thông báo rõ ràng cho người dùng"""
        try:
            # 1. Profiles
            raw_profiles = self.entry_pc_profiles.get().strip()
            self.cfg.setdefault("pc", {})["profiles"] = [p.strip() for p in raw_profiles.split(",") if p.strip()]

            # 2. PC Tasks
            self.cfg.setdefault("pc", {})["search_count"] = int(self.entry_pc_search.get().strip())
            self.cfg.setdefault("pc", {})["interval_check"] = int(self.entry_pc_interval.get().strip())
            self.cfg.setdefault("pc", {})["min_type"] = float(self.entry_pc_min_t.get().strip())
            self.cfg.setdefault("pc", {})["max_type"] = float(self.entry_pc_max_t.get().strip())
            self.cfg.setdefault("pc", {})["min_read"] = float(self.entry_pc_min_r.get().strip())
            self.cfg.setdefault("pc", {})["max_read"] = float(self.entry_pc_max_r.get().strip())

            # 3. Mobile Tasks
            self.cfg.setdefault("mobile", {})["search_count"] = int(self.entry_mob_search.get().strip())
            self.cfg.setdefault("mobile", {})["min_search_delay"] = float(self.entry_mob_del_min.get().strip())
            self.cfg.setdefault("mobile", {})["max_search_delay"] = float(self.entry_mob_del_max.get().strip())

            # 4. General
            self.cfg.setdefault("general", {})["delay_between_accounts"] = int(self.entry_delay_accs.get().strip())
            self.cfg.setdefault("general", {})["auto_close"] = bool(self.switch_auto_close.get())

            # Lưu vào file JSON
            ConfigManager.save(self.cfg)

            # Cập nhật ngược lại giao diện chính
            if self.on_save_callback:
                self.on_save_callback(self.cfg)

            # Đóng cửa sổ cài đặt
            self.destroy()

        except Exception as e:
            self.lbl_save_status.configure(text=f"❌ Lỗi: {e}", text_color=COLOR_DANGER)
