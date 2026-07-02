---
title: API Keys — Local Storage
tags: [tools, setup, security, api-keys]
---

# API Keys — Local Storage

Convention for storing CLI-agent API keys on your local machine. Keys live
**out-of-band** in owner-only files under `~/.config/<vendor>/env`, sourced from
`~/.bashrc`. Keys are **never** committed to git and **never** stored in this Vault
(the Vault syncs to Dropbox).

> First pass uses Claude Code only. The OpenAI/Codex row below is optional — add it
> only if/when you set up Codex.

## Layout

| Tool | Env var | File | Sourced from |
| --- | --- | --- | --- |
| Claude Code | `ANTHROPIC_API_KEY` | `~/.config/anthropic/env` | `~/.bashrc` |
| Codex / OpenAI (optional) | `OPENAI_API_KEY` | `~/.config/openai/env` | `~/.bashrc` |

Each `env` file is a one-liner: `export <VAR>=<key>`.

## Permissions (owner-only)

```bash
chmod 700 ~/.config/anthropic          # dir: only you can list it
chmod 600 ~/.config/anthropic/env      # file: only you can read/write
```

## `~/.bashrc` wiring

```bash
# Claude Code API key — stored out-of-band in ~/.config/anthropic/env (chmod 600)
[ -f ~/.config/anthropic/env ] && source ~/.config/anthropic/env
```

The `[ -f ... ] &&` guard means a missing file is silently skipped (no error on
machines that don't have the key).

## Adding / rotating a key without leaking it to shell history

`read -s` does not echo, and the secret never appears in `history` (only the
`read` command line does):

```bash
read -rs ANTHROPIC_API_KEY \
  && printf 'export ANTHROPIC_API_KEY=%s\n' "$ANTHROPIC_API_KEY" > ~/.config/anthropic/env \
  && chmod 600 ~/.config/anthropic/env \
  && unset ANTHROPIC_API_KEY
# paste the key at the (silent) prompt, press Enter
```

Then reload: `source ~/.bashrc` (or open a new shell) and verify the var is set
**without printing it**: `[ -n "$ANTHROPIC_API_KEY" ] && echo set || echo missing`.

---

Related: [[Tools Index]] · [[Remote Dev — Pattern]]
