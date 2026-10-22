# 🌟 Bing Rewards Bot v8.1 | Edge Native Edition

> **Giải pháp tự động hóa 100% Microsoft Rewards:** Hoàn thành trọn bộ nhiệm vụ **PC Search**, **Nhiệm vụ hàng ngày (Daily Sets / Quizzes / Polls)** và **Mobile Search (EdgA)** trực tiếp trên trình duyệt Microsoft Edge.
> 
> 🛡️ **Không cần giả lập Android (BlueStacks)**: Bảo vệ 100% tài khoản khỏi bị đòi mã OTP hoặc gắn cờ gian lận!  
> 🔄 **Tự động cập nhật EdgeDriver**: Tương thích 100% mỗi khi Microsoft Edge update, không cần tải driver thủ công!  
> 🔕 **Chạy êm ái**: Khởi động không nháy màn hình terminal đen (`StartBot.vbs`).

---

## ✨ Điểm nổi bật phiên bản v8.1

- **Tự động cập nhật Driver:** Tích hợp công nghệ *Selenium Manager* thông minh, tự động kiểm tra phiên bản Edge đang cài trên máy và tải driver tương thích hoàn toàn tự động. Người dùng không bao giờ phải tự đi tìm tải `msedgedriver.exe` nữa!
- **Mobile Emulation chính chủ (`EdgA`):** Kích hoạt chế độ giả lập điện thoại chuẩn Chromium (Viewport 412x915, Touch screen, định danh Edge on Android) ➔ Ăn trọn điểm tìm kiếm di động mỗi ngày!
- **Bảng điểm 6 cột chi tiết:** Theo dõi độc lập `+ ĐIỂM PC`, `+ ĐIỂM MOBILE` và `TỔNG ĐIỂM` sau mỗi phiên chạy để xác nhận điểm tăng thực tế.
- **Lựa chọn linh hoạt:** Hỗ trợ cả chế độ **Chạy tất cả (Auto All)** và **Chạy lẻ 1 Profile** (kèm lựa chọn `Full Run`, `PC Only`, `Mobile Only`).
- **Giao diện Windows 11 Fluent Dark:** Hiện đại, sắc nét, có bảng Cài đặt ⚙️ tùy chỉnh trực quan mà không cần chỉnh sửa code.

---

## 🛠️ Hướng dẫn cài đặt ban đầu (Làm 1 lần duy nhất)

### Bước 1: Cài đặt thư viện Python
Yêu cầu máy tính đã cài đặt **Python 3.10+**. Mở Command Prompt hoặc PowerShell tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

---

## 👥 Hướng dẫn tạo Profile mới & Đăng nhập tài khoản Microsoft

Hệ thống quản lý tài khoản thông qua các **Profile độc lập** của Microsoft Edge. Mọi cookie và phiên đăng nhập được lưu vĩnh viễn trong thư mục `BingBot_Data` của tool, không bao giờ bị văng tài khoản hay bị hỏi lại mật khẩu/OTP.

### 1. Mở trình duyệt Edge của Tool
Nhấp đúp vào file:
```text
Setup_Acc.bat
```
*(Cửa sổ Microsoft Edge độc lập của tool sẽ mở lên).*

### 2. Đăng nhập tài khoản đầu tiên (`Profile 1` hoặc `Default`)
- Truy cập `https://rewards.bing.com` và đăng nhập tài khoản Microsoft thứ nhất của bạn.

### 3. Thêm Profile mới cho tài khoản thứ 2, thứ 3...
- Trên cửa sổ Edge vừa mở, nhấp vào biểu tượng **Avatar** ở góc trên cùng bên phải.
- Chọn **Add profile (Thêm hồ sơ)** ➔ Chọn tiếp **Add (Thêm)**.
- Một cửa sổ Edge mới mở ra cho Profile thứ hai ➔ Truy cập `https://rewards.bing.com` và đăng nhập tài khoản Microsoft thứ 2 của bạn.
- Tiếp tục lặp lại các bước trên nếu bạn có tài khoản thứ 3, thứ 4...

### 4. Cách lấy tên Profile chuẩn xác
- Trên cửa sổ Edge của Profile bạn muốn kiểm tra, gõ vào thanh địa chỉ:
  ```text
  edge://version
  ```
- Nhấn **Enter** và tìm đến dòng **Profile path (Đường dẫn hồ sơ)**:
  - Nếu đường dẫn kết thúc bằng: `...\BingBot_Data\Profile 1` ➔ Tên là: `Profile 1`
  - Nếu đường dẫn kết thúc bằng: `...\BingBot_Data\Profile 2` ➔ Tên là: `Profile 2`
  - Nếu đường dẫn kết thúc bằng: `...\BingBot_Data\Default` ➔ Tên là: `Default`

### 5. Lưu danh sách Profile vào Bot (Không cần đụng code)
- Mở giao diện bot lên ➔ Nhấp vào nút **`⚙️ Cài đặt chuyên sâu`** ở góc dưới bên trái thanh Sidebar.
- Trong tab **👥 Hồ sơ Edge (Profiles)**, nhập danh sách các profile cách nhau bằng dấu phẩy:
  ```text
  Profile 1, Profile 2
  ```
- Nhấn nút **`💾 Lưu & Áp dụng`**. Danh sách sẽ được lưu vào `user_settings.json` và hiển thị ngay trên bảng điểm!

---

## 🚀 Hướng dẫn khởi chạy Bot

### Cách khởi động êm ái không hiện cửa sổ terminal đen (Khuyên dùng)
Nhấp đúp vào file:
👉 **`StartBot.vbs`**  
*(Giao diện đồ họa sẽ mở lên ngay lập tức mà 100% không nhảy bất kỳ cửa sổ CMD đen nào).*

> *Ghi chú: Bạn cũng có thể nhấp đúp vào `StartBot.bat`, file `.bat` này đã được cấu hình chạy ngầm qua `pythonw` và tự đóng cửa sổ console ngay lập tức.*

---

## 🎛️ Hướng dẫn sử dụng các chế độ trên Giao diện

### 1. Chọn chế độ chạy Profile:
- **Chạy tất cả (Auto All):** Bot sẽ tự động chạy xoay vòng lần lượt tất cả các Profile có trong danh sách.
- **Chạy lẻ 1 hồ sơ:** Khi tick chọn mục này, menu dropdown bên dưới sẽ sáng lên cho phép bạn chọn đích danh 1 Profile (ví dụ chỉ chạy riêng `Profile 1`).

### 2. Cần gạt loại nhiệm vụ (Nền tảng):
- **`Full Run`**: Chạy trọn gói cả PC Search, Daily Sets và Mobile Search.
- **`PC Only`**: Chỉ chạy tìm kiếm máy tính và nhiệm vụ hàng ngày.
- **`Mobile Only`**: Chỉ chạy tìm kiếm di động giả lập Edge Android (`EdgA`).

### 3. Đọc bảng điểm Session Stats 6 cột:
- **`HỒ SƠ EDGE`**: Tên Profile đang xử lý.
- **`TRẠNG THÁI`**: *Sẵn sàng* ➔ *Running* (màu cam) ➔ *Done* (màu xanh lá).
- **`ĐIỂM ĐẦU`**: Điểm số ghi nhận lúc bắt đầu phiên.
- **`+ ĐIỂM PC`**: Số điểm kiếm thêm được từ PC Search & Daily Sets (màu xanh lá).
- **`+ ĐIỂM MOBILE`**: Số điểm kiếm thêm được từ Mobile Search (màu cam).
- **`TỔNG ĐIỂM`**: Tổng số điểm tích lũy hiện có của tài khoản (màu xanh Cyan).

---

## 📂 Cấu trúc thư mục dự án

```text
BingSearchBot/
├── core/
│   ├── browser_factory.py     # Tự động cập nhật EdgeDriver & khởi tạo (Desktop + Mobile)
│   ├── pc_engine.py           # Lõi PC (Search + Daily Sets/Quizzes + Đọc điểm)
│   ├── mobile_edge_engine.py  # Lõi Mobile (EdgA Emulation + Touch Events)
│   ├── coordinator.py         # Điều phối luồng tuần tự PC ➔ Mobile
│   └── config_manager.py      # Quản lý cấu hình JSON tập trung
├── ui/
│   ├── theme.py               # Bảng màu Windows 11 Fluent Dark Mode
│   └── settings_window.py     # Cửa sổ Cài đặt hệ thống ⚙️
├── main_gui.py                # Giao diện chính CustomTkinter
├── user_settings.json         # File cấu hình cá nhân (không đụng code)
├── daily_stats.json           # Thống kê điểm số hàng ngày (tự reset mỗi ngày mới)
├── keywords.txt               # Từ điển từ khóa tìm kiếm tự nhiên
├── requirements.txt           # Danh sách thư viện Python
├── Setup_Acc.bat              # Script mở Edge để đăng nhập tài khoản / tạo Profile mới
├── StartBot.vbs               # Khởi động Bot 1-click êm ru (KHÔNG hiện terminal đen)
├── StartBot.bat               # Khởi động Bot qua file Batch
└── README.md                  # Tài liệu hướng dẫn chi tiết
```

---

## ⚠️ Lưu ý an toàn tài khoản
- Không nên chỉnh thời gian tìm kiếm quá ngắn (khuyến nghị giữ nguyên cài đặt mặc định: nghỉ 8 - 15 giây giữa các lượt search di động) để tránh vi phạm chính sách của Microsoft Rewards.
- Không chia sẻ thư mục `BingBot_Data` chứa dữ liệu đăng nhập tài khoản của bạn cho người khác.

---

## 🤝 Đóng góp (Contributing)
Mọi đóng góp, báo lỗi (Issues) hoặc Pull Requests đều được hoan nghênh nhiệt tình!
Nếu thấy dự án hữu ích, đừng quên tặng dự án **⭐ 1 Star** trên GitHub nhé!
