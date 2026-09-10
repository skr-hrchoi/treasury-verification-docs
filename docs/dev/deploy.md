# 설치와 배포 — 다른 PC로 옮기기

이 프로그램은 **서버가 아니라 PC 한 대에서** 돕니다. 웹으로 배포되는 것이 없고,
Windows 작업 스케줄러가 정해진 시각에 실행하는 구조입니다.
담당자가 바뀌거나 PC를 교체할 때 이 문서대로 하면 그대로 살아납니다.

## 무엇이 필요한가

| 항목 | 조건 | 확인 |
| --- | --- | --- |
| Windows PC | 평일 09:10 에 **켜져 있고 로그인**되어 있어야 함 | 절전·자동잠금이 실행을 막지 않는지 |
| Python | 3.11 이상 | `py --version` |
| Git Bash | `run_verification.cmd` 가 `bash.exe` 를 찾아 씀 | `C:\Program Files\Git\bin\bash.exe` 존재 |
| node | 현금 화면 검사가 포털 화면 코드를 실행할 때 필요 | `node --version` |
| 사내망 | 원천(SamsApi) 도달 가능 (VPN 포함) | 사내망 연결 |
| 인터넷 | Supabase 조회, 주식 현재가 교차검증 | |
| **자금관리포털** | **같은 PC에 함께 있어야 함** (아래 참조) | |

!!! danger "자금관리포털과 한 몸입니다"
    현금 화면 검사는 자금관리포털의 스냅샷 파일을 읽고, 그 프로젝트의
    `verify-cash-consistency.js` 를 node 로 **실제 실행**합니다.
    반대로 포털의 자동배포가 이 프로그램의 `cash_recheck.py` 를 부릅니다.

    두 폴더는 **같은 부모 폴더 아래 나란히** 있어야 하고, 서로를 상대경로로 찾습니다.
    한쪽만 옮기면 현금 검사 7건이 통째로 검증불가가 됩니다. 자세한 연결 지점은
    [폴더 구조](repo-layout.md#_2)를 보십시오.

## 설치 절차

**1. 폴더를 옮깁니다**

검증시스템 폴더 전체를 새 PC의 같은 위치 관계로 복사합니다
(자금관리포털과 나란히). `reports\` · `snapshots\` · `logs\` 는 과거 기록이라
옮기지 않아도 동작합니다. 다만 대시보드 달력이 비어 있는 상태로 시작합니다.

**2. 파이썬 의존성을 설치합니다**

```bat
cd /d <검증시스템 폴더>
py -m pip install -r requirements.txt
```

`requests` · `PyYAML` · `jsonpath-ng` · `python-dotenv` 네 개입니다.

**3. 접속 키를 넣습니다**

`.env` 파일을 만들고 아래 **세 개**를 채웁니다. 값은 사내 인수인계 문서에 있습니다.

```ini
COMPANY_API_KEY=            # 사내 자금일보 API 키 (X-API-Key 헤더)
SUPABASE_URL=               # 포털 데이터 저장소 주소
SUPABASE_SERVICE_ROLE_KEY=  # 포털 데이터 조회 키
```

!!! warning "`.env` 는 절대 저장소에 올리지 않습니다"
    `SUPABASE_SERVICE_ROLE_KEY` 는 접근 제한을 통과하는 키입니다.
    파일 밖으로 복사하지 말고, 코드·yaml·문서에 적지 마십시오.

**4. 손으로 한 번 돌려 봅니다**

```bat
run_verification.cmd
```

1분 안에 끝나고 `reports\latest.json` 과 `reports\dashboard.html` 이 생기면 정상입니다.
검증불가가 여러 건이면 [점검표](../manual/troubleshoot.md#64)를 보십시오.

**5. 작업 스케줄러에 등록합니다**

관리자 권한 명령 프롬프트에서:

```bat
schtasks /create /tn "자금관리포털_대시보드검증" ^
  /tr "\"<검증시스템 폴더>\run_verification.cmd\" auto" ^
  /sc weekly /d MON,TUE,WED,THU,FRI /st 09:10 /rl LIMITED /f
```

- `auto` 인자가 **중요합니다.** 이게 없으면 끝에서 `pause` 로 멈춰 창이 남습니다.
- 등록 후 작업 스케줄러에서 **「가장 높은 수준의 권한으로 실행」은 필요 없고**,
  로그인 상태에서만 실행되도록 두는 것이 현재 설정입니다.

**6. 현금 재검증 연결을 확인합니다**

자금관리포털의 `홈페이지배포\auto-deploy.ps1` 이 이 프로그램의 `checks\cash_recheck.py` 를
부릅니다. 포털 쪽 예약작업(`TreasuryDashboard_AutoDeploy`, 평일 매시 05분)이 살아 있는지 보고,
로그에 아래 줄이 남는지 확인합니다.

```
검증시스템 현금 재검증 — RESULT: status=unchanged (exit=0)
```

## 잘 옮겨졌는지 확인하는 법

```bat
py docs\verify_manual_facts.py
```

문서에 적힌 사실 26가지를 실제 시스템과 대조합니다.
경로·예약작업·설정값이 어긋나면 여기서 걸립니다. → [문서 자가 검증](self-check.md)

## 잠시 멈추거나 되돌리려면

| 하고 싶은 일 | 방법 |
| --- | --- |
| 오늘만 안 돌게 | 작업 스케줄러에서 해당 작업 **사용 안 함** |
| 완전히 중지 | `schtasks /delete /tn "자금관리포털_대시보드검증" /f` |
| 현금 재검증만 끄기 | 포털 `auto-deploy.ps1` 의 해당 블록을 주석 처리 (배포는 계속됨) |
| 결과만 초기화 | `reports\` · `snapshots\` 를 비움 (설정·코드는 그대로) |

검증기는 **읽기 전용**이라 멈춰도 포털 데이터에는 영향이 없습니다.
다만 멈춘 동안은 숫자가 틀려도 아무도 모릅니다.
