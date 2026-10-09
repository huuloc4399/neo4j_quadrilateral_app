// ==============================================================================
// QUADRILATERAL KNOWLEDGE GRAPH APP - JAVASCRIPT CONTROLLER
// Kết nối CSDL Đám Mây Neo4j Aura Cloud Free
// ==============================================================================

// Biến trạng thái toàn cục
let treeNetwork = null;
let kgNetwork = null;
let globalTreeNodes = [];
let globalTreeEdges = [];
let globalExercises = [];
let allShapesList = [];

// Trạng thái người chơi
let currentPlayer = localStorage.getItem("neo4j_player") || "Học viên " + Math.floor(100 + Math.random() * 900);
let currentScore = 0;
let currentCoins = 0;

// Trạng thái Quiz
let quizQuestions = [];
let currentQuizIndex = 0;
let quizEarnedScore = 0;
let quizEarnedCoins = 0;

// Modals
let exerciseModal = null;
let quizModal = null;
let leaderboardModal = null;

// ==================== KHỞI TẠO ỨNG DỤNG (ON LOAD) ====================
window.addEventListener("DOMContentLoaded", () => {
    exerciseModal = new bootstrap.Modal(document.getElementById("exerciseModal"));
    quizModal = new bootstrap.Modal(document.getElementById("quizModal"));
    leaderboardModal = new bootstrap.Modal(document.getElementById("leaderboardModal"));

    checkCloudStatus();
    syncPlayerData(currentPlayer);
    loadHierarchyTree();
    loadShapesList();

    // Lắng nghe sự kiện chuyển Tab từ Bootstrap để căn chỉnh lại đồ thị
    const kgTabBtn = document.getElementById("kg-tab");
    if (kgTabBtn) {
        kgTabBtn.addEventListener("shown.bs.tab", () => {
            if (!kgNetwork) {
                loadKnowledgeGraph();
            } else {
                setTimeout(() => {
                    const container = document.getElementById("kgNetwork");
                    if(container.offsetHeight > 0) {
                        kgNetwork.setSize(container.offsetWidth + "px", container.offsetHeight + "px");
                    }
                    kgNetwork.redraw();
                    kgNetwork.fit({ animation: { duration: 400, easingFunction: "easeInOutQuad" } });
                    window.dispatchEvent(new Event('resize'));
                }, 50);
            }
        });
    }

    const treeTabBtn = document.getElementById("tree-tab");
    if (treeTabBtn) {
        treeTabBtn.addEventListener("shown.bs.tab", () => {
            if (treeNetwork) {
                setTimeout(() => {
                    const container = document.getElementById("treeNetwork");
                    if(container.offsetHeight > 0) {
                        treeNetwork.setSize(container.offsetWidth + "px", container.offsetHeight + "px");
                    }
                    treeNetwork.redraw();
                    treeNetwork.fit({ animation: { duration: 400, easingFunction: "easeInOutQuad" } });
                    window.dispatchEvent(new Event('resize'));
                }, 50);
            }
        });
    }
});

// ==================== 1. KIỂM TRA TRẠNG THÁI NEO4J AURA CLOUD ====================
async function checkCloudStatus() {
    const badge = document.getElementById("cloudStatusBadge");
    try {
        const res = await fetch("/api/db/status");
        const data = await res.json();
        if (data.status === "connected") {
            badge.className = "badge bg-success-subtle text-success border border-success-subtle";
            badge.innerHTML = `<i class="bi bi-cloud-check-fill me-1 text-success"></i> Neo4j Aura Cloud: Sẵn sàng (${data.latency_ms}ms | ${data.nodes_count} nodes)`;
        } else {
            badge.className = "badge bg-warning-subtle text-warning border border-warning-subtle";
            badge.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Neo4j Cloud: Chế độ đệm dữ liệu`;
        }
    } catch (err) {
        badge.className = "badge bg-danger-subtle text-danger border border-danger-subtle";
        badge.innerHTML = `<i class="bi bi-cloud-slash-fill me-1"></i> Neo4j Cloud: Ngoại tuyến`;
    }
}

// ==================== 2. ĐỒNG BỘ NGƯỜI CHƠI & ĐỔI TÊN ====================
async function syncPlayerData(username) {
    try {
        const res = await fetch("/api/player/get_or_create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username })
        });
        const data = await res.json();
        currentPlayer = data.username;
        currentScore = data.score;
        currentCoins = data.coins;
        localStorage.setItem("neo4j_player", currentPlayer);
        updatePlayerUI();
    } catch (e) {
        console.error("Lỗi đồng bộ người chơi:", e);
    }
}

function updatePlayerUI() {
    document.getElementById("playerDisplay").innerText = currentPlayer;
    document.getElementById("scoreDisplay").innerText = currentScore;
    document.getElementById("coinsDisplay").innerText = currentCoins;
    const shopCoins = document.getElementById("shopCoinsDisplay");
    if (shopCoins) shopCoins.innerText = currentCoins;
}

function changePlayerName() {
    const newName = prompt("Nhập tên / Nickname của bạn:", currentPlayer);
    if (newName && newName.trim() !== "") {
        syncPlayerData(newName.trim());
    }
}

// ==================== 3. SƠ ĐỒ PHÂN CẤP TỨ GIÁC (TREE VIS-NETWORK) ====================
async function loadHierarchyTree() {
    try {
        const res = await fetch("/api/graph/hierarchy");
        const data = await res.json();
        globalTreeNodes = data.nodes;
        globalTreeEdges = data.edges;
        renderHierarchyTree(globalTreeNodes, globalTreeEdges);

        // Mặc định hiển thị chi tiết Hình vuông hoặc Hình chữ nhật
        const defaultShape = globalTreeNodes.find(n => n.id === "SH_SQUARE") || globalTreeNodes[1];
        if (defaultShape) showShapeDetails(defaultShape);
    } catch (err) {
        console.error("Lỗi tải cây phân cấp:", err);
    }
}

function renderHierarchyTree(nodes, edges) {
    const container = document.getElementById("treeNetwork");
    const isMobile = window.innerWidth <= 768;

    const formattedNodes = nodes.map(n => {
        let bg = "#38bdf8";
        let border = "#0284c7";
        let fontColor = "#0f172a";

        if (n.id === "hinh_hoc_phang") {
            bg = "#e2e8f0";
            border = "#64748b";
        } else if (n.id === "SH_QUAD" || n.id === "tu_giac") {
            bg = "#bae6fd";
            border = "#0284c7";
        } else if (n.id === "SH_TRAP" || n.id === "SH_ISOTRAP" || n.id === "SH_RIGHTTRAP" || n.id === "hinh_thang") {
            bg = "#fed7aa";
            border = "#ea580c";
        } else if (n.id === "SH_PARA" || n.id === "hinh_binh_hanh") {
            bg = "#bbf7d0";
            border = "#16a34a";
        } else if (n.id === "SH_RECT" || n.id === "SH_RHOMBUS" || n.id === "hinh_chu_nhat" || n.id === "hinh_thoi") {
            bg = "#a7f3d0";
            border = "#059669";
        } else if (n.id === "SH_SQUARE" || n.id === "hinh_vuong") {
            bg = "#fbcfe8";
            border = "#db2777";
        }

        return {
            id: n.id,
            label: n.name,
            color: {
                background: bg,
                border: border,
                highlight: { background: "#fbbf24", border: "#d97706" }
            },
            font: { size: isMobile ? 13 : 14, color: fontColor, face: "Plus Jakarta Sans", bold: true },
            shape: "box",
            margin: { top: 9, bottom: 9, left: 14, right: 14 },
            borderWidth: 2,
            shadow: { enabled: true, color: "rgba(0,0,0,0.06)", size: 6, x: 2, y: 3 }
        };
    });

    const formattedEdges = edges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        font: { size: isMobile ? 9 : 10, face: "Plus Jakarta Sans", background: "#ffffff", strokeWidth: 0, color: "#64748b" },
        color: { color: "#94a3b8", highlight: "#f59e0b" },
        smooth: { type: "cubicBezier", forceDirection: "vertical", roundness: 0.3 }
    }));

    const options = {
        layout: {
            hierarchical: {
                direction: "UD",
                sortMethod: "directed",
                levelSeparation: isMobile ? 85 : 105,
                nodeSpacing: isMobile ? 120 : 160
            }
        },
        physics: false,
        interaction: { hover: true, zoomView: true, dragView: true, multiselect: false }
    };

    treeNetwork = new vis.Network(container, {
        nodes: new vis.DataSet(formattedNodes),
        edges: new vis.DataSet(formattedEdges)
    }, options);

    treeNetwork.once("afterDrawing", () => {
        treeNetwork.fit({ animation: { duration: 600, easingFunction: "easeInOutQuad" } });
    });

    treeNetwork.on("click", (params) => {
        if (params.nodes.length > 0) {
            const selected = globalTreeNodes.find(n => n.id === params.nodes[0]);
            if (selected) showShapeDetails(selected);
        }
    });
}

function resetTreeZoom() {
    if (treeNetwork) treeNetwork.fit({ animation: { duration: 400 } });
}

// ==================== 4. HIỂN THỊ CHI TIẾT TỨ GIÁC (SIDE PANEL) ====================
function showShapeDetails(shape) {
    const parentRels = globalTreeEdges.filter(e => e.to === shape.id);
    const childRels = globalTreeEdges.filter(e => e.from === shape.id);

    let parentHtml = parentRels.length > 0
        ? parentRels.map(r => {
            const pNode = globalTreeNodes.find(n => n.id === r.from);
            return `<div class="list-group-item py-1 px-2 border-0 bg-light rounded mb-1 d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-primary small">${pNode ? pNode.name : r.from}</span>
                        <span class="badge bg-secondary-subtle text-secondary" style="font-size: 0.7rem;">${r.label || 'Kế thừa'}</span>
                    </div>`;
        }).join('')
        : '<div class="text-muted small ps-2 fst-italic">Là hình gốc khởi đầu.</div>';

    let childHtml = childRels.length > 0
        ? childRels.map(r => {
            const cNode = globalTreeNodes.find(n => n.id === r.to);
            return `<div class="list-group-item py-1 px-2 border-0 bg-light rounded mb-1 d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-success small">${cNode ? cNode.name : r.to}</span>
                        <span class="badge bg-success-subtle text-success" style="font-size: 0.7rem;">${r.label || 'Tiến hóa'}</span>
                    </div>`;
        }).join('')
        : '<div class="text-muted small ps-2 fst-italic">Hình chuyên biệt nhất (Đỉnh chuỗi).</div>';

    const tip = shape.meo || "Hãy chú ý mối liên hệ giữa các đường chéo và các góc đối của hình này!";

    document.getElementById("shapeDetailsContainer").innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="badge bg-primary px-2 py-1"><i class="bi bi-bookmark-check-fill me-1"></i> Tứ Giác Chuẩn</span>
            <button class="btn btn-sm btn-outline-info py-1 px-2" onclick="openExerciseModal('${shape.id}')">
                <i class="bi bi-pencil-square me-1"></i> Bài toán hình này
            </button>
        </div>

        <h4 class="fw-bold text-dark mb-1">${shape.name}</h4>
        <p class="text-secondary small mb-3">${shape.definition || shape.description || ''}</p>

        <!-- Hộp Mẹo ghi nhớ -->
        <div class="tip-box mb-3 shadow-sm">
            <div class="tip-title">
                <i class="bi bi-lightbulb-fill text-warning"></i> Mẹo Ghi Nhớ & Giải Nhanh
            </div>
            <div class="tip-body">${tip.replace(/\n/g, '<br>')}</div>
        </div>

        <!-- Thẻ Công thức & Tính chất -->
        <div class="card border-0 shadow-sm bg-light mb-3">
            <div class="card-body p-3">
                <div class="mb-2">
                    <span class="section-label d-block">1. Tính Chất Nổi Bật:</span>
                    <div class="small text-dark">${shape.tinh_chat || 'Kế thừa từ hình cha'}</div>
                </div>
                <hr class="my-2 border-secondary-subtle">
                <div class="mb-2">
                    <span class="section-label d-block">2. Chu Vi (P):</span>
                    <span class="formula-tag">${shape.chu_vi || 'N/A'}</span>
                </div>
                <hr class="my-2 border-secondary-subtle">
                <div>
                    <span class="section-label d-block">3. Diện Tích (S):</span>
                    <span class="formula-tag">${shape.dien_tich || 'N/A'}</span>
                </div>
            </div>
        </div>

        <!-- Thẻ Quan hệ phả hệ đồ thị -->
        <div class="card border-0 shadow-sm border-start border-3 border-info mb-2">
            <div class="card-header bg-white fw-bold py-2 px-3 small border-0">
                <i class="bi bi-diagram-2-fill text-info me-1"></i> Mối Quan Hệ Phả Hệ (Knowledge Graph)
            </div>
            <div class="card-body p-3 pt-0">
                <div class="mb-2">
                    <span class="section-label d-block mb-1">Suy ra từ (IS_A):</span>
                    <div class="list-group">${parentHtml}</div>
                </div>
                <div>
                    <span class="section-label d-block mb-1">Tiến hóa mở rộng thành:</span>
                    <div class="list-group">${childHtml}</div>
                </div>
            </div>
        </div>
    `;
}

// ==================== 5. ĐỒ THỊ TRI THỨC TOÀN CẢNH (KNOWLEDGE GRAPH) ====================
async function loadKnowledgeGraph() {
    const container = document.getElementById("kgNetwork");
    if (!container) return;

    const filterProps = document.getElementById("filterProps");
    const filterFormulas = document.getElementById("filterFormulas");
    const filterConditions = document.getElementById("filterConditions");

    const incProps = filterProps ? filterProps.checked : true;
    const incFormulas = filterFormulas ? filterFormulas.checked : true;
    const incConditions = filterConditions ? filterConditions.checked : true;

    // Hiển thị loading spinner nếu chưa khởi tạo đồ thị
    if (!kgNetwork) {
        container.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
                <div class="spinner-border text-info mb-3" style="width: 2.8rem; height: 2.8rem;"></div>
                <div class="fw-bold fs-6 text-dark">Đang nạp Đồ Thị Tri Thức từ Neo4j Cloud...</div>
                <div class="small text-secondary mt-1">Đang xử lý các thực thể Shape, Property, Formula, Condition...</div>
            </div>
        `;
    }

    try {
        const res = await fetch(`/api/graph/knowledge?include_props=${incProps}&include_formulas=${incFormulas}&include_conditions=${incConditions}`);
        const data = await res.json();
        
        // Xóa spinner
        container.innerHTML = "";
        
        renderKnowledgeGraph(data.nodes, data.edges);
    } catch (err) {
        console.error("Lỗi tải Knowledge Graph:", err);
        container.innerHTML = `<div class="alert alert-danger m-4">Lỗi kết nối CSDL Neo4j khi nạp Đồ Thị Tri Thức.</div>`;
    }
}

function renderKnowledgeGraph(nodes, edges) {
    const container = document.getElementById("kgNetwork");
    if (!container) return;

    if (!nodes || nodes.length === 0) {
        container.innerHTML = `<div class="d-flex align-items-center justify-content-center h-100 text-muted">Không có thực thể nào thỏa mãn bộ lọc hiện tại.</div>`;
        return;
    }

    const isMobile = window.innerWidth <= 768;

    const formattedNodes = nodes.map(n => {
        let nodeColor = n.color || "#2563eb";
        let nodeShape = n.shape || "dot";
        let nodeSize = n.size || 20;

        if (n.group === "shape") {
            nodeColor = "#2563eb";
            nodeShape = "dot";
            nodeSize = isMobile ? 22 : 26;
        } else if (n.group === "property") {
            nodeColor = "#10b981";
            nodeShape = "ellipse";
            nodeSize = isMobile ? 14 : 16;
        } else if (n.group === "formula") {
            nodeColor = "#f59e0b";
            nodeShape = "box";
            nodeSize = isMobile ? 14 : 16;
        } else if (n.group === "condition") {
            nodeColor = "#ec4899";
            nodeShape = "diamond";
            nodeSize = isMobile ? 14 : 16;
        }

        return {
            id: n.id,
            label: n.label,
            title: n.title,
            color: {
                background: nodeColor,
                border: "#0f172a",
                highlight: { background: "#fbbf24", border: "#d97706" }
            },
            size: nodeSize,
            shape: nodeShape,
            font: {
                size: isMobile ? 11 : 13,
                face: "Plus Jakarta Sans",
                color: "#0f172a",
                bold: n.group === "shape",
                strokeWidth: 2,
                strokeColor: "#ffffff"
            },
            shadow: { enabled: true, color: "rgba(0,0,0,0.08)", size: 4, x: 1, y: 2 }
        };
    });

    const formattedEdges = edges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: { to: { enabled: true, scaleFactor: 0.6 } },
        color: { color: e.color || "#94a3b8", highlight: "#f59e0b" },
        font: { size: 9, face: "Plus Jakarta Sans", align: "middle", background: "#ffffff", strokeWidth: 0 },
        smooth: { type: "continuous" }
    }));

    const options = {
        physics: {
            enabled: true,
            solver: "forceAtlas2Based",
            forceAtlas2Based: {
                gravitationalConstant: -45,
                centralGravity: 0.008,
                springLength: 95,
                springConstant: 0.08,
                damping: 0.45
            },
            stabilization: {
                enabled: true,
                iterations: 120,
                updateInterval: 25
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            zoomView: true,
            dragView: true,
            multiselect: false
        }
    };

    if (kgNetwork) {
        kgNetwork.destroy();
        kgNetwork = null;
    }

    kgNetwork = new vis.Network(container, {
        nodes: new vis.DataSet(formattedNodes),
        edges: new vis.DataSet(formattedEdges)
    }, options);

    kgNetwork.once("afterDrawing", () => {
        kgNetwork.fit({ animation: { duration: 600, easingFunction: "easeInOutQuad" } });
    });

    kgNetwork.once("stabilizationIterationsDone", () => {
        kgNetwork.fit({ animation: { duration: 400, easingFunction: "easeInOutQuad" } });
    });
}

function resetKgZoom() {
    if (kgNetwork) {
        kgNetwork.fit({ animation: { duration: 400, easingFunction: "easeInOutQuad" } });
    }
}

// ==================== 6. BỘ MÁY SUY LUẬN NHẬN DIỆN TỨ GIÁC (INFERENCE) ====================
async function loadInferenceProperties() {
    const container = document.getElementById("propertiesCheckboxContainer");
    try {
        const res = await fetch("/api/properties");
        const grouped = await res.json();

        let html = "";
        for (const [category, props] of Object.entries(grouped)) {
            let catIcon = "bi-bounding-box";
            if (category.toLowerCase().includes("cạnh")) catIcon = "bi-slash-lg";
            if (category.toLowerCase().includes("góc")) catIcon = "bi-compass";
            if (category.toLowerCase().includes("chéo")) catIcon = "bi-x-lg";

            html += `
                <div class="col-md-4">
                    <div class="card h-100 border shadow-sm">
                        <div class="card-header bg-light py-2 fw-bold small text-dark d-flex align-items-center">
                            <i class="bi ${catIcon} text-primary me-2"></i> Nhóm: ${category}
                        </div>
                        <div class="card-body p-3">
                            ${props.map(p => `
                                <div class="form-check mb-2">
                                    <input class="form-check-input prop-checkbox" type="checkbox" value="${p.name}" id="prop_${p.id}">
                                    <label class="form-check-label small" for="prop_${p.id}" title="${p.description || ''}">
                                        ${p.name}
                                    </label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Lỗi tải danh mục tính chất.</div>`;
    }
}

function clearSelectedProperties() {
    document.querySelectorAll(".prop-checkbox").forEach(cb => cb.checked = false);
    document.getElementById("inferenceResultContainer").style.display = "none";
}

async function runInferenceIdentify() {
    const selected = Array.from(document.querySelectorAll(".prop-checkbox:checked")).map(cb => cb.value);
    const resultBox = document.getElementById("inferenceResultContainer");

    if (selected.length === 0) {
        alert("Vui lòng tích chọn ít nhất 1 tính chất hình học để bắt đầu suy luận!");
        return;
    }

    resultBox.style.display = "block";
    resultBox.innerHTML = `
        <div class="card border-0 shadow-sm p-4 text-center">
            <div class="spinner-border text-primary mx-auto mb-2"></div>
            <div class="fw-bold">Knowledge Graph Neo4j đang thực hiện đối sánh suy luận...</div>
        </div>
    `;

    try {
        const res = await fetch("/api/identify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ properties: selected })
        });
        const data = await res.json();

        if (data.success) {
            confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
            resultBox.innerHTML = `
                <div class="card border-0 shadow-sm border-start border-4 border-success p-4">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <i class="bi bi-check-circle-fill text-success fs-3"></i>
                        <h5 class="fw-bold text-success mb-0">Suy Luận Thành Công!</h5>
                    </div>
                    <p class="text-secondary small mb-3">${data.explanation}</p>

                    <div class="row g-3">
                        ${data.shapes.map(s => `
                            <div class="col-md-6">
                                <div class="card p-3 border bg-light h-100">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <h6 class="fw-bold text-primary mb-0">${s.name}</h6>
                                        <span class="badge bg-success">Thỏa mãn 100%</span>
                                    </div>
                                    <p class="small text-secondary mb-2">${s.definition}</p>
                                    <div class="small text-muted"><strong>Kế thừa:</strong> ${s.ancestors ? s.ancestors.join(' ➔ ') : 'Tứ giác'}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            resultBox.innerHTML = `
                <div class="card border-0 shadow-sm border-start border-4 border-warning p-4">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <i class="bi bi-exclamation-triangle-fill text-warning fs-3"></i>
                        <h5 class="fw-bold text-warning mb-0">Chưa Đủ Dữ Kiện Hoặc Mâu Thuẫn</h5>
                    </div>
                    <p class="text-secondary small mb-3">${data.message}</p>
                    ${data.partials && data.partials.length > 0 ? `
                        <div class="small fw-bold mb-2">Các hình thỏa mãn gần đúng nhất (Gợi ý):</div>
                        <ul class="list-group list-group-flush small">
                            ${data.partials.map(p => `
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    <span>${p.name}</span>
                                    <span class="badge bg-info text-dark">Khớp ${p.matchedCount} tính chất</span>
                                </li>
                            `).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        }
    } catch (err) {
        resultBox.innerHTML = `<div class="alert alert-danger">Lỗi kết nối máy chủ suy luận.</div>`;
    }
}

// ==================== 7. SO SÁNH HAI LOẠI TỨ GIÁC (COMPARE) ====================
async function loadShapesList() {
    try {
        const res = await fetch("/api/shapes");
        allShapesList = await res.json();

        const s1 = document.getElementById("compareSelect1");
        const s2 = document.getElementById("compareSelect2");
        if (s1 && s2) {
            const opts = allShapesList.map(s => `<option value="${s.name}">${s.name}</option>`).join('');
            s1.innerHTML = opts;
            s2.innerHTML = opts;
            if (allShapesList.length > 1) s2.selectedIndex = 1;
        }
    } catch (err) {
        console.error("Lỗi nạp danh sách hình:", err);
    }
}

function loadCompareShapes() {
    if (allShapesList.length === 0) loadShapesList();
}

async function runCompareShapes() {
    const s1 = document.getElementById("compareSelect1").value;
    const s2 = document.getElementById("compareSelect2").value;
    const box = document.getElementById("compareResultContainer");

    box.style.display = "block";
    box.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-success"></div></div>`;

    try {
        const res = await fetch("/api/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ shape1: s1, shape2: s2 })
        });
        const data = await res.json();

        if (res.ok) {
            box.innerHTML = `
                <div class="card border-0 shadow-sm p-4">
                    <h5 class="fw-bold mb-3"><i class="bi bi-diagram-3-fill text-success me-2"></i> Kết Quả Đối Chiếu: ${data.shape1} vs ${data.shape2}</h5>
                    
                    <!-- Giống nhau -->
                    <div class="alert alert-success border-0 mb-3">
                        <h6 class="fw-bold text-success mb-2"><i class="bi bi-check2-circle me-1"></i> Tính Chất Chung (Kế thừa từ tổ tiên chung):</h6>
                        ${data.common_properties.length > 0 ? `
                            <ul class="mb-0 small">
                                ${data.common_properties.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        ` : '<div class="small fst-italic">Không có tính chất đặc trưng chung ngoài tính chất tứ giác cơ bản.</div>'}
                    </div>

                    <div class="row g-3">
                        <!-- Riêng hình 1 -->
                        <div class="col-md-6">
                            <div class="card p-3 border h-100 bg-light">
                                <h6 class="fw-bold text-primary mb-2"><i class="bi bi-star-fill me-1"></i> Tính Chất Riêng Của ${data.shape1}:</h6>
                                ${data.diff_shape1.length > 0 ? `
                                    <ul class="mb-0 small text-secondary">
                                        ${data.diff_shape1.map(p => `<li>${p}</li>`).join('')}
                                    </ul>
                                ` : '<div class="small text-muted">Không có tính chất riêng so với hình đối chiếu.</div>'}
                            </div>
                        </div>

                        <!-- Riêng hình 2 -->
                        <div class="col-md-6">
                            <div class="card p-3 border h-100 bg-light">
                                <h6 class="fw-bold text-purple mb-2" style="color: #9333ea;"><i class="bi bi-star-fill me-1"></i> Tính Chất Riêng Của ${data.shape2}:</h6>
                                ${data.diff_shape2.length > 0 ? `
                                    <ul class="mb-0 small text-secondary">
                                        ${data.diff_shape2.map(p => `<li>${p}</li>`).join('')}
                                    </ul>
                                ` : '<div class="small text-muted">Không có tính chất riêng so với hình đối chiếu.</div>'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            box.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
        }
    } catch (err) {
        box.innerHTML = `<div class="alert alert-danger">Lỗi so sánh dữ liệu.</div>`;
    }
}

// ==================== 8. BÀI TOÁN LUYỆN TẬP ====================
async function openExerciseModal(preselectedShapeId = null) {
    exerciseModal.show();
    if (globalExercises.length === 0) {
        try {
            const res = await fetch("/api/exercises");
            globalExercises = await res.json();
        } catch (err) {
            document.getElementById("exerciseListContainer").innerHTML = `<div class="alert alert-danger">Lỗi tải bài tập.</div>`;
            return;
        }
    }

    if (preselectedShapeId) {
        const btn = Array.from(document.querySelectorAll("#exerciseFilterBar .filter-btn"))
            .find(b => b.getAttribute("onclick") && b.getAttribute("onclick").includes(preselectedShapeId));
        filterExercises(preselectedShapeId, btn || document.querySelectorAll("#exerciseFilterBar .filter-btn")[0]);
    } else {
        filterExercises("all", document.querySelectorAll("#exerciseFilterBar .filter-btn")[0]);
    }
}

let currentExerciseShape = "all";
let currentExerciseGrade = "all";

function filterExercises(shapeId, btnElement) {
    if (shapeId !== undefined) {
        currentExerciseShape = shapeId;
        document.querySelectorAll("#exerciseFilterBar .filter-btn").forEach(b => {
            b.classList.remove("btn-dark", "active");
            b.classList.add("btn-outline-secondary");
        });
        if (btnElement) {
            btnElement.classList.remove("btn-outline-secondary");
            btnElement.classList.add("btn-dark", "active");
        }
    }
    applyExerciseFilters();
}

function filterExercisesByGrade(grade) {
    currentExerciseGrade = grade;
    applyExerciseFilters();
}

function applyExerciseFilters() {
    let list = globalExercises;
    if (currentExerciseShape !== "all") {
        list = list.filter(ex => ex.shape_id === currentExerciseShape);
    }
    if (currentExerciseGrade !== "all") {
        list = list.filter(ex => String(ex.grade) === String(currentExerciseGrade));
    }
    renderExerciseList(list);
}

function renderExerciseList(exercises) {
    const container = document.getElementById("exerciseListContainer");
    if (!exercises || exercises.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-muted small">Chưa có bài toán nào cho mục này.</div>`;
        return;
    }

    container.innerHTML = exercises.map(ex => `
        <div class="card mb-3 p-3 bg-white shadow-sm border rounded-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-info-subtle text-info border border-info-subtle small">${ex.shape_name}</span>
                <span class="badge bg-light text-muted border">Gợi ý: <code>${ex.formula_hint}</code></span>
            </div>
            <h6 class="fw-bold text-dark mb-1" style="font-size: 0.95rem;">${ex.title}</h6>
            <p class="text-secondary small mb-3">${ex.content}</p>

            <div class="row g-2 align-items-center">
                <div class="col-7 col-sm-auto">
                    <div class="input-group input-group-sm">
                        <input type="number" step="any" class="form-control" id="input-ex-${ex.id}" placeholder="Nhập đáp số...">
                        <span class="input-group-text bg-light">${ex.unit}</span>
                    </div>
                </div>
                <div class="col-5 col-sm-auto">
                    <button class="btn btn-sm btn-primary w-100 fw-bold" onclick="checkExerciseAnswer(${ex.id})">Kiểm Tra</button>
                </div>
                <div class="col-12 col-sm-auto mt-1 mt-sm-0">
                    <button class="btn btn-sm btn-link text-decoration-none p-0 text-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#sol-${ex.id}">
                        <i class="bi bi-lightbulb me-1"></i> Xem giải chi tiết
                    </button>
                </div>
            </div>

            <div id="feedback-ex-${ex.id}" class="mt-2" style="display:none;"></div>

            <div class="collapse mt-2" id="sol-${ex.id}">
                <div class="card card-body bg-light p-3 small text-dark border-0 rounded-3">
                    <strong><i class="bi bi-check2-circle text-success me-1"></i> Lời giải chi tiết:</strong>
                    <pre class="mb-0 mt-1" style="font-family: inherit; white-space: pre-wrap; font-size: 0.84rem;">${ex.solution}</pre>
                </div>
            </div>
        </div>
    `).join('');
}

async function checkExerciseAnswer(exId) {
    const inputVal = document.getElementById(`input-ex-${exId}`).value;
    const fb = document.getElementById(`feedback-ex-${exId}`);

    if (inputVal === "") {
        fb.innerHTML = `<span class="badge bg-warning text-dark"><i class="bi bi-exclamation-triangle me-1"></i> Vui lòng nhập đáp số!</span>`;
        fb.style.display = "block";
        return;
    }

    try {
        const res = await fetch("/api/exercises/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ exercise_id: exId, user_answer: inputVal })
        });
        const data = await res.json();

        if (data.is_correct) {
            confetti({ particleCount: 30, spread: 50, origin: { y: 0.8 } });
            currentScore += data.earned_score;
            currentCoins += data.earned_coins;
            updatePlayerUI();
            fb.innerHTML = `
                <div class="alert alert-success py-2 px-3 small mb-0">
                    <i class="bi bi-check-circle-fill me-1"></i> <strong>Chính xác tuyệt đối!</strong> (+${data.earned_score}đ, +${data.earned_coins} xu)
                </div>
            `;
        } else {
            fb.innerHTML = `
                <div class="alert alert-danger py-2 px-3 small mb-0">
                    <i class="bi bi-x-circle-fill me-1"></i> <strong>Chưa chính xác!</strong> Hãy kiểm tra lại công thức hoặc xem gợi ý giải nhé.
                </div>
            `;
        }
        fb.style.display = "block";
    } catch (err) {
        fb.innerHTML = `<span class="badge bg-danger">Lỗi kiểm tra</span>`;
        fb.style.display = "block";
    }
}

// ==================== 9. QUIZ THỬ THÁCH ====================
async function startQuiz() {
    const body = document.getElementById("quizBody");
    body.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-warning mb-2"></div>
            <p class="text-muted small">Đang nạp bộ câu hỏi trắc nghiệm từ Neo4j Cloud...</p>
        </div>
    `;
    quizModal.show();

    try {
        const res = await fetch("/api/quiz");
        let allQuizzes = await res.json();
        
        const gradeSelect = document.getElementById("quizGradeFilter");
        const selectedGrade = gradeSelect ? gradeSelect.value : "all";
        
        if (selectedGrade !== "all") {
            // Lọc quiz theo lớp, các quiz mặc định từ Neo4j chưa có lớp sẽ được tính vào lớp 8
            quizQuestions = allQuizzes.filter(q => {
                const qGrade = q.grade || 8; 
                return String(qGrade) === String(selectedGrade);
            });
        } else {
            quizQuestions = allQuizzes;
        }

        if (quizQuestions.length === 0) {
            body.innerHTML = `<div class="text-center py-5 text-muted"><i class="bi bi-inbox fs-1"></i><br>Chưa có câu hỏi trắc nghiệm nào cho khối lớp này!</div>`;
            return;
        }

        currentQuizIndex = 0;
        quizEarnedScore = 0;
        quizEarnedCoins = 0;
        renderQuizQuestion();
    } catch (err) {
        body.innerHTML = `<div class="alert alert-danger">Lỗi tải quiz.</div>`;
    }
}

function renderQuizQuestion() {
    if (currentQuizIndex >= quizQuestions.length) {
        finishQuizSession();
        return;
    }

    const q = quizQuestions[currentQuizIndex];
    const body = document.getElementById("quizBody");

    let optionsHtml = q.options.map((opt, i) => `
        <button class="btn quiz-opt-btn w-100 mb-2" onclick="submitQuizAnswer(this, '${encodeURIComponent(opt)}', '${encodeURIComponent(q.answer)}', '${encodeURIComponent(q.explain)}')">
            <span class="badge bg-secondary me-2">${String.fromCharCode(65 + i)}</span> ${opt}
        </button>
    `).join('');

    body.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="badge bg-dark">Câu ${currentQuizIndex + 1} / ${quizQuestions.length}</span>
            <div>
                <span class="badge bg-primary me-1">+${quizEarnedScore} đ</span>
                <span class="badge bg-warning text-dark">+${quizEarnedCoins} xu</span>
            </div>
        </div>
        <h6 class="fw-bold mb-3 text-dark" style="font-size: 0.96rem; line-height: 1.4;">${q.question}</h6>
        <div id="quizOptionsContainer">${optionsHtml}</div>
        <div id="quizExplainContainer" class="mt-2" style="display:none;"></div>
    `;
}

function submitQuizAnswer(btn, chosenEncoded, correctEncoded, explainEncoded) {
    const chosen = decodeURIComponent(chosenEncoded);
    const correct = decodeURIComponent(correctEncoded);
    const explain = decodeURIComponent(explainEncoded);

    document.querySelectorAll(".quiz-opt-btn").forEach(b => b.disabled = true);
    const expBox = document.getElementById("quizExplainContainer");

    if (chosen === correct) {
        btn.classList.add("correct-opt");
        quizEarnedScore += 20;
        quizEarnedCoins += 10;
        confetti({ particleCount: 35, spread: 60, origin: { y: 0.7 } });

        expBox.innerHTML = `
            <div class="alert alert-success py-2 px-3 small">
                <strong><i class="bi bi-check-circle-fill me-1"></i> Chính xác!</strong> (+20đ, +10 xu)<br>
                <strong>Căn cứ:</strong> ${explain}
            </div>
            <button class="btn btn-sm btn-primary w-100 fw-bold mt-1" onclick="nextQuizQuestion()">Câu tiếp theo <i class="bi bi-arrow-right"></i></button>
        `;
    } else {
        btn.classList.add("wrong-opt");
        expBox.innerHTML = `
            <div class="alert alert-danger py-2 px-3 small">
                <strong><i class="bi bi-x-circle-fill me-1"></i> Chưa đúng!</strong> Đáp án chính xác là: <u>${correct}</u>.<br>
                <div class="mt-1"><strong>Giải thích 'Tại sao?':</strong> ${explain}</div>
            </div>
            <button class="btn btn-sm btn-primary w-100 fw-bold mt-1" onclick="nextQuizQuestion()">Câu tiếp theo <i class="bi bi-arrow-right"></i></button>
        `;
    }
    expBox.style.display = "block";
}

function nextQuizQuestion() {
    currentQuizIndex++;
    renderQuizQuestion();
}

async function finishQuizSession() {
    const body = document.getElementById("quizBody");
    body.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-success mb-2"></div>
            <p class="text-muted small">Đang cập nhật thành tích lên Cloud...</p>
        </div>
    `;

    try {
        const res = await fetch("/api/quiz/finish", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: currentPlayer,
                earned_score: quizEarnedScore,
                earned_coins: quizEarnedCoins
            })
        });
        const data = await res.json();
        currentScore = data.score;
        currentCoins = data.coins;
        updatePlayerUI();

        confetti({ particleCount: 80, spread: 80, origin: { y: 0.6 } });

        body.innerHTML = `
            <div class="text-center py-3">
                <i class="bi bi-trophy-fill fs-1 text-warning mb-2 d-block"></i>
                <h5 class="fw-bold mb-1">Hoàn Thành Thử Thách!</h5>
                <p class="text-secondary small mb-3">Thành tích của bạn đã được ghi nhận trên Bảng Xếp Hạng</p>
                <div class="d-flex justify-content-center gap-2 mb-4">
                    <span class="badge bg-primary fs-6 p-2">+${quizEarnedScore} Điểm</span>
                    <span class="badge bg-warning text-dark fs-6 p-2">+${quizEarnedCoins} Xu</span>
                </div>
                <div class="d-flex justify-content-center gap-2">
                    <button class="btn btn-warning fw-bold" onclick="startQuiz()">Làm lại</button>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `<div class="alert alert-danger">Lỗi cập nhật kết quả.</div>`;
    }
}

// ==================== 10. BẢNG XẾP HẠNG (LEADERBOARD) ====================
async function openLeaderboard() {
    leaderboardModal.show();
    const tbody = document.getElementById("leaderboardTableBody");
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-3 text-muted">Đang tải...</td></tr>`;

    try {
        const res = await fetch("/api/leaderboard");
        const leaders = await res.json();

        tbody.innerHTML = leaders.map((item, index) => {
            let rank = `<span class="badge bg-secondary">${index + 1}</span>`;
            if (index === 0) rank = `<i class="bi bi-trophy-fill text-warning fs-5"></i>`;
            if (index === 1) rank = `<i class="bi bi-trophy-fill text-secondary fs-5"></i>`;
            if (index === 2) rank = `<i class="bi bi-trophy-fill text-danger fs-5"></i>`;

            const isCurrent = item.username === currentPlayer ? 'table-warning fw-bold' : '';

            return `
                <tr class="${isCurrent}">
                    <td>${rank}</td>
                    <td>${item.username}</td>
                    <td class="text-end text-primary fw-bold">${item.score}</td>
                    <td class="text-end text-warning fw-bold">${item.coins}</td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-danger text-center">Lỗi tải dữ liệu.</td></tr>`;
    }
}



// ==================== 12. THỐNG KÊ CƠ SỞ DỮ LIỆU NEO4J CLOUD ====================
async function loadDatabaseStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        document.getElementById("statShapes").innerText = data.summary.shapes;
        document.getElementById("statProps").innerText = data.summary.properties;
        document.getElementById("statForms").innerText = data.summary.formulas;
        document.getElementById("statRels").innerText = data.summary.relationships;

        const labelsBody = document.getElementById("statLabelsTable");
        labelsBody.innerHTML = data.labels.map(l => `
            <tr>
                <td class="fw-semibold">${l.label}</td>
                <td class="text-end fw-bold text-primary">${l.count}</td>
            </tr>
        `).join('');

        const relsBody = document.getElementById("statRelsTable");
        relsBody.innerHTML = data.relationships.map(r => `
            <tr>
                <td class="fw-semibold">:${r.relationship}</td>
                <td class="text-end fw-bold text-success">${r.count}</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error("Lỗi tải thống kê CSDL:", err);
    }
}
