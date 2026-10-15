# 폴더 구조

```
검증시스템\
│
├─ run_verification.cmd      ← 실행 진입점 (더블클릭용 · 작업 스케줄러가 부르는 것)
├─ run_verification.sh       ← 실제 검증 절차 (Git Bash 로 실행)
├─ CLAUDE.md                 ← 설계 원칙·규칙 (기준 문서)
├─ requirements.txt          ← 외부 의존성 고정
├─ .env                      ← 접속 키 (git 제외 · 외부 공유 금지)
│
├─ config\
│   ├─ metrics.yaml          ← 검사 지표 정의 · 허용 오차 · 회사 목록
│   └─ security_targets.yaml ← 보안 검사 대상 (아직 쓰이지 않음)
│
├─ checks\                   ← 검사 프로그램
│   ├─ metrics\
│   │   ├─ compare.py            내부 정합성 (지사합·통화별합)
│   │   ├─ source_compare.py     현금 총계·시재 원천 대비
│   │   ├─ bond_verify.py        채권 매입금액·평가단가·보유목록
│   │   ├─ stock_verify.py       주식 요약↔종목합·내부정합성·현재가
│   │   └─ cash_screen.py        현금 '화면' 정합성 (전 기준일)
│   ├─ common\
│   │   ├─ samsapi.py            사내 SamsApi 독립 조회 (수집기 코드 미재사용)
│   │   ├─ compare.py            허용 오차 비교 (판정 담당)
│   │   ├─ result.py             표준 결과 레코드
│   │   ├─ snapshot.py           판정 근거 저장
│   │   ├─ http.py               JSON 페치 (file:// 지원)
│   │   ├─ extract.py            응답에서 값 추출
│   │   ├─ errors.py             예외 정의
│   │   └─ timeutil.py           UTC/KST 처리
│   ├─ recheck.py               검증불가 사후 재검증
│   ├─ cash_recheck.py          현금 값 변경 시 현금만 재검증
│   ├─ merge_results.py         부분 결과 합치기
│   ├─ build_dashboard.py       대시보드 HTML 생성
│   ├─ notify.py                결과 알림 (알림 채널 미설정 상태)
│   ├─ backfill.py              과거 리포트 재생성 도구
│   ├─ backfill_bond_bycur.py   과거 리포트를 통화별 채권 기준으로 재생성
│   └─ security\ pipeline\ functional\   ← 아직 껍데기(README만). 실행 목록에서도 주석 처리
│
├─ reports\                  ← 결과 (일자별 JSON · latest.json · dashboard.html) — git 제외
├─ snapshots\                ← 판정 근거 원자료 (시점별 폴더) — git 제외
├─ logs\                     ← cash-recheck.log · notify.log · 현금 지문/판정
├─ tests\                    ← 오프라인 시험 (픽스처 기반)
│
├─ docs\                     ← 변경 기록 · Word 매뉴얼 · 캡처
│   ├─ 자금관리포털_데이터검증시스템_매뉴얼.docx
│   ├─ build_manual.py           Word 매뉴얼 생성기
│   ├─ verify_manual_facts.py    문서 자가 검증 (→ self-check.md)
│   └─ 매뉴얼_캡처\               대시보드 화면 캡처 4장
│
└─ docs-site\                ← 이 문서 사이트 (MkDocs)
    ├─ mkdocs.yml
    ├─ requirements.txt
    └─ docs\
```

## git 에서 제외되는 것

| 대상 | 이유 |
| --- | --- |
| `.env` | 시크릿 |
| `reports/` · `snapshots/` | 실제 금액이 담긴 산출물이고 용량이 큼 (스냅샷 약 30MB) |
| `logs/` | 실행 기록 |

## 외부 프로젝트 의존

이 시스템은 같은 PC 의 **자금관리포털**을 읽습니다.

| 읽는 것 | 쓰는 검사 |
| --- | --- |
| `자금관리포털\홈페이지배포\snap\assets\{회사}.json` | 현금 화면 검사 (기대값 독립 재계산) |
| `자금관리포털\홈페이지배포\snap\cash-detail\{회사}.json` | 현금 화면 검사 (두 소스 대조) |
| `자금관리포털\데이터수집서버\scripts\verify-cash-consistency.js` | 현금 화면 검사 (node 로 실행) |
| `자금관리포털\홈페이지배포\app.js`<br>`자금관리포털\데이터수집서버\public\app.js` | 현금 지문 (화면 코드 해시) |

반대로 자금관리포털의 `홈페이지배포\auto-deploy.ps1` 이
이 시스템의 `checks\cash_recheck.py` 를 호출합니다.

!!! warning "경로가 바뀌면 두 곳을 함께 고쳐야 합니다"
    `cash_screen.py` 의 `portal_dir` 기본값(검증시스템 상위의 `자금관리포털`)과
    `auto-deploy.ps1` 의 `$vsDir`(`..\..\검증시스템`)는 **서로 상대경로로 물려 있습니다.**
    폴더 이름이나 위치를 바꾸면 양쪽 다 확인하십시오.
