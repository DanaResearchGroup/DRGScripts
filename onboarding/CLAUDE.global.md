<!-- Generic group global CLAUDE.md. Merge into ~/.claude/CLAUDE.md. Adjust the vault path to your Dropbox layout. -->

# gstack

For all web browsing, use the `/browse` skill from gstack. Never use `mcp__claude-in-chrome__*` tools.

Available gstack skills:

- `/office-hours`
- `/plan-ceo-review`
- `/plan-eng-review`
- `/plan-design-review`
- `/design-consultation`
- `/design-shotgun`
- `/design-html`
- `/review`
- `/ship`
- `/land-and-deploy`
- `/canary`
- `/benchmark`
- `/browse`
- `/connect-chrome`
- `/qa`
- `/qa-only`
- `/design-review`
- `/setup-browser-cookies`
- `/setup-deploy`
- `/setup-gbrain`
- `/retro`
- `/investigate`
- `/document-release`
- `/document-generate`
- `/codex`
- `/cso`
- `/autoplan`
- `/plan-devex-review`
- `/devex-review`
- `/careful`
- `/freeze`
- `/guard`
- `/unfreeze`
- `/gstack-upgrade`
- `/learn`

# Obsidian Vault

Your Obsidian knowledge vault is at: `$HOME/Dropbox/Vault`
(synced via Dropbox). Use the `obsidian-vault` skill to search/create/manage notes there.

# Subagent preference (global)

Always prefer dispatching subagents (Agent tool, subagent-driven plan execution) over inline execution when possible, to keep the mother session's context window reasonably low.

## Subagent model routing (applies from ANY mother model)

Regardless of which model THIS session runs on, when dispatching a subagent prefer one of the four group role agents (installed in `~/.claude/agents/`, see ONBOARDING step 8) over the generic `general-purpose`/`claude` agent, matching the work to the role. Each role pins its own model + effort, so the routing holds no matter the mother model — a Sonnet, Opus, Fable, or Haiku mother that dispatches `code-implementer` still gets Sonnet, etc.

- **snippet-classifier** (haiku, low) — trivial, low-risk mechanical work: classification, extraction, search/summarization, simple lookups. The cheap janitor.
- **code-implementer** (sonnet, medium) — the DEFAULT worker: well-scoped code changes of known shape, test fixes, routine refactors.
- **architecture-reviewer** (opus, high) — senior judgment: architecture/API design review, cross-cutting tradeoffs, hard tactical review, strategy. "Is this the right design?" not "make this change."
- **project-executor** (fable, high) — a LARGE multi-step mission given as a rough goal (plan → sequence → implement → self-check) that fits within a single session's context.

Boundary — **implementer vs executor** is decided on the scope/autonomy axis: a single well-scoped change of known shape → `code-implementer`; a rough goal that itself needs planning, sequencing, and self-checking → `project-executor`. When unsure, default to `code-implementer`.

Ceiling — `project-executor` is still one subagent dispatch: no `/handoff`, no Phoenix resume, no context-management loop. For genuinely unbounded long-horizon autonomy, use the `autodev` skill on a mother session instead, not this role.

# Superpowers working files (global, all repos)

`docs/superpowers/` (brainstorming specs, implementation plans, and other superpowers
working files) must NEVER be git-tracked or committed in any repo. Treat it as local-only
scratch. When starting work in a repo, ensure `docs/superpowers/` is in `.gitignore`; if any
such file was already staged or committed, untrack it (`git rm --cached`) before proceeding.

# Git history hygiene (global, all repos)

When fixing or amending work that already exists as a commit on the current branch (review-comment fixes, typo fixes, output cleanup), squash the fix into the original commit it amends rather than stacking "address review" / "fix fixes" addition commits — keep one logical change per commit in the final history. ALWAYS ask the user for approval before rewriting history (rebase/squash/amend of existing commits), especially when it requires force-pushing a shared branch.

# Handoff cadence (global)

When the Claude Code context window passes ~35% used, proactively suggest the full handoff cycle:
run `/handoff`, then the user runs `/compact`, then reload from `~/agents/handoffs/.latest` in the
next turn. Surface it as a brief nudge at a natural checkpoint — work committed and green — so a
fresh session can continue cleanly before context gets tight. The user decides whether to act on it.

# Probe the premise before building (global, all repos)

Before building on a premise — what a field actually contains at the read site, whether a channel actually carries flux, whether a data contract survives the boundary it crosses, whether a thing is what it's described as — probe it empirically FIRST. Make premise-probing the mandatory opening step of any non-trivial plan or load-bearing decision, not a per-item habit: dispatch a cheap probe that checks the assumption against the real code/data before writing tasks on top of it. A premise that can't be probed empirically is a design risk to surface, not a footnote.

Treat unverified premises as likely-wrong, not likely-right. Across long arcs of load-bearing checks the probes invert the premise more often than they confirm it (the moments weren't end-of-run; the "healthy" channel was dead; the MW didn't survive the data boundary; the core had zero reactions where the counts implied dozens; the "reference-state-paired" reaction wasn't, in the guard's eyes). A plan built on an unverified premise produces correct implementations of wrong designs — the most expensive failure class, because every downstream review validates against the same false premise.

Corollary — don't build to pass the check. When a guard / test / tripwire refuses your construct, do not reshape the construct to slip under it; a thing built only to make a check go green validates nothing that transfers. Ask first whether the guard caught a real defect (then fix the defect) or exposed a false-positive in itself (then record it as a finding) — not how to get past it.

# Silent-stall prevention (cc-watchdog contract)

Long autonomous sessions must never wait indefinitely on work that could die
silently:

- Run final gates (full test suites, builds) in the mother session as tracked
  background tasks — never owned by a subagent that will stop before the work
  completes.
- Before ending any turn while background/external work is still pending,
  declare a dead-man deadline: `cc-deadman set <expected minutes + 50% margin>
  "<reason>"`.
- First action after resuming from a wait: `cc-deadman clear` (or re-arm for
  the next wait).
- Wrap any command without a natural bound in `timeout`.
