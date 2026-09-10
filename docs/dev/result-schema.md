# 결과 JSON 스키마

모든 검사는 이 스키마로 결과를 내고, `merge_results.py` 가
`reports/{YYYY-MM-DD_HHMM}.json` 및 `reports/latest.json` 으로 합칩니다.

## 파일 형태

```json
{
  "run_at": "2026-09-10_0910",
  "results": [
    {
      "check_id": "metrics.source_vs_dashboard_sinokor",
      "category": "metrics",
      "status": "PASS",
      "severity": "CRITICAL",
      "expected": 123456789012.0,
      "actual": 123456789012,
      "tolerance": 1,
      "detail": "[장금] 총 보유현금 원천(SamsApi 2026-09-09) vs 대시보드 — 차이=0.0 / 허용 절대오차 ±1 → 일치",
      "snapshot_paths": [
        "snapshots/2026-09-10_0910/source_vs_dashboard_sinokor_dashboard.json",
        "snapshots/2026-09-10_0910/source_vs_dashboard_sinokor_source.json"
      ]
    }
  ]
}
```

## 필드

| 필드 | 값 | 설명 |
| --- | --- | --- |
| `check_id` | `metrics.<지표id>` | 지표 식별자. 문의·검색·회귀 추적의 키 |
| `category` | `metrics` \| `security` \| `pipeline` \| `functional` | 지금은 전부 `metrics` |
| `status` | `PASS` \| `FAIL` \| `UNVERIFIABLE` | 판정 |
| `severity` | `CRITICAL` \| `WARNING` \| `INFO` | 심각도 |
| `expected` | 수 \| `null` | 원천에서 재계산한 기대값. 금액 비교가 아닌 항목은 `null` |
| `actual` | 수 \| `null` | 포털의 실측값 |
| `tolerance` | 수 \| `null` | 판정에 쓴 허용 오차 |
| `detail` | 문자열 | **사람이 읽는 판정 근거.** 몇 건을 봤는지·어느 기준일인지·허용 오차가 얼마인지 |
| `snapshot_paths` | 문자열 배열 | 판정에 쓴 원자료 경로 ([스냅샷 규약](snapshots.md)) |

!!! tip "`detail` 은 대충 쓰면 안 됩니다"
    실패했을 때 사람이 가장 먼저 읽는 문장입니다.
    「무엇과 무엇을, 몇 건, 어느 기준일로, 허용 오차 얼마로 비교해 어떤 차이가 났는지」를
    한 줄에 담으십시오. 대시보드 상세 표의 마지막 열에 그대로 나옵니다.

## 만드는 방법

```python
from common import result as R

R.make_result(
    "metrics.source_vs_dashboard_sinokor",
    "metrics",
    R.PASS,                    # PASS / FAIL / UNVERIFIABLE
    R.CRITICAL,                # CRITICAL / WARNING / INFO
    detail="[장금] 총 보유현금 원천(SamsApi 2026-09-09) vs 대시보드 — 차이=0",
    expected=123456789012.0,
    actual=123456789012,
    tolerance=1,
    snapshot_paths=[...],
)
```

`make_result()` 는 `status`·`severity`·`category` 를 `assert` 로 검사합니다.
오타가 나면 조용히 통과하지 않고 **그 자리에서 죽습니다.**

## 사후 재검증이 붙이는 필드

[사후 재검증](recheck.md)으로 정정된 항목에는 아래가 추가됩니다.

| 필드 | 설명 |
| --- | --- |
| `original_status` | 원래 판정 (대개 `UNVERIFIABLE`) |
| `rechecked_at` | 정정 시각 |

대시보드는 이 필드를 보고 **↺ 사후 재검증 (날짜)** 꼬리표를 붙입니다.
정정 사실을 숨기지 않는 것이 규칙입니다.

## 현금 재검증이 붙이는 필드

[현금 재검증](recheck.md#cash)이 그날 리포트의 현금 7건만 갈아끼울 때,
**갈아끼우지 않은 나머지 항목**에는 `carried_from`(원래 실행 시각)이 남습니다.
그 값이 언제 실행분인지 구분하기 위해서입니다.

## 병합 규칙 (`merge_results.py`)

입력 파일은 두 형태를 모두 허용합니다.

- `{"run_at": ..., "results": [...]}` — 표준 래퍼
- `[ {...}, {...} ]` — 결과 배열만

```bat
py checks\merge_results.py --run-at 2026-09-10_0910 --out reports\2026-09-10_0910.json reports\_*.json
```

병합이 실패해도 실행 전체를 죽이지 않고 빈 결과 파일을 남기도록 되어 있습니다
(`run_verification.sh` 의 `||` 분기).
