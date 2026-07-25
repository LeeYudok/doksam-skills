#!/usr/bin/env python3
"""예시 스토리보드 생성 + 클래스 계약 검증.

skills/mobile-web-planner/resources/template.html 이 CSS 클래스의 유일한
정의처다. 이 스크립트는 예시 산출물을 재생성하면서, 생성된 HTML 이 정의되지
않은 클래스를 쓰고 있으면 exit 1 로 막는다.

stdlib 만 사용한다 (이 환경의 Homebrew Python 3.14 는 외부 라이브러리
import 가 깨져 있다).

사용법:
    python3 generate_doksam.py

불변식:
    실행 후 `git diff --exit-code examples/` 가 clean 해야 한다.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = REPO_ROOT / "skills" / "mobile-web-planner" / "resources" / "template.html"
OUTPUT_PATH = REPO_ROOT / "examples" / "doksam_news_storyboard.html"

#: CSS 정의가 없어도 되는 클래스. mermaid.js 가 런타임에 렌더한다.
WHITELIST = frozenset({"mermaid"})

PROJECT_NAME = "덕삼뉴스"
VERSION = "1.0.0"
DOC_DATE = "2026.07.25"
DOC_AUTHOR = "모바일웹 기획 에이전트"


def extract_style(template_html: str) -> str:
    """<style> 블록 내부 CSS 를 반환한다."""
    match = re.search(r"<style>(.*?)</style>", template_html, re.DOTALL)
    if match is None:
        raise ValueError("template 에 <style> 블록이 없다")
    return match.group(1)


def defined_classes(css: str) -> set[str]:
    """CSS 셀렉터에 등장하는 클래스명 집합을 반환한다.

    선언 블록({...})과 세미콜론으로 끝나는 at-rule(@import, @charset)을
    먼저 제거한 뒤 남은 셀렉터에서만 .name 을 찾는다. 선언 값의 소수점
    (0.5)이나 @import URL 의 확장자(.css)를 클래스로 오인하지 않는다.
    """
    selectors = re.sub(r"\{[^{}]*\}", " ", css)
    selectors = re.sub(r"@[\w-]+[^;{}]*;", " ", selectors)
    return set(re.findall(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)", selectors))


def used_classes(html: str) -> set[str]:
    """class 속성에 등장하는 클래스명 집합을 반환한다."""
    names: set[str] = set()
    for value in re.findall(r'class="([^"]*)"', html):
        names.update(value.split())
    return names


def undefined_classes(html: str, css: str) -> list[str]:
    """정의되지 않은 채 사용된 클래스명을 정렬해 반환한다."""
    return sorted(used_classes(html) - defined_classes(css) - WHITELIST)


def build_html(styles: str) -> str:
    """예시 스토리보드 HTML 전체를 조립한다. (Task 4 에서 구현)"""
    raise NotImplementedError


def main() -> int:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    styles = extract_style(template)
    html = build_html(styles)

    missing = undefined_classes(html, styles)
    if missing:
        print(
            "정의되지 않은 CSS 클래스를 사용하고 있다 "
            f"({TEMPLATE_PATH.relative_to(REPO_ROOT)} 에 정의를 추가하거나 "
            "사용을 제거할 것):",
            file=sys.stderr,
        )
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    slide_count = html.count('class="ppt-slide"')
    print(f"생성 완료: {OUTPUT_PATH.relative_to(REPO_ROOT)} (슬라이드 {slide_count}장)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
