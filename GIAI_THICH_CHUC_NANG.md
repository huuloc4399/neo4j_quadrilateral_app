# TÀI LIỆU GIẢI THÍCH CHỨC NĂNG VÀ KIẾN TRÚC HỆ THỐNG

Tài liệu này giải thích chi tiết cấu trúc thư mục, luồng hoạt động của từng chức năng nằm ở file nào, và chi tiết về cơ sở dữ liệu được sử dụng trong dự án.

## 1. Cấu Trúc File & Chức Năng Của Từng File

Dự án hiện tại được xây dựng bằng kiến trúc **Client-Server** với **Flask (Python)** ở Backend và **HTML/CSS/JS thuần + Bootstrap 5** ở Frontend.

### 1.1. Phần Backend (Xử lý Logic & API)
* **`server.py`**: Đây là file quan trọng nhất của Backend, đóng vai trò là Web Server.
  * **Khởi tạo ứng dụng:** Sử dụng Flask để chạy server (`app = Flask(__name__)`).
  * **Kết nối Database:** Chứa hàm `get_neo4j_driver()` và `run_cypher()` để thiết lập kết nối đến máy chủ Neo4j trên Cloud.
  * **Cung cấp API (RESTful):** Định nghĩa các endpoints (đường dẫn) API trả về dữ liệu dạng JSON cho Frontend. Ví dụ:
    * `/api/db/status`: Kiểm tra trạng thái kết nối Neo4j.
    * `/api/hierarchy`, `/api/kg`: Trả về dữ liệu cây phả hệ và đồ thị tri thức.
    * `/api/inference`, `/api/compare`: Xử lý logic suy luận hình học và so sánh 2 hình.
    * `/api/quiz...`, `/api/leaderboard`: Xử lý logic làm bài kiểm tra (trắc nghiệm/bài tập) và tính điểm cho bảng xếp hạng.
* **`requirements.txt`**: Khai báo các thư viện Python cần thiết (Flask, neo4j, gunicorn, v.v.).
* **`Procfile`**: Cấu hình dành cho việc deploy ứng dụng lên các nền tảng đám mây như Render hoặc Heroku.

### 1.2. Phần Frontend (Giao Diện & Tương Tác Người Dùng)
* **`templates/index.html`**: File giao diện chính của người dùng.
  * Chứa cấu trúc HTML (bố cục trang web), hệ thống thanh điều hướng (navbar), các Tab chức năng (Sơ đồ, Đồ thị, So sánh, v.v.).
  * Chứa các Modal (hộp thoại nổi) cho Bài tập, Quiz.
  * Giao diện được thiết kế Responsive (thích ứng mọi thiết bị) bằng Bootstrap 5.
* **`static/js/app.js`**: File chứa toàn bộ logic chạy trên trình duyệt (Client-side).
  * **Gọi API:** Sử dụng `fetch()` để gọi các API từ `server.py` để lấy dữ liệu.
  * **Hiển thị đồ thị:** Sử dụng thư viện `vis-network` để vẽ "Sơ Đồ Phân Cấp" và "Đồ Thị Tri Thức Toàn Cảnh".
  * **Xử lý sự kiện:** Bắt các sự kiện click chuột, chuyển tab, trả lời câu hỏi trắc nghiệm, cập nhật điểm số và giao diện người dùng.
* **`static/css/style.css` (nếu có)**: Chứa các tùy chỉnh CSS về màu sắc, kích thước, hiệu ứng không có sẵn trong Bootstrap.

---

## 2. Giải Thích Chi Tiết Về Cơ Sở Dữ Liệu (Database)

Hệ thống sử dụng **Graph Database (Cơ sở dữ liệu Đồ thị)**. Việc dùng Graph DB là cực kỳ tối ưu cho việc biểu diễn các mối quan hệ hình học phức tạp.

### 2.1. Nền Tảng Database: Neo4j Aura Cloud
* **Hệ quản trị CSDL:** **Neo4j** - Hệ quản trị cơ sở dữ liệu đồ thị số 1 thế giới hiện nay.
* **Nền tảng lưu trữ:** **Neo4j AuraDB Free Cloud**. Đây là dịch vụ lưu trữ Neo4j trên đám mây (Cloud), giúp dữ liệu được online 24/7 mà không cần cài đặt Database ở máy cá nhân.
* **Ngôn ngữ truy vấn:** **Cypher Query Language (CQL)** - Ngôn ngữ chuyên dụng để thao tác với đồ thị (có cú pháp trực quan mô tả các Node và Relationship bằng các mũi tên `()-[]->()`).

### 2.2. Cấu Trúc Dữ Liệu (Data Model)
Trong Graph DB, dữ liệu được chia làm 2 thành phần chính: **Thực thể (Nodes)** và **Mối quan hệ (Relationships)**.

#### A. Các Thực Thể (Nodes)
Được phân loại bằng các `Label` (nhãn) sau:
1. **`(:Shape)`**: Đại diện cho một loại hình (Ví dụ: *Tứ giác, Hình thang, Hình bình hành, Hình chữ nhật, Hình vuông*).
   * Thuộc tính lưu trữ: `id`, `name`, `desc` (Mô tả chi tiết hình).
2. **`(:Property)`**: Đại diện cho các tính chất đặc trưng của hình học.
   * Thuộc tính lưu trữ: `id`, `name`, `desc` (Ví dụ: *"Có 4 góc vuông"*, *"Hai đường chéo cắt nhau tại trung điểm"*).
3. **`(:Formula)`**: Đại diện cho các công thức tính toán.
   * Thuộc tính lưu trữ: `id`, `name` (Ví dụ: `S = a*h`, `P = (a+b)*2`).
4. **`(:RecognitionCondition)`**: Đại diện cho các dấu hiệu nhận biết từ hình này thành hình kia.
   * Thuộc tính lưu trữ: `id`, `name`, `description` (Ví dụ: *"Hình thang có một góc vuông là hình thang vuông"*).

#### B. Các Mối Quan Hệ (Relationships)
Là các đường nối có hướng giữa các Nodes, thể hiện ngữ nghĩa hình học:
1. **`[:IS_A]`**: Thể hiện quan hệ cha - con (kế thừa).
   * *Ví dụ:* `(Hình Vuông) -[:IS_A]-> (Hình Chữ Nhật)`. Hiểu là Hình vuông LÀ MỘT Hình chữ nhật đặc biệt.
2. **`[:HAS_PROPERTY]`**: Hình có tính chất nào.
   * *Ví dụ:* `(Hình Bình Hành) -[:HAS_PROPERTY]-> (Các cạnh đối song song)`.
3. **`[:HAS_FORMULA]`**: Hình có công thức tính nào.
   * *Ví dụ:* `(Hình Thoi) -[:HAS_FORMULA]-> (S = (d1 * d2)/2)`.
4. **`[:RECOGNIZED_BY]`**: Dấu hiệu để nhận biết/chứng minh một hình.
   * Quan hệ nối từ `Shape` đến `RecognitionCondition` và từ `RecognitionCondition` đến `Shape` đích. 
   * *Ví dụ:* `(Hình Thang) -[:RECOGNIZED_BY]-> (Điều kiện góc vuông) -[:RECOGNIZED_BY]-> (Hình Thang Vuông)`.
5. **`[:DERIVED_FROM]`**: Dấu hiệu nhận biết đó được suy ra từ tính chất nào.
   * *Ví dụ:* Điều kiện *"Tứ giác có các cạnh đối bằng nhau"* thì `DERIVED_FROM` tính chất *"Các cạnh đối bằng nhau"*.

### Tóm Lại Về Database
Việc sử dụng **Neo4j** giúp cho tính năng **Suy Luận Truy Vết (Inference)** trong app trở nên rất dễ dàng. Khi người dùng chọn các tính chất, hệ thống dùng Cypher Query để "duyệt" dọc theo các mũi tên `[:HAS_PROPERTY]` và `[:IS_A]` trên đồ thị để xem các tính chất đó hội tụ về hình nào, qua đó gợi ý chính xác đáp án. Điều này rất khó và phức tạp nếu làm bằng SQL truyền thống.
