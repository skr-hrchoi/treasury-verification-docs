# 스냅샷 규약

설계 원칙 ④ — **판정에 쓴 원자료를 그대로 남긴다.**

## 왜 남기나

1. **나중에 되짚기 위해** — "그날 왜 그렇게 판정했나"를 원자료로 확인할 수 있습니다.
2. **검증불가를 되살리기 위해** — 원천이 거절당해도 포털 쪽 값이 남아 있으면
   나중에 그날 기준일로 원천만 다시 불러 [그날의 검증을 재현](recheck.md)할 수 있습니다.

!!! important "순서가 중요합니다"
    검증기는 **원천을 부르기 전에 포털 쪽 값을 먼저 스냅샷으로 저장합니다.**
    원천 호출이 실패해도 증거의 절반은 남습니다. 이 순서를 바꾸면 사후 재검증이 불가능해집니다.

## 파일명 규칙

```
snapshots/{YYYY-MM-DD_HHMM}/{metric_id}_{role}.json
```

`role` 은 `source` · `dashboard` · `dashboard_total` · `dashboard_parts` 등을 씁니다.

### 실제 예 (2026-09-10_0910, 30개)

| 파일 | 남긴 것 |
| --- | --- |
| `bonds_{회사}_source.json` / `bonds_{회사}_dashboard.json` | 채권 원천 응답 / 포털 저장값 |
| `source_vs_dashboard_{회사}_source.json` / `_dashboard.json` | 자금일보 원천 / 포털 현금 |
| `branch_totals_{회사}_dashboard_total.json` / `_dashboard_parts.json` | 전체합 / 부분합 |
| `cash_bycur_{회사}_dashboard_total.json` / `_dashboard_parts.json` | 총계 / 통화별 |
| `stocks_{회사}_dashboard.json` | 주식 저장값 |
| `cash_screen_dashboard.json` / `cash_screen_source.json` / `cash_screen_raw.json` | 화면 추출값 / 원자료 / node 원본 출력 |

## 보관 정책

| 대상 | 규칙 |
| --- | --- |
| 같은 날 여러 번 실행 | 최종 실행본만 남기고 이전 것은 지웁니다 (`run_verification.sh` 의 `find ... -delete`) |
| 현금 재검증 | 이전 재검증본을 정리하고 새 폴더를 만듭니다 (`logs/cash-recheck.log` 에 「이전 재검증본 정리」로 기록) |
| 전체 | git 에서 제외 (`.gitignore`). 용량은 2026-09-10 기준 약 30MB |

## 저장 코드

```python
from common.snapshot import save_snapshot

path = save_snapshot(snap_dir, "source_vs_dashboard_sinokor", "source",
                     url, response, extracted=123456789012.0)
```

반환된 경로를 결과 레코드의 `snapshot_paths` 에 그대로 넣습니다.
대시보드에서 판정 근거를 되짚을 때 이 경로를 씁니다.

!!! warning "스냅샷이 없으면 되살릴 수 없습니다"
    주식 현재가 교차검증과 현금 화면 검사는 **포털 쪽 원자료가 스냅샷에 남지 않아**
    사후 재검증 대상이 아닙니다. 새 검사를 만들 때 이 점을 먼저 결정하십시오 —
    "이 검사는 나중에 되살릴 수 있어야 하는가?"
