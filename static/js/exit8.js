// static/js/exit8.js
let exit8Questions = [];
let exit8CurrentDoor = 1;
let exit8SelectedGrade = "8";
let exit8Timer = null;
let exit8TimeLeft = 0;
let exit8TargetDoor = 8;
let exit8CurrentTrapQuestion = null;

async function openExit8Modal() {
    const modal = new bootstrap.Modal(document.getElementById('exit8Modal'));
    modal.show();
    renderExit8Start();
}

function renderExit8Start() {
    exit8StopTimer();
    const body = document.getElementById("exit8Body");
    body.innerHTML = `
        <h1 class="display-4 fw-bold text-danger mb-3" style="font-family: 'JetBrains Mono', monospace; text-shadow: 0 0 15px rgba(220,53,69,0.5);">THE EXIT 8</h1>
        <p class="lead mb-4 text-light">Bạn đang bị kẹt trong một hành lang vô tận...<br>Hãy chọn đúng ${exit8TargetDoor} cánh cửa an toàn liên tiếp để thoát ra. <br>Nếu dính bẫy, bạn buộc phải giải một bài toán sinh tử với thời gian ngày càng rút ngắn!</p>
        
        <div class="mb-4 w-50" style="min-width: 250px;">
            <label class="form-label fw-bold text-warning">Chọn cấp độ sinh tồn (Khối lớp):</label>
            <select class="form-select form-select-lg text-center fw-bold text-danger bg-dark border-danger" id="exit8GradeSelect">
                <option value="6">Lớp 6</option>
                <option value="7">Lớp 7</option>
                <option value="8" selected>Lớp 8 (Khuyến nghị)</option>
                <option value="9">Lớp 9</option>
                <option value="10">Lớp 10</option>
                <option value="11">Lớp 11</option>
                <option value="12">Lớp 12</option>
            </select>
        </div>
        
        <button class="btn btn-danger btn-lg px-5 fw-bold rounded-pill shadow" onclick="startExit8Game()">
            <i class="bi bi-play-fill me-1"></i> BẮT ĐẦU TRÒ CHƠI
        </button>
    `;
}

async function startExit8Game() {
    exit8SelectedGrade = document.getElementById("exit8GradeSelect").value;
    const body = document.getElementById("exit8Body");
    
    body.innerHTML = `
        <div class="spinner-border text-danger" role="status" style="width: 3rem; height: 3rem;"></div>
        <h4 class="mt-3 text-danger">Đang tạo chiều không gian...</h4>
    `;

    try {
        const res = await fetch("/api/quiz");
        const allQuestions = await res.json();
        
        exit8Questions = allQuestions.filter(q => {
            const qGrade = q.grade || 8;
            return String(qGrade) === String(exit8SelectedGrade);
        });

        // Fallback if empty for some reason
        if (exit8Questions.length === 0) {
            exit8Questions = allQuestions;
        }

        exit8CurrentDoor = 1;
        renderExit8Hallway();
    } catch(err) {
        body.innerHTML = `<div class="alert alert-danger">Lỗi kết nối tà thuật... Vui lòng thử lại.</div>`;
    }
}

function renderExit8Hallway() {
    exit8StopTimer();
    const body = document.getElementById("exit8Body");
    
    body.innerHTML = `
        <div class="mb-4">
            <h5 class="text-secondary text-uppercase" style="letter-spacing: 5px;">Hành lang số</h5>
            <h1 class="display-1 fw-bold text-white mb-0" style="font-family: 'JetBrains Mono', monospace;">${exit8CurrentDoor}</h1>
        </div>
        <p class="mb-5 fs-5 text-light">Phía trước là hai cánh cửa. Một cánh an toàn, một cánh là bẫy tử thần.<br>Số phận của bạn nằm ở quyết định này.</p>
        
        <div class="d-flex gap-4 justify-content-center w-100 flex-wrap">
            <div class="door-card bg-success text-white p-5 rounded-4 shadow position-relative overflow-hidden" 
                 style="cursor:pointer; transition: 0.2s; min-width: 220px;"
                 onclick="chooseExit8Door('green')" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                <i class="bi bi-door-closed-fill" style="font-size: 6rem; text-shadow: 0 4px 10px rgba(0,0,0,0.5);"></i>
                <h3 class="fw-bold mt-3 mb-0" style="letter-spacing: 2px;">CỬA XANH</h3>
            </div>
            
            <div class="door-card bg-danger text-white p-5 rounded-4 shadow position-relative overflow-hidden"
                 style="cursor:pointer; transition: 0.2s; min-width: 220px;"
                 onclick="chooseExit8Door('red')" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                <i class="bi bi-door-closed-fill" style="font-size: 6rem; text-shadow: 0 4px 10px rgba(0,0,0,0.5);"></i>
                <h3 class="fw-bold mt-3 mb-0" style="letter-spacing: 2px;">CỬA ĐỎ</h3>
            </div>
        </div>
    `;
}

function chooseExit8Door(color) {
    // 50% chance of trap
    const isTrap = Math.random() < 0.5;
    
    if (isTrap) {
        triggerExit8Trap();
    } else {
        exit8CurrentDoor++;
        if (exit8CurrentDoor > exit8TargetDoor) {
            renderExit8Victory();
        } else {
            const body = document.getElementById("exit8Body");
            body.innerHTML = `
                <div class="text-success text-center">
                    <i class="bi bi-check-circle-fill" style="font-size: 6rem;"></i>
                    <h1 class="display-3 fw-bold mt-3">AN TOÀN</h1>
                    <p class="fs-5 text-light">Bạn mở cửa và bước vào hành lang tiếp theo...</p>
                </div>
            `;
            setTimeout(renderExit8Hallway, 1500);
        }
    }
}

function triggerExit8Trap() {
    exit8CurrentTrapQuestion = exit8Questions[Math.floor(Math.random() * exit8Questions.length)];
    
    // Time calculation: 30s max, reduces by 3s each door. Min 6s.
    exit8TimeLeft = 30 - ((exit8CurrentDoor - 1) * 3);
    if (exit8TimeLeft < 6) exit8TimeLeft = 6; 
    
    renderExit8TrapScreen();
    
    exit8Timer = setInterval(() => {
        exit8TimeLeft--;
        const timerEl = document.getElementById("exit8TimerDisplay");
        if (timerEl) {
            timerEl.innerText = exit8TimeLeft + "s";
            if (exit8TimeLeft <= 5) {
                timerEl.classList.remove("text-warning");
                timerEl.classList.add("text-danger");
                timerEl.style.transform = "scale(1.2)";
            }
        }
        
        if (exit8TimeLeft <= 0) {
            exit8StopTimer();
            handleExit8TrapAnswer(false, "HẾT GIỜ!");
        }
    }, 1000);
}

function renderExit8TrapScreen() {
    const body = document.getElementById("exit8Body");
    const q = exit8CurrentTrapQuestion;
    
    // Shuffle options
    let opts = [...q.options];
    opts.sort(() => Math.random() - 0.5);

    let optionsHtml = opts.map((opt, i) => `
        <button class="btn btn-outline-light btn-lg w-100 mb-3 text-start fw-bold" 
                style="white-space: normal;"
                onclick="handleExit8TrapAnswer('${encodeURIComponent(opt)}' === '${encodeURIComponent(q.answer)}')">
            <span class="badge bg-secondary me-2 fs-6">${String.fromCharCode(65 + i)}</span> ${opt}
        </button>
    `).join('');

    body.innerHTML = `
        <div class="w-100" style="max-width: 650px; margin: 0 auto;">
            <div class="alert alert-danger border-danger border-2 bg-dark text-danger mb-4 py-3 shadow-lg">
                <h4 class="fw-bold mb-0 text-center" style="letter-spacing: 1px;">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i> CẢNH BÁO: PHÁT HIỆN BẪY!
                </h4>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mb-4 bg-secondary bg-opacity-25 p-3 rounded-3">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-danger fs-5 px-3 py-2">Cửa ${exit8CurrentDoor}</span>
                    <span class="text-light fw-bold ms-2">Giải toán để sống sót!</span>
                </div>
                <div class="fs-1 fw-bold text-warning" style="font-family: 'JetBrains Mono', monospace; transition: 0.3s;" id="exit8TimerDisplay">${exit8TimeLeft}s</div>
            </div>
            
            <div class="card bg-light text-dark mb-4 border-0 shadow">
                <div class="card-body p-4">
                    <h5 class="fw-bold mb-0" style="line-height: 1.6; font-size: 1.25rem;">${q.question}</h5>
                </div>
            </div>
            
            <div>${optionsHtml}</div>
        </div>
    `;
}

function handleExit8TrapAnswer(isCorrect, reason = "SAI ĐÁP ÁN!") {
    exit8StopTimer();
    const body = document.getElementById("exit8Body");
    
    if (isCorrect) {
        body.innerHTML = `
            <div class="text-success text-center">
                <i class="bi bi-shield-fill-check" style="font-size: 7rem; text-shadow: 0 0 20px #198754;"></i>
                <h2 class="fw-bold mt-3 text-uppercase">Phá bẫy thành công!</h2>
                <p class="fs-5 text-light">Bạn đã sử dụng tri thức để tự cứu mình. Tiến lên nào!</p>
            </div>
        `;
        exit8CurrentDoor++;
        setTimeout(() => {
            if (exit8CurrentDoor > exit8TargetDoor) {
                renderExit8Victory();
            } else {
                renderExit8Hallway();
            }
        }, 2500);
    } else {
        body.innerHTML = `
            <div class="text-danger text-center w-100" style="max-width: 600px; margin: 0 auto;">
                <i class="bi bi-skull-fill" style="font-size: 7rem; text-shadow: 0 0 30px red;"></i>
                <h1 class="fw-bold mt-3 text-uppercase display-5">${reason}</h1>
                <p class="fs-5 mb-4 text-light">Hành trình kết thúc tại cửa số <strong>${exit8CurrentDoor}</strong>.</p>
                
                <div class="alert alert-dark bg-opacity-75 text-start mb-5 border-secondary text-light">
                    <h6 class="text-danger fw-bold"><i class="bi bi-journal-x me-2"></i>Ôn tập lại kiến thức:</h6>
                    <hr class="border-secondary mt-1 mb-2">
                    <div class="mb-2"><strong>Câu hỏi:</strong> ${exit8CurrentTrapQuestion.question}</div>
                    <div class="mb-2 text-success"><strong>Đáp án đúng:</strong> ${exit8CurrentTrapQuestion.answer}</div>
                    <div class="text-warning small"><strong>Giải thích:</strong> ${exit8CurrentTrapQuestion.explain || 'Không có giải thích.'}</div>
                </div>
                
                <button class="btn btn-outline-light btn-lg px-5 fw-bold rounded-pill" onclick="renderExit8Start()">
                    <i class="bi bi-arrow-counterclockwise me-2"></i> CHƠI LẠI TỪ ĐẦU
                </button>
            </div>
        `;
    }
}

function renderExit8Victory() {
    exit8StopTimer();
    const body = document.getElementById("exit8Body");
    
    // Add rewards
    if (typeof currentScore !== 'undefined') currentScore += 200;
    if (typeof currentCoins !== 'undefined') currentCoins += 100;
    if (typeof updatePlayerUI === "function") updatePlayerUI();
    
    // Epic confetti
    const duration = 3 * 1000;
    const end = Date.now() + duration;
    (function frame() {
        confetti({
            particleCount: 5,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#ff0000', '#ffffff']
        });
        confetti({
            particleCount: 5,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: ['#ff0000', '#ffffff']
        });
        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    }());

    body.innerHTML = `
        <div class="text-warning text-center w-100">
            <i class="bi bi-door-open-fill" style="font-size: 8rem; text-shadow: 0 0 50px #ffc107;"></i>
            <h1 class="fw-bold mt-2 display-3" style="font-family: 'JetBrains Mono', monospace;">THOÁT HIỂM!</h1>
            <p class="fs-4 text-white mb-4">Chúc mừng! Bạn đã chinh phục thành công 8 cánh cửa sinh tử.</p>
            
            <div class="card bg-dark border-warning mx-auto mb-5" style="max-width: 400px;">
                <div class="card-body">
                    <h5 class="text-light mb-3">Phần Thưởng Kẻ Sống Sót</h5>
                    <div class="d-flex justify-content-center gap-3">
                        <span class="badge bg-primary fs-5 px-3 py-2 border border-primary"><i class="bi bi-star-fill me-1"></i> +200 Điểm</span>
                        <span class="badge bg-warning text-dark fs-5 px-3 py-2 border border-warning"><i class="bi bi-coin me-1"></i> +100 Xu</span>
                    </div>
                </div>
            </div>
            
            <button class="btn btn-warning btn-lg px-5 text-dark fw-bold rounded-pill shadow" onclick="renderExit8Start()">
                <i class="bi bi-controller me-2"></i> CHƠI LẠI
            </button>
        </div>
    `;
}

function exit8StopTimer() {
    if (exit8Timer) {
        clearInterval(exit8Timer);
        exit8Timer = null;
    }
}
