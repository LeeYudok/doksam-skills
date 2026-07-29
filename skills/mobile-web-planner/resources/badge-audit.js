/*
 * badge-audit.js — 렌더된 화면설계서에서 pointer-badge 가 실제로 무엇을 가리키는지 잰다.
 *
 * 배지는 `position:absolute; top:<추정>px` 로 놓이는데, 목업은 `transform:scale(0.9)`
 * (목업 1개) 또는 `zoom:0.9`(2개 이상)로 축소되고 콘텐츠 높이는 렌더해야 정해진다.
 * 그래서 인라인 top 값만 보고는 배지가 의도한 요소 옆에 있는지 알 수 없다 —
 * 정적 검사(check_badge_alignment.py)로는 겹침·순서 역전까지가 한계다.
 *
 * 사용법: 산출물 HTML 을 브라우저로 열고(파일 경로 또는 로컬 서버) 개발자도구
 * 콘솔이나 에이전트의 브라우저 실행 도구에 이 파일 내용을 그대로 붙여 실행한다.
 * 반환값의 `misaligned` 가 비어 있어야 한다.
 *
 *   - gap: 배지 상단과 가장 가까운 콘텐츠 블록 상단의 거리(px, 목업 좌표계)
 *   - 임계값 22px 는 배지 높이(24px)에서 온다 — 그보다 멀면 어떤 블록과도
 *     같은 줄에 있지 않다는 뜻이다.
 *
 * 고칠 때는 대상 요소의 measured top 을 읽어 인라인 top 을 `measured / 0.9` 로 되돌린다
 * (반환값의 `scale` 참고).
 */
(() => {
  const GAP_LIMIT = 22;
  const misaligned = [];
  const summary = { slides: 0, badges: 0, mermaidRendered: 0, mermaidTotal: 0 };

  document.querySelectorAll(".mermaid").forEach((m) => {
    summary.mermaidTotal += 1;
    if (m.querySelector("svg")) summary.mermaidRendered += 1;
  });

  document.querySelectorAll(".ppt-slide").forEach((slide) => {
    const no = (slide.querySelector(".ppt-top-no")?.textContent || "").trim();
    if (!/^NO\.\s*09\./.test(no)) return;
    summary.slides += 1;

    slide.querySelectorAll(".mock-body").forEach((body, mockIndex) => {
      const rect = body.getBoundingClientRect();
      // 스크롤된 목업에서도 좌표가 흔들리지 않게 scrollTop 을 더해 문서 좌표로 환산한다.
      const toLocal = (el) =>
        Math.round(el.getBoundingClientRect().top - rect.top + body.scrollTop);

      const blocks = [...body.querySelectorAll("*")]
        .filter((el) => !el.classList.contains("pointer-badge") && el.offsetHeight > 10)
        .map(toLocal);

      body.querySelectorAll(".pointer-badge").forEach((badge) => {
        summary.badges += 1;
        const top = toLocal(badge);
        const gap = blocks.length ? Math.min(...blocks.map((b) => Math.abs(b - top))) : Infinity;
        if (gap > GAP_LIMIT) {
          misaligned.push({
            slide: no,
            mock: mockIndex,
            badge: badge.textContent.trim(),
            measuredTop: top,
            gap,
          });
        }
      });
    });
  });

  return { scale: 0.9, summary, misaligned };
})();
