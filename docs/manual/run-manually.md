# 7. 손으로 실행하는 방법

## 7.1 가장 쉬운 방법 — 더블클릭

**`run_verification.cmd` 를 더블클릭합니다.**

검은 창이 뜨고 검증이 진행되며, 끝나면 결과 요약과 함께 창이 열린 채 멈춥니다
(아무 키나 누르면 닫힘). 끝나면 대시보드도 함께 갱신됩니다.
전체 1회는 **1분 안에** 끝납니다.

!!! danger "`.sh` 를 직접 더블클릭하지 마십시오"
    `run_verification.sh` 를 직접 더블클릭하면 경로에 공백(「클로드 코드」)이 있어
    Windows 가 경로를 잘라 읽고 실패합니다. 반드시 **`.cmd`** 파일을 쓰십시오.

## 7.2 명령으로 실행 — 부분만 다시 보고 싶을 때

명령 프롬프트에서 검증시스템 폴더로 이동한 뒤 실행합니다.

```bat
cd /d <검증시스템 폴더>
```

| 하고 싶은 일 | 명령 |
| --- | --- |
| 전체 검증 | `run_verification.cmd` |
| 현금 화면만 다시 검사 (값이 바뀐 경우에만) | `py checks\cash_recheck.py` |
| 현금 화면 강제 재검사 (값이 안 바뀌어도) | `py checks\cash_recheck.py --force` |
| 현금 화면 검사 단독 실행 | `py checks\metrics\cash_screen.py --config config\metrics.yaml --snap-dir snapshots\manual --out reports\_cash_screen.json` |
| 채권 검사만, 특정 회사만 | `py checks\metrics\bond_verify.py --config config\metrics.yaml --snap-dir snapshots\manual --out reports\_bonds.json --company sinokor` |
| 주식 검사만 (외부 교차검증 생략) | `py checks\metrics\stock_verify.py --config config\metrics.yaml --snap-dir snapshots\manual --out reports\_stocks.json --no-xcheck` |
| 검증불가 사후 재검증만 (30일치, 실제로 바꾸지는 않음) | `py checks\recheck.py --days 30 --dry-run` |
| 대시보드만 다시 그리기 | `py checks\build_dashboard.py` |
| 이 문서의 사실관계 자가 검증 | `py docs\verify_manual_facts.py` |

### `cash_recheck.py` 의 종료 코드

| 코드 | 뜻 |
| --- | --- |
| `0` | 정상 (변경 없음 또는 재검증 통과) |
| `1` | 현금 검사에 실패(FAIL) 있음 |
| `2` | 재검증 실행 자체가 실패 |

!!! tip "표준출력 한 줄로 판정합니다"
    `cash_recheck.py` 는 콘솔 한글 깨짐과 무관하게 읽히도록
    `RESULT: status=unchanged` 같은 **ASCII 한 줄**을 마지막에 냅니다.
    자동배포(PowerShell)는 이 줄만 보고 결과를 기록합니다.
