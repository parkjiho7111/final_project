/**
 * static/policy_modal.js
 * 정책 모달의 데이터 주입 및 기능 제어 (최종 버전)
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. 모달 닫기 이벤트 (공통)
    const modal = document.getElementById('policy-modal');
    const closeBtn = document.getElementById('modal-close-x-btn'); // X 버튼 ID 확인 필요

    // 닫기 함수
    const closeModal = () => {
        if (!modal) return;
        modal.classList.remove('active');
        document.body.style.overflow = ''; // 스크롤 복구
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    // 배경 클릭 시 닫기
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
});

// 2. 카드 클릭 시 호출되는 함수 (HTML onclick="openCardModal(this)"와 연결)
function openCardModal(element) {
    const modal = document.getElementById('policy-modal');
    if (!modal) return;

    // 2-1. 데이터 가져오기 (HTML 태그의 data-json 속성 파싱)
    const jsonStr = element.getAttribute('data-json');
    if (!jsonStr) return console.error("데이터가 없습니다.");

    try {
        const data = JSON.parse(jsonStr);

        // 2-2. DOM 요소 매핑
        const els = {
            img: document.getElementById('modal-img'),
            category: document.getElementById('modal-category'),
            title: document.getElementById('modal-title'),
            desc: document.getElementById('modal-desc'),
            date: document.getElementById('modal-date'),
            linkBtn: document.getElementById('modal-link-btn'),   // [원문 보러 가기] 버튼
            shareBtn: document.getElementById('modal-share-btn'), // [공유하기] 버튼
            heartBtn: document.getElementById('modal-heart-btn')  // [찜하기] 버튼
        };

        // 2-3. 데이터 주입 (DB 칼럼명에 맞춰서 매핑)

        // [이미지]
        if (els.img) {
            // data.image가 없으면 DB의 img, 그것도 없으면 기본 이미지
            els.img.src = data.image || data.img || '/static/images/card_images/job_1.webp';
        }

        // [카테고리] DB 칼럼: genre (없으면 category)
        if (els.category) {
            els.category.innerText = data.genre || data.category || '기타';
        }

        // [제목] DB 칼럼: title
        if (els.title) {
            els.title.innerText = data.title || '제목 없음';
        }

        // [내용] DB 칼럼: summary (없으면 desc)
        if (els.desc) {
            els.desc.innerText = data.summary || data.desc || '상세 내용이 없습니다.';
        }

        // [마감일] DB 칼럼: period (없으면 date)
        if (els.date) {
            const periodText = data.period || data.date || '상시 모집';
            els.date.innerHTML = `<i class="fa-regular fa-calendar mr-1"></i> ${periodText}`;
        }

        // [핵심 1] 원문 보러 가기 (DB 칼럼: link)
        if (els.linkBtn) {
            if (data.link) {
                els.linkBtn.href = data.link; // href 속성에 URL 주입
                els.linkBtn.classList.remove('opacity-50', 'pointer-events-none'); // 활성화
                els.linkBtn.innerText = "원문 보러 가기"; // 텍스트 복구
            } else {
                els.linkBtn.href = "#";
                els.linkBtn.classList.add('opacity-50', 'pointer-events-none'); // 비활성화 스타일
                els.linkBtn.innerText = "링크 없음";
            }
        }

        // [핵심 2] 공유하기 버튼 (클립보드 복사)
        if (els.shareBtn) {
            // 기존 이벤트 리스너 중복 방지를 위해 onclick 속성으로 재할당
            els.shareBtn.onclick = () => {
                const shareUrl = data.link || window.location.href; // 링크가 있으면 그 링크, 없으면 현재 페이지 주소
                navigator.clipboard.writeText(shareUrl).then(() => {
                    alert('정책 링크가 복사되었습니다!');
                }).catch(err => {
                    console.error('복사 실패:', err);
                });
            };
        }

        // [핵심 3] 찜하기 버튼 (UI 토글)
        if (els.heartBtn) {
            // 버튼 초기화 (이미 찜했는지 확인하는 로직은 추후 백엔드 연동 필요)
            // 우선은 비어있는 하트로 시작한다고 가정
            const icon = els.heartBtn.querySelector('i');
            icon.className = "fa-regular fa-heart text-xl";
            els.heartBtn.classList.remove('border-red-500', 'text-red-500');

            // 클릭 이벤트
            els.heartBtn.onclick = function () {
                // 토글 로직
                const isActive = icon.classList.contains('fa-solid');

                if (!isActive) {
                    // 찜하기 상태로 변경 (채워진 하트 + 빨간색)
                    icon.className = "fa-solid fa-heart text-xl";
                    this.classList.add('border-red-500', 'text-red-500');
                    // TODO: 여기에 백엔드로 '찜하기 API' 요청 보내는 코드 추가
                } else {
                    // 찜 취소 상태로 변경 (빈 하트 + 회색)
                    icon.className = "fa-regular fa-heart text-xl";
                    this.classList.remove('border-red-500', 'text-red-500');
                    // TODO: 여기에 백엔드로 '찜 취소 API' 요청 보내는 코드 추가
                }
            };
        }

        // 2-4. 모달 보여주기
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // 배경 스크롤 막기

        // 애니메이션 효과
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

    } catch (e) {
        console.error("JSON 파싱 에러:", e);
    }
}