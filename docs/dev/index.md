# 개발자 문서

프로그램을 **고치거나 늘리는 사람**을 위한 문서입니다.
쓰는 방법은 [사용자 매뉴얼](../manual/index.md)에 있습니다.

!!! abstract "먼저 읽을 것"
    [설계 원칙과 개발 규칙](conventions.md) — 이 다섯 원칙을 깨는 변경은 되돌려야 합니다.
    기능을 더하기 전에 반드시 확인하십시오.

## 지도

| 문서 | 다루는 것 |
| --- | --- |
| [구조와 데이터 흐름](architecture.md) | 원천 → 저장 → 화면 3층 구조, 실행 파이프라인, 의존 관계 |
| [설계 원칙과 개발 규칙](conventions.md) | 다섯 원칙 · 언어/시간/시크릿 규칙 · 금지 사항 |
| [검사 프로그램 5종](modules.md) | `compare` `source_compare` `bond_verify` `stock_verify` `cash_screen` 상세 |
| [결과 JSON 스키마](result-schema.md) | `make_result` 필드 정의, 병합 규칙 |
| [스냅샷 규약](snapshots.md) | 파일명 규칙, 무엇을 언제 남기는가 |
| [사후 재검증과 현금 재검증](recheck.md) | `recheck.py` · `cash_recheck.py` 의 동작과 지문 구조 |
| [대시보드 생성기](dashboard.md) | `build_dashboard.py` 가 HTML 을 만드는 방식 |
| [설정 레퍼런스](config-reference.md) | `metrics.yaml` 전체 필드 |
| [폴더 구조](repo-layout.md) | 어떤 파일이 어디에 있는가 |
| [검사 항목 추가하기](extending.md) | 지표·회사를 늘리는 절차와 함정 |
| [문서 자가 검증](self-check.md) | 이 문서가 실제 시스템과 어긋나지 않게 지키는 장치 |

## 개발 환경

| | |
| --- | --- |
| 언어 | Python 3.11+ (표준 라이브러리 우선, 외부 의존성은 `requirements.txt` 고정) |
| 실행 | Git Bash (`run_verification.sh`) — Windows 에서는 `run_verification.cmd` 가 감싸서 호출 |
| 외부 의존 | `requests` · `PyYAML` — 그리고 현금 화면 검사에 **node** (포털 화면 코드를 그대로 실행) |
| 시간 | 내부 계산은 UTC, 표시·리포트는 Asia/Seoul. **타임존 없는(naive) datetime 금지** |
| 시크릿 | `.env` 에만 둔다. 코드·yaml 에 직접 쓰지 않는다 |
| 로그·주석 | 한국어 |

!!! warning "이 PC 콘솔은 cp949 입니다"
    `✔`·`🔴` 같은 문자를 그대로 `print` 하면 `UnicodeEncodeError` 로 죽습니다.
    콘솔에 내보내는 스크립트는 stdout 을 UTF-8 로 다시 열거나, ASCII 한 줄만 내십시오
    (`cash_recheck.py` 의 `RESULT: ...` 방식).
