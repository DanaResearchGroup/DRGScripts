# Maintaining the onboarding kit

This documents *why* the onboarding kit is shaped the way it is, so a future maintainer
(or a future Claude Code session) can update it for the next member without re-deriving the
decisions. The member-facing runbook is [ONBOARDING.md](./ONBOARDING.md); this file is for
whoever maintains it.

## Purpose

Let a new Dana Research Group member stand up an **independent mirror** of the PI's
Claude-Code working environment from a small set of committed, self-documenting artifacts —
not by copying secrets or by being granted access to the PI's machines.

## Architecture (the mental model the kit assumes)

- **One real environment, on Linux** (the member's office PC). The agent stack — Claude
  Code, agent-skills, superpowers, and a multiplexer (tmux or Herdr) — lives here and only here.
- **Laptops are dual-role ("mixed by purpose"):** thin client (ssh/mosh + `tmux attach`)
  into the Linux box for heavy work, *plus* native Obsidian for notes. A laptop needs only
  tailscale + a terminal + Obsidian.
- **Independent mirror, not shared infra:** the member gets their own tailnet, own Obsidian
  vault, own Claude account. We hand them a recipe, not access.

## Artifact map

| File | Repo | What it does | Touch when… |
|---|---|---|---|
| `bin/cc-statusline.sh` | agent-skills | Context-% status line (model + bar + %). | The statusline JSON schema changes. |
| `UPDATING.md` | agent-skills | CC-executable "update my skills" runbook (plain `git pull`). | The update flow changes. |
| `SETUP.md` (new-member section) | agent-skills | Minimal clone→symlink→statusline path. | Install steps change. |
| `onboarding/ONBOARDING.md` | DRGScripts | Master CC-executable runbook the member points CC at. | Any step in the end-to-end flow changes. |
| `onboarding/CLAUDE.global.md` | DRGScripts | Genericized global CLAUDE.md to merge into `~/.claude/CLAUDE.md`. | The PI's `~/.claude/CLAUDE.md` gains durable guidance worth sharing. |
| `onboarding/vault-structure.md` | DRGScripts | Vault tree + scaffold + which seeds go where. | The vault layout changes. |
| `onboarding/vault-seeds/**` | DRGScripts | Real files copied into the member's vault (operating manual, wiki index, cheatsheets, tmux.conf). | The seeds drift from the PI's (sanitized) originals. |
| `onboarding/dotfiles/tmux.conf` | DRGScripts | The group tmux config. | The PI's `~/.tmux.conf` changes. |
| `onboarding/dotfiles/herdr-config.toml` | DRGScripts | The group Herdr config (for members who use Herdr instead of/besides tmux). | The PI's `~/.config/herdr/config.toml` changes. |
| `ARC/CLAUDE.md` | DRGScripts | Existing ARC project guide — referenced, not duplicated. | (Maintained independently.) |

## Decisions & rationale

| Decision | Choice | Why |
|---|---|---|
| agent-skills | **clone**, not fork | Members track upstream with a plain `git pull`; no fork divergence to manage. |
| User-specific paths | `/home/alon` → **`$HOME`** in agent-skills prose **and** the PI's `~/.claude/CLAUDE.md` | An agent reading prose expands `$HOME`; works identically for the PI; removes any "personalize" step. |
| `~/.claude/settings.json` | **left literal** | Its paths are personal infra (`~/agents` auto-handoff, the gstack **session-update hook**, gitkraken marketplace) the member never gets; Claude Code does **not** reliably shell-expand `$HOME` in non-command fields (e.g. `extraKnownMarketplaces.path`). Risk > benefit. **NB:** this is the settings.json *hook* only — the gstack **skills** themselves *are* member-facing and are installed in ONBOARDING step 6. |
| gstack **skills** | **member installs** in ONBOARDING step 6 | `CLAUDE.global.md` and the smoke test reference `/browse`, `/review`, `/ship`, … — so gstack must be part of the member setup, not PI-only. It's a separate repo ([garrytan/gstack](https://github.com/garrytan/gstack)) cloned into `~/.claude/skills/gstack`; git-ignored inside agent-skills. |
| Obsidian sync | **Dropbox desktop client only; no remotely-save** | No mobile/phone requirement → filesystem sync is enough. One fewer plugin. |
| Statusline | the **simple context-% script**, not the PI's `~/agents` auto-handoff variant | Self-contained; no extra infra to stand up. |
| Seeds | **sanitized**, real files under `vault-seeds/` | Easy `cp` into place; the PI's real remote-dev note (tailnet IPs, VPN endpoint, cluster/exit-node config) is excluded — a generic `Remote Dev — Pattern` replaces it. |
| First pass | **Claude Code only** | Smaller surface; the deferred list below grows it later. |
| Multiplexer | **Herdr recommended; tmux also supported** (ONBOARDING step 7) | Herdr is agent-state-aware (mouse-first sidebar showing each agent's live state), which the cc-watchdog guard and the agent-skills auto-handoff/Phoenix watchers gate on natively — so it's the recommended default. tmux stays fully supported for members who deliberately prefer a keyboard-first multiplexer. |
| Herdr `settings.json` hook | **member runs `herdr integration install claude`** | Unlike the PI's literal settings.json, the herdr agent-state hook is generated by the installer into the member's own `~/.claude/settings.json` — no personal infra to copy. |
| Silent-stall detection | **cc-watchdog** (`onboarding/watchdog/`): timer-driven dead-man's switch, not hook-driven heuristics | CC-hook watchers only wake at turn ends, so they share the session's blind spot (a 36 h TA die-out in 2026-07 motivated this). Deadlines declared by the session itself make false positives ~zero (a 2.75 h quiet suite run is legitimate work); a 6 h notify-only backstop covers sessions that never declared. Unlike the PI-local auto-handoff/Phoenix stack, this ships to members: standalone (tmux/Herdr + coreutils + systemd user timer + one Slack webhook). |

## Deferred — "later" (and how to un-defer)

| Deferred | How to add when ready |
|---|---|
| **Codex** | Re-introduce the `~/.codex/skills` wiring; add a Codex section to ONBOARDING. The agent-skills repo is already agent-agnostic (see `ADAPTATION.md`). |
| **Slack skills** (`slack-ask`/`slack-notify`) | Follow the existing Slack section in agent-skills `SETUP.md`: create a bot token, set `~/.claude/.slack-bot-token`, add the `#cc-comm`-style channel + allowlist. |
| **MCP servers** (Gmail/Calendar/Drive/Slack) | The member re-authenticates each connector with their own accounts in Claude Code; nothing to copy. |
| **gbrain** | Run the `/setup-gbrain` skill on the member's host. |
| **Cluster compute** (PBS, exit nodes, institution VPN) | Out of scope by design; the member brings their own cluster creds and writes their own `Remote Dev` notes. |
| **`~/agents` auto-handoff infra** | The full statusline + watcher + handoff cron lives in the PI's `~/agents`; port it deliberately if the member wants auto-handoff. |

## Updating the kit for the next member

1. Re-run the leak/secret scans before any push:
   ```bash
   grep -rnEi 'xoxb-|/home/alon|alondana|100\.118|132\.68|zeus|technion|export [A-Z_]*KEY=[A-Za-z0-9]' onboarding/
   ```
2. If the PI's `~/.claude/CLAUDE.md`, `~/.tmux.conf`, or vault operating manual changed,
   re-sync the genericized copies here.
3. Keep the design spec (PI-local, not tracked:
   `docs/superpowers/specs/2026-06-30-mirror-setup-onboarding-design.md`) as the source of
   truth for the decisions above.
