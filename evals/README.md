# Evals for where-did-we-land

Two kinds of check, because two different things break.

**Structural** — run `skills/where-did-we-land/scripts/check_ledger.py` on any generated page. Deterministic, no agent, no API
key. It catches a leaked transcript, an unmerged VTT, a missing receipt, an unresolved thread that
never reached the open-loops table, and broken timeline geometry.

**Behavioural** — the scenarios below. These test whether the *agent takes the right process*, which
no script can check. Run them by hand after any edit to `SKILL.md` or its reference files.

## How to run a scenario

1. Open a **fresh session** so nothing in context biases invocation.
2. Paste the scenario's **Prompt** verbatim. Do not name the skill.
3. Grade against the **Pass rubric** — every box must tick.
4. Log the result under `## Runs` with the date, harness and model.

## Scenarios

| # | File | Tests |
|---|------|-------|
| 01 | `01-trigger-phrasings.md` | fires on the real phrasings, stays quiet on near-misses |
| 02 | `02-messy-two-party.md` | classifies a loop-back, a decision, an unanswered question and a dropped thread |

## What is deliberately not tested here

Format parsing beyond the speaker-header shape. Zoom `.vtt`, Teams `<v>` voice tags, SRT and the JSON
APIs are specified in `skills/where-did-we-land/reference/formats.md` but have never been run against a real export — see the
`blocked-on-sample` issues. Scenario 02 uses the speaker-header shape because it is the one that is
verified.
