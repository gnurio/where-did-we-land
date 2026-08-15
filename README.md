# where-did-we-land

Turns a meeting transcript into one self-contained HTML file: topic timeline, a ledger of where every
thread landed with the quote that proves it, open loops, commitments, stances, and airtime.

Plain HTML on disk. No publishing, no hosting, no server, no build step, no dependencies — open it by
double-clicking, mail it, drop it in a repo. The only capability the skill needs is file read/write.

```
/where-did-we-land ~/Downloads/product-sync.txt
→ ~/Downloads/product-sync-ledger.html
```

## Install

```bash
git clone https://github.com/gnurio/where-did-we-land.git \
  ~/.claude/skills/where-did-we-land
```

| Harness | Where to put this folder |
|---|---|
| Claude Code | `~/.claude/skills/where-did-we-land/` (global) or `.claude/skills/…` (per project) |
| Cursor | `.cursor/rules/` — or keep it anywhere and say "follow SKILL.md in ./where-did-we-land" |
| Cowork | upload the folder; reference `SKILL.md` in the prompt |
| Codex | keep it in the repo; point at `SKILL.md` from `AGENTS.md` or the prompt |

## Getting a transcript in

Run it with no argument and it goes looking. Pasting is the last resort, not the first move.

| # | Rung | Needs |
|---|---|---|
| 1 | **Explicit input** — a path, a share URL, or pasted text | nothing |
| 2 | **Local disk sweep** — `~/Downloads`, `~/Documents/Zoom`, a synced `Meet Recordings/`, recognising Zoom's `GMT…transcript.vtt` and Teams' `.vtt` alongside its `.docx` | filesystem |
| 3 | **A share link** — Otter, Fathom, Grain, tl;dv pages are usually public and fetchable | web fetch |
| 4 | **MCP adapters** — Granola meetings, Google Drive for Meet transcript Docs, Gmail for notetaker recap emails | that MCP |
| 5 | **Ask** — naming what it already checked | — |

`reference/sources.md` holds the filename patterns, which links are auth-walled (Zoom share links and
SharePoint are — ask for the `.vtt`), and the exact MCP searches.

### Formats it accepts

Every meeting tool exports one of five shapes, so five parsers cover the market. `reference/formats.md`
holds the detection and normalisation rules.

| Shape | Looks like | From |
|---|---|---|
| Speaker-header block | `Thor Galle 0:49` then the speech below | **Otter**, Google Meet Docs, Descript |
| WebVTT | `00:00:05.790 --> …` then `Christina: …` or `<v John Smith>…</v>` | **Zoom**, **Teams**, Avoma, Grain |
| SRT | same cues, comma decimals | Otter, Fireflies, Grain, Descript |
| Inline label | `[00:05:32] Alice: …` or `**Sarah (00:00):** …` | Granola exporters, Fireflies MD, tl;dv, Krisp |
| JSON | `{"speaker":…,"text":…,"start_time":…}` | Granola, Fathom, Circleback, Fireflies, Read.ai APIs |

**The one that bites:** VTT, SRT and per-utterance JSON emit a cue every few seconds, so a single
400-word monologue arrives as forty entries. They must be merged back into turns first or the turn
count inflates 10–20× and the airtime chart becomes meaningless. The skill checks its own work: a
20-minute two-person conversation should land around 40–120 turns.

**Rejected outright:** Teams plain-text via Graph (strips speaker attribution entirely — ask for the
`.vtt`), Granola "Copy Notes" (copies the summary, not the transcript), Supernormal imported
recordings (monologue-formatted, no speaker separation).

### The single-speaker check

Roughly two-thirds of a typical Granola library is solo voice notes, not conversations. Those have no
stances, no agreements and no open loops between people, so the skill stops and offers a summary
instead of rendering a page that implies a meeting happened. This matters most when running
unattended.

## Running it automatically

There is no built-in hook — Granola has no local file to watch. Wire it as a scheduled agent that
polls for new meetings:

```
/schedule create "Every weekday at 6pm, list Granola meetings from today.
  For each one with two or more speakers who take turns, run the
  where-did-we-land skill and write the .html into ~/Meetings/ledgers/.
  Skip single-speaker voice notes silently. Report only the file paths."
```

Expect it to skip most days. On a typical month it fires on 2–4 meetings — work 1:1s, workshops, and
messy multi-party calls. That is the honest hit rate; the value is that the ones it catches are the
ones you would otherwise never reconstruct.

## What the page keeps, and what it throws away

The generated file holds **word counts, not words**. `turns` carries
`[speaker, seconds, wordCount]`, so the charts and talk share are exact while the transcript itself
never leaves your machine. The only verbatim text on the page is the handful of quotes chosen as
receipts — typically a dozen or two lines out of several thousand words.

Share the ledger and you share those quotes. You do not share the meeting.

## Files

- `SKILL.md` — the procedure
- `template.html` — the page; renders from the JSON block at its top
- `reference/formats.md` — the five transcript shapes, and the merge rule
- `reference/sources.md` — the acquisition ladder
- `scripts/check_ledger.py` — structural checks on any generated ledger
- `evals/` — trigger and behaviour scenarios

## Checking a ledger

```bash
python3 scripts/check_ledger.py out-ledger.html [transcript.txt]
```

Asserts that no transcript leaked, that the turn count is plausible for the duration (an unmerged VTT
fails loudly here), that every thread carries a state and a receipt, that every unresolved thread
reached the open-loops table, and that the timeline geometry is sane. Pass the source transcript too
and it also confirms every quote appears verbatim — the one check that catches an invented receipt.

Exits non-zero on failure.

## Editing the look

Colour lives in the `:root` custom properties at the top of `template.html`. Speakers draw from
`--indigo` then `--ink-dark`; `--teal-text` marks landed threads, `--muted` open, `--ink` dropped.
Light mode only, by design. Type is Sora for display and Inter for everything else, loaded from Google
Fonts with a system-grotesque fallback — the page renders correctly offline, just without Sora.

All text colours are checked against the 4.5:1 floor on white. If you swap the palette, re-check:
the design-system muted grey `#868A97` measures 3.44:1 and fails, which is why the text step is
`#626673`.

## What it will not do

Infer a state it cannot quote. Where the transcript is genuinely unclear the page says
`No explicit answer` rather than guessing a decision — which is the entire point of the evidence
column.
