# 개발자 문서

**만든 사람이 없어도 유지보수·인수인계가 되도록** 이 프로그램의 구조·데이터·배포·운영 방법을
적어 둔 문서입니다. 쓰는 방법은 [사용자 매뉴얼](../manual/index.md)에 따로 있습니다.

!!! abstract "인수인계 받으셨다면 이 순서로"
    1. [구조와 데이터 흐름](architecture.md) — 무엇을 왜 이렇게 만들었나
    2. [설치와 배포](deploy.md) — 어디서 어떻게 도는가
    3. [운영과 인수인계](handover.md) — 매일·매년 무엇을 해야 하는가
    4. [설계 원칙과 개발 규칙](conventions.md) — **깨면 안 되는 다섯 가지**

## 지도

### 시스템

| 문서 | 다루는 것 |
| --- | --- |
| [구조와 데이터 흐름](architecture.md) | 원천 → 저장 → 화면 3층 구조, 실행 파이프라인, 공통 모듈, 속도제한 대비 |
| [데이터와 접근 권한](data.md) | 어떤 데이터를 어디서 읽고 무엇을 남기나, 접속 키, 권한 범위 |
| [설치와 배포](deploy.md) | 다른 PC로 옮기는 절차, 예약작업 등록, 멈추는 법 |
| [운영과 인수인계](handover.md) | 매일 할 일, 해마다 할 일, 미리 알아 둘 함정 |

### 코드

| 문서 | 다루는 것 |
| --- | --- |
| [설계 원칙과 개발 규칙](conventions.md) | 다섯 원칙 · 언어/시간/시크릿 규칙 · 금지 사항 |
| [검사 프로그램 5종](modules.md) | `compare` `source_compare` `bond_verify` `stock_verify` `cash_screen` 상세 |
| [결과 JSON 스키마](result-schema.md) | `make_result` 필드 정의, 병합 규칙 |
| [스냅샷 규약](snapshots.md) | 파일명 규칙, 무엇을 언제 남기는가 |
| [사후 재검증과 현금 재검증](recheck.md) | `recheck.py` · `cash_recheck.py` 의 동작과 지문 구조 |
| [대시보드 생성기](dashboard.md) | `build_dashboard.py` 가 HTML 을 만드는 방식 |
| [설정 레퍼런스](config-reference.md) | `metrics.yaml` 전체 필드 |
| [폴더 구조](repo-layout.md) | 어떤 파일이 어디에 있는가, 외부 프로젝트 의존 |
| [검사 항목 추가하기](extending.md) | 지표·회사를 늘리는 절차와 함정 |
| [문서 자가 검증](self-check.md) | 이 문서가 실제 시스템과 어긋나지 않게 지키는 장치 |

## 한눈에

| | |
| --- | --- |
| 하는 일 | 포털 화면 숫자가 원천 자료와 같은지 매일 자동 대조 (현재 36개 항목) |
| 도는 곳 | Windows PC 1대 (서버 없음). 작업 스케줄러가 평일 09:10 실행, 1회 35초 |
| 언어 | Python 3.11+ · 외부 의존성 4개(`requests` `PyYAML` `jsonpath-ng` `python-dotenv`) |
| 함께 필요한 것 | Git Bash · node · 같은 PC의 **자금관리포털** ([설치와 배포](deploy.md)) |
| 결과물 | `reports\dashboard.html` (달력형, 인터넷 없이 열림) |
| 데이터가 나가는 곳 | 없음 — 전부 그 PC 안에만 남습니다 |
| 시간 | 내부 계산 UTC, 표시 Asia/Seoul. **naive datetime 금지** |
| 시크릿 | `.env` 에만. 코드·yaml·문서에는 **이름만** |
| 로그·주석 | 한국어 |

!!! warning "이 PC 콘솔은 cp949 입니다"
    `✔`·`🔴` 같은 문자를 그대로 `print` 하면 `UnicodeEncodeError` 로 죽습니다.
    콘솔에 내보내는 스크립트는 stdout 을 UTF-8 로 다시 열거나, ASCII 한 줄만 내십시오
    (`cash_recheck.py` 의 `RESULT: ...` 방식).
