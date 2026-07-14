#!/usr/bin/env bash
# install.sh — point Claude Code's status line at the group cc-statusline.sh.
#
# The script itself lives in the agent-skills repo (cloned in ONBOARDING step 5);
# this installer only wires it into ~/.claude/settings.json. It is surgical
# (touches ONLY the .statusLine key), backs the file up first, and is
# idempotent. Works on Linux and macOS. Requires jq.
#
# Usage:
#   ./install.sh                 # auto-detect the agent-skills statusline
#   ./install.sh /path/to/cc-statusline.sh
#   CC_STATUSLINE=/path/... ./install.sh
set -euo pipefail

# --- portable absolute path (resolves symlinks in the parent dir) -----------
abspath() {
  local path=$1 dir base
  base=${path##*/}
  dir=${path%/*}
  [ "$dir" = "$path" ] && dir=.      # no slash in path -> current dir
  [ -z "$dir" ] && dir=/             # path was like "/foo"
  printf '%s/%s\n' "$(cd "$dir" && pwd -P)" "$base"
}

command -v jq >/dev/null 2>&1 || { echo "error: jq is required (apt install jq / brew install jq)." >&2; exit 1; }

# --- locate the group status line script ------------------------------------
candidate=${1:-${CC_STATUSLINE:-}}
if [ -z "$candidate" ]; then
  for c in "$HOME/.claude/skills/bin/cc-statusline.sh" \
           "$HOME/Code/agent-skills/bin/cc-statusline.sh"; do
    [ -f "$c" ] && candidate=$c && break
  done
fi
if [ -z "$candidate" ] || [ ! -f "$candidate" ]; then
  cat >&2 <<'EOF'
error: could not find the group cc-statusline.sh.

It lives in the agent-skills repo — do ONBOARDING step 5 first
(clone agent-skills and symlink it as ~/.claude/skills), then re-run this,
or pass the path explicitly:

  ./install.sh ~/Code/agent-skills/bin/cc-statusline.sh
EOF
  exit 1
fi

script=$(abspath "$candidate")
chmod +x "$script" 2>/dev/null || true
# Keep the shared library executable-readable too (sourced, not exec'd).
lib="$(dirname "$script")/lib/cc-statusline-lib.sh"
[ -f "$lib" ] || echo "warning: shared lib not found next to the script ($lib); the location segment will be skipped until agent-skills is updated." >&2

# --- patch ~/.claude/settings.json ------------------------------------------
settings="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$settings")"
[ -s "$settings" ] || echo '{}' > "$settings"
jq empty "$settings" >/dev/null 2>&1 || { echo "error: $settings is not valid JSON; aborting so nothing is clobbered." >&2; exit 1; }

old=$(jq -r '.statusLine.command // "(none)"' "$settings")
if [ "$old" = "$script" ]; then
  echo "status line already points at $script — nothing to do."
  exit 0
fi

backup="$settings.bak.$(date +%Y%m%d-%H%M%S)"
cp "$settings" "$backup"
tmp=$(mktemp "${TMPDIR:-/tmp}/cc-statusline.XXXXXX")
jq --arg cmd "$script" '.statusLine = {type: "command", command: $cmd}' "$settings" > "$tmp"
mv "$tmp" "$settings"

echo "status line wired up."
echo "  script : $script"
echo "  was    : $old"
echo "  backup : $backup"
echo
echo "Restart Claude Code (or start a fresh session) to see it —"
echo "a running session reads its status line command at launch."
