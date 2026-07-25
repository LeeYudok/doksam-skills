# Issue #13 — 화면 상세 슬라이드에 목업 2개 이상 배치 지원

**Status:** DONE_WITH_CONCERNS (구현·정적 검증 완료 / 브라우저 실측만 코디네이터에게 남김)

**Branch:** `feat/issue-13-multi-mock`

## 1. 선택한 메커니즘

`zoom` + `:has()` — 이슈가 1순위로 제시한 방향을 채택했다. 단, 개수 판정을 `:nth-of-type` 대신 **형제 결합자(`~`)** 로 바꿨다.

```css
.ppt-wireframe:has(.mock ~ .mock) { gap: 24px; }
.ppt-wireframe:has(.mock ~ .mock) .mock {
  flex: none;
  transform: none;
  zoom: 0.9;
}
.ppt-wireframe:has(.mock ~ .mock ~ .mock ~ .mock) .mock { zoom: 0.68; }
```

### 기각한 것

| 후보 | 기각 이유 |
|---|---|
| `transform: scale()` 유지 | 레이아웃 박스가 320px 그대로라 flex 배치가 틀리고, min-content 로 부풀어 `overflow:hidden` 에 잘린다. 이슈의 진단이 정확했다. |
| 이슈가 쓴 `:nth-of-type(2)` | `nth-of-type` 은 **같은 태그명 형제**의 순서를 센다. 목업 사이에 다른 `div`(구분선·주석용 요소 등)가 끼거나 목업이 `div` 가 아니면 카운트가 어긋난다. `:has(.mock ~ .mock)` 은 "목업 앞에 목업이 있다" 를 직접 표현해 태그명·중간 삽입물과 무관하다. |
| 후보 2 (`aspect-ratio` + `height:100%` 비율 목업) | 목업 내부 인라인 `style` 의 px 값(썸네일 72px, 폰트 14px 등)이 함께 줄지 않아 내용 비율이 깨진다. 이슈가 지적한 위험이 실재한다. `zoom` 은 서브트리 전체 px 를 곱하므로 이 문제가 없다 — 이게 `zoom` 의 결정적 장점이다. |
| flex-shrink 에 맡기기 | 폭만 줄고 높이는 안 줄어 목업 비율이 찌그러진다. 그래서 오히려 `flex: none` 으로 shrink 를 **막았다**. |
| 5개 이상 지원용 추가 tier | 실무 비교 슬라이드는 2~4개면 충분하고, tier 를 무한히 늘리면 CSS 만 부풀고 목업이 판독 불가 크기가 된다. SKILL.md 에 "최대 4개, 그 이상은 슬라이드를 나눈다" 로 명시했다. |

## 2. 폭·높이 예산 산술

전제: `.docwrap { max-width: 1400px }`, `* { box-sizing: border-box }`, 뷰포트 폭 >= 1480 (body padding 40px 양쪽).

**가로**

```
슬라이드 border-box 폭                    1400.0
  - .ppt-slide border 1px * 2               -2.0  -> 1398.0 (content box)
  - .ppt-content padding 12px * 2          -24.0  -> 1374.0  (= 이슈가 말한 콘텐츠 영역 1374)
  - .ppt-desc-panel width                 -380.0
  - .ppt-content gap                       -12.0  -> 982.0  (.ppt-wireframe border-box)
  - .ppt-wireframe border 1px * 2           -2.0  -> 980.0  가용 폭
```

**세로**

```
슬라이드 높이 = 1400 * 9/16                787.5
  - .ppt-slide border 1px * 2               -2.0  -> 785.5
  - .ppt-top-bar height                    -48.0
  - .ppt-content margin-bottom (footer)    -40.0  -> 697.5  (.ppt-content border-box)
  - .ppt-content padding 12px * 2          -24.0  -> 673.5  (.ppt-wireframe border-box, align-items:stretch)
  - .ppt-wireframe border 1px * 2           -2.0  -> 671.5  가용 높이
```

> 이슈 본문의 "가용 폭 약 660px" 은 오류다. 1374 - 380 - 12 = **982**(테두리 빼면 980)이고, 660 에 가까운 숫자는 실제로는 가용 높이(671.5) 쪽이다. 이 정정 덕분에 축소율을 이슈가 상정한 0.62/0.44 보다 훨씬 덜 공격적으로(0.9) 잡을 수 있었다.

**배율별 적재**

| 목업 수 | zoom | 목업 폭 | 총 폭 | 여유 | 총 높이 | 여유 |
|---|---|---|---|---|---|---|
| 1 | (기존 `transform:scale(0.9)`) | 288 (시각) | 288 | 692 | 540 (시각) | 131.5 |
| 2 | 0.9 | 288 | 2*288 + 24 = **600** | 380 | 540 | 131.5 |
| 3 | 0.9 | 288 | 3*288 + 2*24 = **912** | 68 | 540 | 131.5 |
| 4 | 0.68 | 217.6 | 4*217.6 + 3*24 = **942.4** | 37.6 | 408 | 263.5 |
| 5 | 0.68 | 217.6 | 5*217.6 + 4*24 = 1184 | **-204 (초과)** | | |

`gap` 은 `.ppt-wireframe`(zoom 안 걸림) 의 속성이므로 24px 실값 그대로 계산에 들어간다.

2~3개를 0.9 로 통일한 이유: 기존 1개 배치 슬라이드의 **겉보기 크기(288x540)와 정확히 같다.** 2개일 때 여유가 380px 남으니 1.0 이나 1.1 로 키울 수도 있지만, 그러면 2-up 슬라이드의 폰이 1-up 슬라이드보다 **더 커 보여** 문서 전체의 일관성이 깨진다.

## 3. 세 가지 결정

### (1) 메커니즘 — `zoom`, `:has(.mock ~ .mock)` 게이트

위 1절. 핵심은 `zoom` 이 레이아웃 사용값(used value)에 곱해진다는 점과, **서브트리의 모든 px 를 같은 비율로 곱한다**는 점이다. 후자가 이슈 #6 재발을 막는다(4절).

### (2) 캡션 — 새 클래스 `mock-caption` 추가 (인라인 style 기각)

```css
.mock-caption {
  position: absolute; left: 0; right: 0; bottom: -24px;
  text-align: center; font-size: 13px; font-weight: 700; color: #555;
}
```

- **왜 필요한가**: "기본 상태 / 선택됨" 라벨이 없으면 나란히 놓인 목업이 무엇의 변형인지 알 수 없어 비교 슬라이드의 의미가 사라진다. 옵션이 아니라 기능의 일부다.
- **왜 인라인 `style` 이 아닌가**: 이 프로젝트의 "세부 스타일은 인라인으로" 규칙은 *목업 내부 콘텐츠*의 일회성 장식을 겨냥한 것이다. 캡션은 (a) 다중 목업 슬라이드마다 목업 개수만큼 반복되고, (b) `position:absolute; left:0; right:0; bottom:-24px` 라는 **구조적 배치 계약**을 담고 있다. 이걸 슬라이드마다 3~4번 인라인으로 베끼면 오프셋이 어긋나 캡션 높이가 들쭉날쭉해진다. 클래스 계약의 존재 이유에 정확히 부합한다.
- **왜 `absolute` 인가**: `.mock` 이 이미 `position: relative` 다. absolute 로 두면 ① `.mock` 의 column flex 흐름에 참여하지 않아 `.mock-screen { flex:1 }` 의 높이 계산을 건드리지 않고, ② `.mock` 의 **자식**이므로 `:has(.mock ~ .mock)` 형제 카운트에 끼어들지 않고, ③ 폰 프레임(`border: 2px solid #555`) **밖 아래**에 놓여 기기 UI 의 일부로 오독되지 않는다. 별도 wrapper 클래스가 필요 없다.
- 잘림 여부: `bottom:-24px` 는 zoom 0.9 에서 실측 21.6px 만 프레임 아래로 나간다. 목업 아래 여유는 (671.5 - 540)/2 = 65.75px. 충분하다. zoom 0.68 에서는 16.3px vs 여유 131.75px.
- `SKILL.md` Class Quick Reference 표에 등재했고 `TestSkillClassQuickReference` 가 통과한다.

### (3) 번호 — 슬라이드 단위 연속 번호 (①②③④)

이슈가 자연스러워 보인다고 한 방향을 채택. 근거:

- 우측 `desc-list` 는 **슬라이드에 하나뿐**이다. 목업별로 1 부터 다시 시작하면 배지 `1` 이 두 개 이상 존재하고, `desc-num` ① 이 어느 목업의 1 을 가리키는지 마크업만으로는 결정 불가다. **1:1 대응이라는 기존 계약이 깨진다.**
- 목업별 재시작을 하려면 `desc-list` 를 목업별로 그룹핑(헤더 + 별도 리스트)해야 하는데, 그러려면 클래스가 더 늘고 설명 패널 380px 안에서 세로 공간을 잡아먹는다.
- 매기는 순서: **첫 목업의 배지를 위에서 아래로, 그다음 목업으로 이어서**(첫 목업 1·2 → 두 번째 목업 3). 설명 항목에는 어느 목업인지 라벨을 함께 적게 했다 — 예: `<b>필터 목록 (선택됨)</b>`.
- `SKILL.md` 의 "목업 여러 개 배치" 절과 2개 마크업 예시에 명문화했다.

## 4. 이슈 #6 배지 gutter — 배율 무관하게 보존됨

#6 의 불변식은 순수하게 **길이 부등식**이다.

```
badge.left(2px) + badge.width(24px) = 26px  <=  mock-body.padding-left(28px)
```

`zoom: z` 는 서브트리 안 모든 px 의 사용값에 z 를 곱한다. `padding-left`, `left`, `width` 는 전부 `.mock` **내부**(`mock-body`, `pointer-badge`)에 선언된 px 이므로 셋이 동일한 z 로 스케일된다. 부등식은 1차 동차식이므로 양변에 z > 0 을 곱해도 방향이 보존된다.

```
z * 26  <=  z * 28    (모든 z > 0)
```

배율별 실수치:

| zoom | padding-left | badge left | badge width | badge right edge | 여유 |
|---|---|---|---|---|---|
| 1 (참조) | 28.0 | 2.0 | 24.0 | 26.0 | 2.0 |
| 0.9 (2~3개) | 25.2 | 1.8 | 21.6 | 23.4 | **1.8** |
| 0.68 (4개) | 19.04 | 1.36 | 16.32 | 17.68 | **1.36** |

즉 **어떤 배율에서도 여유가 0 보다 크다.** 이게 `zoom` 을 고른 결정적 이유다. 반대로 후보 2(`aspect-ratio` 비율 목업)를 골랐다면 폭만 줄고 `padding-left: 28px`·`left: 2px`·`width: 24px` 는 상수로 남아 **부등식은 살아있되 gutter 가 콘텐츠 폭을 상대적으로 더 잡아먹었을** 것이고, 반대로 인라인 padding 이 함께 줄지 않아 콘텐츠와의 관계가 뒤틀렸을 것이다.

containing block 관련 우려도 없다: 배지의 containing block 은 `mock-body`(인라인 `position:relative`)이고, 이는 zoom 이 걸린 `.mock` **안쪽**이다. 설령 `zoom != 1` 이 `.mock` 에 containing block 을 만든다 해도(표준 `zoom` 은 만들지 않는다) `mock-body` 가 더 가까운 조상이라 배지 좌표 해석은 바뀌지 않는다. `transform: scale()` 이 `.mock` 에 containing block 을 만드는 것과 대비되는 지점인데, 어느 쪽이든 `mock-body` 가 이겨서 무해하다.

`transform: none` 을 함께 준 이유: 기본 `.mock` 규칙의 `transform: scale(0.9)` 를 지우지 않으면 `zoom: 0.9` 와 곱해져 0.81 이 된다. 명시적으로 해제했다.

## 5. 회귀 안전성 — 1개 배치 슬라이드는 바이트 단위로 동일

**증거 1 — 생성 예시 diff 가 CSS 전용이다.**

```
$ git diff --stat examples/
 examples/doksam_news_storyboard.html | 43 ++++++++++++++++++++++++++++++++++++
 1 file changed, 43 insertions(+)
```

43줄 **추가만**, 삭제 0. 모든 추가가 `<style>` 블록 안(263행 부근, `.mock-tab.active` 다음)이다.

**증거 2 — `</style>` 이후 마크업 해시가 동일하다.**

```
markup identical after </style>: True
old markup sha: 931f73c9c309a106
new markup sha: 931f73c9c309a106
```

**증거 3 — 새 규칙이 이 문서에서 매치되지 않는다.**

```
wireframes in example: 2
  mocks in this wireframe: 1
  mocks in this wireframe: 1
```

두 `06.x` 슬라이드 모두 목업 1개라 `:has(.mock ~ .mock)` 이 어디에도 매치되지 않는다. `.mock-caption` 도 예시 마크업에 등장하지 않는다(`new-only CSS classes used in markup: False`). 즉 CSS 텍스트만 늘고 **연산 스타일은 한 줄도 바뀌지 않는다.**

**게이트 설계 요지**: 추가한 3개 규칙이 전부 `:has(.mock ~ .mock)` 하위이고, `.mock-caption` 은 선언만 존재하는 신규 클래스다. 기존 `.mock`·`.ppt-wireframe` 기본 규칙은 **한 글자도 수정하지 않았다.** 따라서 이미 생성된 문서·기존 슬라이드에 영향을 줄 경로가 없다.

`generate_doksam.py` 는 **수정하지 않았다.** 예시에 다중 목업 슬라이드를 넣으면 `tests/test_generate.py` 의 `test_has_seven_slides`·`test_slide_numbers_follow_scheme` 가 깨지는데 `tests/` 는 스코프 밖이다. 대신 아래 프로브 문서로 검증한다.

## 6. 검증 출력 (그대로)

```
$ python3 -m unittest discover -s tests
........................
----------------------------------------------------------------------
Ran 24 tests in 0.004s

OK

$ python3 generate_doksam.py
생성 완료: examples/doksam_news_storyboard.html (슬라이드 7장)
gen exit=0

$ git diff --exit-code examples/     # 커밋 후
diff exit=0
```

## 7. 코디네이터가 브라우저에서 확인할 것

프로브 문서: **`.superpowers/multimock-probe.html`** (재생성: `python3 .superpowers/build_probe.py`)

목업 1/2/3/4개 슬라이드가 순서대로 있고, **페이지가 스스로 치수를 재서 맨 위에 PASS/FAIL 표를 그린다.** 탭 제목도 `ALL PASS` 또는 `N FAIL` 로 바뀐다.

### 절차

```bash
mongoose -d .superpowers -l http://127.0.0.1:8913
# http://127.0.0.1:8913/multimock-probe.html
```

`file://` 로 열어도 된다(외부 리소스 요청 없음, Pretendard 폰트만 미적용).

**창 폭을 1480px 이상으로 키운다** — 그래야 슬라이드가 1400px 가 되고 아래 기대값이 성립한다. 표 상단에 `window.innerWidth` 와 실제 슬라이드 폭이 찍히니 먼저 확인할 것.

### 기대값 (`getBoundingClientRect` 기준, 오차 ±1.5px)

| 요소 | 슬라이드 | 기대값 |
|---|---|---|
| `.ppt-wireframe` content box 폭 | 전부 | **980.00** |
| `.ppt-wireframe` content box 높이 | 전부 | **671.50** |
| `.ppt-wireframe` `scrollWidth <= clientWidth` | 전부 | **true** (가로 잘림 없음) |
| `.ppt-wireframe` `scrollHeight <= clientHeight` | 전부 | **true** (세로 잘림 없음) |
| `.mock` 시각 폭 x 높이 | 1·2·3개 | **288.00 x 540.00** |
| `.mock` 시각 폭 x 높이 | 4개 | **217.60 x 408.00** |
| 인접 `.mock` 간 간격 | 2·3·4개 | **24.00** |
| `.mock` 좌/우 끝이 `.ppt-wireframe` content box 안 | 전부 | **true** |
| `.mock-caption` 아래끝이 `.ppt-wireframe` 안 | 2·3·4개 | **true** |
| `.pointer-badge` 폭 | 1·2·3개 | **21.60** |
| `.pointer-badge` 폭 | 4개 | **16.32** |
| `.pointer-badge` 좌측끝 >= `.mock-screen` 좌측끝 | 전부 | **true** (#6 잘림 없음) |
| `.pointer-badge` 우측끝 <= `mock-body` 첫 콘텐츠 좌측끝 | 전부 | **true** (#6 겹침 없음) |
| 그 간격(gutter 여유) | 1·2·3개 | **1.80** |
| 그 간격(gutter 여유) | 4개 | **1.36** |

총 108개 체크. **하나라도 FAIL 이면 그 행의 actual 값을 알려주면 된다.**

### 눈으로 볼 것

1. **06.1 (1개)** 이 기존 `examples/doksam_news_storyboard.html` 의 `06.1` 과 목업 크기·위치가 같아야 한다(내용은 프로브용 더미). 나란히 열고 비교.
2. 모든 슬라이드에서 주황 배지가 **온전한 정사각형**으로 보여야 한다 — 왼쪽이 반쪽 잘리면 #6 재발이다.
3. 배지가 본문 텍스트(`content A`) 를 덮지 않아야 한다.
4. 캡션("기본 상태" 등)이 폰 프레임 **바로 아래**, 잘리지 않고 보여야 한다.
5. 4개 슬라이드에서 목업이 서로 닿거나 패널 밖으로 나가지 않아야 한다.

## 8. 우려 (Concerns)

1. **브라우저 실측을 못 했다.** 이 워커에 브라우저 제어 권한이 없어(브라우저 선택에 사용자 확인이 필요) 7절의 숫자는 전부 **측정된 CSS 값으로부터의 계산**이다. 프로브가 자체 채점하도록 만들어 확인 비용은 최소화했다. `zoom` 의 반올림 처리는 엔진별로 미세하게 다를 수 있어 오차 ±1.5px 를 뒀다.
2. **`zoom` 브라우저 지원.** Chrome/Edge 는 오래전부터, Safari 도 지원, **Firefox 는 126(2024-05)부터**다. 산출물이 PPT 대체 문서로 크롬에서 열리는 용도라 실질 위험은 낮지만, 아주 오래된 Firefox 에서는 다중 목업이 원래대로 잘린다(1개 배치는 무영향). `:has()` 는 Chrome 105 / Safari 15.4 / Firefox 121 이상.
3. **`transform: scale(0.9)` 과 `zoom: 0.9` 의 렌더 차이.** 겉보기 크기는 288x540 으로 같지만 transform 은 렌더 결과를 확대/축소하는 반면 zoom 은 90% 크기로 **다시 레이아웃**한다. 따라서 1-up 슬라이드와 2-up 슬라이드에서 같은 텍스트의 줄바꿈 위치가 1~2px 다를 수 있다. 통일하려면 1개 배치도 `zoom` 으로 바꿔야 하는데 그건 회귀 금지 요건에 정면으로 걸려서 하지 않았다. **후속 이슈 후보**로 남긴다.
4. **`.mock-caption` 은 `.mock` 의 자식이어야 한다.** `.mock` 의 형제로 두면 flex row 의 독립 아이템이 되어 레이아웃이 깨진다. SKILL.md 에 "`mock` 의 마지막 자식" 으로 명시했으나 CSS 로 강제할 수단은 없다.
5. **5개 이상은 잘린다.** tier 를 더 만들지 않고 SKILL.md 문서 규칙으로 막았다. 에이전트가 규칙을 무시하면 `overflow:hidden` 에 잘린다. 개수 상한을 코드로 검증하고 싶으면 `generate_doksam.py` 에 체크를 넣는 후속 작업이 필요하다(현재 예시에 다중 목업 슬라이드가 없어 검증 대상이 없다).
6. **`SKILL.md`·`template.html` 은 형제 워커 2명과 공유**한다. 충돌 예상 지점: `template.html` 은 `.mock-tab.active` 직후 한 블록만 추가했고, `SKILL.md` 는 (a) 배지 문단 뒤 새 절, (b) Quick Reference 표의 `ppt-wireframe`·`mock` 행 수정 + `mock-caption` 행 추가, (c) Markup 절에 2-목업 예시 추가 — 세 군데다.
