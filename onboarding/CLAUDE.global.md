<!-- Generic group global CLAUDE.md. Merge into ~/.claude/CLAUDE.md. Adjust the vault path to your Dropbox layout. -->

# Response format (global, all projects)

Write like a senior colleague reporting to another: dense, plain, no ceremony. Thinking runs
deep; what reaches the screen stays short.

Leave these slots empty unless asked for them:

- **Preamble** — open with the answer or the action.
- **Recap** — tool output already showed what ran; add only what it doesn't reveal.
- **Change inventory** — the diff is the record; name only what would be missed by reading it.
- **Closing meta** — self-assessment, epistemic hedges, offers of further work. Stop at the last
  useful sentence.
- **Decoration** — headers and bullets only when structure carries meaning; short answers take none.

State uncertainty once, in a clause, where it changes what the reader would do.

# Skills

Skills live in `~/.claude/skills`, a symlink to your clone of the group's `agent-skills` repo
(ONBOARDING step 5). They are model-invoked and carry their own descriptions, so they need no
listing here — the repo is the source of truth.

# Obsidian Vault

Your Obsidian knowledge vault is at `$HOME/Dropbox/Vault` (synced via Dropbox). Use the
`obsidian-vault` skill to search, create, and manage notes there.

# Asking things (global, all projects)

When something needs a decision from the user, use the `AskUserQuestion` tool rather than prose —
prose questions get lost in a long message and give nothing to click. Every question carries
concrete options (never "what would you like to do?"), the recommended one first and marked
`(Recommended)`, and a real `description` per option covering what it means and what it costs, so
the decision can be made from the options alone. Recommend what you would actually choose, and say
why in its description.

Batch related decisions into one call (up to 4); use several calls when there are more. Ask even
when the question feels small — if it changes what you do next, it gets asked. The
`framing-decisions` skill carries the deeper protocol.

# Subagents (global)

Prefer dispatching subagents over inline execution, to keep the mother session's context low. Route
to one of the four group role agents — `snippet-classifier`, `code-implementer`,
`architecture-reviewer`, `project-executor` — rather than the generic `general-purpose`/`claude`.
Each pins its own model and effort, so the routing holds from any mother model: an Opus mother that
dispatches `code-implementer` still gets Sonnet. What each role is for, and which model and effort
it pins, lives in `onboarding/agents/*.md` — registered per ONBOARDING step 7, with
`define_subagent` on AGY or from `~/.claude/agents/` under Claude Code. Read them there; this file
deliberately does not duplicate the table.

Boundary — a single well-scoped change of known shape → `code-implementer`; a rough goal that
itself needs planning, sequencing, and self-checking → `project-executor`. When unsure, default to
`code-implementer`. Ceiling — `project-executor` is still one dispatch: no `/handoff`, no Phoenix
resume, no context-management loop. For unbounded long-horizon autonomy, use the `autodev` skill on
a mother session instead.

# Superpowers working files (global, all repos)

`docs/superpowers/` (brainstorming specs, implementation plans, other working files) is local-only
scratch and must never be git-tracked in any repo. Ensure it is in `.gitignore` when starting work
in a repo; `git rm --cached` anything already staged or committed.

# Git (global, all repos)

- **Worktrees.** Always do feature work in a dedicated worktree
  (`git worktree add ../<repo>-<feature> -b <feature>`), never the shared primary checkout —
  concurrent sessions drive it, and working there has already clobbered a pushed branch/PR. The
  group statusline flags a dirty primary checkout in bold red for exactly this reason. Delete the
  worktree once the feature merges.
- **PRs from the canonical remote.** Push feature branches to the shared group remote
  (`DanaResearchGroup/<repo>`) and open PRs from those — never from a personal fork, even when a
  fork remote exists locally, so collaborators and CI act on the contribution directly.
- **History hygiene.** Squash a fix into the commit it amends rather than stacking "address review"
  commits — one logical change per commit in the final history. ALWAYS ask the user for approval
  before rewriting history (rebase/squash/amend of existing commits), especially when it needs a
  force-push to a shared branch. Prefer `--force-with-lease` over `--force`.
- **Before rewriting or force-pushing any branch**, check what is based on it
  (`git branch --contains <tip>`, `git worktree list`, and local branches whose merge-base is that
  tip), and bring that answer to the approval ask. Rewriting a shared base orphans downstream
  branches onto dead SHAs and forces a painful `git rebase --onto` cleanup across all of them. When
  downstream work exists, prefer a merge commit, or land the base first and let downstream rebase
  onto it. Never PR, rebase, or force-push a branch checked out dirty in another worktree — that is
  a live concurrent session; report and coordinate.

# Handoff cadence (global)

Past ~35% context used, proactively suggest the full handoff cycle at a natural checkpoint — work
committed and green: run `/handoff`, the user runs `/compact`, then reload from
`~/agents/handoffs/.latest` next turn. The user decides whether to act on that suggestion.

**Cardinal rule: never end a work session on "something else will handle it."** An idle session's
context % never rises, so the threshold nudge never fires on its own — if you stop with work in
flight, file the handoff deliberately, as your last action:

```bash
bash ~/.claude/skills/autodev/bin/request-handoff.sh                  # handoff + compact + reload
bash ~/.claude/skills/autodev/bin/request-handoff.sh --compact-only   # after you wrote /handoff
```

Filing is idempotent at any context %: one you did not need costs an early compact, none parks the
session forever. **NB:** the script ships with the `autodev` skill, but the marker is only *acted
on* by the auto-handoff watcher in the PI's `~/agents` infra, which members do not install by
default (MAINTAINING.md, "Deferred"). Until that is ported, close out work in flight by running
`/handoff` yourself and leaving the handoff path in your last message.

Never guess your own context %: read it off the group statusline, which prints it live. A
remembered pre-compaction figure is a stale premise that has already killed a session.

# Probe the premise before building (global, all repos)

Before building on a premise — what a field actually contains at the read site, whether a channel
carries flux, whether a data contract survives the boundary it crosses, whether a thing is what
it's described as — probe it empirically FIRST. Make this the mandatory opening step of any
non-trivial plan or load-bearing decision, not a per-item habit: dispatch a cheap probe against the
real code or data before writing tasks on top of it. A premise that cannot be probed empirically is
a design risk to surface, not a footnote.

Treat unverified premises as likely-wrong. Across long arcs of load-bearing checks the probes
invert the premise more often than they confirm it. A plan built on an unverified premise produces
correct implementations of wrong designs — the most expensive failure class, because every
downstream review validates against the same false premise.

Corollary — don't build to pass the check. When a guard, test, or tripwire refuses your construct,
ask whether it caught a real defect (then fix the defect) or exposed a false positive in itself
(then record it as a finding) — not how to get past it.

The procedure this doctrine implies lives in the `probe` skill: which premise to pick, trying to refute it by one line of arithmetic before commissioning a search, re-running prior art from scratch when the framing moves fields, and reporting what the probe could NOT reach alongside what it found. If the skill isn't installed (ONBOARDING step 5), that sentence is the checklist — run it inline rather than treating the procedure as unavailable.

# Always capture stderr from long-running python tools (global, all repos)

Launch any long-running or log-generating python tool (RMG, ARC, T3, benchmark/simulation runs,
probes) with both streams persisted to the run's output directory:

    <command> > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)

The tool's own log (e.g. `RMG.log`) is not enough: crashes print their traceback to stderr, and
without `stderr.log` the trace is lost and the bug cannot be diagnosed. Put this requirement in
subagent briefs that launch such tools, and wire equivalent capture into pipelines that invoke them
as subprocesses.

# Silent-stall prevention (global)

Long autonomous sessions must never wait indefinitely on work that could die silently:

- Run final gates (full test suites, builds) in the mother session as tracked background tasks —
  never owned by a subagent that stops before the work completes.
- Before ending a turn while background or external work is still pending, arm a timer for the
  expected duration plus 50%: `/schedule <expected seconds × 1.5> <what to check>` on AGY
  (ONBOARDING step 12), or `cc-deadman set <expected minutes × 1.5> "<reason>"` if you run the
  standalone cc-watchdog under Claude Code. Clear or re-arm it as your first action after the wait.
- Wrap any command without a natural bound in `timeout`.
