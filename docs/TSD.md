# TSD — defining-problems 스킬

작성일 2026-10-13 · PRD: [PRD.md](PRD.md)

## 1. 파일 구성

```
problem-definition/                              저장소 = 플러그인 마켓플레이스
├── .claude-plugin/marketplace.json              마켓플레이스 목록 (플러그인 1개)
├── plugins/problem-definition/                  플러그인 루트. 설치하면 이 폴더만 복사된다
│   ├── .claude-plugin/plugin.json               version을 두지 않는다 (커밋마다 새 버전)
│   └── skills/defining-problems/
│       ├── SKILL.md                             절차와 고정 규칙. 호출 시 전체가 컨텍스트에 들어감
│       ├── references/
│       │   ├── interviews.md                    인터뷰 발언 등급, 대체재, 가설 대조, 후보 견주기
│       │   ├── lenses.md                        문제 성격 진단: 유형·4축·고객 관계·수단 출발
│       │   ├── systems.md                       사건→패턴→구조, 시스템 함정 8개, 개입 지점
│       │   ├── quality-bar.md                   좋은 문제 7조건, 가짜 문제, 고쳐 쓰기 예시
│       │   ├── output-template.md               문제 정의서·후보 문서 템플릿
│       │   └── sources.md                       규칙별 출처와 쪽 번호
│       └── evals/                               품질 eval, 트리거 eval
├── docs/PRD.md, TSD.md                          설계 문서 (배포물에 들어가지 않음)
├── scripts/validate.py                          사양 검증 (CI와 pre-commit이 실행)
├── .githooks/                                   pre-commit 검증, post-commit 자동 push
└── .github/workflows/validate.yml               push·PR마다 검증
```

## 2. frontmatter

| 필드 | 값 | 이유 |
|---|---|---|
| `name` | `defining-problems` | 소문자·하이픈, 디렉터리명과 일치, 동명사형 |
| `description` | 트리거 상황 나열(한국어 표현 포함) + 제외 조건 | 호출 판단은 name+description만으로 이뤄진다. 절차는 쓰지 않는다. 절차를 요약하면 에이전트가 본문을 건너뛴다 |
| `metadata` | `author`, `language`, `homepage` | 사양이 허용하는 자유 필드. 도구는 해석하지 않는다 |

쓰지 않는 필드와 이유

- `context: fork`: 포크된 서브에이전트는 대화 이력을 보지 못한다. 인터뷰에 부적합.
- `model`, `allowed-tools`: 호출한 턴에만 적용되어 여러 턴 대화에서는 첫 턴 뒤 효력이 없다.
- `argument-hint`: Claude Code 전용 필드라 Agent Skills 사양 검증(`agentskills validate`)에서 거부된다. 다른 도구와의 호환을 위해 뺐다.
- `disable-model-invocation`: 사용자가 "문제 정의"라는 말을 쓰지 않는 상황에서도 불려야 하므로 켜지 않는다.

## 3. 실행 흐름

```
입력 읽기
  ├─ 기존 정의문을 가져옴 ───────────────► 검토 모드: quality-bar 판정 → 고쳐 쓴 문장
  ├─ "질문 말고"/마감 임박/정보 충분 ──► 초안 모드: 질문 0개, 가정 표시
  └─ 그 외 ──────────────────────────────► 대화 모드: 메시지당 질문 1개, 5개 안에 초안

1 현상 고정      관찰된 사실만. 해결책은 '보류한 해결책' 칸으로
2 성격 진단      lenses.md          → 정의 방식 결정
3 구조 보기      systems.md         (반복되거나 대책이 실패했을 때만)
4 프레임 3개+    각 프레임이 전제하는 해결 방향 → 하나 채택
5 정의문·판정    quality-bar.md     한 문장 공식, 7조건
6 산출           output-template.md 가장 위험한 가정 3개 + 반증 조건
```

모드 판정과 참고 파일 읽기는 모두 관찰 가능한 조건에 건 조건문으로 쓴다
("사용자가 이미 대책을 시도했다고 말했으면 systems.md를 읽는다").

## 4. 자료 → 스킬 매핑

| 자료 | 스킬에서 맡는 역할 | 위치 |
|---|---|---|
| 맥킨지 식 문제해결기법 | 문제=목표와 현상의 간극, Fact-Base, 문제 vs 과제 | SKILL.md 1단계, quality-bar |
| 문제해결능력(산업인력공단) | 발생·탐색·설정형, 문제 vs 문제점, 문제해결 장애요인 | lenses, quality-bar |
| Sequoia Arc PMF | 고객이 문제와 맺는 관계 3유형과 실패 양상 | lenses |
| Rittel & Webber (1973) | tame/wicked 판별, 정식화가 해법을 전제, 멈춤 기준, 증상의 수준 | SKILL.md 4단계, lenses |
| Meadows (2008) | 사건·패턴·구조, 경계, 함정 8개, 개입 지점, "해법의 부재로 정의하지 마라" | systems, SKILL.md 규칙 1 |
| Forrester (1969/1999) | 반직관성, 가까운 원인은 동시 증상, 대책 배가의 악순환 | systems |
| Sarasvathy (2001) | 결과가 주어졌는가 수단이 주어졌는가, 감당 가능한 손실 | lenses |
| Delmar & Shane (2003) | 쓰는 행위가 가정을 드러냄, 사실/가정 비율, 싸게 검증 | SKILL.md 규칙 2, 6단계 |
| 문제의 탄생(장대익) | 한 문장 공식, 좋은 문제 7조건, 가짜 문제, 솔루션 충동, 프레임 다시 쓰기 | quality-bar, SKILL.md |
| AI와 문제정의(가천대) | WHO+GAP+WHY 형식, 빙산→덫→레버리지 순서, 과제 가이드 | output-template, systems |

자료 간 충돌은 숨기지 않고 규칙으로 바꾼다.

- 가설 지향(맥킨지) vs 솔루션 보류(「문제의 탄생」) → 해결책은 지우지 않고 칸을 옮긴다. 순서의 문제로 다룬다.
- 계획 먼저(Delmar) vs 행동 먼저(Sarasvathy) vs 시행착오 불가(Rittel) → 4축 진단 결과에 따라 정의 방식을 달리한다.
- 체념하고 버티는 고객: Sequoia는 Hard Fact(유효한 경로), 「문제의 탄생」은 가짜 문제 징후 → 비용을 실제로 치르는지로 가른다.

## 5. 적용한 작성 기법

| 기법 | 적용 내용 | 출처 |
|---|---|---|
| 기준선 먼저 | 스킬 없이 시나리오 2개를 돌려 실패를 기록하고 그 실패만 겨냥 | Anthropic skill best practices "Build evaluations first"; superpowers writing-skills (2026-09-19) |
| 실패 유형에 맞는 지시 형태 | 출력 모양 문제(해결책 혼입, 프레임 1개)는 금지문이 아니라 템플릿의 필수 칸과 긍정형 레시피로 처리 | superpowers writing-skills "Match the Form to the Failure" |
| description은 트리거만 | "Use when…" + 한국어 발화 예 + 제외 조건. 절차 요약 없음 | superpowers writing-skills; agentskills.io optimizing-descriptions |
| 단계적 공개 | 본문은 절차, 지식은 references/ 한 단계 깊이, 조건부로 읽음 | agentskills.io specification; Anthropic best practices |
| 짧은 본문, 핵심을 위에 | 고정 규칙 3개를 파일 상단에 배치. 자동 압축 뒤 앞부분만 다시 붙음 | code.claude.com/docs/en/skills "Skill content lifecycle" |
| 규칙마다 이유 한 구절, 대문자 강조 없음 | MUST/NEVER 대신 "X 한다, Y 때문에" | anthropics/skills skill-creator; Claude prompting best practices |
| 단계별 완료 기준 | 각 단계 끝에 확인 가능한 조건 | mattpocock/skills writing-for-agents (2026-08-19) |
| 한 번에 한 질문, 선택지는 막혔을 때만 | 초반 조기 수렴 방지 | superpowers brainstorming (2026-10-10) |
| 사실은 에이전트가 찾고 판단만 묻기 | 파일·웹으로 확인 가능한 것은 묻지 않음 | mattpocock/skills grilling (2026-10-07) |
| 진입 모드 3가지 + 가정 목록 | Guided / Context dump / Best guess에 대응 | deanpeters/Product-Manager-Skills workshop-facilitation |
| 재검증 지시 배제 | "다시 확인하라", "서브에이전트로 검증하라" 문구를 넣지 않음. 반증 조건은 산출물의 칸으로 처리 | Prompting Claude Opus 5 "over-verification" |
| 산출물 길이 명시 | 표 밖 설명은 절마다 세 줄 이하, 표의 칸은 한 문장 | Prompting Claude Opus 5 "Written deliverable length" |

조사 원문과 URL은 `references/sources.md` 말미에 있다.

## 6. 평가

### 6.1 결과 품질

- 케이스: `evals/evals.json`. 스킬 있음/없음을 깨끗한 컨텍스트의 서브에이전트로 각각 실행해 비교한다.
- assertion은 객관적으로 확인 가능한 것만 둔다(PRD의 G1~G6에 대응).
- 양쪽에서 항상 통과하는 assertion은 지운다. 스킬의 기여가 아니기 때문이다.

| 케이스 | 겨냥하는 실패 |
|---|---|
| `solution-first-deadline` (시나리오 A) | 해결책 혼입, 프레임 수용, 단정문, 시간 압박 |
| `recurring-after-fixes` (시나리오 B) | 프레임 1개, 구조 미분석, 형식 |
| `too-big-problem` | "교육을 혁신" 류의 시작점 없는 문제 |
| `review-existing-statement` | 사용자의 기존 과제 문장 검토(수혜자 범위 불일치, 수치 없는 비용) |

### 6.2 트리거

- `evals/trigger-evals.json`: should-trigger와 near-miss should-not-trigger 질의.
- 실행: 질의마다 `claude -p "<질의>" --output-format stream-json --verbose`를 돌려 `Skill` 도구 호출에
  `defining-problems`가 있는지 본다. 질의당 3회, 과반으로 판정.
- description을 고칠 때는 실패한 질의의 낱말을 그대로 넣지 않고 상황 범주를 넓힌다(과적합 방지).

### 6.3 대화 모드의 한계

서브에이전트 실행은 한 턴짜리라 여러 턴 인터뷰를 그대로 재현하지 못한다. 대화 모드는
"정보가 부족한 첫 메시지에 질문을 하나만 하는가"까지만 자동으로 본다. 그 뒤 턴은 실제 사용으로 확인한다.

### 6.4 실행 기록 (2026-10-14)

스킬 없음(기준선)과 스킬 있음을 같은 프롬프트로 한 번씩 실행해 사람이 읽고 판정했다.
케이스당 1회라 분산은 재지 않았다.

| 케이스 | 스킬 없음 | 스킬 있음 |
|---|---|---|
| solution-first-deadline | 정의문이 "진단 수단이 없다", 프레임 1개, 농민 행동을 단정문으로 서술, '해결 방향' 절 포함 | 질문 0개. 정의문에 해결책 없음, 프레임 4개, 문장별 등급, 앱은 보류 칸, 위험한 가정 3개에 통화에서 물을 말까지 |
| recurring-after-fixes | 프레임 1개, 형식 자유, 확인 방법 3개 | 프레임 4개, 벌금·회식이 밀어낸 것 설명, 성격 진단, 반증 조건별 이동할 프레임 지정 |
| too-big-problem | (기준선 미실행) | 받은 내용을 진술/보류로 나누고 최근의 구체적 사례를 묻는 질문 1개 |
| review-existing-statement | (기준선 미실행) | 칸별 판정, ④가 해결책의 부재임을 지적, ①을 둘로 분리, 모르는 사실은 [확인 필요] |

트리거 점검: `trigger-evals.json` 중 8개(should 4, should-not 4)를 `claude -p --max-turns 2`로 1회씩 실행.
should 4개는 모두 `defining-problems` 호출, should-not 4개는 미호출(2개는 다른 스킬 호출, 2개는 스킬 없음).
질의당 3회 반복과 나머지 10개 질의는 실행하지 않았다.

실행 뒤 고친 것: 분량 기준(글자 수 → 절마다 세 줄), 초안 모드 판정 기준(둘 이상), 마감 시 안내 문구,
대화 모드 첫 메시지 형식, 검토 모드에서 프레임 규칙과 장애 칸 처리. 이 수정 뒤의 재실행은 하지 않았다.

### 6.5 2차 업데이트 (2026-10-14) — 진형석 특강 반영, 후보 모드 추가

추가 자료: 진형석 박사 가천대 코코네 특강(2026-10-12) 녹취와 슬라이드 96쪽. 문제 정의를 직접 다루는
쪽은 p.7~8뿐이고 나머지는 수출 실무·오픈이노베이션이라, 문제 검증에 옮길 수 있는 것만 반영했다.

| 반영한 것 | 위치 |
|---|---|
| 진입 모드에 '후보' 추가(인터뷰 기록 → 후보 3~5개 → 검증 순서) | SKILL.md, output-template.md |
| 발언 네 등급(한 것·내놓은 것·평가·의향), 유도 질문 표시, 분석 노트 다루기 | interviews.md |
| 대체재 테스트, 반대 증거로 쓰기 | interviews.md, lenses.md |
| 심각성 × 보편성 사분면, 경쟁 부재 읽는 법 | lenses.md |
| 절실성에 "내놓은 것", 규모를 넓이·깊이로, 비대칭성에 문제의 난이도, B2B의 장애 칸 | quality-bar.md |

반영하지 않은 것: 수출 경로, 지원사업, CVC 유형, AI×OI 유형, Sean Ellis 40% 테스트(이미 쓰는 사용자가
있어야 물을 수 있다), 녹취가 심하게 깨진 구간의 수치.

수정 전 스킬(v1)로 같은 인터뷰 과제를 한 번 돌렸다. 포장 후보를 1순위로 뽑는 데는 성공했으나, 실행한
에이전트가 지침이 없어 임의로 판단했다고 보고한 다섯 가지가 이번 수정 대상과 일치했다: 제3자 발언의
근거 등급, 후보 여러 개와 "하나 채택"의 충돌, 사용자 프레임이 없을 때, 대책을 쓴 주체가 응답자일 때,
유도 질문·2차 노트·표본 1명의 처리. 수정 후 스킬로는 작성 세션에서 직접 적용했고, 깨끗한 컨텍스트의
서브에이전트 재실행은 하지 않았다. 트리거 재점검도 하지 않았다(description에 인터뷰 문구 추가).

## 7. 배포와 업데이트

설치 방법은 저장소 `README.md`에 있다. 여기에는 구조가 왜 이런지만 적는다.

- **플러그인을 하위 폴더에 둔 이유**: 마켓플레이스 항목의 `source`가 `./plugins/problem-definition`이면
  설치할 때 그 폴더만 캐시에 복사된다. 설계 문서와 스크립트는 사용자 컨텍스트에 들어가지 않는다.
- **`version`을 두지 않는 이유**: `version`을 적으면 그 문자열이 바뀔 때까지 사용자가 캐시된 사본에 머문다.
  생략하면 커밋 SHA가 버전이 되어 push할 때마다 새 버전으로 인식된다.
- **자동 업데이트는 받는 쪽이 켠다**: 마켓플레이스 파일에는 자동 업데이트를 켜는 필드가 없다. 각 사용자가
  `/plugin` → Marketplaces에서 켜거나 `/plugin marketplace update`를 실행한다.
- **작성자 쪽 반영**: 작성자의 `~/.agents/skills/defining-problems`는 이 저장소의 스킬 폴더를 가리키는
  심볼릭 링크라 편집 즉시 반영된다. 커밋하면 `.githooks/post-commit`이 `main`을 push한다.
- **다른 도구**: `npx skills add cosuss/problem-definition`은 `.claude-plugin/marketplace.json`을 읽어 스킬을
  찾는다. Codex 등은 이 경로로 설치하고 `npx skills update`로 갱신한다.

## 8. 유지보수

- 자료를 추가하면 `references/`의 해당 파일에 규칙으로 넣고 `sources.md`에 출처를 적는다. SKILL.md는 늘리지 않는다.
- 본문을 고치기 전에 고치려는 실패가 실제로 나오는 케이스를 `evals/evals.json`에 먼저 추가한다.
- 커밋 전에 `python3 scripts/validate.py`가 통과해야 한다(pre-commit 훅이 실행한다).
- 쪽 번호는 `sources.md`에 적은 판본 기준이다. Forrester는 스캔본 OCR이라 일부 쪽만 원본과 대조했다.
