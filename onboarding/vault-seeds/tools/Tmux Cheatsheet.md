---
title: Tmux Cheatsheet
tags: [tools, tmux, ssh, remote-dev]
---

# Tmux Cheatsheet

> Part of [[Tools Index]] · companion to [[Remote Dev — Pattern]] (the SSH / Tailscale side of this same workflow).

> Prefix is **`C-a`** (remapped from default `C-b` in the group `tmux.conf`).
> Press prefix, release, then the command key.

## Mental model
Three nested levels — **session → window → pane**:

```
tmux server
└── session  "cc"              ← named; lives on the remote, survives disconnect (tmux ls)
    ├── window 0  "edit"       ← named, tab-like (the [0] [1]… along the status bar)
    │   ├── pane               ← a split inside the window (C-a % / C-a ")
    │   └── pane  [ZOOMED]     ← C-a z toggles one pane to fullscreen and back
    └── window 1  "logs"
        └── pane
```

- **Session** — the top container you attach to / detach from. Named (`-s name`), persists on the machine until killed. You usually live in one per machine.
- **Window** — a full-screen workspace *within* a session, shown as numbered/named tabs on the status bar. Switch with `C-a 0..9` / `C-a n` / `C-a p`.
- **Pane** — a split *within* a window (side-by-side or stacked). One pane can be **zoomed** to fill the window (`C-a z`) and un-zoomed the same way.

## Sessions
| Action | Command |
|---|---|
| New session | `tmux new -s name` |
| List sessions | `tmux ls` |
| Attach | `tmux attach -t name`  (note the `-t`) |
| Attach, detach others | `tmux attach -d -t name` |
| Attach-or-create | `tmux attach -t name \|\| tmux new -s name` |
| Detach (from inside) | `C-a d` |
| Kill session | `tmux kill-session -t name` |
| Rename session | `C-a $` |

## Windows (tabs)
| Action | Key |
|---|---|
| New window | `C-a c` |
| Next / prev | `C-a n` / `C-a p` |
| Go to window N | `C-a 0..9` |
| Window list (pick) | `C-a w` |
| Rename window | `C-a ,` |
| Kill window | `C-a &` |

## Panes (splits)
| Action | Key |
|---|---|
| Split vertical (side by side) | `C-a %` |
| Split horizontal (stacked) | `C-a "` |
| Move between panes | `C-a ←→↑↓` |
| Cycle panes | `C-a o` |
| **Zoom pane fullscreen (toggle)** | `C-a z` |
| Swap pane position | `C-a {` / `C-a }` |
| Cycle layouts | `C-a space` |
| Resize | `C-a :` then `resize-pane -L/-R/-U/-D 10` |
| Kill pane | `C-a x` |

## Copy / scrollback
| Action | Key |
|---|---|
| Enter copy mode | `C-a [` |
| Scroll | arrows / `PgUp` |
| Start selection | `Space` |
| Copy selection | `Enter` |
| Paste | `C-a ]` |
| Exit copy mode | `q` |

(vi keys active: `setw -g mode-keys vi`)

## Command prompt
`C-a :` then type a command, e.g.:
- `source-file ~/.tmux.conf` — reload config
- `new-window`, `kill-session`
- `refresh-client -S` — fix mirrored/stale window sizing

## SSH + tmux workflow
Run tmux on the **remote** Linux host (your office PC), never the laptop. Full networking
setup — Tailscale, the `ssh <host>` alias — lives in [[Remote Dev — Pattern]].

```bash
# laptop → remote
ssh <linux-host>                      # your tailnet host name
tmux attach -t cc || tmux new -s cc   # reattach or create
claude                                # run Claude Code inside tmux
```

Before an expected disconnect, detach cleanly:
```
C-a d
```
Claude Code keeps running on the office PC. On reconnect, `ssh` back in and `tmux attach -t cc`.

One-liner alias (laptop `~/.bashrc`):
```bash
alias cc-attach='ssh <linux-host> -t "tmux attach -t cc || tmux new -s cc"'
```

## Gotchas
- **Don't nest.** You're already in tmux if `$TMUX` is set or the status bar shows `[name]`. Attaching from inside → "sessions should be nested with care." Detach first (`C-a d`), then attach from a plain shell.
- **`tmux attach name`** fails ("too many arguments") — always use **`-t`**: `tmux attach -t name`.
- **CRLF line endings** break `~/.tmux.conf` ("unknown command" on a seemingly empty line). Files edited/pasted via Windows carry `\r`. Fix: `sed -i 's/\r$//' ~/.tmux.conf` or set editor to LF.
- **Send prefix to inner tmux** (if nested anyway): press prefix twice → `C-a C-a`.
- **Garbled redraw on reattach**: `C-a :` then `refresh-client`.
