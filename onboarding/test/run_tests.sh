#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
onboarding="$root/onboarding"

require_text() {
  local pattern=$1 file=$2
  if ! grep -Fq -- "$pattern" "$file"; then
    printf 'missing required text in %s: %s\n' "$file" "$pattern" >&2
    return 1
  fi
}

require_text 'curl -fsSL https://chatgpt.com/codex/install.sh | sh' "$onboarding/ONBOARDING.md"
require_text 'curl -fsSL https://opencode.ai/install | bash' "$onboarding/ONBOARDING.md"
require_text 'ln -sfn ~/Code/agent-skills ~/.agents/skills' "$onboarding/ONBOARDING.md"
require_text '--target codex' "$onboarding/ONBOARDING.md"
require_text '--target opencode' "$onboarding/ONBOARDING.md"
require_text 'herdr integration install codex' "$onboarding/ONBOARDING.md"
require_text 'herdr integration install opencode' "$onboarding/ONBOARDING.md"
require_text "for svc in \"\${services[@]}\"; do" "$onboarding/ONBOARDING.md"
require_text "\"\$VAULT/AGENTS.md\"" "$onboarding/vault-structure.md"
require_text 'Context 188.3k/1050k 17.9% (188.3k/258.4k 72.9%)' "$onboarding/ONBOARDING.md"
require_text 'Context 188.3k/1050k 17.9% (188.3k/258.4k 72.9%)' \
  "$onboarding/statusline/codex/context-model-and-effective.patch"

if grep -Fq -- '--target generic' "$onboarding/ONBOARDING.md"; then
  echo 'obsolete Headroom generic target remains in ONBOARDING.md' >&2
  exit 1
fi

if grep -Fq -- 'systemctl --user restart headroom-agy headroom-codex headroom-opencode' \
  "$onboarding/ONBOARDING.md"; then
  echo 'Headroom restart still assumes every optional client is installed' >&2
  exit 1
fi

git apply --numstat "$onboarding/statusline/codex/context-model-and-effective.patch" >/dev/null

agent_tmp=$(mktemp -d)
trap 'rm -rf "$agent_tmp"' EXIT
python3 "$onboarding/agents/install.py" codex --output "$agent_tmp/codex" >/dev/null
python3 "$onboarding/agents/install.py" opencode --output "$agent_tmp/opencode" >/dev/null
if python3 "$onboarding/agents/install.py" codex --output "$agent_tmp/codex" >/dev/null 2>&1; then
  echo 'agent installer overwrote existing Codex definitions' >&2
  exit 1
fi
python3 - "$agent_tmp" <<'PY'
import pathlib
import sys
import tomllib

root = pathlib.Path(sys.argv[1])
codex = sorted((root / "codex").glob("*.toml"))
opencode = sorted((root / "opencode").glob("*.md"))
assert len(codex) == 4
assert len(opencode) == 4
for path in codex:
    config = tomllib.loads(path.read_text(encoding="utf-8"))
    assert {"name", "description", "developer_instructions"} <= config.keys()
for path in opencode:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\ndescription: ")
    assert "\nmode: subagent\n---\n" in text
PY

python3 - "$onboarding" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
missing = []
for document in root.rglob("*.md"):
    text = document.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        target = target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = (document.parent / target.split("#", 1)[0]).resolve()
        if not path.exists():
            missing.append(f"{document.relative_to(root)} -> {target}")

if missing:
    print("broken local Markdown links:", file=sys.stderr)
    print("\n".join(f"  {item}" for item in missing), file=sys.stderr)
    raise SystemExit(1)
PY

echo 'onboarding checks passed'
