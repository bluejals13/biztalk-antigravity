document.addEventListener("DOMContentLoaded", () => {
    // API URL 설정 (상대 경로로 프론트/백 통합 라우팅 호환 및 로컬 호환)
    const API_BASE_URL = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? window.location.origin
        : "";

    const targetButtons = document.querySelectorAll(".target-btn");
    const selectedTargetChip = document.getElementById("selectedTargetChip");
    const inputText = document.getElementById("inputText");
    const currentCharCount = document.getElementById("currentCharCount");
    const convertBtn = document.getElementById("convertBtn");
    const outputText = document.getElementById("outputText");
    const copyBtn = document.getElementById("copyBtn");
    const loadingOverlay = document.getElementById("loadingOverlay");
    const btnSpinner = document.getElementById("btnSpinner");
    const toast = document.getElementById("toast");

    let currentTarget = "boss";

    const targetLabels = {
        boss: "👔 상사 / 임원 대상",
        colleague: "🤝 타팀 동료 대상",
        client: "🏢 고객 / 외부 대상",
        team: "⚡ 팀 내 동료 대상"
    };

    // 1. 수신 대상 버튼 선택 이벤트
    targetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            targetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            currentTarget = btn.dataset.target;
            if (selectedTargetChip && targetLabels[currentTarget]) {
                selectedTargetChip.textContent = targetLabels[currentTarget];
            }
        });
    });

    // 2. 입력 글자 수 카운터
    if (inputText && currentCharCount) {
        inputText.addEventListener("input", () => {
            currentCharCount.textContent = inputText.value.length;
        });
    }

    // 3. 변환 실행 함수
    async function handleConvert() {
        const text = inputText.value.trim();
        if (!text) {
            alert("변환할 원문 텍스트를 입력해주세요.");
            inputText.focus();
            return;
        }

        // 로딩 상태 시작
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/convert`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    target_audience: currentTarget
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `서버 에러 (${response.status})`);
            }

            const data = await response.json();
            outputText.value = data.converted_text || "변환된 결과가 없습니다.";
            copyBtn.disabled = false;

        } catch (error) {
            console.error("Tone Conversion Error:", error);
            alert(`말투 변환 중 오류가 발생했습니다.\n${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    // 4. 로딩 상태 토글
    function setLoading(isLoading) {
        if (isLoading) {
            loadingOverlay.classList.remove("hidden");
            btnSpinner.classList.remove("hidden");
            convertBtn.disabled = true;
        } else {
            loadingOverlay.classList.add("hidden");
            btnSpinner.classList.add("hidden");
            convertBtn.disabled = false;
        }
    }

    // 5. 클립보드 복사 기능
    async function handleCopy() {
        const textToCopy = outputText.value;
        if (!textToCopy) return;

        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(textToCopy);
            } else {
                outputText.select();
                document.execCommand("copy");
            }
            showToast("클립보드에 복사되었습니다!");
        } catch (err) {
            console.error("Copy failed:", err);
            alert("복사에 실패했습니다.");
        }
    }

    // 6. Toast 알림 팝업
    function showToast(message) {
        toast.textContent = message;
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 2500);
    }

    // 이벤트 리스너 바인딩
    if (convertBtn) {
        convertBtn.addEventListener("click", handleConvert);
    }
    if (copyBtn) {
        copyBtn.addEventListener("click", handleCopy);
    }
});
