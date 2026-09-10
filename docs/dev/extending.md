# 검사 항목 추가하기

## 경우 1 — 회사를 추가한다

`config/metrics.yaml` 의 **두 곳**에 한 줄씩 넣으면 끝입니다. 코드는 고치지 않습니다.

```yaml
source_verification:
  companies:
    - { key: 새회사키, code: 회사코드, name: "표시이름" }   # 원천 대비·채권·주식

cash_screen:
  companies:
    - { key: 새회사키, name: "표시이름" }                   # 현금 화면 검사
```

내부 정합성(`branch_totals_*` · `cash_bycur_*`)은 `metrics:` 배열에 항목을 복사해
회사 필터(`company=eq.새회사키`)만 바꿔 주면 됩니다.

## 경우 2 — 내부 정합성 지표를 추가한다

`metrics:` 배열에 항목 하나를 선언합니다. 코드 수정 없이 동작합니다.

```yaml
- id: 새지표_sinokor
  name: "새 지표 이름 (장금)"
  severity: CRITICAL
  type: internal_consistency
  dashboard:
    auth_env: "SUPABASE_SERVICE_ROLE_KEY"
    api_key_env: "SUPABASE_SERVICE_ROLE_KEY"
    total_endpoint: "${SUPABASE_URL}/rest/v1/..."
    parts_endpoint: "${SUPABASE_URL}/rest/v1/..."
    total_path: "$[0].총계필드"
    parts_path: "$[0].부분[*].값"
  tolerance_type: absolute
  tolerance: 1
```

## 경우 3 — 원천 대비 검사를 새로 만든다

새 스크립트를 `checks/metrics/` 에 만들고 `run_verification.sh` 에 한 줄 추가합니다.
아래를 **반드시** 지키십시오.

1. **기대값은 원천에서 독립 재계산** — 포털·수집기 코드를 import 하지 않는다 (원칙 ②)
2. **판정은 `common/compare.py`** — 직접 `if abs(a-b) < 1` 같은 걸 쓰지 않는다
3. **결과는 `common/result.py` 의 `make_result()`** — 스키마를 손으로 만들지 않는다
4. **원천 호출 전에 포털 값 스냅샷 먼저** — 그래야 [사후 재검증](recheck.md)이 가능해진다
5. **외부 실패는 `UNVERIFIABLE`** — `FetchError` 를 잡아 `FAIL` 로 바꾸지 않는다
6. **단독 실행 가능** — `--config` · `--snap-dir` · `--out` 인자를 갖춘다

```python
#!/usr/bin/env python3
"""새 검사 — 무엇을 왜 보는지 여기에 적는다."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import result as R
from common import samsapi
from common.compare import compare
from common.errors import FetchError
from common.snapshot import save_snapshot

CATEGORY = "metrics"
```

## 화면 지표를 추가할 때의 두 함정

!!! danger "이 둘을 피하지 못하면 만들 이유가 없습니다"
    **① 저장 데이터만 보기**
    화면 계산의 오류는 저장 데이터만 봐서는 잡히지 않습니다.
    2026-08-21 장애 때 Supabase 데이터는 완전히 멀쩡했습니다.
    → 화면 코드를 **실제로 실행**해 렌더링 결과를 비교해야 합니다.

    **② 최신 1행만 보기**
    과거 기준일에서만 나타나는 오류는 최신 1행만 봐서는 **구조적으로** 검출 불가입니다.
    → **전 기준일**을 훑어야 합니다 (현재 회사별 360건).

## 되살릴 수 있게 만들 것인가

새 검사를 만들 때 먼저 정해야 합니다.

| 판단 | 필요한 것 |
| --- | --- |
| 사후 재검증 대상으로 삼는다 | 포털 쪽 원자료를 스냅샷에 남기고, `recheck.py` 의 `HANDLERS` 에 접두어와 핸들러를 등록 |
| 대상이 아니다 | 그 사유를 코드 주석과 문서에 적는다 (예: 주식 현재가 교차검증, 현금 화면 검사) |

## 추가한 뒤 확인

```bat
cd /d <검증시스템 폴더>

py checks\metrics\새검사.py --config config\metrics.yaml --snap-dir snapshots\manual --out reports\_새검사.json
run_verification.cmd

py docs\verify_manual_facts.py
```

마지막 줄이 중요합니다 — 항목 수가 바뀌면 [문서 자가 검증](self-check.md)이 어긋납니다.
**문서의 숫자도 함께 고치십시오.**
