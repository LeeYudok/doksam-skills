#!/usr/bin/env python3
"""기존 명령 경로를 유지하는 mobile-web-planner 번들 검증기 호환 래퍼."""
import sys
from pathlib import Path

BUNDLED_SCRIPTS = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "mobile-web-planner"
    / "scripts"
)
sys.path.insert(0, str(BUNDLED_SCRIPTS))

from validate_storyboard import *  # noqa: F401,F403,E402


if __name__ == "__main__":
    sys.exit(main())
