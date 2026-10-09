// ==============================================================================
// ĐỒ ÁN CUỐI CHƯƠNG NEO4J - NHÓM 08
// ĐỀ TÀI: ỨNG DỤNG HỖ TRỢ HỌC TOÁN HÌNH HỌC PHẲNG (CHỦ ĐỀ TỨ GIÁC)
// FILE: setup_graph.cypher
// ==============================================================================

// 1. TẠO RÀNG BUỘC (CONSTRAINTS) VÀ CHỈ MỤC (INDEXES)
CREATE CONSTRAINT shape_id IF NOT EXISTS FOR (n:Shape) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT property_id IF NOT EXISTS FOR (n:Property) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT formula_id IF NOT EXISTS FOR (n:Formula) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT condition_id IF NOT EXISTS FOR (n:RecognitionCondition) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT theorem_id IF NOT EXISTS FOR (n:Theorem) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT question_id IF NOT EXISTS FOR (n:Question) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT level_id IF NOT EXISTS FOR (n:LearningLevel) REQUIRE n.id IS UNIQUE;

// 2. TẠO CÁC NODE SHAPE (LOẠI TỨ GIÁC)
MERGE (s_quad:Shape {id: 'SH_QUAD', name: 'Tứ giác', definition: 'Hình gồm bốn đoạn thẳng khép kín trong đó bất kì hai đoạn thẳng nào cũng không cùng nằm trên một đường thẳng.', description: 'Tứ giác lồi là tứ giác luôn nằm trong một nửa mặt phẳng có bờ là đường thẳng chứa bất kì cạnh nào của tứ giác.'})
MERGE (s_trap:Shape {id: 'SH_TRAP', name: 'Hình thang', definition: 'Tứ giác có hai cạnh đối song song.', description: 'Hai cạnh song song gọi là hai đáy, hai cạnh còn lại là hai cạnh bên.'})
MERGE (s_isotrap:Shape {id: 'SH_ISOTRAP', name: 'Hình thang cân', definition: 'Hình thang có hai góc kề một đáy bằng nhau.', description: 'Hình thang cân có hai cạnh bên bằng nhau và hai đường chéo bằng nhau.'})
MERGE (s_righttrap:Shape {id: 'SH_RIGHTTRAP', name: 'Hình thang vuông', definition: 'Hình thang có một góc vuông.', description: 'Cạnh bên vuông góc với hai đáy chính là đường cao của hình thang vuông.'})
MERGE (s_para:Shape {id: 'SH_PARA', name: 'Hình bình hành', definition: 'Tứ giác có hai cặp cạnh đối song song.', description: 'Hình bình hành có các cạnh đối bằng nhau, các góc đối bằng nhau, hai đường chéo cắt nhau tại trung điểm của mỗi đường.'})
MERGE (s_rect:Shape {id: 'SH_RECT', name: 'Hình chữ nhật', definition: 'Tứ giác có bốn góc vuông.', description: 'Hình chữ nhật là trường hợp đặc biệt của hình bình hành và hình thang cân; có hai đường chéo bằng nhau và cắt nhau tại trung điểm.'})
MERGE (s_rhombus:Shape {id: 'SH_RHOMBUS', name: 'Hình thoi', definition: 'Tứ giác có bốn cạnh bằng nhau.', description: 'Hình thoi là trường hợp đặc biệt của hình bình hành; hai đường chéo vuông góc với nhau và là đường phân giác các góc.'})
MERGE (s_square:Shape {id: 'SH_SQUARE', name: 'Hình vuông', definition: 'Tứ giác có bốn góc vuông và bốn cạnh bằng nhau.', description: 'Hình vuông đồng thời là hình chữ nhật và hình thoi; có tất cả tính chất của hai hình này.'})

// 3. THIẾT LẬP QUAN HỆ KẾ THỪA (IS_A)
MERGE (s_trap)-[:IS_A {priority: 1}]->(s_quad)
MERGE (s_isotrap)-[:IS_A {priority: 1}]->(s_trap)
MERGE (s_righttrap)-[:IS_A {priority: 1}]->(s_trap)
MERGE (s_para)-[:IS_A {priority: 1}]->(s_quad)
MERGE (s_rect)-[:IS_A {priority: 1}]->(s_para)
MERGE (s_rect)-[:IS_A {priority: 2}]->(s_isotrap)
MERGE (s_rhombus)-[:IS_A {priority: 1}]->(s_para)
MERGE (s_square)-[:IS_A {priority: 1}]->(s_rect)
MERGE (s_square)-[:IS_A {priority: 1}]->(s_rhombus)

// 4. TẠO CÁC TÍNH CHẤT (PROPERTY)
MERGE (p_sum360:Property {id: 'PROP_SUM_ANGLE', name: 'Tổng bốn góc bằng 360°', category: 'Góc', description: 'Tổng các góc trong của tứ giác luôn bằng 360 độ.'})
MERGE (p_2opp_parallel:Property {id: 'PROP_2OPP_PARALLEL', name: 'Có một cặp cạnh đối song song', category: 'Cạnh', description: 'Hai cạnh đối song song tạo thành hai đáy.'})
MERGE (p_opp_parallel:Property {id: 'PROP_OPP_PARALLEL', name: 'Hai cặp cạnh đối song song', category: 'Cạnh', description: 'Cả hai cặp cạnh đối diện đều song song với nhau.'})
MERGE (p_opp_equal:Property {id: 'PROP_OPP_EQUAL', name: 'Các cạnh đối bằng nhau', category: 'Cạnh', description: 'Độ dài hai cạnh đối diện bằng nhau từng đôi một.'})
MERGE (p_4equal_sides:Property {id: 'PROP_4EQUAL_SIDES', name: 'Bốn cạnh bằng nhau', category: 'Cạnh', description: 'Tất cả 4 cạnh của tứ giác đều có độ dài bằng nhau.'})
MERGE (p_opp_angles_equal:Property {id: 'PROP_OPP_ANGLES_EQUAL', name: 'Các góc đối bằng nhau', category: 'Góc', description: 'Hai góc đối diện nhau có số đo bằng nhau.'})
MERGE (p_adjacent_180:Property {id: 'PROP_ADJACENT_180', name: 'Hai góc kề một cạnh bù nhau', category: 'Góc', description: 'Tổng số đo hai góc kề một cạnh bằng 180°.'})
MERGE (p_base_angles_equal:Property {id: 'PROP_BASE_ANGLES_EQUAL', name: 'Hai góc kề một đáy bằng nhau', category: 'Góc', description: 'Các góc ở đáy của hình thang bằng nhau.'})
MERGE (p_1right_angle:Property {id: 'PROP_1RIGHT_ANGLE', name: 'Có ít nhất một góc vuông', category: 'Góc', description: 'Có một góc có số đo bằng 90°.'})
MERGE (p_4right_angles:Property {id: 'PROP_4RIGHT_ANGLES', name: 'Bốn góc vuông', category: 'Góc', description: 'Cả 4 góc trong tứ giác đều là góc vuông (90°).'})
MERGE (p_diag_bisect:Property {id: 'PROP_DIAG_BISECT', name: 'Hai đường chéo cắt nhau tại trung điểm mỗi đường', category: 'Đường chéo', description: 'Giao điểm của hai đường chéo là trung điểm của cả hai đường.'})
MERGE (p_diag_equal:Property {id: 'PROP_DIAG_EQUAL', name: 'Hai đường chéo bằng nhau', category: 'Đường chéo', description: 'Độ dài của hai đường chéo bằng nhau.'})
MERGE (p_diag_perp:Property {id: 'PROP_DIAG_PERP', name: 'Hai đường chéo vuông góc', category: 'Đường chéo', description: 'Hai đường chéo cắt nhau tạo thành góc 90°.'})
MERGE (p_diag_bisector:Property {id: 'PROP_DIAG_BISECTOR', name: 'Đường chéo là đường phân giác các góc', category: 'Đường chéo', description: 'Mỗi đường chéo chia góc ở đỉnh thành hai góc bằng nhau.'})

// 5. LIÊN KẾT SHAPE -> PROPERTY (HAS_PROPERTY)
// Tứ giác
MERGE (s_quad)-[:HAS_PROPERTY]->(p_sum360)

// Hình thang
MERGE (s_trap)-[:HAS_PROPERTY]->(p_sum360)
MERGE (s_trap)-[:HAS_PROPERTY]->(p_2opp_parallel)

// Hình thang cân
MERGE (s_isotrap)-[:HAS_PROPERTY]->(p_2opp_parallel)
MERGE (s_isotrap)-[:HAS_PROPERTY]->(p_base_angles_equal)
MERGE (s_isotrap)-[:HAS_PROPERTY]->(p_diag_equal)

// Hình thang vuông
MERGE (s_righttrap)-[:HAS_PROPERTY]->(p_2opp_parallel)
MERGE (s_righttrap)-[:HAS_PROPERTY]->(p_1right_angle)

// Hình bình hành
MERGE (s_para)-[:HAS_PROPERTY]->(p_opp_parallel)
MERGE (s_para)-[:HAS_PROPERTY]->(p_opp_equal)
MERGE (s_para)-[:HAS_PROPERTY]->(p_opp_angles_equal)
MERGE (s_para)-[:HAS_PROPERTY]->(p_adjacent_180)
MERGE (s_para)-[:HAS_PROPERTY]->(p_diag_bisect)

// Hình chữ nhật
MERGE (s_rect)-[:HAS_PROPERTY]->(p_opp_parallel)
MERGE (s_rect)-[:HAS_PROPERTY]->(p_opp_equal)
MERGE (s_rect)-[:HAS_PROPERTY]->(p_4right_angles)
MERGE (s_rect)-[:HAS_PROPERTY]->(p_diag_bisect)
MERGE (s_rect)-[:HAS_PROPERTY]->(p_diag_equal)

// Hình thoi
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_opp_parallel)
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_4equal_sides)
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_opp_angles_equal)
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_diag_bisect)
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_diag_perp)
MERGE (s_rhombus)-[:HAS_PROPERTY]->(p_diag_bisector)

// Hình vuông
MERGE (s_square)-[:HAS_PROPERTY]->(p_opp_parallel)
MERGE (s_square)-[:HAS_PROPERTY]->(p_4equal_sides)
MERGE (s_square)-[:HAS_PROPERTY]->(p_4right_angles)
MERGE (s_square)-[:HAS_PROPERTY]->(p_diag_bisect)
MERGE (s_square)-[:HAS_PROPERTY]->(p_diag_equal)
MERGE (s_square)-[:HAS_PROPERTY]->(p_diag_perp)
MERGE (s_square)-[:HAS_PROPERTY]->(p_diag_bisector)

// 6. CÔNG THỨC (FORMULA)
MERGE (f_trap_s:Formula {id: 'FORM_TRAP_S', name: 'Diện tích hình thang', expression: 'S = ((a + b) * h) / 2', variables: 'a, b: hai đáy; h: chiều cao', description: 'Diện tích hình thang bằng nửa tích tổng hai đáy với chiều cao.'})
MERGE (f_para_s:Formula {id: 'FORM_PARA_S', name: 'Diện tích hình bình hành', expression: 'S = a * h', variables: 'a: cạnh đáy; h: chiều cao tương ứng', description: 'Diện tích hình bình hành bằng tích một cạnh với chiều cao tương ứng.'})
MERGE (f_para_p:Formula {id: 'FORM_PARA_P', name: 'Chu vi hình bình hành', expression: 'P = 2 * (a + b)', variables: 'a, b: hai cạnh kề', description: 'Chu vi hình bình hành bằng hai lần tổng hai cạnh kề.'})
MERGE (f_rect_s:Formula {id: 'FORM_RECT_S', name: 'Diện tích hình chữ nhật', expression: 'S = a * b', variables: 'a: chiều dài; b: chiều rộng', description: 'Diện tích bằng tích hai kích thước chiều dài và chiều rộng.'})
MERGE (f_rect_p:Formula {id: 'FORM_RECT_P', name: 'Chu vi hình chữ nhật', expression: 'P = 2 * (a + b)', variables: 'a, b: chiều dài và chiều rộng', description: 'Chu vi bằng hai lần tổng của chiều dài và chiều rộng.'})
MERGE (f_rhombus_s:Formula {id: 'FORM_RHOMBUS_S', name: 'Diện tích hình thoi', expression: 'S = (d1 * d2) / 2', variables: 'd1, d2: độ dài hai đường chéo', description: 'Diện tích hình thoi bằng nửa tích độ dài hai đường chéo.'})
MERGE (f_rhombus_p:Formula {id: 'FORM_RHOMBUS_P', name: 'Chu vi hình thoi', expression: 'P = 4 * a', variables: 'a: độ dài cạnh', description: 'Chu vi hình thoi bằng bốn lần độ dài cạnh.'})
MERGE (f_square_s:Formula {id: 'FORM_SQUARE_S', name: 'Diện tích hình vuông', expression: 'S = a^2', variables: 'a: độ dài cạnh', description: 'Diện tích hình vuông bằng bình phương độ dài cạnh.'})
MERGE (f_square_p:Formula {id: 'FORM_SQUARE_P', name: 'Chu vi hình vuông', expression: 'P = 4 * a', variables: 'a: độ dài cạnh', description: 'Chu vi hình vuông bằng bốn lần độ dài cạnh.'})

// LIÊN KẾT SHAPE -> FORMULA (HAS_FORMULA)
MERGE (s_trap)-[:HAS_FORMULA]->(f_trap_s)
MERGE (s_isotrap)-[:HAS_FORMULA]->(f_trap_s)
MERGE (s_righttrap)-[:HAS_FORMULA]->(f_trap_s)
MERGE (s_para)-[:HAS_FORMULA]->(f_para_s)
MERGE (s_para)-[:HAS_FORMULA]->(f_para_p)
MERGE (s_rect)-[:HAS_FORMULA]->(f_rect_s)
MERGE (s_rect)-[:HAS_FORMULA]->(f_rect_p)
MERGE (s_rhombus)-[:HAS_FORMULA]->(f_rhombus_s)
MERGE (s_rhombus)-[:HAS_FORMULA]->(f_rhombus_p)
MERGE (s_square)-[:HAS_FORMULA]->(f_square_s)
MERGE (s_square)-[:HAS_FORMULA]->(f_square_p)

// 7. DẤU HIỆU NHẬN BIẾT (RECOGNITION CONDITION)
MERGE (c_para1:RecognitionCondition {id: 'COND_PARA_1', name: 'Hai cặp cạnh đối song song', description: 'Tứ giác có hai cặp cạnh đối song song là hình bình hành.'})
MERGE (c_para2:RecognitionCondition {id: 'COND_PARA_2', name: 'Hai cặp cạnh đối bằng nhau', description: 'Tứ giác có các cạnh đối bằng nhau là hình bình hành.'})
MERGE (c_para3:RecognitionCondition {id: 'COND_PARA_3', name: 'Một cặp cạnh đối song song và bằng nhau', description: 'Tứ giác có một cặp cạnh đối vừa song song vừa bằng nhau là hình bình hành.'})
MERGE (c_para4:RecognitionCondition {id: 'COND_PARA_4', name: 'Hai đường chéo cắt nhau tại trung điểm mỗi đường', description: 'Tứ giác có hai đường chéo cắt nhau tại trung điểm của mỗi đường là hình bình hành.'})

MERGE (c_rect1:RecognitionCondition {id: 'COND_RECT_1', name: 'Tứ giác có ba góc vuông', description: 'Tứ giác có ba góc vuông là hình chữ nhật.'})
MERGE (c_rect2:RecognitionCondition {id: 'COND_RECT_2', name: 'Hình bình hành có một góc vuông', description: 'Hình bình hành có một góc vuông là hình chữ nhật.'})
MERGE (c_rect3:RecognitionCondition {id: 'COND_RECT_3', name: 'Hình bình hành có hai đường chéo bằng nhau', description: 'Hình bình hành có hai đường chéo bằng nhau là hình chữ nhật.'})
MERGE (c_rect4:RecognitionCondition {id: 'COND_RECT_4', name: 'Hình thang cân có một góc vuông', description: 'Hình thang cân có một góc vuông là hình chữ nhật.'})

MERGE (c_rhombus1:RecognitionCondition {id: 'COND_RHOMBUS_1', name: 'Tứ giác có bốn cạnh bằng nhau', description: 'Tứ giác có bốn cạnh bằng nhau là hình thoi.'})
MERGE (c_rhombus2:RecognitionCondition {id: 'COND_RHOMBUS_2', name: 'Hình bình hành có hai cạnh kề bằng nhau', description: 'Hình bình hành có hai cạnh kề bằng nhau là hình thoi.'})
MERGE (c_rhombus3:RecognitionCondition {id: 'COND_RHOMBUS_3', name: 'Hình bình hành có hai đường chéo vuông góc', description: 'Hình bình hành có hai đường chéo vuông góc là hình thoi.'})
MERGE (c_rhombus4:RecognitionCondition {id: 'COND_RHOMBUS_4', name: 'Hình bình hành có một đường chéo là phân giác', description: 'Hình bình hành có một đường chéo là đường phân giác của một góc là hình thoi.'})

MERGE (c_square1:RecognitionCondition {id: 'COND_SQUARE_1', name: 'Hình chữ nhật có hai cạnh kề bằng nhau', description: 'Hình chữ nhật có hai cạnh kề bằng nhau là hình vuông.'})
MERGE (c_square2:RecognitionCondition {id: 'COND_SQUARE_2', name: 'Hình chữ nhật có hai đường chéo vuông góc', description: 'Hình chữ nhật có hai đường chéo vuông góc là hình vuông.'})
MERGE (c_square3:RecognitionCondition {id: 'COND_SQUARE_3', name: 'Hình thoi có một góc vuông', description: 'Hình thoi có một góc vuông là hình vuông.'})
MERGE (c_square4:RecognitionCondition {id: 'COND_SQUARE_4', name: 'Hình thoi có hai đường chéo bằng nhau', description: 'Hình thoi có hai đường chéo bằng nhau là hình vuông.'})

// LIÊN KẾT SHAPE -> CONDITION (HAS_CONDITION)
MERGE (s_para)-[:HAS_CONDITION]->(c_para1)
MERGE (s_para)-[:HAS_CONDITION]->(c_para2)
MERGE (s_para)-[:HAS_CONDITION]->(c_para3)
MERGE (s_para)-[:HAS_CONDITION]->(c_para4)
MERGE (s_rect)-[:HAS_CONDITION]->(c_rect1)
MERGE (s_rect)-[:HAS_CONDITION]->(c_rect2)
MERGE (s_rect)-[:HAS_CONDITION]->(c_rect3)
MERGE (s_rect)-[:HAS_CONDITION]->(c_rect4)
MERGE (s_rhombus)-[:HAS_CONDITION]->(c_rhombus1)
MERGE (s_rhombus)-[:HAS_CONDITION]->(c_rhombus2)
MERGE (s_rhombus)-[:HAS_CONDITION]->(c_rhombus3)
MERGE (s_rhombus)-[:HAS_CONDITION]->(c_rhombus4)
MERGE (s_square)-[:HAS_CONDITION]->(c_square1)
MERGE (s_square)-[:HAS_CONDITION]->(c_square2)
MERGE (s_square)-[:HAS_CONDITION]->(c_square3)
MERGE (s_square)-[:HAS_CONDITION]->(c_square4)

// 8. CÂU HỎI TRẮC NGHIỆM (QUIZ) & GIẢI THÍCH "TẠI SAO?"
// Câu 1
MERGE (q1:Question {id: 'Q01', content: 'Hình chữ nhật có hai đường chéo vuông góc với nhau là hình gì?', difficulty: 'Cơ bản', status: 'Active'})
MERGE (a1_1:Answer {id: 'A01_1', content: 'Hình bình hành', isCorrect: false})
MERGE (a1_2:Answer {id: 'A01_2', content: 'Hình vuông', isCorrect: true})
MERGE (a1_3:Answer {id: 'A01_3', content: 'Hình thang cân', isCorrect: false})
MERGE (a1_4:Answer {id: 'A01_4', content: 'Hình thoi', isCorrect: false})
MERGE (sol1:Solution {id: 'SOL01', content: 'Hình chữ nhật có hai đường chéo vuông góc là hình vuông.', explanation: 'Theo dấu hiệu nhận biết: Hình chữ nhật vốn có 4 góc vuông và 2 đường chéo bằng nhau; khi bổ sung thêm tính chất hai đường chéo vuông góc (đặc trưng của hình thoi), hình đó trở thành hình vuông.'})
MERGE (q1)-[:HAS_ANSWER]->(a1_1)
MERGE (q1)-[:HAS_ANSWER]->(a1_2)
MERGE (q1)-[:HAS_ANSWER]->(a1_3)
MERGE (q1)-[:HAS_ANSWER]->(a1_4)
MERGE (q1)-[:HAS_SOLUTION]->(sol1)
MERGE (sol1)-[:USES_PROPERTY {stepOrder: 1}]->(p_4right_angles)
MERGE (sol1)-[:USES_PROPERTY {stepOrder: 2}]->(p_diag_perp)
MERGE (sol1)-[:USES_CONDITION]->(c_square2)
MERGE (s_square)-[:HAS_QUESTION]->(q1)

// Câu 2
MERGE (q2:Question {id: 'Q02', content: 'Hình bình hành có một góc vuông thì trở thành hình gì?', difficulty: 'Cơ bản', status: 'Active'})
MERGE (a2_1:Answer {id: 'A02_1', content: 'Hình thoi', isCorrect: false})
MERGE (a2_2:Answer {id: 'A02_2', content: 'Hình thang', isCorrect: false})
MERGE (a2_3:Answer {id: 'A02_3', content: 'Hình chữ nhật', isCorrect: true})
MERGE (a2_4:Answer {id: 'A02_4', content: 'Hình vuông', isCorrect: false})
MERGE (sol2:Solution {id: 'SOL02', content: 'Hình bình hành có một góc vuông là hình chữ nhật.', explanation: 'Hình bình hành có các góc đối bằng nhau và các góc kề bù nhau. Khi có một góc bằng 90°, ba góc còn lại cũng bằng 90°, thỏa mãn định nghĩa hình chữ nhật.'})
MERGE (q2)-[:HAS_ANSWER]->(a2_1)
MERGE (q2)-[:HAS_ANSWER]->(a2_2)
MERGE (q2)-[:HAS_ANSWER]->(a2_3)
MERGE (q2)-[:HAS_ANSWER]->(a2_4)
MERGE (q2)-[:HAS_SOLUTION]->(sol2)
MERGE (sol2)-[:USES_CONDITION]->(c_rect2)
MERGE (s_rect)-[:HAS_QUESTION]->(q2)

// Câu 3
MERGE (q3:Question {id: 'Q03', content: 'Khẳng định nào sau đây là ĐÚNG về mối quan hệ giữa các hình?', difficulty: 'Trung bình', status: 'Active'})
MERGE (a3_1:Answer {id: 'A03_1', content: 'Mọi hình bình hành đều là hình chữ nhật', isCorrect: false})
MERGE (a3_2:Answer {id: 'A03_2', content: 'Hình vuông vừa là hình chữ nhật vừa là hình thoi', isCorrect: true})
MERGE (a3_3:Answer {id: 'A03_3', content: 'Hình thoi luôn có hai đường chéo bằng nhau', isCorrect: false})
MERGE (a3_4:Answer {id: 'A03_4', content: 'Hình thang luôn là hình thang cân', isCorrect: false})
MERGE (sol3:Solution {id: 'SOL03', content: 'Hình vuông vừa là hình chữ nhật, vừa là hình thoi.', explanation: 'Dựa trên quan hệ kế thừa đồ thị IS_A: (Hình vuông)-[:IS_A]->(Hình chữ nhật) và (Hình vuông)-[:IS_A]->(Hình thoi). Do đó hình vuông kế thừa đầy đủ mọi tính chất của cả hai hình này.'})
MERGE (q3)-[:HAS_ANSWER]->(a3_1)
MERGE (q3)-[:HAS_ANSWER]->(a3_2)
MERGE (q3)-[:HAS_ANSWER]->(a3_3)
MERGE (q3)-[:HAS_ANSWER]->(a3_4)
MERGE (q3)-[:HAS_SOLUTION]->(sol3)
MERGE (s_square)-[:HAS_QUESTION]->(q3)

// 9. CÁC MỨC TRÌNH ĐỘ HỌC (LEARNING LEVEL)
MERGE (lvl1:LearningLevel {id: 'LVL_BASIC', name: 'Cơ bản', rank: 1, minScore: 0, maxScore: 5, description: 'Nhận biết khái niệm, công thức và tính chất cơ bản của các tứ giác.'})
MERGE (lvl2:LearningLevel {id: 'LVL_INTER', name: 'Trung bình', rank: 2, minScore: 6, maxScore: 8, description: 'Vận dụng tính chất, dấu hiệu nhận biết để suy luận và giải thích hình học.'})
MERGE (lvl3:LearningLevel {id: 'LVL_ADV', name: 'Nâng cao', rank: 3, minScore: 9, maxScore: 10, description: 'So sánh cấu trúc phân cấp, chứng minh định lý và giải bài toán hình học phức hợp.'})
