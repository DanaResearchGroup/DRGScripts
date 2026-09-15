# Maintaining the onboarding kit

This documents *why* the onboarding kit is shaped the way it is, so a future maintainer
(or a future coding-agent session) can update it for the next member without re-deriving the
decisions. The member-facing runbook is [ONBOARDING.md](./ONBOARDING.md); this file is for
whoever maintains it.

## Purpose

Let a new Dana Research Group member stand up an **independent mirror** of the PI's
coding-agent working environment from a small set of committed, self-documenting artifacts —
not by copying secrets or by being granted access to the PI's machines.

## Architecture (the mental model the kit assumes)

- **One real environment, on Linux** (the member's office PC). Antigravity, Codex, OpenCode,
  agent-skills, Headroom, and a multiplexer (tmux or Herdr) live here and only here.
- **Laptops are dual-role ("mixed by purpose"):** thin client (ssh/mosh + `tmux attach`)
  into the Linux box for heavy work, *plus* native Obsidian for notes. A laptop needs only
  tailscale + a terminal + Obsidian.
- **Independent mirror, not shared infra:** the member gets their own tailnet, own Obsidian
  vault, and own provider accounts. We hand them a recipe, not access.

## Artifact map

| File | Repo | What it does | Touch when… |
|---|---|---|---|
| `bin/cc-statusline.sh` + `bin/lib/cc-statusline-lib.sh` | agent-skills | Status line: model + colour-coded context-% + git location (repo/branch/worktree/dirty). Shares the lib with the PI's autodev variant. | The statusline JSON schema changes, or the colours/format need tuning. |
| `onboarding/statusline/{install.sh,README.md}` | DRGScripts | Installer that wires `bin/cc-statusline.sh` into `~/.claude/settings.json` (surgical `.statusLine` patch, backup, idempotent) + the member-facing doc. | The install/settings wiring changes. |
| `onboarding/statusline/codex/**` | DRGScripts | Pinned Codex TUI patch and build instructions for the dual model/effective context display. | Upstream Codex changes the affected TUI code, group model limits change, or stock Codex gains equivalent support. |
| `UPDATING.md` | agent-skills | CC-executable "update my skills" runbook (plain `git pull`). | The update flow changes. |
| `SETUP.md` (new-member section) | agent-skills | Minimal clone→symlink→statusline path. | Install steps change. |
| `onboarding/ONBOARDING.md` | DRGScripts | Master agent-executable runbook for Antigravity, Codex, and OpenCode. | Any step in the end-to-end flow changes. |
| `onboarding/CLAUDE.global.md` | DRGScripts | Genericized global CLAUDE.md to merge into `~/.claude/CLAUDE.md`. Every byte is loaded into every session the member ever runs, so it is kept near the size of the PI's own file — see "Keeping it small" below. | The PI's `~/.claude/CLAUDE.md` gains durable guidance worth sharing. |
| `onboarding/AGENTS.global.md` | DRGScripts | Client-neutral global instructions copied to Codex and OpenCode. | Shared policy changes or either client changes its instruction path. |
| `onboarding/agents/*.md` + `install.py` | DRGScripts | Canonical subagent roles plus the Codex TOML/OpenCode Markdown translator. AGY registers the source roles per session. | A role, model tier mapping, native agent schema, or routing boundary changes. |
| `onboarding/vault-structure.md` | DRGScripts | Vault tree + scaffold + which seeds go where. | The vault layout changes. |
| `onboarding/vault-seeds/**` | DRGScripts | Real files copied into the member's vault (operating manual, wiki index, cheatsheets, tmux.conf). | The seeds drift from the PI's (sanitized) originals. |
| `onboarding/dotfiles/tmux.conf` | DRGScripts | The group tmux config. | The PI's `~/.tmux.conf` changes. |
| `onboarding/dotfiles/herdr-config.toml` | DRGScripts | The group Herdr config (for members who use Herdr instead of/besides tmux). | The PI's `~/.config/herdr/config.toml` changes. |
| `ARC/CLAUDE.md` | DRGScripts | Existing ARC project guide — referenced, not duplicated. | (Maintained independently.) |
| `contract/**` | agent-skills | The start gate: `PreToolUse` hook denies the first `Edit`/`Write`/`NotebookEdit` in an opted-in repo until a note records Intent/Verifier/Non-goals/Gates. Member-facing in ONBOARDING step 13. | The hook contract, CLI subcommands, or the four field names change — keep the field names in lockstep with `pm-creator`'s ledger, which is what lets a ticket outgrow the tier without translation. |

## Decisions & rationale

| Decision | Choice | Why |
|---|---|---|
| agent-skills | **clone**, not fork | Members track upstream with a plain `git pull`; no fork divergence to manage. |
| User-specific paths | `/home/alon` → **`$HOME`** in agent-skills prose **and** the PI's `~/.claude/CLAUDE.md` | An agent reading prose expands `$HOME`; works identically for the PI; removes any "personalize" step. |
| `~/.claude/settings.json` | **left literal**, except `.statusLine` | Its paths are personal infra (`~/agents` auto-handoff, gitkraken marketplace) the member never gets; Claude Code does **not** reliably shell-expand `$HOME` in non-command fields (e.g. `extraKnownMarketplaces.path`). Risk > benefit. The **one** key the member does get is `.statusLine` — a *command* field (absolute path is safe), written surgically by `onboarding/statusline/install.sh` (backup + idempotent), not by copying the PI's file. **NB:** the settings.json *hooks* stay PI-only — but the **skills** themselves *are* member-facing (ONBOARDING step 5). |
| Skills | **one clone exposed at `~/.agents/skills` and `~/.claude/skills`** (ONBOARDING step 5) | Codex and OpenCode share the agent-standard path; the Claude-compatible path preserves Claude Code and older skill assumptions. One `git pull` updates both. |
| Obsidian sync | **Dropbox desktop client only; no remotely-save** | No mobile/phone requirement → filesystem sync is enough. One fewer plugin. |
| Statusline | the **group `bin/cc-statusline.sh`** (model + colour-coded context-% + git location), not the PI's `~/agents` auto-handoff variant | Both variants share `bin/lib/cc-statusline-lib.sh` so model/context/location never drift between them; the member gets the clean one — no `~/agents` infra to stand up. Wired by `onboarding/statusline/install.sh`. |
| Seeds | **sanitized**, real files under `vault-seeds/` | Easy `cp` into place; the PI's real remote-dev note (tailnet IPs, VPN endpoint, cluster/exit-node config) is excluded — a generic `Remote Dev — Pattern` replaces it. |
| Supported clients | **Antigravity, Codex, and OpenCode** | Members choose their client and provider while sharing project `AGENTS.md`, skills, Headroom, Herdr, and the Linux host. |
| Headroom profiles | **one service per client** (`agy:8787`, `codex:8788`, `opencode:8789`) | Each integration can be inspected, tuned, restarted, and removed independently. Codex and OpenCode use native targets; AGY uses `GEMINI_BASE_URL`. |
| Codex context footer | **native status line by default; optional pinned source build for both budgets** | Stock Codex exposes `context-used` but no arbitrary footer command. The small patch is tested against one commit and installed beside the official binary as `codex-drg`. |
| Cross-client skills | **shared discovery path, explicit compatibility** | A symlink makes a skill visible; it does not translate Claude tool names or hook protocols. Each client-specific skill must be ported or marked with an honest compatibility constraint in `agent-skills`. |
| Multiplexer | **Herdr recommended; tmux also supported** (ONBOARDING step 6) | Herdr is agent-state-aware (mouse-first sidebar showing each agent's live state), which the cc-watchdog guard and the agent-skills auto-handoff/Phoenix watchers gate on natively — so it's the recommended default. (Members on AGY no longer install cc-watchdog; it stays PI-side, and the watchers remain deferred.) tmux stays fully supported for members who deliberately prefer a keyboard-first multiplexer. |
| Herdr integrations | **members run the installer for each supported client** | `herdr integration install codex` and `herdr integration install opencode` generate client-native hooks without copying PI-specific configuration. AGY currently has no Herdr integration target and simply runs inside a pane. |
| Contract gate — repo list | **the onboarding agent asks; no default list ships** | Which repos to gate is a judgment about where a misread request is expensive, and that varies per member — a list we guessed is one they disable in a week. ONBOARDING step 13 directs the agent to `AskUserQuestion` (multi-select) over the repos the member actually cloned. This is also the *second* member-facing `~/.claude/settings.json` hook after herdr's: it follows the herdr precedent (member runs an installer against their own file) rather than the "left literal" rule, because the hook paths are `~/.claude/skills/...` and carry no PI-personal infra. |
| Silent-stall detection | **cc-watchdog** (`onboarding/watchdog/`): timer-driven dead-man's switch, not hook-driven heuristics | CC-hook watchers only wake at turn ends, so they share the session's blind spot (a 36 h TA die-out in 2026-07 motivated this). Deadlines declared by the session itself make false positives ~zero (a 2.75 h quiet suite run is legitimate work); a 6 h notify-only backstop covers sessions that never declared. It shipped to members while the first pass was Claude Code; on AGY they use the native `/schedule` timer instead (ONBOARDING step 12) and cc-watchdog stays PI-side. It remains standalone (tmux/Herdr + coreutils + systemd user timer + one Slack webhook) for anyone still on Claude Code. |

## Keeping `CLAUDE.global.md` small

It is loaded into the context of every session the member runs, forever, so its size is a
standing tax. Target rough parity with the PI's own `~/.claude/CLAUDE.md` (~7.5 KB / ~1,900
tokens); check with `wc -c` against both when syncing. Three kinds of content have been pulled
out and belong here, not there:

- **Maintainer rationale.** The Skills section used to explain that it once held a list of ~35
  skills, which went stale — an agent reading a stale list keeps trying to invoke skills that no
  longer exist, so the repo is the source of truth instead. That *why* is a maintenance decision;
  the member's file only needs the rule.
- **Duplicated tables.** The four subagent role descriptions live in `onboarding/agents/*.md`.
  Restating model/effort in `CLAUDE.global.md` doubles the cost and creates a second thing to keep
  in lockstep.
- **PI-project war stories.** The probe-the-premise section carried five specific inversions from
  the PI's own runs (the dead channel, the MW that didn't survive the boundary, the empty core).
  They are persuasive to whoever lived them and opaque to a new member.

Conversely, do **not** trim a rule down to nothing to hit the target — when the silent-stall
section was a cut candidate, the right move was rewriting it around AGY's `/schedule` (members
have no `cc-deadman`, so it had been pointing at commands they never installed), not deleting it.

## Deferred — "later" (and how to un-defer)

| Deferred | How to add when ready |
|---|---|
| **Slack skills** (`slack-ask`/`slack-notify`) | Follow the existing Slack section in agent-skills `SETUP.md`: create a bot token, set `~/.claude/.slack-bot-token`, add the `#cc-comm`-style channel + allowlist. |
| **MCP servers** (Gmail/Calendar/Drive/Slack) | The member re-authenticates each connector with their own accounts in Claude Code; nothing to copy. |
| **gbrain** | Run the `/setup-gbrain` skill on the member's host. |
| **Cluster compute** (PBS, exit nodes, institution VPN) | Out of scope by design; the member brings their own cluster creds and writes their own `Remote Dev` notes. |
| **`~/agents` auto-handoff infra** | The full statusline + watcher + handoff cron lives in the PI's `~/agents`; port it deliberately if the member wants auto-handoff. |
| **Contract gate on Antigravity** | ONBOARDING step 13 is Claude-Code-only: the gate returns CC's `permissionDecision: deny` JSON from a `PreToolUse` hook in `~/.claude/settings.json`. Porting means finding AGY's equivalent pre-tool interception under `~/.gemini/config/` and re-emitting the denial in whatever shape AGY expects; `bin/contract` and the note format are agent-agnostic and need no change. Same shape as the statusline port (ONBOARDING step 5). |

## Updating the kit for the next member

1. Re-run the leak/secret scans before any push:
   ```bash
   grep -rnEi 'xoxb-|/home/alon|alondana|100\.118|132\.68|zeus|technion|export [A-Z_]*KEY=[A-Za-z0-9]' onboarding/
   ```
2. If the PI's global instructions, `~/.tmux.conf`, or vault operating manual changed,
   re-sync the genericized copies here.
3. Audit `agent-skills` for client-specific tool names and paths. Test changed skills once in
   Codex and OpenCode, and update their `compatibility` metadata instead of assuming discovery
   means support.
4. Keep the design spec (PI-local, not tracked:
   `docs/superpowers/specs/2026-06-30-mirror-setup-onboarding-design.md`) as the source of
   truth for the decisions above.
