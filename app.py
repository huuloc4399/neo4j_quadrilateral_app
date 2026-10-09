import streamlit as st
from neo4j import GraphDatabase
import pyvis.network as net
import streamlit.components.v1 as components

# Cau hinh giao dien Streamlit chuyen nghiep, khong dung emoji
st.set_page_config(
    page_title="He thong Ho tro Hoc toan Tu giac - Neo4j",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thong tin ket noi Neo4j Aura
NEO4J_URI = "neo4j+s://ce509dc3.databases.neo4j.io"
NEO4J_USER = "ce509dc3"
NEO4J_PASS = "0_jtQh4inSO0zp6Wesv2alboUutMGuBm-S5Mq8D5RqI"

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def run_query(query, params=None):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]

# --- SIDEBAR ---
with st.sidebar:
    st.title("HÌNH HỌC TỨ GIÁC")
    st.caption("Ứng dụng Knowledge Graph trên cơ sở dữ liệu Neo4j")
    
    st.info("Trạng thái: Đã kết nối cơ sở dữ liệu Neo4j Aura")
    
    menu = st.radio(
        "Chức năng hệ thống:",
        [
            "1. Tra cứu Tứ giác",
            "2. Đồ thị Tri thức (Knowledge Graph)",
            "3. Nhận diện Tứ giác theo tính chất",
            "4. So sánh hai loại Tứ giác",
            "5. Trắc nghiệm và giải thích 'Tại sao?'",
            "6. Thống kê cơ sở dữ liệu Neo4j"
        ]
    )
    
    st.divider()
    st.markdown("**ĐỀ TÀI MÔN HỌC: DỮ LIỆU NOSQL**")
    st.markdown("**Giảng viên hướng dẫn:** ThS. Trần Quang Bình")
    st.caption("Nhóm thực hiện: Nhóm 08\n- Nguyễn Hữu Lộc\n- Nguyễn Thị Quyên\n- Dương Chí Khải")

# --- 1. TRA CUU TU GIAC (FR01, FR02, FR05, FR06) ---
if menu == "1. Tra cứu Tứ giác":
    st.header("1. Tra cứu thông tin chi tiết các loại tứ giác")
    st.caption("Căn cứ yêu cầu chức năng FR01, FR02, FR05, FR06 trong hồ sơ đặc tả.")
    
    shapes = run_query("MATCH (s:Shape) RETURN s.id AS id, s.name AS name ORDER BY s.name")
    shape_names = [s['name'] for s in shapes]
    
    selected_shape = st.selectbox("Lựa chọn loại tứ giác cần tra cứu:", shape_names, index=shape_names.index("Hình vuông") if "Hình vuông" in shape_names else 0)
    
    if selected_shape:
        col1, col2 = st.columns([1, 1])
        
        info = run_query("""
            MATCH (s:Shape {name: $name})
            OPTIONAL MATCH (s)-[:IS_A]->(parent:Shape)
            RETURN s.definition AS definition, s.description AS description, collect(parent.name) AS parents
        """, {"name": selected_shape})
        
        if info:
            data = info[0]
            with col1:
                st.subheader("Định nghĩa và phân loại")
                st.markdown(f"**Định nghĩa:** {data['definition']}")
                st.markdown(f"**Mô tả:** {data['description']}")
                if data['parents']:
                    st.markdown(f"**Quan hệ kế thừa trực tiếp (IS_A):** {', '.join(data['parents'])}")
                
                # Cong thuc
                formulas = run_query("""
                    MATCH (s:Shape {name: $name})-[:HAS_FORMULA]->(f:Formula)
                    RETURN f.name AS name, f.expression AS expression, f.variables AS variables, f.description AS description
                """, {"name": selected_shape})
                st.subheader("Công thức hình học")
                if formulas:
                    for f in formulas:
                        st.markdown(f"- **{f['name']}**: `{f['expression']}` ({f['variables']})")
                        st.caption(f"{f['description']}")
                else:
                    st.write("Chưa có công thức áp dụng riêng.")
                    
            with col2:
                # Tinh chat
                properties = run_query("""
                    MATCH (s:Shape {name: $name})-[:HAS_PROPERTY]->(p:Property)
                    RETURN p.name AS name, p.category AS category, p.description AS description
                    ORDER BY p.category
                """, {"name": selected_shape})
                st.subheader("Tính chất hình học")
                if properties:
                    for p in properties:
                        st.markdown(f"- **[{p['category']}]** {p['name']}: {p['description']}")
                
                # Dau hieu nhan biet
                conditions = run_query("""
                    MATCH (s:Shape {name: $name})-[:HAS_CONDITION]->(c:RecognitionCondition)
                    RETURN c.name AS name, c.description AS description
                """, {"name": selected_shape})
                st.subheader("Dấu hiệu nhận biết")
                if conditions:
                    for c in conditions:
                        st.markdown(f"- **{c['name']}**: {c['description']}")

# --- 2. KNOWLEDGE GRAPH TUONG TAC (FR08) ---
elif menu == "2. Đồ thị Tri thức (Knowledge Graph)":
    st.header("2. Bản đồ tri thức hình học tứ giác (Knowledge Graph)")
    st.caption("Căn cứ yêu cầu chức năng FR08 - Biểu diễn trực quan các thực thể và mối quan hệ trên Neo4j.")
    
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        include_props = st.checkbox("Hiển thị các nút Tính chất (Property)", value=True)
    with col_filter2:
        include_formulas = st.checkbox("Hiển thị Công thức (Formula) và Dấu hiệu (Condition)", value=False)
        
    cypher_graph = """
        MATCH (s:Shape)
        OPTIONAL MATCH (s)-[r_is:IS_A]->(s2:Shape)
        RETURN s, r_is, s2
    """
    results = run_query(cypher_graph)
    
    # Khoi tao do thi pyvis
    graph = net.Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#222222", directed=True, cdn_resources="remote")
    graph.force_atlas_2based()
    
    # Them Shape nodes
    shapes = run_query("MATCH (s:Shape) RETURN s.id AS id, s.name AS name")
    for s in shapes:
        graph.add_node(s['id'], label=s['name'], color="#1d4ed8", size=25, title=s['name'], shape="dot")
        
    # Them quan he IS_A
    for r in results:
        if r['s'] and r['s2']:
            graph.add_edge(r['s']['id'], r['s2']['id'], label="IS_A", color="#3b82f6", arrows="to", width=2)
            
    # Them Properties
    if include_props:
        prop_res = run_query("MATCH (s:Shape)-[r:HAS_PROPERTY]->(p:Property) RETURN s.id AS s_id, p.id AS p_id, p.name AS p_name, p.category AS p_cat")
        for pr in prop_res:
            graph.add_node(pr['p_id'], label=pr['p_name'], color="#059669", size=15, title=f"[{pr['p_cat']}] {pr['p_name']}", shape="ellipse")
            graph.add_edge(pr['s_id'], pr['p_id'], label="HAS_PROPERTY", color="#10b981", arrows="to")
            
    # Them Formulas & Conditions
    if include_formulas:
        f_res = run_query("MATCH (s:Shape)-[r:HAS_FORMULA]->(f:Formula) RETURN s.id AS s_id, f.id AS f_id, f.expression AS f_expr")
        for fr in f_res:
            graph.add_node(fr['f_id'], label=fr['f_expr'], color="#d97706", size=15, title=fr['f_expr'], shape="box")
            graph.add_edge(fr['s_id'], fr['f_id'], label="HAS_FORMULA", color="#f59e0b", arrows="to")
            
        c_res = run_query("MATCH (s:Shape)-[r:HAS_CONDITION]->(c:RecognitionCondition) RETURN s.id AS s_id, c.id AS c_id, c.name AS c_name")
        for cr in c_res:
            graph.add_node(cr['c_id'], label=cr['c_name'], color="#db2777", size=15, title=cr['c_name'], shape="box")
            graph.add_edge(cr['s_id'], cr['c_id'], label="HAS_CONDITION", color="#ec4899", arrows="to")

    html_content = graph.generate_html()
    components.html(html_content, height=620)
    st.caption("Chú thích: Màu xanh dương: Loại Tứ giác (Shape) | Màu xanh lá: Tính chất (Property) | Màu vàng: Công thức (Formula) | Màu hồng: Dấu hiệu nhận biết (Condition)")

# --- 3. NHAN DIEN TU GIAC THEO TINH CHAT (FR03, FR04) ---
elif menu == "3. Nhận diện Tứ giác theo tính chất":
    st.header("3. Hệ thống suy luận nhận diện tứ giác theo tính chất")
    st.caption("Căn cứ yêu cầu chức năng FR03, FR04 - Suy luận loại hình và kiểm tra tính đầy đủ của dữ kiện.")
    st.write("Lựa chọn các tính chất hình học đã biết để hệ thống đối sánh trên đồ thị Neo4j:")
    
    all_properties = run_query("MATCH (p:Property) RETURN p.name AS name, p.category AS category ORDER BY p.category, p.name")
    
    categories = {}
    for p in all_properties:
        cat = p['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p['name'])
        
    selected_props = []
    cols = st.columns(len(categories))
    for i, (cat, props) in enumerate(categories.items()):
        with cols[i]:
            st.subheader(f"Nhóm: {cat}")
            for prop in props:
                if st.checkbox(prop, key=f"chk_{prop}"):
                    selected_props.append(prop)
                    
    st.divider()
    if st.button("Thực hiện nhận diện", type="primary"):
        if not selected_props:
            st.warning("Thông báo: Vui lòng chọn ít nhất một tính chất để nhận diện.")
        else:
            query = """
                MATCH (s:Shape)-[:HAS_PROPERTY]->(p:Property)
                WHERE p.name IN $selected
                WITH s, count(DISTINCT p) AS matchedCount
                WHERE matchedCount = size($selected)
                RETURN s.name AS name, s.definition AS definition, matchedCount
                ORDER BY matchedCount DESC
            """
            results = run_query(query, {"selected": selected_props})
            
            if results:
                st.success(f"Kết quả: Đã xác định được {len(results)} loại tứ giác thỏa mãn toàn bộ {len(selected_props)} tính chất được chọn:")
                for r in results:
                    st.markdown(f"### {r['name']}")
                    st.write(f"- Định nghĩa: {r['definition']}")
                    
                st.info("Cơ sở suy luận: Các hình trên đều chứa đầy đủ tập tính chất được chọn thông qua quan hệ phân loại và kế thừa (IS_A) trong Knowledge Graph.")
            else:
                st.error("Thông báo: Không tìm thấy loại tứ giác nào sở hữu đồng thời tất cả các tính chất trên (Tập tính chất chưa đủ hoặc có mâu thuẫn).")

# --- 4. SO SANH HAI LOAI TU GIAC (FR07) ---
elif menu == "4. So sánh hai loại Tứ giác":
    st.header("4. So sánh hai loại tứ giác")
    st.caption("Căn cứ yêu cầu chức năng FR07 - Phân tích điểm tương đồng và khác biệt giữa hai loại hình.")
    
    shapes = run_query("MATCH (s:Shape) RETURN s.name AS name ORDER BY s.name")
    names = [s['name'] for s in shapes]
    
    col1, col2 = st.columns(2)
    with col1:
        shape1 = st.selectbox("Loại hình thứ nhất:", names, index=names.index("Hình chữ nhật") if "Hình chữ nhật" in names else 0)
    with col2:
        shape2 = st.selectbox("Loại hình thứ hai:", names, index=names.index("Hình thoi") if "Hình thoi" in names else 1)
        
    if shape1 and shape2:
        if shape1 == shape2:
            st.warning("Vui lòng chọn hai loại hình khác nhau để tiến hành so sánh.")
        else:
            props1 = run_query("MATCH (s:Shape {name: $name})-[:HAS_PROPERTY]->(p:Property) RETURN collect(p.name) AS props", {"name": shape1})[0]['props']
            props2 = run_query("MATCH (s:Shape {name: $name})-[:HAS_PROPERTY]->(p:Property) RETURN collect(p.name) AS props", {"name": shape2})[0]['props']
            
            common = list(set(props1) & set(props2))
            diff1 = list(set(props1) - set(props2))
            diff2 = list(set(props2) - set(props1))
            
            st.subheader("Điểm giống nhau (Tính chất chung kế thừa)")
            if common:
                for p in common:
                    st.markdown(f"- {p}")
            else:
                st.write("Không có tính chất đặc trưng chung.")
                
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.subheader(f"Tính chất riêng của {shape1}")
                if diff1:
                    for p in diff1:
                        st.markdown(f"- {p}")
                else:
                    st.write("Không có tính chất riêng so với hình đối chiếu.")
            with col_d2:
                st.subheader(f"Tính chất riêng của {shape2}")
                if diff2:
                    for p in diff2:
                        st.markdown(f"- {p}")
                else:
                    st.write("Không có tính chất riêng so với hình đối chiếu.")

# --- 5. TRAC NGHIEM VA GIAI THICH TAI SAO (FR10, FR11) ---
elif menu == "5. Trắc nghiệm và giải thích 'Tại sao?'":
    st.header("5. Luyện tập trắc nghiệm và giải thích logic 'Tại sao?'")
    st.caption("Căn cứ yêu cầu chức năng FR10, FR11 - Kiểm tra kiến thức và truy xuất căn cứ suy luận từ Knowledge Graph.")
    
    questions = run_query("""
        MATCH (q:Question)-[:HAS_ANSWER]->(a:Answer)
        RETURN q.id AS id, q.content AS content, q.difficulty AS diff, collect({id: a.id, content: a.content, isCorrect: a.isCorrect}) AS answers
        ORDER BY q.id
    """)
    
    for i, q in enumerate(questions):
        st.subheader(f"Câu {i+1} [Mức độ: {q['diff']}]: {q['content']}")
        ans_options = [ans['content'] for ans in q['answers']]
        user_choice = st.radio(f"Lựa chọn đáp án cho Câu {i+1}:", ans_options, key=f"q_{q['id']}")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            check_ans = st.button("Kiểm tra đáp án", key=f"btn_chk_{q['id']}")
            
        if check_ans:
            chosen_ans = next(ans for ans in q['answers'] if ans['content'] == user_choice)
            if chosen_ans['isCorrect']:
                st.success("Đáp án chính xác.")
            else:
                st.error("Đáp án chưa chính xác.")
                
            sol = run_query("""
                MATCH (q:Question {id: $qid})-[:HAS_SOLUTION]->(s:Solution)
                OPTIONAL MATCH (s)-[:USES_CONDITION]->(c:RecognitionCondition)
                RETURN s.content AS content, s.explanation AS explanation, c.name AS cond_name, c.description AS cond_desc
            """, {"qid": q['id']})
            
            if sol:
                s_data = sol[0]
                with st.expander("Căn cứ giải thích 'Tại sao?' (Truy xuất từ Knowledge Graph)", expanded=True):
                    st.markdown(f"**Kết luận:** {s_data['content']}")
                    st.markdown(f"**Giải thích chi tiết:** {s_data['explanation']}")
                    if s_data['cond_name']:
                        st.info(f"Dấu hiệu nhận biết áp dụng: {s_data['cond_name']} ({s_data['cond_desc']})")
        st.divider()

# --- 6. THONG KE DATABASE NEO4J (FR18) ---
elif menu == "6. Thống kê cơ sở dữ liệu Neo4j":
    st.header("6. Thống kê cơ sở dữ liệu đồ thị Neo4j")
    st.caption("Căn cứ yêu cầu chức năng FR18 - Quản trị và giám sát các nút và liên kết trong Knowledge Graph.")
    
    col1, col2, col3, col4 = st.columns(4)
    shapes_count = run_query("MATCH (n:Shape) RETURN count(n) AS c")[0]['c']
    prop_count = run_query("MATCH (n:Property) RETURN count(n) AS c")[0]['c']
    form_count = run_query("MATCH (n:Formula) RETURN count(n) AS c")[0]['c']
    rel_count = run_query("MATCH ()-[r]->() RETURN count(r) AS c")[0]['c']
    
    col1.metric("Loại Tứ giác (Shape)", shapes_count)
    col2.metric("Tính chất (Property)", prop_count)
    col3.metric("Công thức (Formula)", form_count)
    col4.metric("Liên kết (Relationships)", rel_count)
    
    st.subheader("Thống kê chi tiết các loại Node:")
    all_nodes = run_query("MATCH (n) RETURN DISTINCT labels(n)[0] AS Label, count(n) AS SoLuong ORDER BY SoLuong DESC")
    st.table(all_nodes)
    
    st.subheader("Thống kê chi tiết các loại Quan hệ (Relationship):")
    all_rels = run_query("MATCH ()-[r]->() RETURN DISTINCT type(r) AS QuanHe, count(r) AS SoLuong ORDER BY SoLuong DESC")
    st.table(all_rels)
