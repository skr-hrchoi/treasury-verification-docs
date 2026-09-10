#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공개 안전성 검사 — 공개 저장소에 실으면 안 되는 것이 문서에 섞였는지 본다.

왜 필요한가
  이 저장소는 공개다. 사내 문서에서 문단을 옮겨 붙이다 보면 실제 금액이나 사내 주소가
  같이 딸려 오기 쉽다. 사람 눈으로는 놓치므로 push 전에 기계가 한 번 더 본다.

무엇을 보나
  ① .env 에 들어 있는 실제 키 값이 그대로 나타나는가 (있으면 즉시 실패)
  ② 사내 서버 주소·포트
  ③ 절대 경로 (D:\\... )
  ④ 금액으로 읽히는 큰 숫자 — 화이트리스트(허용 오차·설정값·예시 값)는 통과

실행:  py tools\\check_public_safe.py       (종료코드 0 = 공개해도 안전)
"""

from __future__ import annotations

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)                    # docs-site
ROOT = os.path.dirname(SITE)                    # 검증시스템
DOCS = os.path.join(SITE, "docs")
ENV = os.path.join(ROOT, ".env")

# 문서에 나와도 되는 숫자 — 설정값·허용 오차·예시로 정한 값
ALLOWED_NUMBERS = {
    "100000000",      # cash_screen.tolerance (1억)
    "123456789012",   # 결과 스키마 예시 값
    "20260910",       # 예시 데이터 생성기의 난수 시드
}

PATTERNS = [
    # 파일명(samsapi.py)·필드명(samsapi.host)이 아니라 '도메인'만 잡는다: 점 두 개 이상 + 끝이 TLD
    ("사내 서버 주소", re.compile(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+){2,}\.(?:kr|com|net|org|io)\b", re.I)),
    ("사내 포트", re.compile(r"\b8400\b")),
    ("절대 경로", re.compile(r"[A-Za-z]:\\{1,2}클로드")),
]

# 금액으로 읽히는 숫자: 콤마 3묶음 이상 또는 9자리 이상 연속 숫자
MONEY = re.compile(r"\b\d{1,3}(?:,\d{3}){2,}\b|\b\d{9,}\b")


def env_secrets() -> list[str]:
    if not os.path.exists(ENV):
        return []
    out = []
    for line in io.open(ENV, encoding="utf-8"):
        if "=" in line and not line.strip().startswith("#"):
            v = line.split("=", 1)[1].strip()
            if len(v) >= 8:
                out.append(v)
    return out


def main() -> int:
    secrets = env_secrets()
    problems: list[str] = []
    scanned = 0

    for dp, _, fns in os.walk(DOCS):
        for fn in sorted(fns):
            if not fn.endswith((".md", ".css", ".yml")):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, SITE)
            s = io.open(p, encoding="utf-8", errors="ignore").read()
            scanned += 1

            for v in secrets:
                if v in s:
                    problems.append(f"{rel}: .env 의 실제 키 값이 문서에 있음")

            for label, pat in PATTERNS:
                for m in pat.finditer(s):
                    line = s[:m.start()].count("\n") + 1
                    problems.append(f"{rel}:{line}: {label} — {m.group(0)}")

            for m in MONEY.finditer(s):
                raw = m.group(0).replace(",", "")
                if raw in ALLOWED_NUMBERS:
                    continue
                line = s[:m.start()].count("\n") + 1
                problems.append(f"{rel}:{line}: 금액으로 읽히는 숫자 — {m.group(0)}")

    print(f"공개 안전성 검사 — 문서 {scanned}개")
    if problems:
        print(f"\n[막힘] {len(problems)}건. 고친 뒤 다시 실행하십시오.\n")
        for x in problems:
            print("  ·", x)
        return 1
    print("\n[통과] 실제 금액 · 사내 주소 · 절대 경로 · 접속 키 없음. 공개해도 안전합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
