# Third-Party Notices

이 저장소는 [MIT License](LICENSE)로 배포됩니다. 아래는 함께 쓰이는 제3자 저작물의 출처와 라이선스입니다.

성격이 두 가지로 갈립니다. **저장소에 포함된 것**은 라이선스가 고지를 요구하므로 반드시 남겨야 하고, **산출물이 실행 시 내려받는 것**은 우리가 배포하는 것이 아니라 의무는 없지만 의존 관계를 밝히기 위해 적습니다.

---

## 저장소에 포함된 것

### Phosphor Icons

- **출처**: <https://github.com/phosphor-icons/core>
- **라이선스**: MIT License
- **저작권**: Copyright (c) 2023 Phosphor Icons

아이콘 `path` 데이터가 인라인 SVG 형태로 이 저장소에 들어 있습니다.

| 위치 | 내용 |
|---|---|
| `skills/mobile-web-planner/SKILL.md` | 마크업 예시의 아이콘 |
| `skills/mobile-web-planner/tests/fixtures/runtime-parity/claude.html` | 픽스처 |
| `docs/samples/*.png` | 위 아이콘이 렌더된 화면 캡처 |

이 스킬들이 만드는 산출물에도 같은 방식으로 들어갑니다 — 이모지 대신 Phosphor `path` 를 인라인 `<svg>` 로 넣는 것이 이 저장소의 규약입니다 (`AGENTS.md` 참고).

```
MIT License

Copyright (c) 2023 Phosphor Icons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 산출물이 실행 시 내려받는 것

`skills/mobile-web-planner/resources/template.html` 로 만든 화면설계서 HTML 은 아래 두 가지를 CDN 에서 불러옵니다. 저장소에 사본을 두지 않으므로 재배포에 해당하지 않지만, 산출물을 열면 이들이 필요합니다.

### mermaid

- **출처**: <https://github.com/mermaid-js/mermaid>
- **라이선스**: MIT License
- **저작권**: Copyright (c) 2014 - 2022 Knut Sveidqvist
- **로드 경로**: `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`

`04 Information Architecture` · `06 Service Flow` · `07.x Sequence Diagram` 슬라이드의 다이어그램을 렌더합니다. 오프라인에서는 다이어그램이 원문 텍스트로 남습니다.

### Pretendard

- **출처**: <https://github.com/orioncactus/pretendard>
- **라이선스**: SIL Open Font License, Version 1.1
- **저작권**: Copyright (c) 2021, Kil Hyung-jin
  (원본 서체: Copyright 2014-2021 Adobe · Copyright (c) 2016 The Inter Project Authors · Copyright 2021 The M PLUS FONTS Project Authors)
- **로드 경로**: `https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css`

산출물의 본문 서체입니다. 없으면 시스템 기본 산세리프로 대체됩니다(`-apple-system, sans-serif`).

OFL 은 폰트 파일 자체의 재배포에 조건을 걸며, 폰트로 **렌더된 이미지**(`docs/samples/*.png` 등)에는 제약을 두지 않습니다.

---

## 해당 없음

- **OOXML 네임스페이스 URL** (`http://schemas.openxmlformats.org/...`) — `export_deck.py` 가 만드는 `.pptx` 에 들어가는 ECMA-376 표준 식별자입니다. 저작물이 아니라 스키마 이름입니다.
- **벤더링된 코드** — `node_modules` · `vendor` · `third_party` 디렉터리가 없습니다. 외부 코드를 통째로 복사해 둔 곳이 없습니다.

---

## 자산을 추가할 때

새 외부 자산을 들여오면 이 파일에 항목을 추가합니다. 산출물 템플릿이 참조하는 외부 호스트가 여기서 다뤄지는지는 `tests/test_third_party_notices.py` 가 검사합니다.
