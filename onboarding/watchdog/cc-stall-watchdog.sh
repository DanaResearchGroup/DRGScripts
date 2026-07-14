#!/usr/bin/env bash
# cc-stall-watchdog.sh — enforce cc-deadman declarations; catch silent die-outs.
# Driven by a systemd user timer every 5 min. NEVER by a Claude Code hook:
# hook-driven watchers only wake when a turn ends, which is exactly the blind
# spot that produced 36 h stalls. See README.md.
set -uo pipefail

WD_HOME="${CC_WATCHDOG_HOME:-$HOME/.cc-watchdog}"
STATE_DIR="$WD_HOME/state"
ARCHIVE_DIR="$STATE_DIR/archive"
LOG_FILE="$WD_HOME/log"
CONFIG="$WD_HOME/config"

# Defaults; override in ~/.cc-watchdog/config (sourced below).
GRACE_MIN=60
BACKSTOP_HOURS=6
BACKSTOP_RENOTIFY_HOURS=12
RECOVERY_BACKOFF_HOURS=24
BUSY_RE='esc to interrupt'
# PI-machine Phoenix state; absent (harmless) on member machines.
AGENTS_STATE="${CC_WATCHDOG_AGENTS_STATE:-$HOME/agents/state}"

mkdir -p "$STATE_DIR" "$ARCHIVE_DIR"
# shellcheck source=/dev/null
[[ -f "$CONFIG" ]] && . "$CONFIG"

log() { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG_FILE"; }

notify() { # $1 = message
  local msg=${1//\"/\'}
  log "NOTIFY: $msg"
  [[ -n "${WATCHDOG_DRY:-}" ]] && return 0
  if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
    curl -sf -X POST -H 'Content-type: application/json' \
      --data "{\"text\": \"$msg\"}" "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 \
      || log "ERROR: Slack post failed"
  else
    log "WARNING: SLACK_WEBHOOK_URL unset — falling back to notify-send"
    notify-send "cc-watchdog" "$msg" 2>/dev/null || true
  fi
}

pane_alive() { tmux list-panes -a -F '#{pane_id}' 2>/dev/null | grep -qx "$1"; }
pane_busy()  { tmux capture-pane -p -t "$1" 2>/dev/null | grep -q "$BUSY_RE"; }
pane_idle()  { pane_alive "$1" && ! pane_busy "$1"; }
session_name() { tmux display-message -p -t "$1" '#{session_name}' 2>/dev/null || echo '?'; }

get_field() { sed -n "s/^$2=//p" "$1" | head -1; }
set_field() {
  grep -v "^$2=" "$1" > "$1.tmp" || true
  echo "$2=$3" >> "$1.tmp"
  mv "$1.tmp" "$1"
}

phoenix_owns() { # $1 = pane — true iff Phoenix is limit-waiting on this pane's session
  local f sid
  for f in "$AGENTS_STATE"/*.limit-wait; do
    [[ -e "$f" ]] || return 1
    sid=$(basename "$f" .limit-wait)
    [[ "$(cat "$AGENTS_STATE/$sid.tmux-pane" 2>/dev/null)" == "$1" ]] && return 0
  done
  return 1
}

main() {
  shopt -s nullglob
  local f
  for f in "$STATE_DIR"/*.deadline; do process_deadline "$f"; done
  backstop_scan
}

# Sourceable for tests; runs only when executed.
[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
