# 변경 기록

플러그인에는 버전 번호를 두지 않는다. `main`의 커밋이 곧 버전이다. 여기에는 받는 사람이 알아야 할 변화만 적는다.

## 2026-10-14

- 배포 구조로 정리: 플러그인 마켓플레이스(`.claude-plugin/marketplace.json`)와 플러그인 폴더(`plugins/problem-definition/`)
- frontmatter를 Agent Skills 사양에 맞춤: `argument-hint` 제거, `metadata` 추가
- 출처 파일에서 개인 경로를 지우고 서지 정보로 바꿈
- 검증 스크립트, pre-commit 검증, GitHub Actions 추가
- 후보 모드 추가: 인터뷰 기록에서 문제 정의 후보 3~5개를 뽑아 검증 순서를 낸다 (`references/interviews.md`)
- 심각성 × 보편성 사분면, 대체재 테스트, 발언 등급(한 것·내놓은 것·평가·의향) 추가

## 2026-10-13

- 첫 버전: 초안·대화·검토 모드, 고정 규칙 3개, 성격 진단, 시스템 구조 분석, 한 문장 공식과 7조건
