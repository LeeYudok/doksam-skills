"""스킬 트리거(description) 경계가 서로 겹치지 않는지 검증한다 (stdlib only).

스킬은 frontmatter 의 `description` 으로 선택된다. 두 스킬의 description 이
같은 어휘를 공유하면 한 요청에 여러 개가 동시에 뜨고 서로를 밀어낸다.
AGENTS.md 7장이 이것을 "기술이 아니라 작업 단위로 나눈다" 는 규약으로 정해
두었지만, 지금까지 지키는지 재는 것이 없었다 (이슈 #130).

판정 방법:

1. description 에서 판별 키워드를 뽑는다. 한글은 조사를 떼고, 영문은
   소문자로 정규화한다.
2. 스킬 1/3 이상에 나타나는 낱말은 **일반어**로 보고 버린다. "코드" 처럼
   어느 스킬 설명에나 나오는 낱말까지 세면 모든 쌍이 겹쳐 보인다.
3. 남은 판별 키워드로 쌍마다 겹침을 잰다 —
   `|A ∩ B| / min(|A|, |B|)`. 짧은 description 이 긴 것에 통째로 삼켜지는
   경우를 잡아야 하므로 분모는 합집합이 아니라 더 작은 쪽이다.

면제는 **허용 목록이 아니라 조건**이다. 두 스킬이 서로를 알고 경계를
명시한 경우 — 한쪽 description 이 상대 스킬의 이름을 부르는 경우 — 만
면제한다. 이름을 하나씩 등록하는 허용 목록은 다음 스킬에서 또 깨진다.
"""
import itertools
import re
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

#: 겹침이 이 값을 넘고 서로를 명시하지도 않으면 경계가 흐린 것으로 본다.
#: 2026-08-17 기준 서로를 명시하지 않은 쌍의 최대치는 0.167 이고, 서로를
#: 명시한 두 쌍(mobile-web-planner↔nextjs-implementer, db-expert↔sqlite-expert)
#: 은 면제된다.
OVERLAP_THRESHOLD = 0.30

#: 한글 조사·어미. 긴 것부터 떼야 "으로" 가 "로" 에 먼저 잘리지 않는다.
JOSA = (
    "으로서", "으로", "로서", "에서", "에게", "이나", "하고", "까지", "부터",
    "이란", "라고", "이라", "와", "과", "을", "를", "이", "가", "은", "는",
    "의", "에", "로", "도", "만", "나", "며", "고",
)

#: 트리거를 가르지 못하는 기능어. 빈도 필터로도 걸러지지만, 스킬 수가
#: 적을 때는 빈도만으로 부족해 명시한다.
STOPWORDS = {
    "사용한다", "사용", "때", "것", "등", "및", "또는", "그리고", "쓴다", "한다",
    "하거나", "다룰", "요청", "요청할", "말할", "작업", "문제", "경우", "위한",
    "자체", "고유", "직접", "함께", "같은", "모든", "다음", "이것", "그것",
    "스킬", "사용자", "사용자가", "쓰지", "않는다", "대상", "대상이다",
}


def skill_dirs():
    return sorted(d for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").is_file())


def description(skill: Path) -> str:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"{skill} 에 description 이 없다")
    return match.group(1).strip()


def strip_josa(word: str) -> str:
    for josa in JOSA:
        if len(word) > len(josa) + 1 and word.endswith(josa):
            return word[: -len(josa)]
    return word


def keywords(text: str) -> set:
    """description 에서 판별 후보 낱말을 뽑는다."""
    found = set()
    for token in re.findall(r"[A-Za-z][A-Za-z0-9.+#/_-]*", text):
        if len(token) > 1:
            found.add(token.lower())
    for token in re.findall(r"[가-힣]+", text):
        token = strip_josa(token)
        if len(token) >= 2 and token not in STOPWORDS:
            found.add(token)
    return found


def discriminative(keyword_sets: dict) -> dict:
    """스킬 1/3 이상에 나타나는 일반어를 걷어낸 키워드 집합."""
    frequency = Counter()
    for words in keyword_sets.values():
        frequency.update(words)
    limit = max(1, len(keyword_sets) // 3)
    generic = {word for word, count in frequency.items() if count > limit}
    return {name: words - generic for name, words in keyword_sets.items()}


def names_each_other(name_a: str, desc_a: str, name_b: str, desc_b: str) -> bool:
    """한쪽이 상대 스킬 이름을 불러 경계를 명시했는가."""
    def mentions(desc: str, name: str) -> bool:
        return name in desc or name.replace("-", " ") in desc
    return mentions(desc_a, name_b) or mentions(desc_b, name_a)


def overlaps(descriptions: dict):
    """(겹침, a, b, 공유 키워드) 목록. 서로를 명시한 쌍은 제외한다."""
    sets = discriminative({name: keywords(d) for name, d in descriptions.items()})
    result = []
    for a, b in itertools.combinations(sorted(sets), 2):
        if names_each_other(a, descriptions[a], b, descriptions[b]):
            continue
        shared = sets[a] & sets[b]
        if not shared or not sets[a] or not sets[b]:
            continue
        score = len(shared) / min(len(sets[a]), len(sets[b]))
        result.append((score, a, b, sorted(shared)))
    return sorted(result, reverse=True)


class TestTriggerBoundaries(unittest.TestCase):
    def setUp(self):
        self.descriptions = {d.name: description(d) for d in skill_dirs()}

    def test_no_two_skills_share_a_trigger(self):
        for score, a, b, shared in overlaps(self.descriptions):
            with self.subTest(pair=f"{a} x {b}"):
                self.assertLess(
                    score, OVERLAP_THRESHOLD,
                    f"{a} 와 {b} 의 description 이 트리거를 공유한다 "
                    f"(겹침 {score:.2f}): {', '.join(shared)}. "
                    "AGENTS.md 7장대로 작업 단위로 경계를 다시 긋거나, "
                    "한쪽 description 이 상대 스킬 이름을 불러 무엇을 맡지 "
                    "않는지 명시하라.",
                )

    def test_detects_a_planted_collision(self):
        """규칙이 실제로 겹침을 잡는지 — 안 잡히면 통과는 의미가 없다."""
        planted = dict(self.descriptions)
        planted["fake-a"] = "고래 상어 해파리 산호초 를 다룰 때 사용한다."
        planted["fake-b"] = "고래 상어 해파리 산호초 조사를 할 때 사용한다."
        scores = [
            score for score, a, b, _ in overlaps(planted)
            if {a, b} == {"fake-a", "fake-b"}
        ]
        self.assertTrue(scores, "심어 둔 충돌 쌍이 목록에 없다")
        self.assertGreaterEqual(
            scores[0], OVERLAP_THRESHOLD,
            "심어 둔 충돌이 임계값을 넘지 못해 실패로 잡히지 않는다",
        )

    def test_naming_the_other_skill_exempts_the_pair(self):
        """경계를 명시한 쌍은 어휘가 겹쳐도 면제된다."""
        planted = dict(self.descriptions)
        planted["fake-a"] = "고래 상어 해파리 산호초 를 다룰 때 사용한다. 심해는 fake-b 를 쓴다."
        planted["fake-b"] = "고래 상어 해파리 산호초 조사를 할 때 사용한다."
        colliding = [
            (a, b) for _, a, b, _ in overlaps(planted)
            if {a, b} == {"fake-a", "fake-b"}
        ]
        self.assertFalse(colliding, "경계를 명시한 쌍이 면제되지 않았다")


class TestKeywordExtraction(unittest.TestCase):
    def test_josa_is_stripped(self):
        self.assertEqual(strip_josa("스키마를"), "스키마")
        self.assertEqual(strip_josa("클러스터로"), "클러스터")

    def test_short_words_survive_josa_stripping(self):
        """조사처럼 보이는 두 글자 낱말을 잘라내면 의미가 사라진다."""
        self.assertEqual(strip_josa("빌드"), "빌드")

    def test_latin_tokens_are_lowercased(self):
        self.assertIn("sqlite", keywords("SQLite 파일을 읽는다"))


if __name__ == "__main__":
    unittest.main()
