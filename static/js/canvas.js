// ==================== 6. BẢNG VẼ TỨ GIÁC (CANVAS) ====================
let canvas, ctx;
let points = [
    { id: 'A', x: 100, y: 100 },
    { id: 'B', x: 400, y: 100 },
    { id: 'C', x: 450, y: 300 },
    { id: 'D', x: 150, y: 300 }
];
let draggedPoint = null;
const POINT_RADIUS = 10;
const GRID_SIZE = 50;

window.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('geometryCanvas');
    if(!canvas) return;
    ctx = canvas.getContext('2d');

    // Khởi tạo kích thước Canvas
    const resizeObserver = new ResizeObserver(() => {
        resizeCanvas();
    });
    resizeObserver.observe(canvas.parentElement);

    // Xử lý sự kiện chuột
    canvas.addEventListener('mousedown', onPointerDown);
    canvas.addEventListener('mousemove', onPointerMove);
    window.addEventListener('mouseup', onPointerUp);
    
    // Xử lý sự kiện cảm ứng trên Mobile/Tablet
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        onPointerDown({ clientX: touch.clientX, clientY: touch.clientY });
    }, {passive: false});
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        onPointerMove({ clientX: touch.clientX, clientY: touch.clientY });
    }, {passive: false});
    window.addEventListener('touchend', onPointerUp);

    // Kích hoạt tab canvas load lại kích thước
    const canvasTabBtn = document.getElementById("canvas-tab");
    if (canvasTabBtn) {
        canvasTabBtn.addEventListener("shown.bs.tab", () => {
            resizeCanvas();
            resetCanvas();
        });
    }

    setTimeout(resizeCanvas, 100);
});

function resizeCanvas() {
    if(!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    if(rect.width === 0 || rect.height === 0) return;
    canvas.width = rect.width;
    canvas.height = rect.height;
    drawCanvas();
}

function resetCanvas() {
    const w = canvas.width;
    const h = canvas.height;
    points = [
        { id: 'A', x: w * 0.3, y: h * 0.3 },
        { id: 'B', x: w * 0.7, y: h * 0.3 },
        { id: 'C', x: w * 0.8, y: h * 0.7 },
        { id: 'D', x: w * 0.2, y: h * 0.7 }
    ];
    drawCanvas();
}

function getMousePos(evt) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

function onPointerDown(e) {
    const pos = getMousePos(e);
    for (let p of points) {
        if (Math.hypot(p.x - pos.x, p.y - pos.y) <= POINT_RADIUS * 2) {
            draggedPoint = p;
            break;
        }
    }
}

function onPointerMove(e) {
    if (draggedPoint) {
        const pos = getMousePos(e);
        // Giới hạn điểm không vượt quá khung vẽ
        draggedPoint.x = Math.max(POINT_RADIUS, Math.min(canvas.width - POINT_RADIUS, pos.x));
        draggedPoint.y = Math.max(POINT_RADIUS, Math.min(canvas.height - POINT_RADIUS, pos.y));
        drawCanvas();
    } else {
        const pos = getMousePos(e);
        const isHover = points.some(p => Math.hypot(p.x - pos.x, p.y - pos.y) <= POINT_RADIUS * 2);
        canvas.style.cursor = isHover ? 'grab' : 'crosshair';
    }
}

function onPointerUp(e) {
    if(draggedPoint) {
        draggedPoint = null;
        classifyShape(); // Chốt hình dạng khi nhả chuột
    }
}

function drawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid();
    
    // Vẽ khối tứ giác
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    
    // Đổ màu
    ctx.fillStyle = 'rgba(13, 110, 253, 0.15)'; 
    ctx.fill();
    ctx.strokeStyle = '#0d6efd';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Vẽ các điểm neo (vertices)
    for (let p of points) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, POINT_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#dc3545'; // Đỏ
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Vẽ Text A, B, C, D
        ctx.fillStyle = '#212529';
        ctx.font = 'bold 16px "Plus Jakarta Sans", sans-serif';
        ctx.fillText(p.id, p.x + 14, p.y - 14);
    }
    
    classifyShape();
}

function drawGrid() {
    ctx.strokeStyle = '#dee2e6';
    ctx.lineWidth = 1;
    for(let x = 0; x <= canvas.width; x += GRID_SIZE) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for(let y = 0; y <= canvas.height; y += GRID_SIZE) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
}

// Lô-gic Hình học
function distance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
}

function isParallel(p1, p2, p3, p4) {
    // Cạnh p1-p2 và p3-p4
    const v1 = {x: p2.x - p1.x, y: p2.y - p1.y};
    const v2 = {x: p4.x - p3.x, y: p4.y - p3.y};
    const cross = v1.x * v2.y - v1.y * v2.x;
    const len1 = Math.hypot(v1.x, v1.y);
    const len2 = Math.hypot(v2.x, v2.y);
    if(len1 === 0 || len2 === 0) return false;
    return Math.abs(cross / (len1 * len2)) < 0.05; // Độ lệch cho phép 5%
}

function angleBetween(p1, p2, p3) {
    // Góc tại đỉnh p2
    const v1 = {x: p1.x - p2.x, y: p1.y - p2.y};
    const v2 = {x: p3.x - p2.x, y: p3.y - p2.y};
    const dot = v1.x * v2.x + v1.y * v2.y;
    const len1 = Math.hypot(v1.x, v1.y);
    const len2 = Math.hypot(v2.x, v2.y);
    if(len1 === 0 || len2 === 0) return 0;
    const cosAngle = Math.max(-1, Math.min(1, dot / (len1 * len2)));
    return Math.acos(cosAngle) * 180 / Math.PI;
}

function isRightAngle(angle) {
    return Math.abs(angle - 90) < 6; // Dung sai 6 độ khi kéo thả thủ công
}

function classifyShape() {
    const A = points[0], B = points[1], C = points[2], D = points[3];
    
    const AB = distance(A, B);
    const BC = distance(B, C);
    const CD = distance(C, D);
    const DA = distance(D, A);
    const AC = distance(A, C); // Đường chéo
    const BD = distance(B, D); // Đường chéo

    const angleA = angleBetween(D, A, B);
    const angleB = angleBetween(A, B, C);
    const angleC = angleBetween(B, C, D);
    const angleD = angleBetween(C, D, A);
    
    // Kiểm tra tính song song
    const isAB_CD_Parallel = isParallel(A, B, C, D);
    const isAD_BC_Parallel = isParallel(A, D, B, C);

    // Kiểm tra độ dài cạnh (Dung sai 12px)
    const equalSidesTol = (len1, len2) => Math.abs(len1 - len2) < 12;
    
    const allSidesEqual = equalSidesTol(AB, BC) && equalSidesTol(BC, CD) && equalSidesTol(CD, DA);
    const hasRightAngles = isRightAngle(angleA) && isRightAngle(angleB) && isRightAngle(angleC) && isRightAngle(angleD);
    const oneRightAngle = isRightAngle(angleA) || isRightAngle(angleB) || isRightAngle(angleC) || isRightAngle(angleD);
    
    let shapeId = "SH_QUAD";

    // Phân loại hình theo điều kiện nhận biết
    if (allSidesEqual && hasRightAngles) {
        shapeId = "SH_SQUARE"; // Hình vuông
    } else if (isAB_CD_Parallel && isAD_BC_Parallel && hasRightAngles) {
        shapeId = "SH_RECT"; // Hình chữ nhật
    } else if (allSidesEqual) {
        shapeId = "SH_RHOMBUS"; // Hình thoi
    } else if (isAB_CD_Parallel && isAD_BC_Parallel) {
        shapeId = "SH_PARA"; // Hình bình hành
    } else if (isAB_CD_Parallel || isAD_BC_Parallel) {
        // Hình thang
        const diagEqual = equalSidesTol(AC, BD);
        if (oneRightAngle) {
            shapeId = "SH_RIGHTTRAP"; // Hình thang vuông
        } else if (diagEqual) {
            shapeId = "SH_ISOTRAP"; // Hình thang cân
        } else {
            shapeId = "SH_TRAP"; // Hình thang thường
        }
    }

    renderShapeResult(shapeId, {AB, BC, CD, DA, angleA, angleB, angleC, angleD});
}

function renderShapeResult(shapeId, geo) {
    const container = document.getElementById("canvasResultContainer");
    if(!container) return;

    if (typeof globalTreeNodes === 'undefined' || globalTreeNodes.length === 0) {
        container.innerHTML = `<div class="text-center p-4 text-muted"><div class="spinner-border spinner-border-sm text-primary mb-2"></div><br>Đang tải dữ liệu tri thức Neo4j...</div>`;
        return;
    }

    const shape = globalTreeNodes.find(n => n.id === shapeId) || globalTreeNodes.find(n => n.id === "SH_QUAD");
    if(!shape) return;

    const ms = (val) => Math.round(val);
    
    let propertiesHtml = "<i>Chưa có tính chất cụ thể</i>";
    if (shape.tinh_chat && shape.tinh_chat !== "Kế thừa từ hình cha") {
        propertiesHtml = shape.tinh_chat.split(';').map(p => `<li class="mb-1">${p.trim()}</li>`).join('');
    }
    
    container.innerHTML = `
        <div class="alert alert-primary mb-3">
            <h5 class="fw-bold mb-1"><i class="bi bi-star-fill text-warning me-2"></i>${shape.name}</h5>
            <div class="small">${shape.definition}</div>
        </div>
        
        <h6 class="fw-bold text-dark mb-2 border-bottom pb-1"><i class="bi bi-rulers me-2"></i> Cạnh (Pixels)</h6>
        <div class="row g-2 mb-3 small text-center">
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">AB = ${ms(geo.AB)}</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">BC = ${ms(geo.BC)}</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">CD = ${ms(geo.CD)}</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">DA = ${ms(geo.DA)}</div></div>
        </div>
        
        <h6 class="fw-bold text-dark mb-2 border-bottom pb-1"><i class="bi bi-arrows-angle-expand me-2"></i> Góc (Độ)</h6>
        <div class="row g-2 mb-3 small text-center">
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">∠A ≈ ${ms(geo.angleA)}°</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">∠B ≈ ${ms(geo.angleB)}°</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">∠C ≈ ${ms(geo.angleC)}°</div></div>
            <div class="col-6"><div class="p-1 bg-light rounded border border-secondary-subtle">∠D ≈ ${ms(geo.angleD)}°</div></div>
        </div>

        <h6 class="fw-bold text-success mb-2 border-bottom pb-1"><i class="bi bi-calculator me-2"></i> Công thức nổi bật</h6>
        <div class="small mb-3">
            <div class="mb-1"><span class="badge bg-secondary">Chu vi</span> <span class="fw-bold text-dark">${shape.chu_vi}</span></div>
            <div><span class="badge bg-secondary">Diện tích</span> <span class="fw-bold text-dark">${shape.dien_tich}</span></div>
        </div>

        <h6 class="fw-bold text-danger mb-2 border-bottom pb-1"><i class="bi bi-lightbulb me-2"></i> Tính chất quan trọng</h6>
        <ul class="small text-muted ps-3 mb-0">
            ${propertiesHtml}
        </ul>
    `;
}
