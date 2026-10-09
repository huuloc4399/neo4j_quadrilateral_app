# BỘ CÔNG THƯƠNG - TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HCM
## KHOA CÔNG NGHỆ THÔNG TIN - MÔN: DỮ LIỆU NOSQL
### ĐỒ ÁN: XÂY DỰNG ỨNG DỤNG HỖ TRỢ HỌC TOÁN HÌNH HỌC PHẲNG (TỨ GIÁC) SỬ DỤNG NEO4J CLOUD
**Giảng viên hướng dẫn:** ThS. Trần Quang Bình  
**Nhóm sinh viên thực hiện (Nhóm 08):**
1. Nguyễn Hữu Lộc
2. Nguyễn Thị Quyên
3. Dương Chí Khải

---

# HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG HỆ THỐNG (PHIÊN BẢN NÂNG CẤP MỚI NHẤT)

Hệ thống đã được **thiết kế lại toàn diện** thành ứng dụng Web Full-Stack hiện đại, kết hợp hài hòa giữa **Đồ thị tri thức suy luận logic Neo4j** và **Trải nghiệm học tập trực quan (Gamification EdTech)** giống trang web mẫu `https://neo4j-hinhhoc.onrender.com/`.

---

## 1. Yêu cầu Môi trường & Cấu hình CSDL Đám Mây (Neo4j Aura Cloud Free)

### 1.1. Cấu hình CSDL Đám mây (Đã kết nối sẵn trong file `.env`):
* **Nhà cung cấp:** Neo4j AuraDB (Gói Miễn Phí Cloud Free Tier)
* **URI:** `neo4j+s://ce509dc3.databases.neo4j.io`
* **Username:** `ce509dc3`
* **Password:** `0_jtQh4inSO0zp6Wesv2alboUutMGuBm-S5Mq8D5RqI`
* CSDL đang hoạt động trực tuyến với đầy đủ các thực thể (`Shape`, `Property`, `Formula`, `RecognitionCondition`, `Question`, `Answer`, `Solution`) và liên kết (`IS_A`, `HAS_PROPERTY`, `HAS_FORMULA`, `HAS_CONDITION`, `HAS_QUESTION`, `HAS_SOLUTION`).

### 1.2. Cài đặt thư viện phụ thuộc:
Mở Terminal / PowerShell tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```

---

## 2. Cách Khởi Chạy Ứng Dụng

### Cách 1: Khởi chạy Ứng dụng Web Đồ Họa Mới (Khuyến nghị)
1. Chạy file batch:
   * Nhấp đúp vào file `run.bat` trên Windows, **HOẶC**
2. Chạy qua dòng lệnh:
   ```bash
   python server.py
   ```
3. Truy cập trình duyệt web tại địa chỉ:
   ```text
   http://localhost:5000
   ```

*(Ghi chú: Nếu muốn chạy lại phiên bản Streamlit cũ để đối chiếu đồ án, thực thi lệnh: `streamlit run app_streamlit_backup.py`)*

---

## 3. Các Tính Năng Đột Phá Đã Được Thiết Kế Lại

### 3.1. Thanh Điều Hướng & Hồ Sơ Học Viên (Top Bar)
* **Chỉ báo trạng thái Cloud Real-time:** Đèn tín hiệu xanh hiển thị kết nối máy chủ Neo4j Aura Cloud cùng độ trễ (latency ms) và số lượng nodes thực tế.
* **Tài khoản học viên:** Bấm vào thẻ tên để đổi Nickname. Lưu trữ điểm số (Score ⭐) và Ví xu (Coins 🪙) đồng bộ trên trình duyệt.
* **Bộ nút thao tác nhanh:** Truy cập nhanh Bài toán, Bảng xếp hạng, Đổi quà và Quiz.

### 3.2. Chức năng 1: Sơ Đồ Phân Cấp & Tra Cứu Tứ Giác
* **Cây phả hệ Vis-Network:** Hiển thị trực quan quá trình tiến hóa từ *Hình học phẳng $\rightarrow$ Tứ giác $\rightarrow$ Hình thang $\rightarrow$ Hình bình hành $\rightarrow$ Hình chữ nhật/Hình thoi $\rightarrow$ Hình vuông*.
* **Bảng chi tiết bên phải khi nhấp vào hình:**
  * Định nghĩa chuẩn và mô tả hình học.
  * **Hộp Mẹo Ghi Nhớ & Giải Nhanh:** Các mẹo độc quyền (thơ vui tính diện tích hình thang, mẹo nhận diện góc và đường chéo).
  * Công thức Chu vi $P$ và Diện tích $S$ sắc nét.
  * Mối quan hệ phả hệ đồ thị (*Suy ra từ* và *Tiến hóa thành*).
  * Nút tắt *"Bài toán hình này"* mở ngay các bài tập thực hành liên quan.

### 3.3. Chức năng 2: Bản Đồ Tri Thức Toàn Cảnh (Knowledge Graph)
* Mạng lưới đa thực thể kết nối giữa **Tứ giác (Xanh dương)**, **Tính chất (Xanh lá)**, **Công thức (Vàng cam)** và **Dấu hiệu nhận biết (Hồng cánh sen)**.
* Bộ lọc bật/tắt linh hoạt từng tầng thực thể để người học quan sát trực quan.

### 3.4. Chức năng 3: Bộ Máy Suy Luận Nhận Diện Thông Minh (Inference Engine)
* Người học tích chọn các tính chất đã biết theo từng nhóm trực quan (**Cạnh**, **Góc**, **Đường chéo**).
* Bấm *"Thực Hiện Suy Luận Nhận Diện"*: Hệ thống chạy thuật toán truy vấn Cypher đối sánh đồ thị trực tiếp trên Neo4j Aura Cloud để tìm ra loại tứ giác thỏa mãn kèm căn cứ suy luận.
* Hỗ trợ tìm kiếm gần đúng (Partial matches) nếu dữ kiện bài toán còn thiếu.

### 3.5. Chức năng 4: So Sánh Đối Chiếu Hai Loại Tứ Giác
* Chọn 2 hình bất kỳ để hệ thống tự động trích xuất:
  * **Tính chất chung:** Các tính chất mà cả hai hình cùng kế thừa từ tổ tiên chung trong đồ thị tri thức.
  * **Tính chất riêng biệt:** Nêu bật sự khác biệt giúp học sinh không bị nhầm lẫn khi làm bài thi.

### 3.6. Chức năng 5: Bài Toán Luyện Tập Thực Hành
* Ngân hàng bài tập thực tế (tính diện tích khu vườn, sân bóng đá, màn hình tivi, viên gạch hình thoi, khung diều...).
* Cho phép nhập đáp số tự động kiểm tra Đúng/Sai.
* Nút *"Xem giải chi tiết"* mở ra từng bước phân tích và công thức áp dụng.
* Thưởng ngay +10 điểm và +5 xu khi giải đúng bài toán!

### 3.7. Chức năng 6: Đấu Trường Quiz Thử Thách & Giải Thích "Tại Sao?"
* Các câu hỏi trắc nghiệm kiểm tra nhận thức và tư duy logic.
* Tích hợp cơ chế suy luận truy vết từ `Question` $\rightarrow$ `Solution` $\rightarrow$ `RecognitionCondition` để giải thích tường tận căn cứ lý thuyết vì sao đáp án đó là đúng.
* Hoàn thành Quiz nhận thưởng lớn (+20đ, +10 xu) kèm hiệu ứng pháo hoa chúc mừng.

### 3.8. Chức năng 7: Bảng Xếp Hạng & Cửa Hàng Đổi Quà (Gamification)
* **Bảng Xếp Hạng:** Vinh danh các học viên có điểm số và số xu cao nhất với các danh hiệu Vàng, Bạc, Đồng.
* **Cửa Hàng Đổi Quà:** Dùng số xu kiếm được từ việc giải toán và làm quiz để đổi lấy các phần quà thú vị: *Bộ thước & bút kẻ hình học, Sổ tay bí kíp toán hình, Huy hiệu nhà hình học vàng, Voucher trà sữa*.

### 3.9. Chức năng 8: Giám Sát & Thống Kê CSDL Neo4j Cloud
* Bảng điều khiển quản trị thời gian thực thể hiện các thông số trực tiếp từ Neo4j Aura Cloud:
  * Số lượng các loại Tứ giác, Tính chất, Công thức, Dấu hiệu, Liên kết.
  * Bảng phân bố Node Labels và Relationship Types.

---

## 4. Hướng dẫn Triển khai Lên Cloud (Render / Railway)
1. Thư mục dự án đã có sẵn file `Procfile` (`web: gunicorn server:app`).
2. Đẩy mã nguồn lên kho lưu trữ GitHub của bạn.
3. Tạo Web Service mới trên [Render.com](https://render.com), liên kết với GitHub repository.
4. Cài đặt Environment Variables trên Render:
   * `NEO4J_URI`: `neo4j+s://ce509dc3.databases.neo4j.io`
   * `NEO4J_USER`: `ce509dc3`
   * `NEO4J_PASS`: `0_jtQh4inSO0zp6Wesv2alboUutMGuBm-S5Mq8D5RqI`
5. Nhấn **Deploy** để trang web tự động chạy online 24/7!
