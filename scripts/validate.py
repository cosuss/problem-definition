#!/usr/bin/env python3
"""저장소가 배포 가능한 상태인지 검사한다. 표준 라이브러리만 쓴다.

검사 항목
- 스킬 frontmatter가 Agent Skills 사양(agentskills.io/specification)에 맞는가
- SKILL.md가 가리키는 references 파일이 모두 있는가
- 저장소 어디에도 비밀값(토큰·키)과 비밀 파일(.env, 개인키)이 없는가
- 배포물에 개인 경로가 들어 있지 않은가
- eval JSON과 플러그인 매니페스트가 올바른가

실행: python3 scripts/validate.py   (실패하면 종료 코드 1)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_SKILL_LINES = 500
# 배포물에 들어가면 안 되는 개인 경로. 예시 문장에 쓰는 `~/.claude/skills` 같은 표준 위치는 허용한다.
PERSONAL_PATH_RE = re.compile(r"/Users/[^/\s]+|~/(Documents|Downloads|Desktop|workspace)\b")

# 커밋하면 post-commit 훅이 바로 push하므로, 올라가면 안 되는 것은 커밋 전에 여기서 막는다.
SECRET_RE = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    r"|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[abprs]-[A-Za-z0-9-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:api[_-]?key|secret|token|passwd|password)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_./+-]{20,}"
)
SECRET_FILE_RE = re.compile(r"(^|/)(\.env(\..+)?|id_(rsa|ed25519)(\.pub)?|settings\.local\.json|credentials[^/]*|[^/]+\.(pem|key|p12|pfx))$")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
MAX_SCAN_BYTES = 1_000_000

errors = []


def fail(path, message):
    errors.append(f"{Path(path).relative_to(ROOT)}: {message}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail(path, f"JSON을 읽을 수 없다: {e}")
        return None


def parse_frontmatter(path):
    """최상위 키와 문자열 값만 읽는다. 중첩 값(metadata)은 키만 확인한다."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        fail(path, "파일 맨 앞에 BOM이 있다. BOM 없는 UTF-8로 저장한다")
        return {}, text
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        fail(path, "frontmatter가 없다")
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        fail(path, "frontmatter가 닫히지 않았다")
        return {}, text
    fields = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("\"'")
    return fields, text[end + 4 :]


def check_repo_hygiene():
    """스킬 폴더 밖까지 포함해 저장소 전체에서 비밀값·비밀 파일·개인 경로를 찾는다."""
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or not path.is_file():
            continue
        if SECRET_FILE_RE.search(rel.as_posix()):
            fail(path, "비밀 파일로 보이는 이름이다. 저장소에 두지 않는다")
            continue
        if path.stat().st_size > MAX_SCAN_BYTES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in SECRET_RE.finditer(text):
            # 값을 출력하지 않고 앞 4자만 보여 준다.
            fail(path, f"비밀값으로 보이는 문자열이 있다: {match.group(0)[:4]}…")
        if rel != Path("scripts/validate.py") and path.suffix in {".md", ".json", ".yml", ".yaml"}:
            for match in PERSONAL_PATH_RE.finditer(text):
                fail(path, f"개인 경로가 들어 있다: {match.group(0)}")


def check_skill(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        fail(skill_dir, "SKILL.md가 없다")
        return
    fields, body = parse_frontmatter(skill_md)

    unknown = set(fields) - ALLOWED_FIELDS
    if unknown:
        fail(skill_md, f"사양에 없는 frontmatter 필드: {sorted(unknown)}")

    name = fields.get("name", "")
    if not NAME_RE.match(name) or len(name) > 64:
        fail(skill_md, f"name이 규칙에 맞지 않는다(소문자·숫자·하이픈, 64자 이하): {name!r}")
    if name != skill_dir.name:
        fail(skill_md, f"name({name})이 폴더명({skill_dir.name})과 다르다")

    description = fields.get("description", "")
    if not description:
        fail(skill_md, "description이 비어 있다")
    elif len(description) > 1024:
        fail(skill_md, f"description이 1024자를 넘는다: {len(description)}자")

    lines = skill_md.read_text(encoding="utf-8").count("\n")
    if lines > MAX_SKILL_LINES:
        fail(skill_md, f"{lines}줄이다. {MAX_SKILL_LINES}줄 이하로 줄이고 나머지는 references로 옮긴다")

    for ref in sorted(set(re.findall(r"`(references/[\w./-]+)`", body))):
        if not (skill_dir / ref).exists():
            fail(skill_md, f"가리키는 파일이 없다: {ref}")

    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".json"}:
            text = path.read_text(encoding="utf-8")
            for match in PERSONAL_PATH_RE.finditer(text):
                fail(path, f"개인 경로가 들어 있다: {match.group(0)}")
            if path.suffix == ".json":
                load_json(path)

    trigger = skill_dir / "evals" / "trigger-evals.json"
    if trigger.exists():
        data = load_json(trigger) or []
        for i, item in enumerate(data):
            if not isinstance(item.get("query"), str) or not isinstance(item.get("should_trigger"), bool):
                fail(trigger, f"{i}번 항목에 query(문자열)와 should_trigger(불리언)가 있어야 한다")

    quality = skill_dir / "evals" / "evals.json"
    if quality.exists():
        data = load_json(quality) or {}
        if data.get("skill_name") != name:
            fail(quality, f"skill_name이 스킬 이름({name})과 다르다")
        for case in data.get("evals", []):
            for key in ("id", "prompt", "assertions"):
                if not case.get(key):
                    fail(quality, f"케이스 {case.get('id', '?')}에 {key}가 없다")


def main():
    marketplace = load_json(MARKETPLACE)
    if marketplace is None:
        print("\n".join(errors))
        return 1
    for key in ("name", "owner", "plugins"):
        if key not in marketplace:
            fail(MARKETPLACE, f"{key} 필드가 없다")

    check_repo_hygiene()

    skill_count = 0
    for entry in marketplace.get("plugins", []):
        source = entry.get("source")
        if not isinstance(source, str):
            continue
        plugin_dir = (ROOT / source).resolve()
        if ROOT not in plugin_dir.parents:
            fail(MARKETPLACE, f"source가 저장소 밖을 가리킨다: {source}")
            continue
        if not plugin_dir.is_dir():
            fail(MARKETPLACE, f"source 경로가 없다: {source}")
            continue
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        manifest = load_json(manifest_path) if manifest_path.exists() else {}
        if manifest:
            if manifest.get("name") != entry.get("name"):
                fail(manifest_path, f"name이 마켓플레이스 항목({entry.get('name')})과 다르다")
            # version을 적으면 그 문자열을 바꿀 때까지 사용자가 업데이트를 받지 못한다.
            if "version" in manifest or "version" in entry:
                fail(manifest_path, "version을 두지 않는다. 생략해야 커밋마다 새 버전으로 배포된다")
        for skill_md in sorted((plugin_dir / "skills").glob("*/SKILL.md")):
            check_skill(skill_md.parent)
            skill_count += 1

    if skill_count == 0:
        fail(MARKETPLACE, "스킬을 하나도 찾지 못했다")

    if errors:
        print(f"검증 실패 ({len(errors)}건)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"검증 통과: 스킬 {skill_count}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
