import re
import json

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_exercises = """EXERCISES_DATA = [
    {
        "id": 1,
        "grade": 8,
        "shape_id": "SH_TRAP",
        "shape_name": "Hình thang",
        "title": "Tính diện tích mảnh đất hình thang",
        "content": "Một mảnh đất hình thang có đáy lớn dài 18m, đáy bé dài 12m và chiều cao là 9m. Hãy tính diện tích mảnh đất này.",
        "formula_hint": "S = (a + b) × h / 2",
        "correct_answer": 135,
        "unit": "m²",
        "solution": "Áp dụng công thức S = (a + b) × h / 2:\nS = (18 + 12) × 9 / 2 = 30 × 9 / 2 = 135 m²."
    },
    {
        "id": 2,
        "grade": 8,
        "shape_id": "SH_TRAP",
        "shape_name": "Hình thang",
        "title": "Tìm chiều cao hình thang khi biết diện tích",
        "content": "Một hình thang có diện tích bằng 90 cm², biết tổng độ dài hai đáy là 30 cm. Tính chiều cao của hình thang đó.",
        "formula_hint": "h = 2 × S / (a + b)",
        "correct_answer": 6,
        "unit": "cm",
        "solution": "Từ công thức S = (a + b) × h / 2 => h = (2 × S) / (a + b).\nThay số: h = (2 × 90) / 30 = 180 / 30 = 6 cm."
    },
    {
        "id": 3,
        "grade": 8,
        "shape_id": "SH_ISOTRAP",
        "shape_name": "Hình thang cân",
        "title": "Tính chu vi hình thang cân",
        "content": "Một hình thang cân có đáy lớn 14 cm, đáy bé 6 cm và cạnh bên dài 5 cm. Tính chu vi hình thang cân này.",
        "formula_hint": "P = a + b + 2c (với c là cạnh bên)",
        "correct_answer": 30,
        "unit": "cm",
        "solution": "Vì hình thang cân có hai cạnh bên bằng nhau (c = 5 cm), chu vi P = a + b + 2 × c = 14 + 6 + 2 × 5 = 30 cm."
    },
    {
        "id": 4,
        "grade": 8,
        "shape_id": "SH_PARA",
        "shape_name": "Hình bình hành",
        "title": "Tính diện tích khu vườn hình bình hành",
        "content": "Một khu vườn hình bình hành có độ dài đáy là 24m và chiều cao tương ứng là 15m. Tính diện tích khu vườn.",
        "formula_hint": "S = a × h",
        "correct_answer": 360,
        "unit": "m²",
        "solution": "Áp dụng công thức S = a × h:\nS = 24 × 15 = 360 m²."
    },
    {
        "id": 5,
        "grade": 8,
        "shape_id": "SH_PARA",
        "shape_name": "Hình bình hành",
        "title": "Tính chu vi hình bình hành",
        "content": "Hình bình hành ABCD có độ dài cạnh a = 14 cm và cạnh b = 8 cm. Chu vi của hình bình hành đó là bao nhiêu?",
        "formula_hint": "P = 2 × (a + b)",
        "correct_answer": 44,
        "unit": "cm",
        "solution": "Áp dụng công thức P = 2 × (a + b):\nP = 2 × (14 + 8) = 2 × 22 = 44 cm."
    },
    {
        "id": 6,
        "grade": 6,
        "shape_id": "SH_RECT",
        "shape_name": "Hình chữ nhật",
        "title": "Tính diện tích sân bóng đá mini",
        "content": "Một sân bóng đá mini hình chữ nhật có chiều dài 25m và chiều rộng 15m. Tính diện tích của sân.",
        "formula_hint": "S = a × b",
        "correct_answer": 375,
        "unit": "m²",
        "solution": "Áp dụng công thức S = a × b:\nS = 25 × 15 = 375 m²."
    },
    {
        "id": 7,
        "grade": 7,
        "shape_id": "SH_RECT",
        "shape_name": "Hình chữ nhật",
        "title": "Tính độ dài đường chéo màn hình tivi",
        "content": "Một màn hình tivi hình chữ nhật có chiều rộng 30 cm và chiều dài 40 cm. Tính độ dài đường chéo của màn hình.",
        "formula_hint": "d = √(a² + b²)",
        "correct_answer": 50,
        "unit": "cm",
        "solution": "Theo định lý Pythagore trong tam giác vuông:\nd = √(30² + 40²) = √(900 + 1600) = √2500 = 50 cm."
    },
    {
        "id": 8,
        "grade": 8,
        "shape_id": "SH_RHOMBUS",
        "shape_name": "Hình thoi",
        "title": "Tính diện tích viên gạch trang trí hình thoi",
        "content": "Một viên gạch trang trí hình thoi có độ dài hai đường chéo lần lượt là 16 cm và 12 cm. Diện tích của viên gạch là bao nhiêu?",
        "formula_hint": "S = (d₁ × d₂) / 2",
        "correct_answer": 96,
        "unit": "cm²",
        "solution": "Áp dụng công thức S = (d₁ × d₂) / 2:\nS = (16 × 12) / 2 = 192 / 2 = 96 cm²."
    },
    {
        "id": 9,
        "grade": 8,
        "shape_id": "SH_RHOMBUS",
        "shape_name": "Hình thoi",
        "title": "Tính chu vi biển báo hình thoi",
        "content": "Một biển báo hình thoi có cạnh dài 25 cm. Chu vi của biển báo đó là bao nhiêu?",
        "formula_hint": "P = 4 × a",
        "correct_answer": 100,
        "unit": "cm",
        "solution": "Vì 4 cạnh của hình thoi bằng nhau, P = 4 × a:\nP = 4 × 25 = 100 cm."
    },
    {
        "id": 10,
        "grade": 6,
        "shape_id": "SH_SQUARE",
        "shape_name": "Hình vuông",
        "title": "Tính diện tích mảnh vườn hình vuông",
        "content": "Một mảnh vườn hình vuông có chu vi là 48m. Hỏi diện tích mảnh vườn đó là bao nhiêu mét vuông?",
        "formula_hint": "Cạnh a = P / 4, sau đó S = a²",
        "correct_answer": 144,
        "unit": "m²",
        "solution": "1. Độ dài cạnh hình vuông: a = 48 / 4 = 12 m.\n2. Diện tích mảnh vườn: S = a² = 12² = 144 m²."
    },
    {
        "id": 11,
        "grade": 8,
        "shape_id": "SH_QUAD",
        "shape_name": "Tứ giác",
        "title": "Tính góc còn lại của tứ giác",
        "content": "Tứ giác ABCD có số đo ba góc lần lượt là: góc A = 70°, góc B = 110°, góc C = 85°. Hỏi số đo góc D bằng bao nhiêu độ?",
        "formula_hint": "Tổng 4 góc trong tứ giác bằng 360°",
        "correct_answer": 95,
        "unit": "°",
        "solution": "Tổng các góc trong một tứ giác bằng 360°.\nSố đo góc D = 360° - (70° + 110° + 85°) = 360° - 265° = 95°."
    },
    {
        "id": 12,
        "grade": 9,
        "shape_id": "SH_QUAD",
        "shape_name": "Tứ giác nội tiếp",
        "title": "Tính góc đối diện của tứ giác nội tiếp",
        "content": "Tứ giác ABCD nội tiếp đường tròn (O). Biết góc A = 105°. Tính số đo góc C đối diện.",
        "formula_hint": "Tổng 2 góc đối của tứ giác nội tiếp bằng 180°",
        "correct_answer": 75,
        "unit": "°",
        "solution": "Vì ABCD nội tiếp đường tròn, nên tổng hai góc đối A + C = 180°.\n=> góc C = 180° - 105° = 75°."
    },
    {
        "id": 13,
        "grade": 10,
        "shape_id": "SH_PARA",
        "shape_name": "Hình bình hành",
        "title": "Toạ độ đỉnh thứ 4 của hình bình hành",
        "content": "Trong mặt phẳng toạ độ Oxy, cho hình bình hành ABCD với A(1;2), B(4;3), C(6;7). Hoành độ x của điểm D là bao nhiêu?",
        "formula_hint": "x_A + x_C = x_B + x_D",
        "correct_answer": 3,
        "unit": "",
        "solution": "Tính chất trung điểm 2 đường chéo (x_A+x_C = x_B+x_D).\n=> 1 + 6 = 4 + x_D => x_D = 7 - 4 = 3."
    },
    {
        "id": 14,
        "grade": 11,
        "shape_id": "SH_SQUARE",
        "shape_name": "Hình chóp tứ giác đều",
        "title": "Tính diện tích mặt đáy chóp tứ giác đều",
        "content": "Hình chóp tứ giác đều S.ABCD có cạnh đáy bằng 8 cm. Tính diện tích mặt đáy ABCD.",
        "formula_hint": "Đáy là hình vuông, S = a²",
        "correct_answer": 64,
        "unit": "cm²",
        "solution": "Hình chóp tứ giác đều có đáy là hình vuông.\nDiện tích đáy S = 8² = 64 cm²."
    },
    {
        "id": 15,
        "grade": 12,
        "shape_id": "SH_RECT",
        "shape_name": "Hình chữ nhật (Oxyz)",
        "title": "Khoảng cách trong không gian Oxyz",
        "content": "Trong không gian Oxyz, một mảnh giấy hình chữ nhật có kích thước 3x4 nằm trên mặt phẳng Oxy. Độ dài đường chéo của nó bằng bao nhiêu?",
        "formula_hint": "d = √(a² + b²)",
        "correct_answer": 5,
        "unit": "",
        "solution": "Trong mặt phẳng Oxy, hình chữ nhật vẫn giữ nguyên tính chất.\nĐường chéo d = √(3² + 4²) = √25 = 5."
    }
]"""

new_quizzes = """    extra_questions = [
        {
            "id": "EX_01",
            "grade": 6,
            "question": "Công thức tính diện tích (S) của Hình chữ nhật có chiều dài a và chiều rộng b là gì?",
            "options": ["S = a²", "S = a × b", "S = (a + b) × h / 2", "S = 2(a + b)"],
            "answer": "S = a × b",
            "explain": "Diện tích hình chữ nhật bằng tích hai kích thước chiều dài và chiều rộng: S = a × b.",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_02",
            "grade": 8,
            "question": "Khi Hình bình hành có hai đường chéo vuông góc với nhau thì nó trở thành hình nào?",
            "options": ["Hình chữ nhật", "Hình thang cân", "Hình thoi", "Hình vuông"],
            "answer": "Hình thoi",
            "explain": "Theo dấu hiệu nhận biết: Hình bình hành có hai đường chéo vuông góc là hình thoi.",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_03",
            "grade": 8,
            "question": "Tứ giác có 4 góc vuông và 4 cạnh bằng nhau là hình gì?",
            "options": ["Hình bình hành", "Hình chữ nhật", "Hình thoi", "Hình vuông"],
            "answer": "Hình vuông",
            "explain": "Hình vuông là tứ giác đặc biệt có đồng thời 4 góc vuông và 4 cạnh bằng nhau.",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_04",
            "grade": 8,
            "question": "Hình thang có hai góc kề một đáy bằng nhau thì trở thành hình gì?",
            "options": ["Hình bình hành", "Hình thang cân", "Hình thang vuông", "Hình chữ nhật"],
            "answer": "Hình thang cân",
            "explain": "Theo định nghĩa: Hình thang có hai góc kề một đáy bằng nhau là hình thang cân.",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_05",
            "grade": 7,
            "question": "Trong tam giác vuông, bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông. Đây là định lý gì?",
            "options": ["Định lý Talet", "Định lý Pythagore", "Định lý Sin", "Định lý Cosin"],
            "answer": "Định lý Pythagore",
            "explain": "Định lý Pythagore là định lý kinh điển dùng nhiều trong tính toán đường chéo tứ giác.",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_06",
            "grade": 9,
            "question": "Một tứ giác có tổng số đo hai góc đối diện bằng 180 độ thì tứ giác đó là:",
            "options": ["Hình thoi", "Tứ giác ngoại tiếp", "Tứ giác nội tiếp", "Hình bình hành"],
            "answer": "Tứ giác nội tiếp",
            "explain": "Dấu hiệu nhận biết quan trọng nhất của tứ giác nội tiếp là tổng 2 góc đối bằng 180 độ.",
            "difficulty": "Khá"
        },
        {
            "id": "EX_07",
            "grade": 10,
            "question": "Cho hình bình hành ABCD, đẳng thức vectơ nào sau đây ĐÚNG?",
            "options": ["Vectơ AB = Vectơ CD", "Vectơ AD = Vectơ CB", "Vectơ AB = Vectơ DC", "Vectơ AC = Vectơ BD"],
            "answer": "Vectơ AB = Vectơ DC",
            "explain": "Trong hình bình hành ABCD, cạnh AB song song và cùng chiều với cạnh DC, nên Vectơ AB = Vectơ DC.",
            "difficulty": "Khá"
        },
        {
            "id": "EX_08",
            "grade": 11,
            "question": "Qua 3 điểm không thẳng hàng trong không gian, ta xác định được bao nhiêu mặt phẳng?",
            "options": ["1", "2", "3", "Vô số"],
            "answer": "1",
            "explain": "Ba điểm không thẳng hàng luôn xác định duy nhất một mặt phẳng (Cơ sở Hình học không gian lớp 11).",
            "difficulty": "Cơ bản"
        },
        {
            "id": "EX_09",
            "grade": 12,
            "question": "Công thức tính thể tích Khối chóp (V) có diện tích đáy B và chiều cao h là gì?",
            "options": ["V = B.h", "V = 1/3 B.h", "V = 1/2 B.h", "V = 3 B.h"],
            "answer": "V = 1/3 B.h",
            "explain": "Thể tích khối chóp luôn bằng một phần ba tích của diện tích đáy và chiều cao.",
            "difficulty": "Cơ bản"
        }
    ]"""

content = re.sub(r'EXERCISES_DATA\s*=\s*\[.*?\]\n\n# Bộ nhớ tạm', new_exercises + '\n\n# Bộ nhớ tạm', content, flags=re.DOTALL)
content = re.sub(r'extra_questions\s*=\s*\[.*?\]', new_quizzes, content, flags=re.DOTALL)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)
