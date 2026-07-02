# Obsidian vault — structure & scaffold

How a new member's Obsidian vault should be laid out, and how to seed it. The member's
Claude Code runs this as part of [ONBOARDING.md](./ONBOARDING.md).

## Target tree

```
Vault/
├── CLAUDE.md              ← knowledge-base operating manual (seeded)
├── Code/
│   ├── ARC/
│   └── T3/
├── knowledge/
│   ├── raw/
│   └── wiki/
│       └── index.md       ← map-of-content home (seeded)
├── tools/                 ← cheatsheets (seeded)
├── Projects/
├── Meetings/
├── Strategy/
└── Thoughts/
```

The agent's **default working area is `knowledge/`** (see the seeded `CLAUDE.md`). The
other folders are yours to fill as you go.

## 1. Pick your vault path

Store the vault inside your Dropbox folder so the desktop client syncs it across machines
(no remotely-save / mobile plugin needed). Adjust to your Dropbox layout:

```bash
VAULT="$HOME/Dropbox/Vault"
```

## 2. Scaffold the folders

```bash
mkdir -p "$VAULT"/{Code/ARC,Code/T3,knowledge/raw,knowledge/wiki,tools,Projects,Meetings,Strategy,Thoughts}
```

## 3. Copy the seed files

Seed files live next to this doc under `vault-seeds/`, mirroring the vault layout. From a
clone of this repo:

```bash
SEEDS="<path-to-DRGScripts-clone>/onboarding/vault-seeds"
cp -n "$SEEDS/CLAUDE.md"                       "$VAULT/CLAUDE.md"
cp -n "$SEEDS/knowledge/wiki/index.md"         "$VAULT/knowledge/wiki/index.md"
cp -n "$SEEDS/tools/"*.md                      "$VAULT/tools/"
```

`cp -n` won't overwrite anything you've already created.

## 4. Open it in Obsidian

Open Obsidian → "Open folder as vault" → select `$VAULT`. On each laptop, point the
Dropbox client at the same folder and open the same vault there. No remotely-save plugin
— the Dropbox desktop client handles filesystem sync.

## What the seeds are

| Seed | Becomes | Notes |
|---|---|---|
| `vault-seeds/CLAUDE.md` | `Vault/CLAUDE.md` | The knowledge-base operating manual (how the wiki is built, page types, the ingestion loop). |
| `vault-seeds/knowledge/wiki/index.md` | `knowledge/wiki/index.md` | Generalized map-of-content — empty topic/entity/source lists you grow. |
| `vault-seeds/tools/Tmux Cheatsheet.md` | `tools/Tmux Cheatsheet.md` | Generic tmux reference keyed to the group `tmux.conf` (prefix `C-a`). |
| `vault-seeds/tools/Remote Dev — Pattern.md` | `tools/Remote Dev — Pattern.md` | Generic laptop→host pattern with `<placeholders>` — fill in your own tailnet host. |
| `vault-seeds/tools/API Keys — Local Storage.md` | `tools/API Keys — Local Storage.md` | Out-of-band key-storage convention (no secrets — a how-not-to-leak guide). |
| `vault-seeds/tools/Tools Index.md` | `tools/Tools Index.md` | Hub linking the tools notes. |

> These seeds are **sanitized**. The PI's real remote-dev note (specific tailnet IPs, VPN
> endpoints, cluster/exit-node config) is intentionally **not** included — the generic
> `Remote Dev — Pattern` replaces it.
