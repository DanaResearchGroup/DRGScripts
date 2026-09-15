# Status lines

This directory contains the Claude Code status-line installer below and the optional
[Codex dual-budget enhancement](./codex/README.md). OpenCode currently exposes usage through
its TUI and `opencode stats` rather than a configurable footer command.

## Claude Code

A one-line status line that tells you, at a glance, **which model** you're on,
**how full the context window is** (colour-coded), and **where you are in git**
— repo, branch, and whether you're in a worktree or the primary checkout.

```
Opus 4.8  12.3k  (18.4%)   agent-skills@my-feature*  [wt:agent-skills-feature]
└─model   └─ctx  └─context  └─repo    └─branch └─dirty  └─you're in a worktree
          tokens    used %          (main repo name)     (uncommitted changes)
```

## What each part means

| Segment | Meaning |
|---|---|
| `Opus 4.8` | Model display name (trailing `(…)` qualifiers stripped). |
| `12.3k` | Total input tokens in context. |
| `(18.4%)` | Context-window used, **colour-coded**: green `<25%`, yellow `25–40%`, **bold red `≥40%`** (40% is roughly where a handoff pays off). |
| `repo@branch` | Repo name (cyan) and current branch (yellow). The repo name is the *main* repo, so it stays stable even inside a worktree. Detached HEAD shows a short SHA. |
| `*` | Red — the working tree has uncommitted changes. |
| `[wt:name]` | Magenta — you're in a linked **worktree** (the group default for feature work). |
| `[primary]` | Dim — you're in the **primary checkout**, clean. |
| `[!primary]` | Bold red — you're **editing the primary checkout** (dirty). That's the anti-pattern the "work in a worktree" rule warns against, so it's flagged loudly. |

Outside a git repo, the whole location segment is simply omitted.

## Prerequisites

- **jq** and **git** (git optional — without it, only model + context % show).
- The **agent-skills** repo cloned and symlinked as `~/.claude/skills`
  (ONBOARDING step 5). The status line script itself lives there
  (`bin/cc-statusline.sh` + `bin/lib/cc-statusline-lib.sh`); this folder only
  wires it into your settings.

## Install

```bash
cd ~/Code/DRGScripts/onboarding/statusline
./install.sh
```

The installer finds the group `cc-statusline.sh` (in `~/.claude/skills/bin/`),
makes it executable, and points `~/.claude/settings.json` at it. It is
**surgical** — it only sets the `.statusLine` key, backs the file up first
(`settings.json.bak.<timestamp>`), and is idempotent (re-running is a no-op).

Then **restart Claude Code** (or start a fresh session) — a running session
reads its status-line command at launch.

Pass an explicit path if auto-detect can't find it:

```bash
./install.sh ~/Code/agent-skills/bin/cc-statusline.sh
```

## Customising

Colours and thresholds live in one place —
`~/.claude/skills/bin/lib/cc-statusline-lib.sh`:

- `cc_ctx_color` — the `<25 / <40 / else` percentage bands and their colours.
- `cc_location` — the repo/branch/worktree glyphs and colours.

Because agent-skills is a plain clone you keep current with `git pull` (or
*"update my agent-skills"*), heavy local edits will conflict on update — prefer
proposing changes upstream.

## Troubleshooting

- **No status line at all** → restart the session; confirm
  `jq -r '.statusLine' ~/.claude/settings.json` shows the command.
- **Location segment missing** → you're not in a git repo, `git` isn't
  installed, or agent-skills predates the shared lib (`git pull` it).
- **Colours look like `\033[...`** → your terminal isn't interpreting ANSI;
  the markers are plain ASCII (`@ * [wt:…]`) so the text still reads fine.
- **Slow in a huge repo** → the dirty check runs `git status`; it's fine for
  the group's script repos, negligible next to Claude Code's refresh throttle.

## Uninstall / revert

Restore the backup the installer made, or point `.statusLine` elsewhere:

```bash
cp ~/.claude/settings.json.bak.<timestamp> ~/.claude/settings.json
```

## Relationship to the PI's status line

The PI runs a superset variant (`autodev/bin/cc-statusline.sh`) that adds the
auto-handoff / Phoenix badge on top of this exact rendering — both source the
same `bin/lib/cc-statusline-lib.sh`, so the model/context/location part never
drifts between them. Members get the clean version with no `~/agents` infra to
stand up.
