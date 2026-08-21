---
title: Browser Auto-Open and Dynamic Tab Title - Plan
type: feat
date: 2026-08-21
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-plan-bootstrap
execution: code
---

# Browser Auto-Open and Dynamic Tab Title - Plan

## Goal Capsule

- **Objective:** The `where-did-we-land` skill auto-opens the ledger it generates in the system browser, and the ledger's browser tab title carries the meeting's participants, date, and topic instead of the static string "Where did we land?".
- **Authority hierarchy:** This plan's Key Technical Decisions govern implementation mechanism. Existing repo conventions (`skills/where-did-we-land/SKILL.md` prose style, `template.html`'s helper functions, `check_ledger.py`'s `Report`/`check_*` pattern) govern style within that mechanism.
- **Stop conditions:** Stop and ask if implementation would require changing `D.meta.title` or `D.meta.headline` rendering (template.html:309-310) — those must stay untouched per R4/KTD7.
- **Execution profile:** Small, bounded, single-session work. No phased delivery.
- **Tail ownership:** The implementing agent owns updating `skills/where-did-we-land/SKILL.md`, `skills/where-did-we-land/template.html`, and `skills/where-did-we-land/scripts/check_ledger.py`, and verifying against fixture data before declaring done.

---

## Product Contract

### Summary

Add two behaviors to the `where-did-we-land` skill: auto-opening the generated ledger in the system browser once it validates, and computing a meaningful browser tab title from the meeting's participants, date, and topic. The on-page heading and lede stay exactly as they are today.

### Problem Frame

Today the skill tells the user where the file is and stops — the user has to go open it themselves. Separately, every generated ledger's browser tab reads the static "Where did we land?" string regardless of which meeting it is, because `template.html`'s `<title>` tag is hardcoded and never wired to the JSON payload that drives the rest of the page.

### Requirements

**Browser auto-open**
- R1. The generated ledger opens automatically in the user's default browser, on macOS, Linux, and Windows, regardless of which agent harness is running the skill.
- R2. The browser opens only after the ledger passes structural validation (`check_ledger.py` exits 0) — never on an unvalidated or failed write.
- R3. If the browser cannot be opened — the open command fails (no display, headless session) or the harness has no shell/exec capability to attempt it at all — the skill proceeds to its existing report with no additional message.

**Dynamic tab title**
- R4. The generated ledger's browser tab title reflects participants, meeting date (when known), and topic, replacing the static "Where did we land?" string. The on-page heading (`D.meta.title`) and lede (`D.meta.headline`) are unchanged.
- R5. A meeting date appears in the tab title only when it can be read directly from the transcript's own content. It is never inferred from the source filename, file modification time, or asked of the user.
- R6. `check_ledger.py` validates the new optional `meta.date` field's format as part of its existing structural-validation gate.

### Scope Boundaries

- No changes to `reference/formats.md` or `reference/sources.md` — the date-sourcing rule (R5) is documented alongside the `meta.date` schema entry in `SKILL.md`, not as a new transcript-parsing rule.
- No changes to `evals/` scenario files.
- No new automated test runner, CI workflow, or JS test framework added to the repo (see KTD9) — the repo currently has none of these, and this work does not warrant introducing one.

#### Deferred to Follow-Up Work

- A committed JS unit-test harness for `template.html`'s render script, if this kind of logic needs testing again in the future.

---

## Planning Contract

### Key Technical Decisions

- KTD1. Browser-open command is OS-detected (`open` on macOS, `xdg-open` on Linux, `start` on Windows) rather than macOS-only. (session-settled: user-directed — chosen over a macOS-only `open` call: the skill installs cross-platform via the plugin marketplace, so it must work on every install, not just this user's machine.)
- KTD2. The open command fires only after `check_ledger.py` exits 0 — the existing Done-when bar at the end of step 6 — not immediately after the file is written. (session-settled: user-directed — chosen over opening immediately after write: the user wants the browser to show only a finished, validated page.)
- KTD3. No special-case handling when the open command fails. The skill proceeds straight to its existing "give the user the file path" report. (session-settled: user-approved — chosen over adding a "couldn't auto-open" message: the report already always states the file path, so a failure message adds nothing.)
- KTD4. Tab title segments join with a literal `|` character. `template.html` elsewhere joins display strings with `·` (footer stat line at template.html:443-444, eyebrow separator via CSS at template.html:64), but this plan follows the user's explicit choice rather than the in-file convention. (session-settled: user-directed — chosen over the file's existing `·` separator: the user explicitly specified `|`.)
- KTD5. The meeting date is read only from the transcript's own content (header or preamble); never from the source filename, file modification time, or by asking the user. When absent, the date segment is dropped from the title with no dangling separator (`names | topic`, not `names | | topic`). (session-settled: user-directed — chosen over also accepting filename-derived or user-stated dates: the user wants zero risk of a wrong or guessed date in the tab title.)
- KTD6. Participant names in the tab title use first names only: `&`-joined up to 3 participants (`Dana & Amir & Priya`), and `FirstName + N others` beyond 3, where N is the total participant count minus 1. (session-settled: user-approved.)
- KTD7. The on-page H1 (`D.meta.title`, template.html:309) and lede (`D.meta.headline`, template.html:310) are left untouched. The tab title is new, independent logic reading `D.participants`, the new `D.meta.date`, and the existing `D.meta.kind`. (session-settled: user-directed — chosen over repurposing `meta.title` for the tab title: `meta.title` already drives the on-page heading, and repurposing it would change that heading's content.)
- KTD8. `check_ledger.py` treats a present-but-malformed `meta.date` as a hard validation failure (`r.bad`), matching its existing posture on other structural fields (e.g. `check_turn_count`, `check_geometry`), rather than warning and continuing. An absent `meta.date` is not a failure — it's noted (`r.note`) and the check passes. This means a malformed `meta.date` also blocks R1's browser auto-open, since R2/KTD2 gate opening on `check_ledger.py` exiting 0 — an intentional consequence, consistent with the validator's existing all-or-nothing posture on every other structural field, not a special case invented for this one. (session-settled: user-approved.)
- KTD9. The tab-title JS logic is verified during implementation by opening fixture-rendered ledgers in a real browser and reading `document.title` for each case, rather than adding a JS test framework to the repo. The repo has no `package.json`, no JS test runner, and no CI (confirmed by research) — its only automated test surface is `check_ledger.py`, which inspects the embedded JSON, not rendered output. Adding a JS harness for one template file's title-join logic is disproportionate. "Reading `document.title`" means visually inspecting the rendered browser tab label — no DOM query or automation tooling is required. (session-settled: user-approved.)
- KTD10. When the harness running the skill has no shell/exec capability at all, the auto-open step is skipped silently, falling through to the existing report — same posture as a failed open command (R3). SKILL.md already documents this class of gap for a different step ("Where no shell exists (Cowork), count each turn by hand," SKILL.md:39), so a shell-only mechanism for auto-open needs the same explicit carve-out; without it, R1's "regardless of which agent harness" claim silently fails to hold on a shell-less harness. Not session-settled — surfaced by feasibility review, not the earlier grilling session.
- KTD11. The date segment is built by parsing `D.meta.date`'s ISO string manually (or via UTC-based accessors) rather than `new Date(D.meta.date)` plus local-time getters. A date-only ISO string parses as UTC midnight per the ECMAScript spec; formatting it with local getters renders as the previous day in any timezone behind UTC. Not session-settled — a correctness fix surfaced by feasibility review, not a design tradeoff.

### Assumptions

None — all load-bearing decisions above are session-settled; nothing here was inferred without user confirmation.

### Sources / Research

- `skills/where-did-we-land/SKILL.md:122-176` — steps 6 ("Write the page") and 7 ("Report"); step 7 is currently three prose sentences with no "Done when" line, unlike steps 0-6.
- `skills/where-did-we-land/SKILL.md:35-37` — the one existing precedent for an inline shell snippet inside SKILL.md prose (step 1's `awk` example); use the same style for the OS-detection open command.
- `skills/where-did-we-land/template.html:174-446` — the render script is a single IIFE with no `DOMContentLoaded` wrapper, running inline at the bottom of `<body>`. Existing helpers: `el()`, `fail()`, `mmss()`, `scol()`, `avatar()`. No existing string-join helper for a `names | date | topic`-shaped string, but `.map().join()` is an established idiom nearby (template.html:327-328, 443-444).
- `skills/where-did-we-land/template.html:292-318` — the hero block reads `D.meta.kind`, `D.meta.title`, `D.meta.headline`, and `D.participants` in sequence; optional fields use an inline `||` fallback (`D.meta.kind || 'Conversation record'`) except where presence changes DOM structure (`if (D.meta.clipUrl)`), which is the right model for `meta.date`'s presence changing whether the title has 2 or 3 segments.
- `skills/where-did-we-land/scripts/check_ledger.py:29-41` — the `Report` class (`.ok`/`.bad`/`.note`) and the all-checks-run, aggregate-at-the-end pattern (`sys.exit(1 if r.failed else 0)` at line 273).
- `skills/where-did-we-land/scripts/check_ledger.py:179-184` — `check_headline_news`'s `.get()`-with-guard style is the closest existing precedent for an optional field check, matching how `meta.date` should be read.
- Confirmed via repo-wide search: no `package.json`, no `pytest.ini`/`pyproject.toml`, no `tests/` directory, no `.github/workflows/` — no CI or automated test runner exists anywhere in this repo (informs KTD9).
- `skills/where-did-we-land/evals/README.md` — the only two testing surfaces the repo already uses are `check_ledger.py` ("Structural... deterministic, no agent") and hand-run behavioral scenarios ("no script can check... run by hand").

---

## Implementation Units

### U1. Auto-open the ledger in the browser

**Goal:** After the ledger validates, the skill opens it in the system's default browser, on any OS, in any agent harness.

**Requirements:** R1, R2, R3

**Dependencies:** None

**Files:**
- `skills/where-did-we-land/SKILL.md`

**Approach:**
- Add an instruction to step 7 ("Report", SKILL.md:174-176) that fires after step 6's existing Done-when bar is met (SKILL.md:172), per KTD2.
- Give an OS-detection shell snippet (mirroring the inline-command style already used for step 1's `awk` example at SKILL.md:35-37) that picks `open` (macOS), `xdg-open` (Linux), or `start` via `cmd /c start` (Windows — `start` is a `cmd.exe` built-in, not a standalone executable, so it needs the `cmd /c` wrapper to run from a POSIX-style shell), per KTD1.
- State plainly that a failed open command is not an error — the flow continues straight to the existing file-path report, per KTD3. Do not add new report text for this case.
- State that when no shell/exec tool is available at all (e.g. Cowork), skip the open step entirely and fall through to the report, per KTD10 and R3 — the same posture as a failed command, not a separate error path.
- Match step 7's existing prose style (terse, imperative, no sub-bullets) rather than introducing a numbered sub-list.

**Test scenarios:**
- Test expectation: none — this is a prose instruction change to an LLM-facing procedure, not executable code. Correctness is that the instruction is unambiguous, includes working OS-detection shell syntax, and is positioned after the validation gate.

**Verification:** Re-read step 7 after editing: it should read as one coherent sequence (validate → open → report) with no ambiguity about ordering, the shell snippet should be copy-paste-runnable on a real macOS shell, and the no-shell fallback (KTD10) should be stated plainly enough that an agent in a shell-less harness knows to skip straight to the report.

---

### U2. Document the `meta.date` field

**Goal:** The `meta.date` schema field is documented alongside the rest of the schema, so anyone reading `SKILL.md` (including the implementer of U3/U4) knows it exists, when to populate it, and what it looks like.

**Requirements:** R5, R6

**Dependencies:** None

**Files:**
- `skills/where-did-we-land/SKILL.md`

**Approach:**
- Add `date?` to the `meta` schema table entry (SKILL.md:126-141), an ISO date string, marked optional per existing `?`-suffix convention (matching `sourceUrl?`, `clipUrl?`, `clipLabel?`).
- State the sourcing rule inline: populate only when a date is visible in the transcript's own content/header/preamble — never from filename, file modification time, or by asking the user (KTD5).
- Extend the abbreviated JSON example (SKILL.md:149-169) with `"date":"2026-08-21"` to show the field in context — keep the rest of the example unchanged. Required, not optional: the Definition of Done checks for it.

**Test scenarios:**
- Test expectation: none — pure documentation. Correctness is that the schema table and example match exactly what `template.html` (U3) reads and `check_ledger.py` (U4) validates.

**Verification:** The field name, optionality marker, and format description in `SKILL.md` match the field name and format `template.html` and `check_ledger.py` actually implement.

---

### U3. Compute the browser tab title dynamically

**Goal:** `template.html` sets `document.title` from the meeting's data — participants, date, topic — instead of the hardcoded string, without changing the on-page heading or lede.

**Requirements:** R4, R5

**Dependencies:** U2 (field name and semantics for `meta.date`), U4 (guarantees a malformed `meta.date` is rejected before this code ever runs)

**Files:**
- `skills/where-did-we-land/template.html`

**Approach:**
- Add title-computation logic to the existing render IIFE (template.html:174-446), placed near the existing `D.meta.title` read (template.html:309) since it draws on the same parsed data, per KTD7.
- Build the names segment from `D.participants`: first name only per participant, `&`-joined up to 3, else `FirstName + N others` (KTD6).
- Build the date segment from `D.meta.date` when present, formatted without a year (e.g. `Aug 21`); omit the segment entirely when absent (KTD5). Parse the ISO string manually (e.g. split on `-`) or with UTC-based accessors, never `new Date(D.meta.date)` plus local-time getters, per KTD11 — the local-getter path renders the wrong day in any timezone behind UTC.
- Build the topic segment from `D.meta.kind` (already read elsewhere in the file with a fallback; reuse the same value).
- Join present segments with `|` (KTD4), skipping any absent segment so there's no dangling separator.
- Set `document.title` to the joined string. Do not modify the `el('h1', null, D.meta.title, hero)` or lede lines (template.html:309-310) (KTD7).
- `check_ledger.py` (U4) already rejects a malformed `meta.date` before this code would ever see it, so this logic does not need defensive handling for an invalid date string — only for its absence.

**Patterns to follow:** `el()`, `mmss()` and the existing `.map().join()` idiom (template.html:327-328) for building display strings; `D.meta.kind || 'Conversation record'` (template.html:294) as the model for reading an optional field with a fallback vs. `if (D.meta.clipUrl)` (template.html:308) as the model for a field whose presence changes output structure — `meta.date` follows the latter, since its absence removes a whole title segment rather than substituting a default.

**Test scenarios:**
- 2 participants ("Dana", "Amir"), `meta.kind` "Weekly sync", `meta.date` "2026-08-21" → tab title exactly `Dana & Amir | Aug 21 | Weekly sync`.
- 3 participants, date present → all three names `&`-joined, e.g. `Dana & Amir & Priya | Aug 21 | Weekly sync`.
- 5 participants → `Dana + 4 others | Aug 21 | Weekly sync`.
- 1 participant → no `&`, just the single first name segment.
- `meta.date` absent or empty → date segment dropped entirely: `Dana & Amir | Weekly sync`, no dangling `|`.
- `meta.date` = `"2026-08-21"`, verified with the test machine's local timezone set behind UTC (e.g. US Pacific) → title still shows `Aug 21`, not `Aug 20` (KTD11's off-by-one case).
- Integration: after this change, the on-page H1 text and lede paragraph render identically to before — same source fields, same output, confirming this addition didn't consume or overwrite them.

**Verification:** For each test scenario above, build a fixture JSON payload, write it into a copy of `template.html`, open it in a real browser (per KTD9), and read `document.title` directly — it must match the expected string exactly. Visually confirm the H1/lede are unchanged from a ledger generated before this change.

---

### U4. Validate `meta.date` in `check_ledger.py`

**Goal:** `check_ledger.py` catches a malformed `meta.date` before it reaches a generated page, consistent with its existing structural checks.

**Requirements:** R6

**Dependencies:** U2 (field name and semantics for `meta.date`)

**Files:**
- `skills/where-did-we-land/scripts/check_ledger.py`

**Approach:**
- Add a new `check_meta_date(d, r)` function, following the existing `check_*(d, r)` signature and the `Report.ok`/`.bad`/`.note` pattern (check_ledger.py:29-41).
- Read `d["meta"].get("date")` (optional-field `.get()` style, matching `check_headline_news`, check_ledger.py:179-184).
- Absent or empty → `r.note(...)`, not a failure.
- Present and a valid ISO date → `r.ok(...)`.
- Present and not a valid ISO date → `r.bad(...)` (KTD8).
- Wire the new check into `main()` alongside the other unconditional checks (check_ledger.py:260-268).

**Test scenarios:**
- `meta.date` = `"2026-08-21"` (valid ISO) → check passes (`r.ok`), overall script exits 0 (when all other checks also pass).
- `meta.date` absent from the JSON → check passes with a note, overall script exits 0.
- `meta.date` = `""` (empty string) → treated the same as absent — a note, not a failure.
- `meta.date` = `"Aug 21, 2026"` (non-ISO) → check fails (`r.bad`), overall script exits 1.
- Integration: when only `check_meta_date` fails and every other check passes, `main()`'s aggregated exit code is still 1 — confirming this check's failure isn't silently absorbed by the aggregate-at-the-end pattern.

**Verification:** Run `python3 scripts/check_ledger.py <fixture>.html` against fixtures covering each scenario above; confirm the printed line (`✓`/`✗`/`·`) and the process exit code match expectations.

---

## Verification Contract

- `python3 skills/where-did-we-land/scripts/check_ledger.py <fixture>.html` exits 0 for fixtures with a valid or absent `meta.date`, and exits 1 for a fixture with a malformed `meta.date`.
- Fixture ledgers covering the U3 test scenarios (participant counts 1, 2, 3, 5; date present and absent), opened in a real browser, show the exact expected `document.title` for each.
- `git diff -- skills/where-did-we-land/template.html` shows no changes to the `el('h1', null, D.meta.title, hero)` or lede lines — only additions elsewhere in the render script.
- `SKILL.md` step 7, read in isolation, unambiguously sequences: validation already passed (from step 6) → open in browser (OS-detected command) → report file path and findings to the user.

## Definition of Done

- All four units (U1-U4) implemented and verified per their Verification fields above.
- `check_ledger.py` includes and runs `check_meta_date` as part of its unconditional check sequence.
- `SKILL.md`'s schema table and abbreviated JSON example include `date?` with its sourcing rule.
- No changes to `template.html`'s H1/lede lines (template.html:309-310) — confirmed via diff review.
- No new dependencies, test framework, or CI configuration added to the repo (per KTD9 and Scope Boundaries).
- No leftover fixture files, scratch scripts, or experimental code from verification left in the diff.
