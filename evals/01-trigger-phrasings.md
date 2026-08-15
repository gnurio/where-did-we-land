# 01 — Trigger phrasings: does the skill fire, and does it stay quiet?

Run each line as its own fresh-session prompt, with a transcript file present in the working directory
where the prompt implies one. Do NOT name the skill. Record what fired.

## Should fire

| Prompt | Why |
|---|---|
| "Where did we land on all this?" (+ a transcript) | the literal name |
| "What did we actually decide in this meeting?" | the core question |
| "Go through this transcript and tell me what's still open" | open loops |
| "Reconstruct this conversation for me" | reconstruction |
| "Did anyone agree on anything here?" | stances |
| "This meeting was a mess — what happened?" | the real user phrasing |
| "Who talked the most and what did they talk about?" | airtime + threads |
| "Turn this Otter export into something I can read" | format-led |

## Should NOT fire

These are near-misses. Firing on them is a false positive — the skill builds a page, which is far more
than any of these asked for.

| Prompt | Should do instead |
|---|---|
| "Summarise this meeting in three bullets" | plain summary |
| "Draft an agenda for tomorrow's sync" | no transcript involved |
| "Pull the action items out of this transcript" | a list, not a page |
| "Clean up the speaker labels in this file" | a text edit |
| "What's my calendar tomorrow?" | nothing to do with transcripts |

## Pass rubric

- [ ] ≥7 of 8 "should fire" prompts invoke the skill or run its process
- [ ] 0 of 5 "should not fire" prompts produce a generated HTML page
- [ ] On "Pull the action items out", the response is a list — it does not silently escalate to a full ledger
- [ ] When it fires without a transcript in the prompt, it goes looking (checks `~/Downloads`, offers Granola) before asking the user to paste

## Runs
