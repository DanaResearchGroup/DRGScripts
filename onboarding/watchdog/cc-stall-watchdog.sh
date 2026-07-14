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

# --- multiplexer seam: pane keys "herdr:<id>" route to the herdr CLI -------
is_herdr() { [[ "$1" == herdr:* ]]; }
hid() { printf '%s' "${1#herdr:}"; }

herdr_status() { # $1 = full pane key → agent_status, empty if unreachable
  herdr pane get "$(hid "$1")" 2>/dev/null \
    | sed -n 's/.*"agent_status"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1
}

pane_alive() {
  if is_herdr "$1"; then
    local out
    # unreachable herdr => assume alive: never false-VANISH a session we can't see
    out=$(herdr pane list 2>/dev/null) || return 0
    grep -qF "\"$(hid "$1")\"" <<<"$out"
  else
    tmux list-panes -a -F '#{pane_id}' 2>/dev/null | grep -qx "$1"
  fi
}

pane_busy() {
  if is_herdr "$1"; then [[ "$(herdr_status "$1")" == working ]]
  else tmux capture-pane -p -t "$1" 2>/dev/null | grep -q "$BUSY_RE"; fi
}

pane_idle() {
  if is_herdr "$1"; then
    local s; s=$(herdr_status "$1")
    # 'blocked' (agent waiting for input) is deliberately NOT idle: a blocked
    # agent must not self-clear its deadline — tier 1 should reach the user.
    [[ "$s" == idle || "$s" == done ]]
  else
    pane_alive "$1" && ! pane_busy "$1"
  fi
}

session_name() {
  if is_herdr "$1"; then printf '%s' "$1"
  else tmux display-message -p -t "$1" '#{session_name}' 2>/dev/null || echo '?'; fi
}

get_field() { sed -n "s/^$2=//p" "$1" | head -1; }
set_field() {
  grep -v "^$2=" "$1" > "$1.tmp" || true
  echo "$2=$3" >> "$1.tmp"
  mv "$1.tmp" "$1"
}

phoenix_owns() { # $1 = pane key — Phoenix records herdr panes in <sid>.herdr-pane
  local f sid
  for f in "$AGENTS_STATE"/*.limit-wait; do
    [[ -e "$f" ]] || return 1
    sid=$(basename "$f" .limit-wait)
    if is_herdr "$1"; then
      [[ "$(cat "$AGENTS_STATE/$sid.herdr-pane" 2>/dev/null)" == "$(hid "$1")" ]] && return 0
    else
      [[ "$(cat "$AGENTS_STATE/$sid.tmux-pane" 2>/dev/null)" == "$1" ]] && return 0
    fi
  done
  return 1
}

RECOVERY_PROMPT_TMPL='Dead-man deadline expired for: %s. Your awaited work likely died silently. Check honest status (process alive? output complete?) and continue or re-run.'

inject_recovery() { # $1 pane, $2 reason
  log "RECOVER: injecting into $1 (reason: $2)"
  [[ -n "${WATCHDOG_DRY:-}" ]] && return 0
  if is_herdr "$1"; then
    # shellcheck disable=SC2059
    herdr pane run "$(hid "$1")" "$(printf "$RECOVERY_PROMPT_TMPL" "$2")" >/dev/null 2>&1 \
      || log "ERROR: herdr pane run failed for $1 (external control unavailable?)"
    return 0
  fi
  if pane_busy "$1"; then
    tmux send-keys -t "$1" Escape
    sleep 5
  fi
  # shellcheck disable=SC2059
  tmux send-keys -t "$1" -l "$(printf "$RECOVERY_PROMPT_TMPL" "$2")"
  sleep 1
  tmux send-keys -t "$1" Enter
}

cc_panes() { # emit "<pane_id> <pane_pid>" for panes running a claude process
  local pane ppid
  while read -r pane ppid; do
    pstree -p "$ppid" 2>/dev/null | grep -q 'claude(' && printf '%s %s\n' "$pane" "$ppid"
  done < <(tmux list-panes -a -F '#{pane_id} #{pane_pid}' 2>/dev/null)
}

pane_transcript_mtime() { # $1 = pane_pid → epoch mtime of newest transcript, or fail
  local cpid cwd munged newest
  cpid=$(pstree -p "$1" 2>/dev/null | grep -o 'claude([0-9]\+)' | head -1 | tr -dc 0-9)
  [[ -n "$cpid" ]] || return 1
  cwd=$(readlink "/proc/$cpid/cwd" 2>/dev/null) || return 1
  munged=$(printf '%s' "$cwd" | sed 's#[/.]#-#g')
  newest=$(ls -t "$HOME/.claude/projects/$munged"/*.jsonl 2>/dev/null | head -1)
  [[ -n "$newest" ]] || return 1
  stat -c %Y "$newest"
}

backstop_scan() {
  local now pane ppid bs since tmtime stamp
  now=$(date +%s)
  while read -r pane ppid; do
    bs="$STATE_DIR/pane-$pane.busy-since"
    if ! pane_busy "$pane"; then rm -f "$bs"; continue; fi
    [[ -f "$bs" ]] || echo "$now" > "$bs"
    [[ -f "$STATE_DIR/$pane.deadline" ]] && continue      # declared: ladder owns it
    since=$(cat "$bs")
    (( now - since >= BACKSTOP_HOURS * 3600 )) || continue
    tmtime=$(pane_transcript_mtime "$ppid") || continue    # can't resolve → skip, no guess
    (( now - tmtime >= BACKSTOP_HOURS * 3600 )) || continue
    stamp="$STATE_DIR/pane-$pane.backstop-notified"
    if [[ -f "$stamp" ]] && (( now - $(cat "$stamp") < BACKSTOP_RENOTIFY_HOURS * 3600 )); then
      continue
    fi
    notify "cc-watchdog BACKSTOP: [$(session_name "$pane")] busy >${BACKSTOP_HOURS}h, transcript stale, no declared deadline — possible silent stall (notify-only)"
    echo "$now" > "$stamp"
  done < <(cc_panes)
}

process_deadline() { # $1 = deadline file
  local f=$1 pane deadline setts reason transcript notified recovered now
  pane=$(get_field "$f" pane);       deadline=$(get_field "$f" deadline)
  setts=$(get_field "$f" set);       reason=$(get_field "$f" reason)
  transcript=$(get_field "$f" transcript)
  notified=$(get_field "$f" notified); recovered=$(get_field "$f" recovered)
  now=$(date +%s)

  if ! pane_alive "$pane"; then
    notify "cc-watchdog: pane $pane VANISHED with unmet deadline: $reason"
    mv "$f" "$ARCHIVE_DIR/"; return
  fi

  if phoenix_owns "$pane"; then log "DEFER: Phoenix owns $pane"; return; fi

  # Self-clear: the session did something after declaring, and is idle again.
  if [[ -n "$transcript" && -f "$transcript" ]] \
      && (( $(stat -c %Y "$transcript") > setts )) && pane_idle "$pane"; then
    log "SELF-CLEAR: $pane progressed and is idle ($reason)"
    mv "$f" "$ARCHIVE_DIR/"; return
  fi

  (( now < deadline )) && return

  if [[ -z "$notified" ]]; then
    notify "cc-watchdog: [$(session_name "$pane")] deadline MISSED ($(( (now - deadline) / 60 )) min overdue): $reason"
    set_field "$f" notified "$now"
    return
  fi

  if [[ -z "$recovered" ]]; then
    (( now >= deadline + GRACE_MIN * 60 )) || return
    local lr="$STATE_DIR/pane-$pane.last-recovery"
    if [[ -f "$lr" ]] && (( now - $(cat "$lr") < RECOVERY_BACKOFF_HOURS * 3600 )); then
      notify "cc-watchdog: [$(session_name "$pane")] stalled AGAIN within ${RECOVERY_BACKOFF_HOURS}h of a recovery — notify-only backoff: $reason"
      set_field "$f" recovered "$now"
      set_field "$f" recovery_kind backoff
      return
    fi
    inject_recovery "$pane" "$reason"
    set_field "$f" recovered "$now"
    set_field "$f" recovery_kind inject
    echo "$now" > "$lr"
    return
  fi

  # "RECOVERY FAILED ... after injection" is only truthful when an injection
  # actually happened; backoff-mode deadlines already got their final notice.
  if [[ "$(get_field "$f" recovery_kind)" == inject ]] \
      && [[ -z "$(get_field "$f" failed)" ]] && (( now >= recovered + GRACE_MIN * 60 )); then
    notify "cc-watchdog: [$(session_name "$pane")] RECOVERY FAILED (no progress ${GRACE_MIN} min after injection): $reason"
    set_field "$f" failed "$now"
  fi
}

main() {
  shopt -s nullglob
  local f
  for f in "$STATE_DIR"/*.deadline; do process_deadline "$f"; done
  backstop_scan
}

# Sourceable for tests; runs only when executed.
[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
