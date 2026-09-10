#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공개 문서용 대시보드 캡처를 만들기 위한 '예시 데이터' 대시보드 생성기.

왜 필요한가
  문서 사이트는 공개다. 실제 대시보드 캡처에는 회사별 보유 금액이 그대로 찍혀 있어 실을 수 없다.
  그렇다고 캡처를 빼면 화면 설명이 크게 부실해진다.
  → 진짜 대시보드 생성기(checks/build_dashboard.py)에 '지어낸 숫자'를 먹여 같은 화면을 만든다.
    화면 모양·색·배치는 실물 그대로이고 금액만 가짜다.

덤으로: 실제 운영에서는 아직 실패 이력이 없어 「위험·실패·주의」 색을 캡처할 수 없다.
       예시 데이터에는 일부러 그런 날을 섞어 문서에서 네 가지 상태를 모두 보여준다.

실행:  py tools\\make_demo_dashboard.py
결과:  tools\\_demo\\dashboard.html  (git 제외)
"""

from __future__ import annotations

import datetime as dt
import json
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)                 # docs-site
ROOT = os.path.dirname(SITE)                 # 검증시스템
OUT = os.path.join(HERE, "_demo")
REPORTS = os.path.join(OUT, "reports")

random.seed(20260910)   # 돌릴 때마다 같은 그림이 나오도록 고정

# 실제 지표 구성과 같은 뼈대 (2026-09-10 실행 기준). 값은 전부 지어낸 것이다.
CRIT, WARN = "CRITICAL", "WARNING"
SPEC = [
    # (check_id, 심각도, 기준금액 or None)
    ("metrics.cash_screen_group",            CRIT, 3_120_000_000_000),
    ("metrics.cash_screen_sinokor",          CRIT, 1_740_000_000_000),
    ("metrics.cash_screen_heung",            CRIT,   920_000_000_000),
    ("metrics.cash_screen_hansung",          CRIT,   460_000_000_000),
    ("metrics.cash_source_match_sinokor",    CRIT, None),
    ("metrics.cash_source_match_heung",      CRIT, None),
    ("metrics.cash_source_match_hansung",    CRIT, None),
    ("metrics.source_vs_dashboard_sinokor",  CRIT, 1_739_402_115_600),
    ("metrics.source_vs_dashboard_heung",    CRIT,   918_651_030_400),
    ("metrics.source_vs_dashboard_hansung",  CRIT,   459_228_770_100),
    ("metrics.cash_on_hand_sinokor",         WARN,       120_000_000),
    ("metrics.cash_on_hand_heung",           WARN,         2_400_000),
    ("metrics.cash_on_hand_hansung",         WARN,         3_100_000),
    ("metrics.branch_totals_sinokor",        CRIT, 1_739_402_115_600),
    ("metrics.branch_totals_heung",          CRIT,   918_651_030_400),
    ("metrics.branch_totals_hansung",        CRIT,   459_228_770_100),
    ("metrics.cash_bycur_sinokor",           CRIT, 1_739_402_115_600),
    ("metrics.cash_bycur_heung",             CRIT,   918_651_030_400),
    ("metrics.cash_bycur_hansung",           CRIT,   459_228_770_100),
    ("metrics.bond_purchase_sinokor_KRW",    CRIT,    30_000_000_000),
    ("metrics.bond_purchase_sinokor_USD",    CRIT,       180_000_000),
    ("metrics.bond_purchase_sinokor_JPY",    CRIT,     3_000_000_000),
    ("metrics.bond_price_sinokor",           CRIT, None),
    ("metrics.bond_holdings_sinokor",        WARN, None),
    ("metrics.bond_purchase_heung_KRW",      CRIT,    30_000_000_000),
    ("metrics.bond_purchase_heung_USD",      CRIT,       120_000_000),
    ("metrics.bond_purchase_heung_JPY",      CRIT,     3_000_000_000),
    ("metrics.bond_price_heung",             CRIT, None),
    ("metrics.bond_holdings_heung",          WARN, None),
    ("metrics.bond_price_hansung",           CRIT, None),
    ("metrics.bond_holdings_hansung",        WARN, None),
    ("metrics.stock_summary_sinokor",        CRIT,    40_000_000_000),
    ("metrics.stock_internal_sinokor",       CRIT, None),
    ("metrics.stock_price_xcheck_sinokor",   WARN, None),
    ("metrics.stock_summary_heung",          CRIT, None),
    ("metrics.stock_summary_hansung",        CRIT, None),
]

NAME_KO = {"sinokor": "장금", "heung": "흥아", "hansung": "한성"}
NAME_FULL = {"sinokor": "장금상선", "heung": "흥아라인", "hansung": "한성라인", "group": "장금상선계열"}


def detail_for(cid: str, status: str, exp, act, as_of: str) -> str:
    co = next((NAME_KO[k] for k in NAME_KO if cid.endswith(k) or f"_{k}_" in cid), "장금")
    full = next((NAME_FULL[k] for k in NAME_FULL if cid.endswith(k)), "장금상선")
    if "cash_screen" in cid:
        s = (f"[{full}] 현금 화면 정합성 — 전 기준일 360건 검사, "
             f"총보유현금·통화별합계·계열사별합계·추이그래프 ")
        return s + ("전부 일치(독립 재계산 대비 최대 오차 0억). ※ 예시 데이터"
                    if status == "PASS" else "중 2곳이 어긋남(최대 오차 3억). ※ 예시 데이터")
    if "cash_source_match" in cid:
        return f"[{full}] 통화별 원금 두 소스 일치 — 179일 × 4통화 대조, 차이 없음. ※ 예시 데이터"
    if "bond_purchase" in cid:
        cur = cid.rsplit("_", 1)[1]
        return f"[{co}] 채권 매입금액 원천 대비 · {cur} — " + ("일치" if status == "PASS" else "불일치") + ". ※ 예시 데이터"
    if "bond_price" in cid:
        return f"[{co}] 채권 평가단가 원천 대비 ({as_of} 기준) — 일치. ※ 예시 데이터"
    if "bond_holdings" in cid:
        return f"[{co}] 보유 채권 목록 — 원천과 저장 목록 일치. ※ 예시 데이터"
    if "stock_summary" in cid and exp is None:
        return f"[{co}] 보유주식 없음"
    if "stock_" in cid:
        return f"[{co}] 주식 검사 — 일치. ※ 예시 데이터"
    if status == "UNVERIFIABLE":
        return "검증 불가: 사내 API 속도제한(HTTP 429) — 다음 실행 때 사후 재검증 대상. ※ 예시 데이터"
    kind = "전체합 vs 부분합"
    return (f"{kind} — 기대={exp}, 실측={act}, 차이={(act or 0) - (exp or 0)} / "
            f"허용 절대오차 ±1 → " + ("일치" if status == "PASS" else "불일치") + ". ※ 예시 데이터")


def make_run(day: dt.date, mode: str) -> dict:
    """mode: ok | unver | fail | crit"""
    as_of = (day - dt.timedelta(days=1)).isoformat()
    results = []
    for i, (cid, sev, base) in enumerate(SPEC):
        status, exp, act = "PASS", None, None
        if base is not None:
            # 날짜별로 조금씩 흔들리게 — 기준값에 비례시켜야 작은 항목이 음수로 뒤집히지 않는다.
            drift = int(base * random.uniform(-0.02, 0.02) / 1_000_000) * 1_000_000
            exp = base + drift
            act = exp
        if mode == "unver" and cid in ("metrics.bond_price_sinokor", "metrics.bond_holdings_sinokor"):
            status = "UNVERIFIABLE"
            exp = act = None
        if mode == "fail" and cid == "metrics.stock_price_xcheck_sinokor":
            status = "FAIL"
        if mode == "crit" and cid == "metrics.cash_screen_group":
            status = "FAIL"
            act = exp + 300_000_000
        results.append({
            "check_id": cid, "category": "metrics", "status": status, "severity": sev,
            "expected": float(exp) if exp is not None else None,
            "actual": act, "tolerance": 1 if base else None,
            "detail": detail_for(cid, status, exp, act, as_of),
            "snapshot_paths": [],
            "as_of": as_of,
        })
    return {"run_at": f"{day.isoformat()}_0910", "results": results}


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(REPORTS, exist_ok=True)

    # 2026-09-01 ~ 09-10 평일. 상태를 섞어 네 가지 색을 모두 보여준다.
    modes = {3: "unver", 4: "fail", 5: "crit"}      # 그 외는 정상 (네 가지 색이 모두 나오게)
    day = dt.date(2026, 9, 1)
    n = 0
    while day <= dt.date(2026, 9, 10):
        if day.weekday() < 5:
            run = make_run(day, modes.get(n, "ok"))
            with open(os.path.join(REPORTS, f"{run['run_at']}.json"), "w", encoding="utf-8") as fh:
                json.dump(run, fh, ensure_ascii=False, indent=1)
            n += 1
        day += dt.timedelta(days=1)

    out_html = os.path.join(OUT, "dashboard.html")
    rc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "checks", "build_dashboard.py"),
         "--reports-dir", REPORTS,
         "--config", os.path.join(ROOT, "config", "metrics.yaml"),
         "--out", out_html],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if rc.returncode != 0:
        print("대시보드 생성 실패:", rc.stderr[:500])
        return 1
    print(f"예시 대시보드 생성 완료 ({n}일치): {out_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
