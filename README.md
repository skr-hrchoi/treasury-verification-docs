# 자금관리포털 데이터 검증 시스템 — 개발 문서

포털 화면의 숫자가 원천 자료와 맞는지 매일 자동으로 대조하는 감시 장치의
**운영 매뉴얼 + 개발자 문서**입니다. MkDocs Material 로 만들고 GitHub Pages 로 발행합니다.

📖 **문서 보기**: https://skr-hrchoi.github.io/treasury-verification-docs/

## 공개 기준

이 저장소는 공개입니다. 조직의 다른 `*-docs` 저장소와 같은 기준을 따릅니다.

| 싣는 것 | 싣지 않는 것 |
| --- | --- |
| 설계·구조·동작 원리 | 회사별 실제 보유 금액 |
| 검사 항목 정의와 허용 오차 | 사내 서버 주소·포트 |
| 운영 절차·장애 대응·변경 이력 | 접속 키·토큰 (`.env` 값) |
| 화면 사용법 | 절대 경로 (`D:\...`) |

- 문서에 나오는 금액과 **화면 캡처는 전부 지어낸 예시 값**입니다.
  실제 대시보드 생성기에 가짜 데이터를 먹여 만들었습니다 → `tools/make_demo_dashboard.py`
- 사내 주소는 「사내 문서 참조」로 대신합니다.
- 실제 수치는 사내 대시보드(`reports\dashboard.html`)와 사내 Word 매뉴얼에서 봅니다.

> 문서를 고칠 때 실제 금액·사내 주소가 섞여 들어가지 않게 하십시오.
> 확인 명령: `py tools\check_public_safe.py`

## 로컬에서 보기

```bat
py -m pip install -r requirements.txt      :: 처음 한 번만
py -m mkdocs serve                          :: http://127.0.0.1:8000 실시간 미리보기
py -m mkdocs build --strict                 :: site\ 로 정적 HTML 생성 (링크·앵커 검증 포함)
```

## 발행

`main` 에 push 하면 GitHub Actions 가 빌드해 GitHub Pages 로 올립니다
(`.github/workflows/deploy.yml`). 최초 1회만 저장소 설정에서
**Settings → Pages → Source: GitHub Actions** 로 지정하면 됩니다.

## 구성

```
docs-site\
├─ mkdocs.yml              사이트 설정 (테마·내비게이션)
├─ requirements.txt        mkdocs-material 버전 고정
├─ .github\workflows\      GitHub Pages 자동 발행
├─ tools\
│   ├─ make_demo_dashboard.py  예시 데이터 대시보드 (캡처용)
│   └─ check_public_safe.py    공개 금지 정보가 섞였는지 검사
└─ docs\
    ├─ index.md            홈
    ├─ manual\             사용자 매뉴얼 9장
    ├─ dev\                개발자 문서 11편
    ├─ changelog.md        변경 이력
    └─ assets\             스타일 + 화면 캡처(예시 데이터)
```

## 문서를 고칠 때

1. `docs\` 아래 Markdown 을 고칩니다.
2. **사실(숫자·시각·경로)을 바꿨으면** 검증시스템 쪽 확인 프로그램도 함께 고칩니다.
   ```bat
   py <검증시스템 폴더>\docs\verify_manual_facts.py
   ```
3. 공개 안전성 확인 후 push 합니다.
   ```bat
   py tools\check_public_safe.py && py -m mkdocs build --strict
   ```

소스 코드는 사내에서 관리하며 이 저장소에는 문서만 있습니다.
