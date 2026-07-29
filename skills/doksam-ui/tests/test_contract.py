"""doksam-ui 가 SSOT 로 인용하는 ui.doksam.com 엔드포인트 계약 검증 (stdlib only).

이 스킬은 사이트를 단일 진실원천으로 삼고 /llms.txt 를 live-fetch 하라고
지시한다. 그 엔드포인트가 죽거나 형식이 바뀌면 스킬이 조용히 낡으므로
실제 응답을 검증한다.

네트워크가 없거나 사이트가 일시 장애면 fail 이 아니라 skip 한다 — CI 머지
게이트가 외부 사이트 가용성에 볼모 잡히면 안 된다. 대신 문서 자체의 오프라인
계약(URL 표기 일관성)은 항상 검증한다.
"""
import json
import re
import unittest
import urllib.error
import urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
BASE = "https://ui.doksam.com"
TIMEOUT = 5


def fetch(path):
    """본문을 반환하고, 네트워크·사이트 문제면 None 을 반환한다."""
    try:
        req = urllib.request.Request(
            BASE + path, headers={"User-Agent": "doksam-skills-contract-test"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            if res.status != 200:
                return None
            return res.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None


class TestOfflineContract(unittest.TestCase):
    """네트워크 없이도 항상 검증하는 문서 자체 계약."""

    def test_all_cited_urls_are_on_the_ssot_host(self):
        """SKILL.md 가 인용하는 절대 URL 은 전부 ui.doksam.com 이어야 한다."""
        urls = re.findall(r"https://[a-z0-9.\-]+", SKILL_MD)
        self.assertTrue(urls)
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(url.startswith(BASE))

    def test_registry_install_command_form(self):
        """설치 명령 표기가 레지스트리 규약과 일치해야 한다."""
        self.assertIn("npx shadcn add https://ui.doksam.com/r/", SKILL_MD)
        self.assertIn('"@doksam-ui": "https://ui.doksam.com/r/{name}.json"',
                      SKILL_MD)


class TestLiveEndpoints(unittest.TestCase):
    """인용하는 엔드포인트가 실제로 살아 있고 기대 형식인지 (불가 시 skip)."""

    def test_llms_txt_is_a_machine_readable_catalog(self):
        body = fetch("/llms.txt")
        if body is None:
            self.skipTest("ui.doksam.com/llms.txt 접근 불가 — 네트워크/사이트")
        self.assertIn("npx shadcn add https://ui.doksam.com/r/", body)
        # SKILL.md 워크플로가 언급하는 프로필 5종이 카탈로그에 있어야 한다.
        for profile in ("profile-admin", "profile-service", "profile-data",
                        "profile-docs", "profile-console"):
            with self.subTest(profile=profile):
                self.assertIn(profile, body)

    def test_registry_index_is_valid_json(self):
        body = fetch("/r/registry.json")
        if body is None:
            self.skipTest("ui.doksam.com/r/registry.json 접근 불가")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.fail("/r/registry.json 이 유효한 JSON 이 아니다")
        self.assertTrue(data, "레지스트리 인덱스가 비어 있다")

    def test_rules_md_is_raw_markdown(self):
        body = fetch("/rules.md")
        if body is None:
            self.skipTest("ui.doksam.com/rules.md 접근 불가")
        self.assertTrue(body.lstrip().startswith("#"),
                        "raw markdown 이 아니라 HTML 로 보인다")
        # 다이제스트가 요약해 온 핵심 규칙 표식이 원문에 남아 있어야 한다.
        for marker in ("하드코딩", "shadcn", "Phosphor"):
            with self.subTest(marker=marker):
                self.assertIn(marker, body)


if __name__ == "__main__":
    unittest.main()
