# problem-definition

좋은 문제 정의를 뽑아내는 `defining-problems` 스킬과, 그 스킬로 만든 문제 정의 산출물을 두는 곳이다.

```
problem-definition/
├── skills/defining-problems/   스킬 원본 (SKILL.md, references/, evals/, docs/PRD.md·TSD.md)
└── research/                   스킬로 만든 문제 정의 문서
```

## 스킬 연결

원본은 이 폴더에 있고, 도구들은 심볼릭 링크로 읽는다. 이 폴더를 옮기면 첫 번째 링크를 다시 건다.

```
~/.agents/skills/defining-problems  →  ~/workspace/cocone-school/problem-definition/skills/defining-problems   (Codex)
~/.claude/skills/defining-problems  →  ../../.agents/skills/defining-problems                                  (Claude Code)
```

쓰는 법: `/defining-problems <상황 설명, 검토할 정의문, 또는 인터뷰 기록 경로>`

## research

| 파일 | 내용 |
|---|---|
| `2026-10-14-interview-problem-candidates.md` | NH 애그테크 딸기 농가 인터뷰 2건에서 뽑은 문제 정의 후보 5개와 검증 순서 |
