# CLAUDE.md — Knowledge Base Operating Manual

This Obsidian vault is a **persistent, compounding wiki**, not a RAG dump. Raw sources
come in; you read them, extract what matters, and **integrate** that knowledge into a
living, interlinked set of wiki pages. Knowledge is compiled once and kept current — not
re-derived from scratch on every question.

Your job is to keep the wiki the single best representation of everything that has been
read. When a new source arrives, the wiki should get richer: entities gain detail, topic
summaries get revised, contradictions get flagged, cross-links multiply.

> **Default working area: `knowledge/`.** Read from and write to `knowledge/` for all
> knowledge-base work. Source material goes in `knowledge/raw/`; every page you author goes in `knowledge/wiki/`. Do **not** create or modify notes elsewhere in the vault
> (`Projects/`, `Meetings/`, `Strategy/`, `Thoughts/`, etc.) unless the user explicitly asks. When a
> source or request doesn't say where something belongs, it belongs in `knowledge/`.

> **Vault-wide rule — always use proper links.** This applies to *every* note you create
> or edit anywhere in the vault, not just `knowledge/`. Never leave a note as an orphan
> (nothing links to it, it links to nothing) — those float disconnected in Obsidian's
> graph view. Whenever you write or touch a note:
> - Use Obsidian `[[wikilinks]]` (not bare text or Markdown `[]()` links) to reference
>   other notes, people, concepts, projects, and topics.
> - Link the first mention of anything that has — or should have — its own note.
> - Make links **bidirectional in spirit**: when you link a note into a parent/hub, also
>   add it to that hub's list (e.g. a new sub-page links to its parent `[[Parent Topic]]`
>   *and* is listed on the `Parent Topic` page) so both ends connect in the graph.
> - Match link text to the target note's exact title (use `[[Title|display text]]` if you
>   need different wording). A link to a not-yet-created note is fine — it's a useful stub.
> - If you create a note that has no natural home, connect it to the nearest relevant hub
>   or index note rather than leaving it isolated.

---

## 1. Where things live

```
knowledge/
  raw/                  ← incoming source material, grouped into topic subfolders
    <topic>/            ← e.g. grid-storage/, carbon-policy/ — one folder per theme
      <source>.md
  wiki/                 ← the compiled, interlinked knowledge base (you maintain this)
```

- **`knowledge/raw/`** — never rewrite the content of a source. It is the immutable record
  of what was actually said. You may rename for clarity and add a short header (see §5).
  - **Group sources by topic, not by file type.** Put each source in a
    `raw/<topic>/` subfolder named for its theme (`raw/grid-storage/`,
    `raw/carbon-policy/`). Do **not** sort by format (no `raw/pdfs/`, `raw/articles/`).
  - Use lowercase-kebab-case topic folders. Reuse an existing topic folder when one fits
    rather than spawning a near-duplicate; create a new one only for a genuinely new theme.
  - A source that spans two topics goes in the best-fit folder — the wiki's cross-links,
    not the raw folder, capture the overlap. Date-prefix files when ordering helps
    (`2026-03-grid-storage-report.md`).
  - The `raw/` topic folders mirror the themes that become `wiki/topics/` pages — keeping
    the names aligned makes provenance easy to trace.
- **`knowledge/wiki/`** — everything you author. Organized by page type (below).

Leave the rest of the vault (`Projects/`, `Meetings/`, `Strategy/`, `Thoughts/`, etc.) alone unless
explicitly asked. This manual governs `knowledge/` only.

---

## 2. Page types

Every wiki page is exactly one of these. Put the type in frontmatter.

| Type      | Purpose                                              | Folder                 |
|-----------|------------------------------------------------------|------------------------|
| `entity`  | A person, org, place, product, concept, term         | `wiki/entities/`       |
| `topic`   | A synthesized summary of a theme across many sources  | `wiki/topics/`         |
| `source`  | One note per ingested source: summary + provenance   | `wiki/sources/`        |
| `index`   | A map-of-content (MOC) hub linking related pages      | `wiki/` (root of wiki) |

Create these subfolders on first use. Start with `wiki/index.md` as the home MOC.

---

## 3. Page structure & conventions

### Frontmatter (every wiki page)
```yaml
---
type: entity | topic | source | index
title: Human Readable Title
aliases: [other names, abbreviations]   # so links resolve; omit if none
created: YYYY-MM-DD
updated: YYYY-MM-DD                       # bump every time you touch the page
sources: ["[[source-note-name]]", ...]   # which source notes back this page
status: stub | developing | stable        # how settled the synthesis is
---
```

### Body conventions
- **Filenames**: lowercase-kebab-case, descriptive (`carbon-border-adjustment.md`).
  The `title` frontmatter carries the pretty name.
- **Links**: use `[[wikilinks]]` liberally. Link the first mention of any entity/topic
  that has (or should have) its own page. A link to a page that doesn't exist yet is a
  *good thing* — it marks a stub to create later.
- **No Dataview**: this vault has no Dataview plugin. Do not write ```dataview``` queries.
  Maintain index/MOC pages by hand with plain wikilinks.
- **Every claim is traceable.** When you assert something, make it possible to find which
  source it came from — either via the `sources:` frontmatter, an inline `([[source]])`,
  or a `## Sources` section at the bottom. No orphan claims.
- **Write the synthesis, not a transcript.** Topic/entity pages are *your* compiled
  understanding in prose, not pasted quotes. Quote only when the exact wording matters.
- **Headings**: keep pages skimmable. Lead with a 1–3 sentence summary, then detail.

### Entity page skeleton
```markdown
## Summary
One paragraph: what/who this is and why it matters.

## Key facts
- ... ([[source]])

## Relationships
- Works with [[other-entity]]; part of [[topic]].

## Open questions / contradictions
- ...

## Sources
- [[source-note-name]]
```

### Topic page skeleton
```markdown
## Summary
The current best synthesis in 2–5 sentences.

## What we know
Prose synthesis, linking entities and citing sources inline.

## Tensions & contradictions
- Source A claims X ([[a]]); Source B claims not-X ([[b]]). Current read: ...

## Open questions
- ...

## Sources
- [[a]] · [[b]]
```

### Source note skeleton (`wiki/sources/`)
```markdown
## Provenance
- Original: [[../raw/<file>]] (or URL)
- Author / publisher: ...
- Date of source: YYYY-MM-DD   |   Ingested: YYYY-MM-DD

## Summary
3–6 sentences capturing the source's core claims.

## Extracted points
- Claim → which wiki page it updated ([[page]]).

## Contradicts / confirms
- Confirms [[topic]] on X. Contradicts [[entity]]'s claim that Y.
```

---

## 4. Linking & contradiction policy

- **Bidirectional in spirit**: if page A links B because they're related, make sure B is
  reachable from A's neighborhood (an index, a "Relationships" line). Don't create
  dead-end pages.
- **Contradictions are first-class.** Never silently overwrite an older claim with a newer
  one. Record both, attribute each to its source, date them, and write your current best
  judgment. Old claims that turn out wrong get struck through with a note, not deleted —
  the reasoning trail has value.
- **Stubs are welcome.** A `[[link]]` to a not-yet-written page is a to-do, not an error.

---

## 5. Processing a new source — the core loop

When asked to ingest something (a file dropped in `knowledge/raw/`, a URL, pasted text):

1. **Capture the raw.** Ensure the original lives in the right topic subfolder —
   `knowledge/raw/<topic>/`. Reuse an existing topic folder if one fits; create a new
   `raw/<topic>/` only for a genuinely new theme (and ask the user if the right topic is
   unclear). If it came as a URL or paste, save a copy there. Add a one-line header
   (source, date) only — don't alter the body.
2. **Read it fully.** Understand it before writing anything.
3. **Create the source note** in `wiki/sources/` using the skeleton in §3. This is the
   provenance anchor for every claim you're about to integrate.
4. **Integrate, don't append.** For each key point:
   - Find the relevant entity/topic page. **Update it in place** — revise the summary,
     add the fact, strengthen or weaken the synthesis.
   - If no page exists, create one (start as `status: stub` if thin).
   - Add `[[wikilinks]]` between newly related pages.
5. **Reconcile contradictions.** Where the new source disagrees with existing pages, apply
   the §4 policy — record both sides, attribute, judge.
6. **Update affected indexes/MOCs.** Add new pages to the relevant `index` page so they're
   reachable.
7. **Bump `updated:`** on every page you touched, and list the new source in their
   `sources:`.
8. **Report.** Summarize for the user: which pages were created/updated, what
   contradictions surfaced, what stubs are now waiting.
9. **Log learnings.** At the end of a working session, update [[learnings.md]] (see §6).

> The test of a good ingestion: a later question that spans several sources should be
> answerable by reading the wiki, with the contradictions already flagged and the
> cross-references already in place — without re-reading the raw sources.

---

## 6. End-of-session learnings

After each session, append to `learnings.md` at the vault root. Record what worked, what
didn't, and any convention you and the user converged on, so the next session starts
smarter. Keep it honest — failures and dead-ends are the most valuable entries.

---

## 7. Operating principles

- **Compound, don't restate.** Each session should leave the wiki measurably richer.
- **Faithful provenance over tidy prose.** If you're unsure where a claim came from, say so
  rather than inventing a citation.
- **Prefer revising an existing page to creating a near-duplicate.** Check aliases/links
  first. One canonical page per entity/topic.
- **Ask when ambiguous.** If a source could update several pages or implies a structural
  change, surface the choice rather than guessing.
- **Small, reviewable changes.** Tell the user what you changed and why.
