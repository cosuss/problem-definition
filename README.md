# problem-definition

막연한 상황 설명, 아이디어, 인터뷰 기록에서 **근거가 표시된 문제 정의**를 뽑아내는 에이전트 스킬이다.
Claude Code, Codex 등 [Agent Skills](https://agentskills.io) 사양을 따르는 도구에서 쓴다. 진행 언어는 한국어다.

A Korean-language agent skill that turns vague situations, solution ideas, or interview notes into an
evidence-labelled problem definition. Works with any tool that supports the Agent Skills format.

## 무엇을 하는가

스킬 없이 물으면 에이전트는 대개 세 가지를 틀린다. 이 스킬은 그 세 가지를 고정 규칙으로 잡는다.

1. **문제 문장에 해결책을 넣지 않는다.** "~가 없다"는 해결책의 부재다. 가져온 해결책은 `보류한 해결책` 칸으로 옮긴다.
2. **모든 서술에 근거 등급을 붙인다.** `[확인]` · `[진술]` · `[가정]`
3. **프레임을 셋 이상 만든 뒤 고른다.** 프레임마다 그것이 전제하는 해결 방향을 적는다.

들어온 내용에 따라 네 가지로 움직인다.

| 이런 걸 주면 | 이렇게 한다 |
|---|---|
| 막연한 고민 | 한 번에 하나씩 묻고(최대 5개) 초안을 낸다 |
| 급한 마감, "질문하지 마" | 묻지 않고 초안을 내고, 확인할 것 세 가지를 붙인다 |
| 이미 쓴 문제 정의문 | 칸별로 판정하고 고쳐 쓴 문장을 낸다 |
| 인터뷰 녹취·메모 | 발언을 등급별로 나누고 후보 3~5개를 견주어 검증 순서를 낸다 |

## 설치

### Claude Code

```
/plugin install problem-definition --marketplace cosuss/problem-definition
```

Claude Code 2.1.275 이전 버전에서는 두 단계로 한다.

```
/plugin marketplace add cosuss/problem-definition
/plugin install problem-definition@cosuss-skills
```

설치한 뒤 `/problem-definition:defining-problems <상황>`으로 부르거나, 문제 정의 얘기를 꺼내면 알아서 호출된다.

### Codex와 그 밖의 도구

```bash
npx skills add cosuss/problem-definition -g -a codex
```

`-a`에 쓰는 도구 이름을 넣는다(`claude-code`, `codex`, `cursor` 등). `-g`를 빼면 현재 프로젝트에만 설치된다.

### 직접 복사

`plugins/problem-definition/skills/defining-problems/` 폴더를 통째로 도구의 스킬 폴더에 넣는다
(Claude Code는 `~/.claude/skills/`, Codex는 `~/.agents/skills/`).

저장소가 비공개인 동안에는 저장소 접근 권한과, 프롬프트 없이 동작하는 git 인증이 필요하다.
GitHub이면 `gh auth login` 뒤 `gh auth setup-git`을 한 번 실행한다.

## 업데이트 받기

이 플러그인은 버전 번호가 없고 `main`의 커밋이 곧 버전이다. 새 커밋이 올라오면 새 버전으로 인식된다.

| 설치 방법 | 업데이트 |
|---|---|
| Claude Code 플러그인 | 자동: `/plugin` → **Marketplaces** → `cosuss-skills` → **Enable auto-update** (한 번만 켜면 된다). 수동: `/plugin marketplace update cosuss-skills` |
| `npx skills` | `npx skills update` |
| 직접 복사 | 폴더를 다시 복사한다 |

바뀐 내용은 [CHANGELOG.md](CHANGELOG.md)에 있다.

## 쓰는 법

```
/problem-definition:defining-problems 과제 주제는 청년 인구 유출이야. 지금까지 정착 지원금이 있었는데 효과가 없었어.
/problem-definition:defining-problems 내가 쓴 문제 정의문 봐줘: "직장인들은 점심 메뉴 고르기를 어려워한다."
/problem-definition:defining-problems interviews/ 폴더의 녹취 세 개에서 문제 후보를 뽑아줘
```

잘 쓰는 요령

- 해결책 말고 **최근에 실제로 있었던 일**을 준다. 인터뷰 메모, 회의록, 숫자가 있으면 `[가정]`이 `[확인]`으로 바뀐다.
- 대책을 써 봤다면 **무엇을 했고 어떻게 됐는지**를 같이 준다. 그래야 구조 분석이 켜진다.
- `[확인 필요]`를 지어서 채우지 않는다. 확인하지 못했으면 등급을 남긴 채 가설로 쓴다.
- 산출물의 `가장 위험한 가정` 표는 다음 인터뷰 질문지로 그대로 쓸 수 있다.

쓰지 않는 게 나은 경우: 문제가 이미 합의됐고 기능이나 화면을 설계할 때, 개념을 공부할 때.

## 구성

```
.claude-plugin/marketplace.json        마켓플레이스 목록
plugins/problem-definition/            설치되는 플러그인
└── skills/defining-problems/
    ├── SKILL.md                       절차와 고정 규칙
    ├── references/                    필요할 때만 읽는 판별 기준과 템플릿
    └── evals/                         품질·트리거 평가 케이스
docs/                                  설계 문서 (PRD, TSD)
scripts/validate.py                    사양 검증
```

## 근거 자료

규칙마다 출처와 쪽 번호를 [`references/sources.md`](plugins/problem-definition/skills/defining-problems/references/sources.md)에 적었다.
Rittel & Webber(1973), Meadows(2008), Forrester(1969), Sarasvathy(2001), Delmar & Shane(2003), Sequoia Arc,
한국산업인력공단 가이드북과, 강의 자료 네 편(장대익, 진형석, 가천대, 맥킨지 교육 슬라이드)을 썼다.
강의 자료는 원문을 싣지 않고 규칙으로 옮긴 내용만 담았다.

## 고치는 법

1. 고치려는 실패가 실제로 나오는 입력을 `evals/evals.json`에 먼저 넣는다. 스킬 없이도 잘 되는 것은 넣지 않는다.
2. `SKILL.md`는 짧게 유지하고 지식은 `references/`에 넣는다. 새 규칙에는 `sources.md`에 출처를 적는다.
3. `python3 scripts/validate.py`가 통과해야 한다.

저장소를 받아 고치는 사람은 한 번 실행해 둔다. 커밋 전에 검증이 돌고, `main`에 커밋하면 바로 push된다.

```bash
git config core.hooksPath .githooks
```
