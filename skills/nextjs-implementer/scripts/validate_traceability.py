#!/usr/bin/env python3
"""Business Rules와 traceability.json의 화면·규칙·파일 연결을 검증한다."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


SCREEN_RE = re.compile(r"(?m)^##\s+([A-Z]{2,6}-[A-Z]{2,12}-\d{3})\b")
RULE_RE = re.compile(
    r"\b([A-Z]{2,6}-[A-Z]{2,12}-\d{3}\.(?:IN|OUT|INT|EDGE)-\d{2})\b")


def duplicates(values):
    return sorted(value for value, count in Counter(values).items() if count > 1)


def validate(manifest, rules_md, repo_root):
    violations = []
    br_screens = SCREEN_RE.findall(rules_md)
    br_rules = RULE_RE.findall(rules_md)
    if duplicates(br_screens):
        violations.append(f"Business Rules 중복 화면 ID: {', '.join(duplicates(br_screens))}")
    if duplicates(br_rules):
        violations.append(f"Business Rules 중복 규칙 ID: {', '.join(duplicates(br_rules))}")

    screens = manifest.get("screens") if isinstance(manifest, dict) else None
    if not isinstance(screens, list):
        return violations + ["traceability.json의 screens는 배열이어야 한다"]

    manifest_screens = []
    manifest_rules = []
    for index, screen in enumerate(screens, 1):
        if not isinstance(screen, dict) or not screen.get("screenId"):
            violations.append(f"screens[{index}]에 screenId가 없다")
            continue
        screen_id = screen["screenId"]
        manifest_screens.append(screen_id)
        implementations = screen.get("implementation")
        if not isinstance(implementations, list) or not implementations:
            violations.append(f"{screen_id}에 implementation 파일이 없다")
        else:
            for path in implementations:
                if not isinstance(path, str) or not (repo_root / path).is_file():
                    violations.append(f"{screen_id} 구현 파일 없음: {path}")

        rules = screen.get("rules")
        if not isinstance(rules, list):
            violations.append(f"{screen_id}의 rules는 배열이어야 한다")
            continue
        for rule in rules:
            if not isinstance(rule, dict) or not rule.get("ruleId"):
                violations.append(f"{screen_id}에 ruleId 없는 규칙 연결이 있다")
                continue
            rule_id = rule["ruleId"]
            manifest_rules.append(rule_id)
            if not rule_id.startswith(screen_id + "."):
                violations.append(f"규칙 ID가 다른 화면에 연결됨: {screen_id} → {rule_id}")
            tests = rule.get("tests")
            if not isinstance(tests, list) or not tests:
                violations.append(f"{rule_id}에 테스트 파일이 없다")
            else:
                for path in tests:
                    if not isinstance(path, str) or not (repo_root / path).is_file():
                        violations.append(f"{rule_id} 테스트 파일 없음: {path}")

    for label, values in (("화면", manifest_screens), ("규칙", manifest_rules)):
        dup = duplicates(values)
        if dup:
            violations.append(f"traceability.json 중복 {label} ID: {', '.join(dup)}")

    missing_screens = sorted(set(br_screens) - set(manifest_screens))
    extra_screens = sorted(set(manifest_screens) - set(br_screens))
    missing_rules = sorted(set(br_rules) - set(manifest_rules))
    extra_rules = sorted(set(manifest_rules) - set(br_rules))
    if missing_screens:
        violations.append(f"traceability.json 화면 ID 누락: {', '.join(missing_screens)}")
    if extra_screens:
        violations.append(f"Business Rules에 없는 화면 ID: {', '.join(extra_screens)}")
    if missing_rules:
        violations.append(f"traceability.json 규칙 ID 누락: {', '.join(missing_rules)}")
    if extra_rules:
        violations.append(f"Business Rules에 없는 규칙 ID: {', '.join(extra_rules)}")
    return violations


def main(argv=None):
    parser = argparse.ArgumentParser(description="기획↔구현 traceability 검증")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("business_rules", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        rules_md = args.business_rules.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"오류: 입력을 읽을 수 없음: {exc}", file=sys.stderr)
        return 2
    violations = validate(manifest, rules_md, args.repo_root)
    for violation in violations:
        print(f"[위반] {violation}")
    if violations:
        print(f"traceability 위반 {len(violations)}건")
        return 1
    print("traceability 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
