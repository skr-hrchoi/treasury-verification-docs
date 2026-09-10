# 설정 레퍼런스 (`config/metrics.yaml`)

원칙 ⑤ — **검사 대상은 코드가 아니라 이 파일에 선언한다.**

## 파일 구성

```yaml
defaults:              # 공통 기본값
source_verification:   # 원천 대비 검증 (현금·채권·주식)
metrics:               # 내부 정합성 지표 배열 (compare.py 가 읽음)
cash_screen:           # 현금 화면 검사
```

## `defaults`

| 키 | 현재 값 | 설명 |
| --- | --- | --- |
| `timezone` | `Asia/Seoul` | 표시·리포트 기준 |
| `freshness_max_delay_minutes` | `60` | 신선도 검사용(아직 미사용) |
| `anomaly_threshold_relative` | `0.5` | 이상치 검사용(아직 미사용) |

## `source_verification`

```yaml
source_verification:
  samsapi:
    host: "<사내 자금일보 API 호스트>"   # 사내망 전용 · 실제 값은 사내 문서 참조
    port: <포트>
    api_key_env: "COMPANY_API_KEY"     # 환경변수 '이름' (값 아님)
  supabase:
    url_env: "SUPABASE_URL"
    key_env: "SUPABASE_SERVICE_ROLE_KEY"
    table: "cash_detail"
  tolerance: 1
  bond_tolerance_abs: 1
  bond_tolerance_rel: 0.001
  stock_summary_tol_abs: 1
  stock_price_tol_rel: 0.025
  stock_price_xcheck: true
  companies:
    - { key: sinokor, code: SNKO, name: "장금" }
    - { key: heung,   code: HALK, name: "흥아" }
    - { key: hansung, code: HSLI, name: "한성" }
```

| 키 | 쓰는 곳 | 설명 |
| --- | --- | --- |
| `samsapi.host` / `port` | `common/samsapi.py` | 사내망 전용 주소 |
| `*_env` | 전부 | **환경변수 이름**만 적는다. 값은 `.env` 에 |
| `tolerance` | `source_compare` | 현금 총계·시재 (원) |
| `bond_tolerance_abs` | `bond_verify` | 매입금액·경과이자 (현지통화) |
| `bond_tolerance_rel` | `bond_verify` | 평가단가 (0.001 = 0.1%) |
| `stock_summary_tol_abs` | `stock_verify` | 요약↔종목합 |
| `stock_price_tol_rel` | `stock_verify` | 현재가 교차검증 (0.025 = 2.5%) |
| `stock_price_xcheck` | `stock_verify` | `false` 면 S3 생략 |
| `companies[]` | 전부 | `key`(내부 키) · `code`(SamsApi 회사코드) · `name`(표시명) |

## `metrics[]` — 내부 정합성 지표

`compare.py` 가 읽는 배열입니다. 항목 하나가 지표 하나입니다.

```yaml
- id: branch_totals_sinokor
  name: "지사별 통장합계 정합성 (장금)"
  severity: CRITICAL
  type: internal_consistency
  dashboard:
    auth_env: "SUPABASE_SERVICE_ROLE_KEY"
    api_key_env: "SUPABASE_SERVICE_ROLE_KEY"
    total_endpoint: "${SUPABASE_URL}/rest/v1/branch_totals?company=eq.sinokor&order=effective_date.desc&limit=1&select=total_krw,branches"
    parts_endpoint: "${SUPABASE_URL}/rest/v1/branch_totals?company=eq.sinokor&order=effective_date.desc&limit=1&select=total_krw,branches"
    total_path: "$[0].total_krw"
    parts_path: "$[0].branches[*].balanceKRW"
  tolerance_type: absolute
  tolerance: 1
```

| 키 | 설명 |
| --- | --- |
| `id` | 지표 id. `check_id` 는 `metrics.<id>` 가 된다 |
| `name` | 대시보드 표시 이름 |
| `severity` | `CRITICAL` / `WARNING` / `INFO` |
| `type` | 현재는 `internal_consistency` |
| `dashboard.total_endpoint` / `parts_endpoint` | 전체합·부분합을 가져올 URL. `${ENV}` 는 환경변수로 치환 |
| `dashboard.total_path` / `parts_path` | 응답에서 값을 뽑는 경로 |
| `tolerance_type` | `exact` / `absolute` / `relative` |
| `tolerance` | 허용 오차. **코드에 하드코딩 금지** |

!!! tip "Supabase 는 배열로 응답합니다"
    최신 1행을 `order=...desc&limit=1` 로 고른 뒤 `$[0]` 으로 접근하는 것이 관례입니다.

### 값 획득 방식 (설계상 지원)

| 방식 | 설명 |
| --- | --- |
| `value_path` | 응답에서 **이미 계산된 값**을 JSONPath 로 추출 |
| `compute` | 원시 레코드에서 **독립 재계산** (`op`: `count`/`sum`/`avg`/`min`/`max`/`distinct_count`/`rate`) |

원칙 ②에 따라 가능하면 `compute` 를 씁니다. 엔진 동작은 `tests/metrics.test.yaml` 오프라인 픽스처로 검증돼 있습니다.

## `cash_screen`

```yaml
cash_screen:
  portal_dir: ""                # 비우면 검증시스템 상위의 '자금관리포털' 을 자동 사용
  tolerance: 100000000          # 화면 표시가 억원 반올림이므로 1억원 허용
  source_tolerance: 1           # 통화별 원금(두 소스) 대조는 원 단위
  companies:
    - { key: sinokor, name: "장금상선" }
    - { key: heung,   name: "흥아라인" }
    - { key: hansung, name: "한성라인" }
```

!!! warning "`tolerance: 100000000` 을 낮추지 마십시오"
    화면이 **억 단위로 반올림해서** 보여주기 때문에 1억 원 미만 차이는 화면상 구분되지 않습니다.
    이 값을 낮추면 반올림 때문에 매일 실패가 납니다.
    원 단위 정확도는 `source_vs_dashboard_*`(±1원)가 따로 지킵니다.

## 시크릿 (`.env`)

| 키 | 용도 |
| --- | --- |
| `COMPANY_API_KEY` | SamsApi `X-API-Key` |
| `SUPABASE_URL` · `SUPABASE_SERVICE_ROLE_KEY` | 포털 저장 데이터 조회 (RLS 우회) |

`.env` 는 git 에서 제외됩니다. 값을 코드·yaml·문서에 옮겨 적지 마십시오.
