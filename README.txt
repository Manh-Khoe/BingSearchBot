Bước 1: Mở trình duyệt Edge bằng cái Profile mới mà bạn muốn thêm. Bước 2: Trên thanh địa chỉ, gõ dòng lệnh này và Enter: edge://version Bước 3: Nhìn xuống dòng Profile path (Đường dẫn hồ sơ).

Bạn sẽ thấy một đường dẫn kiểu: C:\Users\ASUS\AppData\Local\Microsoft\Edge\User Data\Profile 11
Bước 2: Cập nhật vào Code Bạn tìm đến dòng PROFILES_LIST trong code và thêm tên vừa tìm được vào trong ngoặc vuông, để trong dấu nháy kép "" và cách nhau bằng dấu phẩy ,.

Ví dụ bạn tìm được tên là Profile 11, sửa code thành:

Python

# DANH SÁCH PROFILE
# Thêm bao nhiêu cũng được, miễn đúng tên thư mục
PROFILES_LIST = ["Default", "Profile 4", "Profile 11"]