import time
from utils import clean_system, load_keywords
from core.pc_engine import PCEngine
from core.mobile_edge_engine import MobileEdgeEngine

class BotCoordinator:
    """Bộ điều phối luồng công việc Edge Native Automation (PC & Mobile Emulation)"""
    def __init__(self, log_callback, stats_callback=None):
        self.log = log_callback
        self.stats = stats_callback
        self.is_running = True

        self.pc_engine = PCEngine(self.log, self.stats, self.should_stop)
        self.mobile_engine = MobileEdgeEngine(self.log, self.should_stop)

    def should_stop(self):
        return not self.is_running

    def stop(self):
        self.is_running = False

    def run_all(self, settings, target_profiles=None, run_mode="Full Run"):
        """Khởi chạy toàn bộ chu trình tự động hóa trên các Profile Edge chỉ định"""
        self.is_running = True
        keywords = load_keywords()
        clean_system()

        pc_cfg = settings.get("pc", {})
        mob_cfg = settings.get("mobile", {})
        gen_cfg = settings.get("general", {})

        profiles = target_profiles or pc_cfg.get("profiles", ["Profile 1"])
        self.log(f"🚀 Bắt đầu chế độ [{run_mode}] cho {len(profiles)} Profile: {profiles}")

        for idx, profile in enumerate(profiles):
            if self.should_stop(): break

            self.log(f"\n👤 ================= BẮT ĐẦU: [{profile}] =================")
            if self.stats: self.stats(profile, status="Running")

            start_p = None
            pc_finish_p = None
            mob_finish_p = None

            # Xác định các tác vụ cần chạy theo run_mode và checkbox
            should_run_pc = (run_mode in ["Full Run", "PC Only"]) and (pc_cfg.get("do_search", True) or pc_cfg.get("do_daily_sets", True))
            should_run_mob = (run_mode in ["Full Run", "Mobile Only"]) and mob_cfg.get("do_search", True)

            # -----------------------------------------------------------------
            # 1. NHIỆM VỤ PC (DESKTOP EDGE)
            # -----------------------------------------------------------------
            if should_run_pc and not self.should_stop():
                self.log(f"🖥️ [PC Mode] Đang mở Edge cho [{profile}]...")
                driver = None
                try:
                    driver = self.pc_engine.create_driver(profile, is_mobile=False)
                    if driver:
                        # Đọc điểm đầu phiên
                        raw_start = self.pc_engine.get_points_safe(driver, max_retries=6)
                        if raw_start == "N/A":
                            raw_start = self.pc_engine.fetch_points_via_rewards_page(driver)
                        
                        if raw_start != "N/A":
                            start_p = self.pc_engine.parse_points(raw_start)
                            self.log(f"🎯 [{profile}] Điểm ban đầu: {start_p}")
                            if self.stats: self.stats(profile, start_p=start_p, current_p=start_p)

                        # Chạy PC Search
                        if pc_cfg.get("do_search", True) and not self.should_stop():
                            self.pc_engine.run_pc_search(
                                driver=driver,
                                profile_dir=profile,
                                max_count=pc_cfg.get("search_count", 30),
                                keywords=keywords,
                                settings=pc_cfg,
                                is_auto_mode=True
                            )

                        # Chạy Daily Sets
                        if pc_cfg.get("do_daily_sets", True) and not self.should_stop():
                            self.pc_engine.run_daily_sets(driver, profile)

                        # Đọc điểm chốt sau khi chạy PC
                        raw_pc_end = self.pc_engine.fetch_points_via_rewards_page(driver)
                        if raw_pc_end != "N/A":
                            pc_finish_p = self.pc_engine.parse_points(raw_pc_end)
                            pc_gain = (pc_finish_p - start_p) if (start_p and pc_finish_p >= start_p) else 0
                            self.log(f"🏁 [{profile}] Hoàn tất PC: +{pc_gain} điểm (Tổng: {pc_finish_p})")
                            if self.stats: self.stats(profile, pc_gain=pc_gain, current_p=pc_finish_p)

                    else:
                        self.log(f"❌ Không thể mở Edge PC cho [{profile}]")
                except Exception as e:
                    self.log(f"[LỖI PC {profile}] {e}")
                finally:
                    if driver:
                        try: driver.quit()
                        except: pass
                    clean_system()

            # Nghỉ ngắn chuyển sang chế độ Mobile
            if not self.should_stop() and should_run_mob:
                self.log("⏳ Nghỉ 5s chuyển sang chế độ Mobile Emulation...")
                time.sleep(5)

            # -----------------------------------------------------------------
            # 2. NHIỆM VỤ MOBILE (EDGE NATIVE EMULATION - EDGA)
            # -----------------------------------------------------------------
            if should_run_mob and not self.should_stop():
                self.log(f"📱 [Mobile Emulation] Đang mở Edge Mobile cho [{profile}]...")
                mob_driver = None
                try:
                    mob_driver = self.pc_engine.create_driver(profile, is_mobile=True)
                    if mob_driver:
                        # Nếu chưa có điểm đầu (do chỉ chạy Mobile Only)
                        if start_p is None:
                            raw_mob_start = self.pc_engine.fetch_points_via_rewards_page(mob_driver)
                            if raw_mob_start != "N/A":
                                start_p = self.pc_engine.parse_points(raw_mob_start)
                                self.log(f"🎯 [{profile}] Điểm ban đầu (Mobile): {start_p}")
                                if self.stats: self.stats(profile, start_p=start_p, current_p=start_p)

                        # Chạy Mobile Search
                        self.mobile_engine.run_mobile_search(
                            driver=mob_driver,
                            profile_dir=profile,
                            max_count=mob_cfg.get("search_count", 20),
                            keywords=keywords,
                            settings=mob_cfg
                        )

                        # Đọc điểm chốt sau khi chạy Mobile
                        raw_mob_end = self.pc_engine.fetch_points_via_rewards_page(mob_driver)
                        if raw_mob_end != "N/A":
                            mob_finish_p = self.pc_engine.parse_points(raw_mob_end)
                            base_p = pc_finish_p if pc_finish_p is not None else start_p
                            mob_gain = (mob_finish_p - base_p) if (base_p and mob_finish_p >= base_p) else 0
                            self.log(f"🏁 [{profile}] Hoàn tất Mobile: +{mob_gain} điểm (Tổng: {mob_finish_p})")
                            if self.stats: self.stats(profile, mob_gain=mob_gain, current_p=mob_finish_p)
                    else:
                        self.log(f"❌ Không thể mở Edge Mobile cho [{profile}]")
                except Exception as e:
                    self.log(f"[LỖI Mobile {profile}] {e}")
                finally:
                    if mob_driver:
                        try: mob_driver.quit()
                        except: pass
                    clean_system()

            if self.stats: self.stats(profile, status="Done")
            self.log(f"✅ Hoàn tất chu trình cho [{profile}]!")

            # Nghỉ chuyển sang Profile tiếp theo
            if not self.should_stop() and idx < len(profiles) - 1:
                delay = gen_cfg.get("delay_between_accounts", 15)
                self.log(f"⏳ Nghỉ {delay}s trước khi chuyển Profile tiếp theo...")
                time.sleep(delay)

        self.log("\n🎉 ================= TẤT CẢ HỒ SƠ ĐÃ HOÀN TẤT =================")
