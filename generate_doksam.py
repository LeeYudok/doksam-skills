import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
template_path = REPO_ROOT / 'skills' / 'mobile_web_planner' / 'resources' / 'template.html'
output_path = REPO_ROOT / 'examples' / 'doksam_news_storyboard.html'

with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

# Extract styles
style_match = re.search(r'<style>(.*?)</style>', template, re.DOTALL)
styles = style_match.group(1) if style_match else ""

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>화면설계서 · 메인홈–기사상세 | 덕삼뉴스</title>
<link rel="preconnect" href="https://cdnjs.cloudflare.com">
<style>
{styles}
</style>
</head>
<body>
<div class="docwrap">

  <div class="dochead">
    <div>
      <div class="kicker">화면설계서 · Screen Design Spec</div>
      <h1>덕삼뉴스 (Doksam News) · 메인 홈 → 기사 상세</h1>
      <p>바쁜 현대인을 위해 글로벌 핵심 이슈를 빠르고 직관적으로 전달하는 미니멀리즘 플랫폼</p>
      <span class="status-pill">● 초안 — 검토 전</span>
    </div>
    <div class="doc-meta">
      <span>문서번호</span><b>WF-2026-0725-DOKSAM</b>
      <span>작성</span><b>모바일웹 기획 에이전트</b>
      <span>대상 채널</span><b>모바일 앱</b>
      <span>작성일</span><b>2026-07-25</b>
    </div>
  </div>

  <div class="notice">
    <b>주의:</b> 본 문서는 <code>mobile-web-planner</code> 스킬을 통해 생성된 '덕삼뉴스' 기획서의 예시입니다.
  </div>

  <!-- ================= STORYBOARD ================= -->
  <div class="section-title"><span class="num">1</span><h2>스토리보드 · User Flow</h2></div>
  <p class="section-sub">사용자 액션과 화면 전환 트리거를 순서대로 표현합니다.</p>

  <div class="storyboard">
    <div class="sb-node">
      <div class="sb-step-label">Screen 01</div>
      <div class="sb-thumb">
        <div class="bar"></div>
        <div class="body">
          <div class="ph" style="height:40px;background:#EAF1FC;border-radius:8px;"></div>
          <div class="ph" style="height:14px;width:80%;margin:10px auto;"></div>
          <div class="ph" style="height:24px;"></div>
          <div class="ph" style="height:24px;"></div>
        </div>
      </div>
      <div class="sb-title">메인 홈</div>
      <div class="sb-desc">속보 하이라이트 · 카테고리 탭</div>
    </div>

    <div class="sb-arrow">
      <svg viewBox="0 0 24 10" fill="none"><path d="M0 5H22M22 5L16 1M22 5L16 9" stroke="currentColor" stroke-width="2"/></svg>
      <div class="sb-trigger">기사 카드 클릭</div>
    </div>

    <div class="sb-node">
      <div class="sb-step-label">Screen 02</div>
      <div class="sb-thumb">
        <div class="bar"></div>
        <div class="body">
          <div class="ph" style="height:60px;background:#DCE3EE;border-radius:4px;"></div>
          <div class="ph" style="height:10px;width:40%;margin:6px 0;"></div>
          <div class="ph" style="height:8px;width:90%;margin-bottom:4px;"></div>
          <div class="ph" style="height:8px;width:80%;margin-bottom:4px;"></div>
        </div>
      </div>
      <div class="sb-title">기사 상세</div>
      <div class="sb-desc">본문 가독성 · 공유 및 북마크</div>
    </div>
  </div>

  <!-- ================= SCREEN 01 ================= -->
  <div class="section-title"><span class="num">2</span><h2>화면 상세 · 메인 홈 (Home)</h2></div>

  <div class="screen-block">
    <div>
      <div class="screen-head"><span class="screen-id">SCR-01</span><span class="screen-name">메인 홈</span></div>
      <div class="mock">
        <div class="mock-screen">
          <div class="mock-status"></div>
          <div class="mock-header"><span style="font-weight:800;color:var(--navy-deep);">덕삼뉴스</span><span class="ic">🔍 🔔</span></div>
          <div class="mock-body">
            
            <div style="background:#FDEBEC; border-radius:10px; padding:14px; margin-bottom:14px;">
              <div style="font-size:10px; font-weight:800; color:#C22B36; margin-bottom:4px;">BREAKING NEWS</div>
              <div style="font-size:15px; font-weight:800; color:#1A1A1A;">글로벌 혁신 AI, 세상을 바꾸다</div>
            </div>

            <div class="filter-tabs">
              <div class="filter-tab active">Top Stories</div>
              <div class="filter-tab">World</div>
              <div class="filter-tab">Business</div>
              <div class="filter-tab">Tech</div>
            </div>

            <div class="card-mini" style="display:flex; gap:12px; align-items:center;">
               <div style="width:60px; height:60px; background:#EAF1FC; border-radius:8px;"></div>
               <div style="flex:1;">
                 <div style="font-size:13px; font-weight:800; color:#1A1A1A;">경제 지표 회복세 뚜렷...</div>
                 <div style="font-size:10px; color:#8A8F98; margin-top:4px;">Business · 2시간 전</div>
               </div>
            </div>
            <div class="card-mini" style="display:flex; gap:12px; align-items:center;">
               <div style="width:60px; height:60px; background:#EAF1FC; border-radius:8px;"></div>
               <div style="flex:1;">
                 <div style="font-size:13px; font-weight:800; color:#1A1A1A;">새로운 모바일 기획 에이전트 출시</div>
                 <div style="font-size:10px; color:#8A8F98; margin-top:4px;">Tech · 3시간 전</div>
               </div>
            </div>

          </div>
          <div class="mock-footer">
            <div class="mock-tab active"><div class="dot"></div>Home</div>
            <div class="mock-tab"><div class="dot"></div>Discover</div>
            <div class="mock-tab"><div class="dot"></div>Search</div>
            <div class="mock-tab"><div class="dot"></div>Saved</div>
            <div class="mock-tab"><div class="dot"></div>Profile</div>
          </div>
        </div>
      </div>
    </div>

    <div>
      <p class="spec-note">사용자가 앱을 켜자마자 가장 중요한 글로벌 속보를 시각적으로 확인하고, 카테고리별 뉴스를 직관적으로 탐색할 수 있는 진입점입니다.</p>
      <table class="spec">
        <tr><th>필드ID</th><th>명칭</th><th>구분</th><th>타입</th><th>설명</th></tr>
        <tr><td>gnb_logo</td><td>서비스 로고</td><td><span class="tag req">필수</span></td><td>Image</td><td>덕삼뉴스 로고 노출</td></tr>
        <tr><td>breaking_news</td><td>속보 영역</td><td><span class="tag opt">선택</span></td><td>Banner</td><td>긴급 속보 발생 시에만 붉은색 테마로 노출</td></tr>
        <tr><td>category_tab</td><td>카테고리 탭</td><td><span class="tag req">필수</span></td><td>Tab</td><td>Top Stories, World 등 좌우 스와이프 가능</td></tr>
        <tr><td>news_feed</td><td>뉴스 피드 리스트</td><td><span class="tag req">필수</span></td><td>List</td><td>우측 썸네일, 좌측 타이틀 및 메타정보(분야, 시간)</td></tr>
        <tr><td>bottom_tab</td><td>하단 탭 바</td><td><span class="tag req">필수</span></td><td>Tab×5</td><td>Home/Discover/Search/Saved/Profile</td></tr>
      </table>
      <div class="event-box">
        <h4>이벤트 · 연계</h4>
        <ul>
          <li><span class="tag event">on tap</span> <b>news_feed</b> 항목 클릭 → <b>SCR-02</b> 기사 상세 화면으로 이동</li>
          <li><span class="tag event">swipe</span> 카테고리 탭 영역 좌우 스와이프 시 탭 변경 및 피드 갱신</li>
          <li><span class="tag event">refresh</span> Pull-to-refresh 시 최신 뉴스 데이터 재조회</li>
        </ul>
      </div>

      <div class="states-title">상태값 · State</div>
      <div class="state-strip">
        <div class="state-chip loading"><span class="st-label">LOADING</span><p>기사 카드 스켈레톤 UI 노출</p></div>
        <div class="state-chip error"><span class="st-label">ERROR</span><p>상단 배너 "오프라인 상태입니다"</p></div>
      </div>
    </div>
  </div>

  <!-- ================= SCREEN 02 ================= -->
  <div class="section-title"><span class="num">3</span><h2>화면 상세 · 기사 상세 (Article Detail)</h2></div>

  <div class="screen-block">
    <div>
      <div class="screen-head"><span class="screen-id">SCR-02</span><span class="screen-name">기사 상세</span></div>
      <div class="mock">
        <div class="mock-screen" style="position:relative;">
          <div class="mock-status"></div>
          
          <div style="height:140px; background:#DCE3EE; position:relative;">
             <div class="mock-header" style="background:transparent; border:none; position:absolute; top:0; width:100%;">
                <span class="ic" style="color:#1A1A1A; font-weight:800; background:rgba(255,255,255,0.7); padding:4px; border-radius:50%;">‹</span>
             </div>
          </div>

          <div class="mock-body" style="border-radius:18px 18px 0 0; margin-top:-18px; position:relative; z-index:2; padding:24px 16px;">
            <div style="font-size:11px; color:#5C8FEE; font-weight:700; margin-bottom:6px;">TECH</div>
            <div style="font-size:18px; font-weight:800; color:#1A1A1A; line-height:1.4; margin-bottom:12px;">새로운 모바일 기획 에이전트 출시, UX/UI 디자인의 패러다임을 바꾸다</div>
            <div style="font-size:10px; color:#8A8F98; display:flex; gap:10px; margin-bottom:24px;">
               <span>김기자</span><span>2026.07.25</span><span>3 min read</span>
            </div>

            <div style="font-size:13px; color:#333; line-height:1.6;">
               새롭게 출시된 모바일웹 플래너 에이전트는 기획자의 의도를 정확히 파악하여...
               <br><br>
               이제 단 몇 분 만에 완벽한 IA와 스토리보드를 구축할 수 있습니다.
            </div>
          </div>
          
          <div class="mock-footer" style="position:absolute; bottom:0; width:100%; display:flex; justify-content:space-between; padding:12px 24px; box-shadow:0 -2px 10px rgba(0,0,0,0.05);">
             <span style="font-size:16px;">🤍 24</span>
             <span style="font-size:16px;">💬 12</span>
             <span style="font-size:16px;">🔖</span>
             <span style="font-size:16px;">📤</span>
          </div>
        </div>
      </div>
    </div>

    <div>
      <p class="spec-note">기사 본문을 가독성 높게 제공하며, 사용자가 기사에 대한 의견을 남기거나 쉽게 공유/스크랩 할 수 있도록 지원합니다.</p>
      <table class="spec">
        <tr><th>필드ID</th><th>명칭</th><th>구분</th><th>타입</th><th>설명</th></tr>
        <tr><td>header_img</td><td>헤더 이미지</td><td><span class="tag opt">선택</span></td><td>Image</td><td>기사 최상단 썸네일, 스크롤 시 패럴랙스 효과</td></tr>
        <tr><td>article_title</td><td>기사 타이틀</td><td><span class="tag req">필수</span></td><td>Text</td><td>굵고 명확한 헤드라인 폰트</td></tr>
        <tr><td>meta_info</td><td>메타 정보</td><td><span class="tag req">필수</span></td><td>Text</td><td>기자 이름, 카테고리, 발행일, 예상 읽기 시간</td></tr>
        <tr><td>sticky_bar</td><td>하단 스티키 바</td><td><span class="tag req">필수</span></td><td>Toolbar</td><td>좋아요, 댓글, 북마크(스크랩), 공유 버튼 고정</td></tr>
      </table>
      <div class="event-box">
        <h4>이벤트 · 연계</h4>
        <ul>
          <li><span class="tag event">scroll</span> 화면 아래로 스크롤 시 헤더 이미지가 자연스럽게 흐려짐</li>
          <li><span class="tag event">on tap</span> 하단 '공유(Share)' 클릭 시 OS 기본 공유 시스템 호출</li>
          <li><span class="tag event">on tap</span> 하단 '북마크(Bookmark)' 클릭 시 아이콘이 채워지며 Saved 탭에 저장</li>
        </ul>
      </div>

    </div>
  </div>

  <div class="section-title"><span class="num">4</span><h2>공통 정책 및 예외 처리</h2></div>
  <div class="policy-grid">
    <div class="policy-card">
      <h3>오프라인 상태 처리</h3>
      <table class="err">
        <tr><th>상태</th><th>안내 메시지</th><th>기능 제한</th></tr>
        <tr><td class="mono">Network Error</td><td>"오프라인 상태입니다."</td><td>새로운 기사 로딩 불가</td></tr>
        <tr><td class="mono">Offline Read</td><td>"저장된 기사만 읽을 수 있습니다."</td><td>Saved 탭의 북마크 기사만 열람 허용</td></tr>
      </table>
    </div>

    <div class="policy-card">
      <h3>접근성 가이드라인 (Accessibility)</h3>
      <ul class="a11y-list">
        <li>기사 본문 폰트 크기 조절 기능 (OS 설정 연동)</li>
        <li>저시력자를 위한 다크모드 (Dark Theme) 지원</li>
        <li>모든 이미지 및 썸네일에 대체 텍스트(alt text) 제공</li>
      </ul>
    </div>
  </div>

</div>
</body>
</html>
"""

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'생성 완료: {output_path}')
