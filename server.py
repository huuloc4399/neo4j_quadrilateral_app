import os
import time
import json
from flask import Flask, jsonify, request, render_template, send_from_directory
from neo4j import GraphDatabase, exceptions as neo4j_exceptions
from dotenv import load_dotenv

# Tải cấu hình biến môi trường từ .env
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# Cấu hình kết nối Neo4j Aura Cloud Free
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://ce509dc3.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "ce509dc3")
NEO4J_PASS = os.getenv("NEO4J_PASS", "0_jtQh4inSO0zp6Wesv2alboUutMGuBm-S5Mq8D5RqI")

driver = None

def get_driver():
    global driver
    if driver is None:
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        except Exception as e:
            print("Lỗi tạo driver Neo4j:", e)
            return None
    return driver

def run_cypher(query, params=None):
    drv = get_driver()
    if not drv:
        return None
    try:
        with drv.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    except Exception as e:
        print("Lỗi truy vấn Cypher:", e)
        return None

# ==============================================================================
# BỘ DỮ LIỆU BỔ TRỢ (MẸO GHI NHỚ, BÀI TẬP, QUÀ TẶNG, LEADERBOARD LƯU TRỮ)
# ==============================================================================
SHAPE_TIPS = {
    "hinh_hoc_phang": "Không gian 2 chiều là nền tảng của hình học. Hãy luôn quan sát đỉnh, cạnh đối, góc vuông và đường chéo.",
    "SH_QUAD": "Mẹo góc: Tổng 4 góc của một tứ giác luôn bằng 360°. Lấy 360° trừ tổng 3 góc đã biết để tìm góc còn lại.",
    "tu_giac": "Mẹo góc: Tổng 4 góc của một tứ giác luôn bằng 360°. Lấy 360° trừ tổng 3 góc đã biết để tìm góc còn lại.",
    "SH_TRAP": "Bài thơ diện tích:\n\"Muốn tính diện tích hình thang\nĐáy lớn đáy nhỏ ta mang cộng vào\nCộng vào nhân với chiều cao\nChia đôi lấy nửa thế nào cũng ra!\"",
    "hinh_thang": "Bài thơ diện tích: Đáy lớn đáy nhỏ ta mang cộng vào, nhân với chiều cao, chia đôi lấy nửa thế nào cũng ra!",
    "SH_ISOTRAP": "Hình thang cân: 2 cạnh bên bằng nhau, 2 góc kề một đáy bằng nhau, và 2 đường chéo bằng nhau. Nhận biết từ hình thang có 2 góc đáy bằng nhau.",
    "SH_RIGHTTRAP": "Hình thang vuông: Có 1 góc vuông kề đáy. Cạnh bên vuông góc với 2 đáy chính là đường cao h.",
    "SH_PARA": "Nhận biết nhanh: Cặp cạnh đối song song và bằng nhau. Hai đường chéo cắt nhau tại trung điểm mỗi đường. S = a × h.",
    "hinh_binh_hanh": "Nhận biết nhanh: Cặp cạnh đối song song và bằng nhau. Hai đường chéo cắt nhau tại trung điểm mỗi đường. S = a × h.",
    "SH_RECT": "Mẹo nhanh: Hình bình hành có 1 góc vuông là hình chữ nhật. Đường chéo tính bằng định lý Pythagore: d = √(a² + b²).",
    "hinh_chu_nhat": "Mẹo nhanh: Hình bình hành có 1 góc vuông là hình chữ nhật. Đường chéo tính bằng định lý Pythagore: d = √(a² + b²).",
    "SH_RHOMBUS": "Mẹo đường chéo: 2 đường chéo vuông góc tại trung điểm và là tia phân giác các góc. Diện tích S = (d₁ × d₂) / 2.",
    "hinh_thoi": "Mẹo đường chéo: 2 đường chéo vuông góc tại trung điểm và là phân giác các góc. Diện tích S = (d₁ × d₂) / 2.",
    "SH_SQUARE": "Vua của các hình học phẳng: Vừa là hình chữ nhật đặc biệt (4 cạnh bằng nhau), vừa là hình thoi đặc biệt (4 góc vuông). Kế thừa toàn bộ tính chất của cả hai hình!",
    "hinh_vuong": "Vua của các hình học phẳng: Kế thừa đầy đủ mọi tính chất của cả Hình chữ nhật và Hình thoi.",
    "SH_KITE": "Hình diều: Có 2 cặp cạnh kề bằng nhau, hai đường chéo vuông góc. Diện tích S = (d₁ × d₂) / 2 giống hình thoi.",
    "hinh_dieu": "Hình diều: Có 2 cặp cạnh kề bằng nhau, hai đường chéo vuông góc. Diện tích S = (d₁ × d₂) / 2."
}

EXERCISES_DATA = [
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
]

# Bộ nhớ tạm lưu trữ Leaderboard và Players
PLAYERS_DB = {
    "Nguyễn Hữu Lộc": {"score": 350, "coins": 180},
    "Nguyễn Thị Quyên": {"score": 310, "coins": 150},
    "Dương Chí Khải": {"score": 280, "coins": 120},
    "ThS. Trần Quang Bình": {"score": 500, "coins": 300},
}

# ==============================================================================
# ROUTES & RESTFUL APIS
# ==============================================================================

@app.route("/")
def index():
    return render_template("index.html")

# 1. Trạng thái kết nối Neo4j Aura Cloud Free
@app.route("/api/db/status", methods=["GET"])
def db_status():
    t_start = time.time()
    res = run_cypher("MATCH (n) RETURN count(n) as total_nodes")
    latency = round((time.time() - t_start) * 1000, 2)
    
    if res is not None and len(res) > 0:
        total_nodes = res[0]["total_nodes"]
        rel_res = run_cypher("MATCH ()-[r]->() RETURN count(r) as total_rels")
        total_rels = rel_res[0]["total_rels"] if rel_res else 0
        return jsonify({
            "status": "connected",
            "host": NEO4J_URI,
            "user": NEO4J_USER,
            "cloud_provider": "Neo4j AuraDB (Cloud Free)",
            "latency_ms": latency,
            "nodes_count": total_nodes,
            "rels_count": total_rels
        })
    else:
        return jsonify({
            "status": "disconnected",
            "host": NEO4J_URI,
            "error": "Không thể kết nối đến máy chủ Neo4j Aura Cloud. Vui lòng kiểm tra lại URI/Password trong file .env",
            "latency_ms": latency
        }), 500

# 2. Lấy dữ liệu đồ thị phân cấp Tứ giác (Dành cho Vis-network Tree)
@app.route("/api/graph/hierarchy", methods=["GET"])
def graph_hierarchy():
    # 1. Truy vấn các Shape từ Neo4j Cloud
    cypher_shapes = """
        MATCH (s:Shape)
        OPTIONAL MATCH (s)-[:HAS_FORMULA]->(f:Formula)
        OPTIONAL MATCH (s)-[:HAS_PROPERTY]->(p:Property)
        RETURN s.id AS id, s.name AS name, s.definition AS definition, s.description AS description,
               collect(DISTINCT {name: f.name, expr: f.expression}) AS formulas,
               collect(DISTINCT p.name) AS properties
        ORDER BY s.id
    """
    shapes_data = run_cypher(cypher_shapes)
    
    # 2. Truy vấn quan hệ kế thừa IS_A
    cypher_edges = """
        MATCH (child:Shape)-[r:IS_A]->(parent:Shape)
        RETURN child.id AS from_id, parent.id AS to_id, type(r) AS type,
               child.name AS child_name, parent.name AS parent_name
    """
    edges_data = run_cypher(cypher_edges)
    
    # Nếu kết nối cloud ok
    if shapes_data and edges_data:
        nodes = []
        for s in shapes_data:
            s_id = s["id"]
            # Chuẩn hóa công thức chu vi và diện tích
            p_formula = "Tùy thuộc các cạnh"
            s_formula = "Không có công thức chung"
            for f in s.get("formulas", []):
                fname = (f.get("name") or "").lower()
                if "chu vi" in fname:
                    p_formula = f.get("expr") or p_formula
                elif "diện tích" in fname:
                    s_formula = f.get("expr") or s_formula
            
            nodes.append({
                "id": s_id,
                "name": s["name"],
                "definition": s.get("definition", ""),
                "description": s.get("description", ""),
                "chu_vi": p_formula,
                "dien_tich": s_formula,
                "tinh_chat": "; ".join(s.get("properties", [])[:3]) if s.get("properties") else "Kế thừa từ hình cha",
                "meo": SHAPE_TIPS.get(s_id, SHAPE_TIPS.get(s["name"], "Quan sát kỹ các đường chéo và cạnh đối để nhận dạng hình chuẩn xác nhất."))
            })
            
        # Nút gốc đại diện
        root_exists = any(n["id"] == "hinh_hoc_phang" for n in nodes)
        if not root_exists:
            nodes.insert(0, {
                "id": "hinh_hoc_phang",
                "name": "Hình học phẳng",
                "definition": "Không gian 2 chiều là nền tảng của hình học.",
                "description": "Bao gồm tất cả các đa giác trong mặt phẳng.",
                "chu_vi": "Tùy thuộc từng hình",
                "dien_tich": "Tùy thuộc từng hình",
                "tinh_chat": "Không gian 2 chiều phẳng",
                "meo": SHAPE_TIPS["hinh_hoc_phang"]
            })
            
        edges = []
        # Nối Hình học phẳng -> Tứ giác
        edges.append({
            "from": "hinh_hoc_phang",
            "to": "SH_QUAD",
            "label": "Bao gồm đa giác 4 cạnh",
            "type": "BAO_GOM"
        })
        
        # Trong Neo4j, mối quan hệ kế thừa IS_A lưu child -> parent (ví dụ: Hình vuông IS_A Hình chữ nhật).
        # Khi vẽ cây phả hệ tự nhiên từ gốc đến chi tiết (Root -> Leaf): ta vẽ parent -> child
        for e in edges_data:
            edges.append({
                "from": e["to_id"],
                "to": e["from_id"],
                "label": "Kế thừa & phát triển",
                "type": "TIEN_HOA_THANH"
            })
            
        return jsonify({"nodes": nodes, "edges": edges})
        
    # Fallback dữ liệu nội bộ chuẩn xác nếu Cloud gián đoạn
    return jsonify({
        "nodes": [
            {"id": "hinh_hoc_phang", "name": "Hình học phẳng", "chu_vi": "Tùy từng hình", "dien_tich": "Tùy từng hình", "meo": SHAPE_TIPS["hinh_hoc_phang"]},
            {"id": "SH_QUAD", "name": "Tứ giác", "chu_vi": "P = a + b + c + d", "dien_tich": "Tùy từng hình", "meo": SHAPE_TIPS["SH_QUAD"]},
            {"id": "SH_TRAP", "name": "Hình thang", "chu_vi": "P = a + b + c + d", "dien_tich": "S = (a + b) × h / 2", "meo": SHAPE_TIPS["SH_TRAP"]},
            {"id": "SH_ISOTRAP", "name": "Hình thang cân", "chu_vi": "P = a + b + 2c", "dien_tich": "S = (a + b) × h / 2", "meo": SHAPE_TIPS["SH_ISOTRAP"]},
            {"id": "SH_RIGHTTRAP", "name": "Hình thang vuông", "chu_vi": "P = a + b + c + h", "dien_tich": "S = (a + b) × h / 2", "meo": SHAPE_TIPS["SH_RIGHTTRAP"]},
            {"id": "SH_PARA", "name": "Hình bình hành", "chu_vi": "P = 2(a + b)", "dien_tich": "S = a × h", "meo": SHAPE_TIPS["SH_PARA"]},
            {"id": "SH_RECT", "name": "Hình chữ nhật", "chu_vi": "P = 2(a + b)", "dien_tich": "S = a × b", "meo": SHAPE_TIPS["SH_RECT"]},
            {"id": "SH_RHOMBUS", "name": "Hình thoi", "chu_vi": "P = 4a", "dien_tich": "S = (d₁ × d₂) / 2", "meo": SHAPE_TIPS["SH_RHOMBUS"]},
            {"id": "SH_SQUARE", "name": "Hình vuông", "chu_vi": "P = 4a", "dien_tich": "S = a²", "meo": SHAPE_TIPS["SH_SQUARE"]}
        ],
        "edges": [
            {"from": "hinh_hoc_phang", "to": "SH_QUAD", "label": "Bao gồm"},
            {"from": "SH_QUAD", "to": "SH_TRAP", "label": "Có 1 cặp cạnh đối song song"},
            {"from": "SH_TRAP", "to": "SH_ISOTRAP", "label": "2 góc đáy bằng nhau"},
            {"from": "SH_TRAP", "to": "SH_RIGHTTRAP", "label": "Có 1 góc vuông"},
            {"from": "SH_QUAD", "to": "SH_PARA", "label": "2 cặp cạnh đối song song"},
            {"from": "SH_PARA", "to": "SH_RECT", "label": "Có 1 góc vuông"},
            {"from": "SH_PARA", "to": "SH_RHOMBUS", "label": "4 cạnh bằng nhau"},
            {"from": "SH_RECT", "to": "SH_SQUARE", "label": "4 cạnh bằng nhau"},
            {"from": "SH_RHOMBUS", "to": "SH_SQUARE", "label": "Có 1 góc vuông"}
        ]
    })

# 3. Lấy dữ liệu Knowledge Graph đa tầng (Shapes, Properties, Formulas, Conditions)
@app.route("/api/graph/knowledge", methods=["GET"])
def graph_knowledge():
    inc_props = request.args.get("include_props", "true") == "true"
    inc_formulas = request.args.get("include_formulas", "true") == "true"
    inc_conditions = request.args.get("include_conditions", "true") == "true"

    nodes = []
    edges = []

    # 1. Shapes
    shapes = run_cypher("MATCH (s:Shape) RETURN s.id AS id, s.name AS name, s.definition AS definition")
    if shapes:
        for s in shapes:
            nodes.append({
                "id": s["id"],
                "label": s["name"],
                "group": "shape",
                "title": f"<b>{s['name']}</b><br>{s.get('definition', '')}",
                "color": "#2563eb",
                "size": 26,
                "shape": "dot"
            })

    # Quan hệ IS_A giữa các Shape
    isa_rels = run_cypher("MATCH (s:Shape)-[r:IS_A]->(parent:Shape) RETURN s.id AS s_id, parent.id AS p_id")
    if isa_rels:
        for r in isa_rels:
            edges.append({
                "from": r["s_id"],
                "to": r["p_id"],
                "label": "IS_A",
                "color": "#3b82f6",
                "arrows": "to",
                "width": 2
            })

    # 2. Properties
    if inc_props:
        props = run_cypher("""
            MATCH (s:Shape)-[:HAS_PROPERTY]->(p:Property)
            RETURN s.id AS s_id, p.id AS p_id, p.name AS p_name, p.category AS p_cat, p.description AS p_desc
        """)
        added_props = set()
        if props:
            for p in props:
                pid = p["p_id"]
                if pid not in added_props:
                    nodes.append({
                        "id": pid,
                        "label": p["p_name"],
                        "group": "property",
                        "title": f"<b>[{p['p_cat']}]</b> {p['p_name']}<br>{p.get('p_desc', '')}",
                        "color": "#10b981",
                        "size": 16,
                        "shape": "ellipse"
                    })
                    added_props.add(pid)
                edges.append({
                    "from": p["s_id"],
                    "to": pid,
                    "label": "HAS_PROP",
                    "color": "#059669",
                    "arrows": "to"
                })

    # 3. Formulas
    if inc_formulas:
        forms = run_cypher("""
            MATCH (s:Shape)-[:HAS_FORMULA]->(f:Formula)
            RETURN s.id AS s_id, f.id AS f_id, f.name AS f_name, f.expression AS f_expr, f.description AS f_desc
        """)
        added_forms = set()
        if forms:
            for f in forms:
                fid = f["f_id"]
                if fid not in added_forms:
                    nodes.append({
                        "id": fid,
                        "label": f["f_expr"],
                        "group": "formula",
                        "title": f"<b>{f['f_name']}</b>: {f['f_expr']}<br>{f.get('f_desc', '')}",
                        "color": "#f59e0b",
                        "size": 16,
                        "shape": "box"
                    })
                    added_forms.add(fid)
                edges.append({
                    "from": f["s_id"],
                    "to": fid,
                    "label": "FORMULA",
                    "color": "#d97706",
                    "arrows": "to"
                })

    # 4. Conditions
    if inc_conditions:
        conds = run_cypher("""
            MATCH (s:Shape)-[:HAS_CONDITION]->(c:RecognitionCondition)
            RETURN s.id AS s_id, c.id AS c_id, c.name AS c_name, c.description AS c_desc
        """)
        added_conds = set()
        if conds:
            for c in conds:
                cid = c["c_id"]
                if cid not in added_conds:
                    nodes.append({
                        "id": cid,
                        "label": c["c_name"],
                        "group": "condition",
                        "title": f"<b>{c['c_name']}</b><br>{c.get('c_desc', '')}",
                        "color": "#ec4899",
                        "size": 16,
                        "shape": "diamond"
                    })
                    added_conds.add(cid)
                edges.append({
                    "from": c["s_id"],
                    "to": cid,
                    "label": "CONDITION",
                    "color": "#db2777",
                    "arrows": "to"
                })

    # Fallback an toàn nếu Cloud DB mất kết nối tạm thời
    if not nodes:
        fallback_shapes = [
            {"id": "SH_QUAD", "name": "Tứ giác", "def": "Đa giác có 4 cạnh khép kín"},
            {"id": "SH_TRAP", "name": "Hình thang", "def": "Có 1 cặp cạnh đối song song"},
            {"id": "SH_ISOTRAP", "name": "Hình thang cân", "def": "Hình thang có 2 góc đáy bằng nhau"},
            {"id": "SH_RIGHTTRAP", "name": "Hình thang vuông", "def": "Hình thang có 1 góc vuông"},
            {"id": "SH_PARA", "name": "Hình bình hành", "def": "Có 2 cặp cạnh đối song song"},
            {"id": "SH_RECT", "name": "Hình chữ nhật", "def": "Tứ giác có 4 góc vuông"},
            {"id": "SH_RHOMBUS", "name": "Hình thoi", "def": "Tứ giác có 4 cạnh bằng nhau"},
            {"id": "SH_SQUARE", "name": "Hình vuông", "def": "4 góc vuông và 4 cạnh bằng nhau"}
        ]
        for s in fallback_shapes:
            nodes.append({
                "id": s["id"], "label": s["name"], "group": "shape",
                "title": f"<b>{s['name']}</b><br>{s['def']}",
                "color": "#2563eb", "size": 26, "shape": "dot"
            })
        edges.extend([
            {"from": "SH_TRAP", "to": "SH_QUAD", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_ISOTRAP", "to": "SH_TRAP", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_RIGHTTRAP", "to": "SH_TRAP", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_PARA", "to": "SH_QUAD", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_RECT", "to": "SH_PARA", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_RHOMBUS", "to": "SH_PARA", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_SQUARE", "to": "SH_RECT", "label": "IS_A", "color": "#3b82f6", "arrows": "to"},
            {"from": "SH_SQUARE", "to": "SH_RHOMBUS", "label": "IS_A", "color": "#3b82f6", "arrows": "to"}
        ])

    return jsonify({"nodes": nodes, "edges": edges})

# 4. Lấy chi tiết toàn bộ các hình tứ giác (Lookup & Tra cứu)
@app.route("/api/shapes", methods=["GET"])
def get_all_shapes():
    cypher = """
        MATCH (s:Shape)
        OPTIONAL MATCH (s)-[:IS_A]->(parent:Shape)
        OPTIONAL MATCH (s)-[:HAS_FORMULA]->(f:Formula)
        OPTIONAL MATCH (s)-[:HAS_PROPERTY]->(p:Property)
        OPTIONAL MATCH (s)-[:HAS_CONDITION]->(c:RecognitionCondition)
        RETURN s.id AS id, s.name AS name, s.definition AS definition, s.description AS description,
               collect(DISTINCT parent.name) AS parents,
               collect(DISTINCT {name: f.name, expr: f.expression, vars: f.variables, desc: f.description}) AS formulas,
               collect(DISTINCT {name: p.name, category: p.category, desc: p.description}) AS properties,
               collect(DISTINCT {name: c.name, desc: c.description}) AS conditions
        ORDER BY s.id
    """
    results = run_cypher(cypher)
    if results:
        # Bổ sung mẹo ghi nhớ
        for item in results:
            item["tip"] = SHAPE_TIPS.get(item["id"], SHAPE_TIPS.get(item["name"], ""))
        return jsonify(results)
    return jsonify([])

# 5. Lấy danh sách tất cả tính chất phân theo nhóm Cạnh, Góc, Đường chéo (Cho bộ máy suy luận)
@app.route("/api/properties", methods=["GET"])
def get_properties():
    cypher = """
        MATCH (p:Property)
        RETURN p.id AS id, p.name AS name, p.category AS category, p.description AS description
        ORDER BY p.category, p.name
    """
    props = run_cypher(cypher)
    grouped = {}
    if props:
        for p in props:
            cat = p.get("category", "Khác")
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(p)
    return jsonify(grouped)

# 6. BỘ MÁY SUY LUẬN NHẬN DIỆN TỨ GIÁC THEO TÍNH CHẤT (Inference Engine)
@app.route("/api/identify", methods=["POST"])
def identify_shape():
    data = request.get_json() or {}
    selected_props = data.get("properties", [])
    if not selected_props:
        return jsonify({"success": False, "error": "Vui lòng chọn ít nhất một tính chất hình học để nhận diện."}), 400

    cypher = """
        MATCH (s:Shape)-[:HAS_PROPERTY]->(p:Property)
        WHERE p.name IN $selected
        WITH s, count(DISTINCT p) AS matchedCount, collect(p.name) AS matchedProps
        WHERE matchedCount = size($selected)
        OPTIONAL MATCH (s)-[:IS_A*]->(ancestor:Shape)
        RETURN s.id AS id, s.name AS name, s.definition AS definition, s.description AS description,
               matchedCount, matchedProps, collect(DISTINCT ancestor.name) AS ancestors
        ORDER BY size(ancestors) DESC
    """
    results = run_cypher(cypher, {"selected": selected_props})
    
    if results and len(results) > 0:
        return jsonify({
            "success": True,
            "matched_count": len(results),
            "shapes": results,
            "explanation": f"Hệ thống đã truy vấn Knowledge Graph Neo4j và xác định có {len(results)} hình sở hữu toàn bộ {len(selected_props)} tính chất bạn chọn. Hình hẹp nhất thỏa mãn điều kiện là: {results[0]['name']}."
        })
    else:
        # Tìm các hình khớp một phần (Partial matches) để gợi ý cho người học
        partial_cypher = """
            MATCH (s:Shape)-[:HAS_PROPERTY]->(p:Property)
            WHERE p.name IN $selected
            WITH s, count(DISTINCT p) AS matchedCount, collect(p.name) AS matchedProps
            RETURN s.name AS name, matchedCount, matchedProps
            ORDER BY matchedCount DESC
            LIMIT 3
        """
        partials = run_cypher(partial_cypher, {"selected": selected_props})
        return jsonify({
            "success": False,
            "message": "Không tìm thấy loại tứ giác nào sở hữu đồng thời tất cả các tính chất trên (Tập tính chất mâu thuẫn hoặc chưa có hình tương ứng trong CSDL).",
            "partials": partials or []
        })

# 7. SO SÁNH HAI LOẠI TỨ GIÁC (Common & Difference comparison)
@app.route("/api/compare", methods=["POST"])
def compare_shapes():
    data = request.get_json() or {}
    name1 = data.get("shape1")
    name2 = data.get("shape2")

    if not name1 or not name2:
        return jsonify({"error": "Vui lòng cung cấp đủ hai hình để so sánh."}), 400

    if name1 == name2:
        return jsonify({"error": "Vui lòng chọn hai loại hình khác nhau để tiến hành so sánh."}), 400

    cypher = """
        MATCH (s:Shape) WHERE s.name IN [$name1, $name2]
        OPTIONAL MATCH (s)-[:HAS_PROPERTY]->(p:Property)
        RETURN s.name AS name, collect(DISTINCT p.name) AS props
    """
    res = run_cypher(cypher, {"name1": name1, "name2": name2})
    props_dict = {r["name"]: set(r["props"]) for r in res}

    p1 = props_dict.get(name1, set())
    p2 = props_dict.get(name2, set())

    common = list(p1 & p2)
    diff1 = list(p1 - p2)
    diff2 = list(p2 - p1)

    return jsonify({
        "shape1": name1,
        "shape2": name2,
        "common_properties": common,
        "diff_shape1": diff1,
        "diff_shape2": diff2
    })

# 8. BÀI TOÁN LUYỆN TẬP
@app.route("/api/exercises", methods=["GET"])
def get_exercises():
    shape_id = request.args.get("shape_id")
    if shape_id and shape_id != "all":
        filtered = [ex for ex in EXERCISES_DATA if ex["shape_id"] == shape_id or ex["shape_name"].lower() == shape_id.lower()]
        return jsonify(filtered)
    return jsonify(EXERCISES_DATA)

@app.route("/api/exercises/check", methods=["POST"])
def check_exercise():
    data = request.get_json() or {}
    ex_id = data.get("exercise_id")
    user_val = data.get("user_answer")

    ex = next((e for e in EXERCISES_DATA if e["id"] == ex_id), None)
    if not ex:
        return jsonify({"error": "Không tìm thấy bài toán."}), 404

    try:
        val = float(user_val)
        is_correct = abs(val - ex["correct_answer"]) < 0.05
        return jsonify({
            "is_correct": is_correct,
            "correct_answer": ex["correct_answer"],
            "unit": ex["unit"],
            "solution": ex["solution"],
            "earned_score": 10 if is_correct else 0,
            "earned_coins": 5 if is_correct else 0
        })
    except (ValueError, TypeError):
        return jsonify({"error": "Đáp số phải là một số hợp lệ."}), 400

# 9. BỘ CÂU HỎI TRẮC NGHIỆM QUIZ VÀ GIẢI THÍCH TẠI SAO TỪ NEO4J
@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    # Truy vấn các câu hỏi có trong Neo4j Aura Cloud DB
    cypher = """
        MATCH (q:Question)-[:HAS_ANSWER]->(a:Answer)
        OPTIONAL MATCH (q)-[:HAS_SOLUTION]->(s:Solution)
        OPTIONAL MATCH (s)-[:USES_CONDITION]->(c:RecognitionCondition)
        RETURN q.id AS id, q.content AS question, q.difficulty AS diff,
               collect({content: a.content, isCorrect: a.isCorrect}) AS answers,
               s.content AS sol_content, s.explanation AS explanation,
               c.name AS cond_name
        ORDER BY q.id
    """
    cloud_questions = run_cypher(cypher)
    quiz_items = []

    if cloud_questions:
        for q in cloud_questions:
            options = [ans["content"] for ans in q["answers"]]
            correct_ans = next((ans["content"] for ans in q["answers"] if ans["isCorrect"]), "")
            explain = q.get("explanation") or q.get("sol_content") or "Dựa trên định nghĩa và dấu hiệu nhận biết trong hình học."
            if q.get("cond_name"):
                explain += f" (Căn cứ dấu hiệu: {q['cond_name']})"
            quiz_items.append({
                "id": q["id"],
                "question": q["question"],
                "options": options,
                "answer": correct_ans,
                "explain": explain,
                "difficulty": q.get("diff", "Cơ bản")
            })

    # Thêm các câu hỏi mở rộng thú vị
        extra_questions = [
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
    ],


    all_questions = quiz_items + extra_questions
    return jsonify(all_questions)

# 10. LƯU KẾT QUẢ QUIZ & CẬP NHẬT ĐIỂM NGƯỜI CHƠI
@app.route("/api/quiz/finish", methods=["POST"])
def finish_quiz():
    data = request.get_json() or {}
    username = data.get("username", "Khách").strip()
    earned_score = int(data.get("earned_score", 0))
    earned_coins = int(data.get("earned_coins", 0))

    if username not in PLAYERS_DB:
        PLAYERS_DB[username] = {"score": 0, "coins": 0}

    PLAYERS_DB[username]["score"] += earned_score
    PLAYERS_DB[username]["coins"] += earned_coins

    return jsonify({
        "username": username,
        "score": PLAYERS_DB[username]["score"],
        "coins": PLAYERS_DB[username]["coins"],
        "earned_score": earned_score,
        "earned_coins": earned_coins
    })

# 11. ĐỒNG BỘ NGƯỜI CHƠI (Get or Create Player)
@app.route("/api/player/get_or_create", methods=["POST"])
def get_or_create_player():
    data = request.get_json() or {}
    username = data.get("username", "Học viên").strip()
    if not username:
        username = "Học viên"

    if username not in PLAYERS_DB:
        PLAYERS_DB[username] = {"score": 0, "coins": 0}

    p = PLAYERS_DB[username]
    return jsonify({
        "username": username,
        "score": p["score"],
        "coins": p["coins"]
    })

# 12. BẢNG XẾP HẠNG (LEADERBOARD)
@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    sorted_players = []
    for uname, pdata in PLAYERS_DB.items():
        sorted_players.append({
            "username": uname,
            "score": pdata["score"],
            "coins": pdata["coins"]
        })
    sorted_players.sort(key=lambda x: (x["score"], x["coins"]), reverse=True)
    return jsonify(sorted_players[:15])

# 14. THỐNG KÊ TOÀN DIỆN CƠ SỞ DỮ LIỆU NEO4J AURA CLOUD
@app.route("/api/stats", methods=["GET"])
def get_database_stats():
    # 1. Tổng quan
    shapes_c = run_cypher("MATCH (n:Shape) RETURN count(n) AS c")
    props_c = run_cypher("MATCH (n:Property) RETURN count(n) AS c")
    forms_c = run_cypher("MATCH (n:Formula) RETURN count(n) AS c")
    conds_c = run_cypher("MATCH (n:RecognitionCondition) RETURN count(n) AS c")
    quests_c = run_cypher("MATCH (n:Question) RETURN count(n) AS c")
    rels_c = run_cypher("MATCH ()-[r]->() RETURN count(r) AS c")

    # 2. Phân bố nhãn Node
    node_labels = run_cypher("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """)

    # 3. Phân bố loại quan hệ Relationship
    rel_types = run_cypher("""
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(r) AS count
        ORDER BY count DESC
    """)

    return jsonify({
        "summary": {
            "shapes": shapes_c[0]["c"] if shapes_c else 8,
            "properties": props_c[0]["c"] if props_c else 14,
            "formulas": forms_c[0]["c"] if forms_c else 9,
            "conditions": conds_c[0]["c"] if conds_c else 16,
            "questions": quests_c[0]["c"] if quests_c else 3,
            "relationships": rels_c[0]["c"] if rels_c else 54
        },
        "labels": node_labels or [],
        "relationships": rel_types or []
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Khởi chạy ứng dụng Web Tứ Giác Neo4j tại http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
