# 8. 설정 변경 방법

## 8.1 설정 파일

| 파일 | 무엇을 정하나 |
| --- | --- |
| `config\metrics.yaml` | 검사 대상 지표, 허용 오차, 심각도, 회사 목록, 원천/포털 접속 방법 |
| `config\security_targets.yaml` | 보안 검사 대상 — 보안 검사는 아직 만들지 않아 쓰이지 않습니다 |
| `.env` | 접속 키·토큰. 값은 이 파일에만 두고 코드·yaml 에 직접 쓰지 않습니다 |

전체 항목 설명은 [설정 레퍼런스](../dev/config-reference.md)에 있습니다.

## 8.2 회사를 추가하려면 {: #82 }

코드를 고칠 필요 없이 `metrics.yaml` 의 **두 곳**에 한 줄씩 추가하면 됩니다.

```yaml
source_verification:
  companies:
    - { key: sinokor, code: SNKO, name: "장금" }
    - { key: heung,   code: HALK, name: "흥아" }
    - { key: hansung, code: HSLI, name: "한성" }
    - { key: 새회사키, code: 회사코드, name: "표시이름" }   # ← 이 한 줄

cash_screen:
  companies:
    - { key: 새회사키, name: "표시이름" }                   # ← 현금 화면 검사에도 추가
```

## 8.3 허용 오차를 바꾸려면

| 설정 이름 | 현재 값 | 무엇의 허용 오차인가 |
| --- | --- | --- |
| `source_verification.tolerance` | `1` | 현금 총계·시재 원천 대비 (원) |
| `source_verification.bond_tolerance_abs` | `1` | 채권 매입금액·경과이자 (현지통화) |
| `source_verification.bond_tolerance_rel` | `0.001` | 채권 평가단가 (0.1%) |
| `source_verification.stock_summary_tol_abs` | `1` | 주식 요약↔종목합 |
| `source_verification.stock_price_tol_rel` | `0.025` | 주식 현재가 교차검증 (2.5%) |
| `cash_screen.tolerance` | `100000000` | 현금 화면 (1억 원 — 화면이 억 단위 반올림 표시이므로) |
| `cash_screen.source_tolerance` | `1` | 두 원자료 통화별 원금 대조 (원) |

오차를 넓히면 대시보드는 조용해지지만 그만큼 **못 잡는 범위**가 생깁니다.
특정 지표가 늘 미세하게 흔들려 시끄러울 때만 올리고, 왜 올렸는지 함께 기록해 두십시오.

## 8.4 바꾸면 안 되는 것

- **검증기가 포털·수집기의 계산 코드를 가져다 쓰는 변경** — 원칙 ②.
  같은 버그를 양쪽에서 반복합니다.
- **AI가 직접 숫자를 비교해 통과/실패를 판정하게 하는 변경** — 원칙 ①.
- **사내망 오류를 FAIL 로 처리하는 변경** — 원칙 ③. 진짜 실패를 못 알아보게 됩니다.
- **새 화면 지표를 '저장 데이터만 보기' 또는 '최신 1행만 보기'로 만드는 것** —
  화면 계산의 오류는 저장 데이터만 봐서는 잡히지 않고,
  과거 기준일에서만 나타나는 오류는 최신 1행만 봐서는 구조적으로 잡을 수 없습니다.
