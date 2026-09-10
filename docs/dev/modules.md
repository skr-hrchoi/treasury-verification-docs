# 검사 프로그램 5종

`run_verification.sh` 가 이 순서로 부릅니다. 모두 `--out` 으로 부분 결과 JSON 을 냅니다.

| # | 스크립트 | 산출 | 외부 의존 |
| --- | --- | --- | --- |
| ① | `checks/metrics/compare.py` | 6개 | 없음 (Supabase 만) |
| ② | `checks/metrics/source_compare.py` | 6개 | SamsApi |
| ③ | `checks/metrics/bond_verify.py` | 12개 | SamsApi |
| ④ | `checks/metrics/stock_verify.py` | 5개 | 야후 파이낸스(선택) |
| ⑤ | `checks/metrics/cash_screen.py` | 7개 | **node** + 포털 스냅샷 |

---

## ① `compare.py` — 내부 정합성

`metrics.yaml` 의 `metrics:` 배열을 읽어 `type: internal_consistency` 항목을 검사합니다.
**외부 API 를 쓰지 않으므로 사내망이 끊긴 날에도 항상 돌아갑니다.**

```
전체합(total_endpoint → total_path) vs 부분합(parts_endpoint → parts_path 의 합)
```

| 지표 | 항등식 |
| --- | --- |
| `branch_totals_{회사}` | 지사별 잔액의 합 = `total_krw` |
| `cash_bycur_{회사}` | 통화별 합계(`byCur`)의 합 = 총계(`totalKRW.totalKRW`) |

- 단독 실행: `py checks/metrics/compare.py --config config/metrics.yaml --metric branch_totals_sinokor`
- Supabase 는 최신 1행을 `order=...desc&limit=1` 로 고른 뒤 `$[0]` 으로 접근합니다.

---

## ② `source_compare.py` — 현금 원천 대비

회사별로 SamsApi 자금일보에서 **총 보유현금(KRW)을 독립 재계산**해 Supabase `cash_detail` 최신 행과 비교합니다.

| 지표 | 비교 대상 | 심각도 |
| --- | --- | --- |
| `source_vs_dashboard_{회사}` | 원천 총 보유현금 ↔ `classification.totalKRW.totalKRW` | CRITICAL |
| `cash_on_hand_{회사}` | 원천 계정 1001 '현금'(시재) ↔ (총계 − 은행 명세 합) | WARNING |

- **같은 영업일(as_of) 기준**으로만 비교합니다.
- 사내망 미도달·타임아웃·키 없음은 `UNVERIFIABLE`.
- 옵션: `--company sinokor`

---

## ③ `bond_verify.py` — 채권 원천 대비

SamsApi 와 Supabase `cash_assets.payload.bonds[]` 를 비교합니다.

| 코드 | 검사 | 비교 방식 | 심각도 |
| --- | --- | --- | --- |
| B1 | 매입금액 | `fa/bondlist` ↔ 저장 `buyAmount` 를 **통화별 합계**로 대조. 경과이자는 종목별로 함께 확인 | CRITICAL |
| B2 | 평가단가 | `fa/falist` ↔ 저장 `prices[해당일]` | CRITICAL |
| B3 | 보유 목록 | 원천 `bond_number` 집합 ↔ 저장 목록 (신규 편입·만기 누락) | WARNING |

!!! note "통화를 섞지 않는 이유"
    통화를 섞어 더한 합계는 금액으로 읽을 수 없고, 환율로 환산하면 **고정돼 있어야 할 취득원가가
    환율 따라 흔들립니다.** 원천도 통화별 원금액으로 들고 있으므로 같은 자로 비교합니다.
    지표 id 가 `bond_purchase_{회사}_{통화}` 로 쪼개진 것도 이 때문입니다.

- 옵션: `--company sinokor`

---

## ④ `stock_verify.py` — 주식 3각 검증

주식은 대조할 **사내 원천 API 가 없습니다.** 그래서 세 각도로 나눠 봅니다.

| 코드 | 검사 | 내용 | 심각도 |
| --- | --- | --- | --- |
| S1 | 요약↔종목합 | `stockSummary` 가 Σ`stocks[]` 와 일치하는지 (배당·매도정산·매도수량·실현손익·매수수량) | CRITICAL |
| S2 | 내부 정합성 | `shares` == `sharesSeries[-1]` | CRITICAL |
| S3 | 현재가 교차검증 | 대시보드(네이버) 종가 ↔ 야후 파이낸스. **겹치는 날짜만** 비교 | WARNING |

- S1·S2 는 저장 데이터만으로 **완전 결정적**(외부 의존 0).
- S3 는 외부 무료 소스라 도달 실패·겹치는 날짜 없음은 `UNVERIFIABLE`(FAIL 아님).
- 옵션: `--company sinokor`, `--no-xcheck`(S3 생략)

!!! warning "보유수량을 거래원장에서 재계산하지 않는다"
    무상증자·액면분할·원장 이전 기초보유 때문에 독립 재현이 불가능해 **오탐**이 납니다.
    S1(요약↔종목합)으로 집계 오류를 잡는 것으로 갈음합니다.

---

## ⑤ `cash_screen.py` — 현금 '화면' 정합성

이 시스템에서 **가장 중요한 검사**이고, 다른 넷과 성격이 다릅니다.
저장된 값이 아니라 **화면에 찍히는 문자열**을 검사합니다.

### 무엇을 어떻게 보나

1. **화면값 추출** — 자금관리포털의 `데이터수집서버/scripts/verify-cash-consistency.js` 를
   `node <script> --all --json <out>` 으로 실행합니다.
   이 스크립트는 브라우저 없이 실제 `app.js` 를 그대로 돌려 화면 문자열을 뽑습니다.
   *검증 대상이 '렌더링 결과'이므로 화면 코드를 실행하는 것 자체가 검사의 목적입니다.*
2. **기대값 독립 재계산** — 화면 코드를 재사용하지 않고, 스냅샷 원자료
   (`snap/assets/{회사}.json` 의 통화별 잔액·환율)에서 총 보유현금을 파이썬으로 다시 계산합니다.
3. **두 원자료 교차대조** — `cash-detail`(은행 명세 집계)의 통화별 원금과
   `assets`(자금일보)의 통화별 잔액이 일치하는지 확인합니다.

### 판정

| 조건 | 결과 |
| --- | --- |
| 화면 4값 상호 불일치 / 화면값 ≠ 독립 재계산값 / 두 원자료 원금 불일치 | `FAIL` (CRITICAL) |
| node 실행 불가 · 스냅샷 없음 | `UNVERIFIABLE` (원칙 ③) |

### 산출 지표 7개

- `cash_screen_group` · `cash_screen_{회사}` — 4개 (계열 합산 + 3사)
- `cash_source_match_{회사}` — 3개

### 반드시 지켜야 할 두 가지

!!! danger "전 기준일을 훑는다 / 화면 코드를 실행한다"
    - **전 기준일**: 2026-08-21 장애는 과거 기준일에서만 어긋났습니다.
      '최신 1행'만 보는 검사로는 구조적으로 검출 불가입니다.
    - **화면 코드 실행**: 저장 데이터는 멀쩡했고 화면 계산만 틀렸습니다.
      데이터만 보는 검사로는 잡히지 않습니다.

- 단독 실행:
  ```bat
  py checks\metrics\cash_screen.py --config config\metrics.yaml --snap-dir snapshots\manual --out reports\_cash_screen.json
  ```
- node 종료코드 `1` 은 '불일치 있음'(정상 동작)이고, `2` 이상이 실행 실패입니다.
