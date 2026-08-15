---
name: where-did-we-land
description: Reconstruct a meeting or workshop transcript into a single self-contained HTML page — every thread, where it landed, what was left open, who committed to what, and who held the floor. Use when the user points at a transcript (Otter, Granola, Zoom, Teams, Fathom, raw notes) and asks where they landed, what was decided, what is still open, how the conversation went, or asks to visualise or reconstruct a conversation.
---

Answer the question the room is actually asking: **where did we land, and what did we leave open?**

A transcript is a log. What you build from it is a **ledger** — every thread, where it ended, and the line of dialogue that proves it.

Two kinds of claim live on the page and they never mix.

- **Counts are measured.** Turns, timings and word counts come from the transcript verbatim.
- **States are inferred.** Every state carries a **receipt** — the quote it was read from. A state without a receipt does not ship.

Output is a plain `.html` file written to disk. No publishing step, no hosting, no server. The only capability this needs is reading and writing a file, so it runs identically in Claude Code, Cursor, Cowork and Codex.

## Run

### 0. Get the transcript, and check it is a conversation

**Go and find it.** Asking the user to paste is the last rung, not the first — a path, a share link, a download sitting in `~/Downloads`, or an MCP the session already has will usually get there without them lifting a finger.

Work down the ladder in **`reference/sources.md`**: explicit input → local disk sweep → fetch a link → MCP adapters (Granola, Google Drive for Meet, Gmail for notetaker recaps) → ask. It carries the filename patterns each tool writes, which share links are fetchable and which are auth-walled, and the exact searches for each MCP.

Then check the precondition: **two or more speakers who actually take turns.** A solo dictation has no stances, no agreements and no open loops between people; the page would render hollow and imply a conversation happened. Say so plainly and offer a summary instead.

**Done when** you hold transcript text with at least two speakers alternating, or you have stopped and told the user why — naming the rungs you already tried.

### 1. Normalise to turns

Emit one entry per speaker turn: `[speakerIndex, secondsFromStart, wordCount]`.

**The transcript itself never enters the page.** Only word counts do, so the charts and talk share stay exact while the meeting stays on the user's machine. The sole verbatim text that ships is the receipts chosen in step 3.

Counting: where a shell is available, count exactly rather than by eye —

```bash
awk '{n+=NF} END {print n}' <<< "$turn_text"
```

Where no shell exists (Cowork), count each turn by hand. Turns average around 70 words so per-turn error stays small, and the method belongs in `caveats`.

Every tool on the market exports one of five shapes — speaker-header block, WebVTT, SRT, inline label, or JSON. **Read `reference/formats.md`** for how to recognise each one, what to do with the labels each tool emits, and which exports to reject outright.

The trap it exists to prevent: **cue-based formats (VTT, SRT) and per-utterance JSON are not turns.** One monologue arrives as forty cues. Merge consecutive entries by the same speaker before going further, or every count on the page is wrong by an order of magnitude.

Transcription tools also mis-split turns — one speaker's block swallowing the other's reply, a stray `Speaker 1`. Leave the split as the transcript has it and name each one in `caveats`, with what it does to the talk-share number.

Give an unattributable speaker index `-1`; those turns are excluded from the counts.

**Done when** every entry is one speaker's uninterrupted turn — a 20-minute two-person conversation lands around 40–120 of them — and every mis-split you noticed is named in a caveat.

### 2. Group turns into threads

A thread is one subject under discussion, not one topic sentence. Ten turns of call-and-response about the same decision are one thread.

A subject that comes back after the conversation moved on is the **same thread with a second segment**. Those gaps are the loop-backs the page draws — they are the most valuable thing on it, so keep them rather than merging a thread into one long bar.

Mark small talk, agenda-setting and sign-off as `substantive: false`; they stay on the timeline but drop out of the landed/open score.

**Done when** every turn belongs to a thread, and each thread's `segs` mark the stretches where it actually held the floor.

### 3. State each thread, with its receipt

| state | what it means |
|---|---|
| `decided` | a choice was made and said out loud |
| `agreed` | one party's position was taken up by the other |
| `action` | a named person owns a next step |
| `closed` | a social or admin thread that ran its course |
| `open` | live, and explicitly unresolved |
| `partial` | direction set, specifics missing |
| `ambiguous` | addressed sideways; the question itself never got answered |
| `unanswered` | raised out loud, no response |
| `dropped` | died mid-thread on a topic switch |

Pick the state, then copy the quote that shows it — **verbatim**, character for character.

Real speech is full of false starts and repetition: *"I've got a bunch of I think low-level updates"*, *"for the first the tasks improvement stuff"*. Tidying those is the easiest mistake to make and it quietly misrepresents what was said. Keep the disfluencies. Where a quote is too long, cut with an explicit `…` rather than smoothing over the join — `scripts/check_ledger.py` treats each side of an ellipsis as its own fragment and looks for both in the source.

Where the transcript will not support a firmer state, `ambiguous` is the honest answer and the page is built to display it.

**Done when** every thread has a state from this table and a `quote` a reader can check it against — confirmed by running `scripts/check_ledger.py <page> <transcript>`.

### 4. Harvest the four registers

- `openLoops` — the question, and what happened instead of an answer.
- `commitments` — owner, what, when, and `firmness` read from the language used ("I'll do X" is firm; "we should probably" is not).
- `stances` — who agreed with whom, and any reversal. Someone changing their own earlier position is a finding. So is a meeting with no disagreement in it at all.
- `caveats` — what would make a reader wrong to trust this page.

**Done when** every thread stated `unanswered`, `dropped` or `ambiguous` appears in `openLoops`.

### 5. Write the page

Copy `template.html`, replace the whole `<script type="application/json" id="convo">` block with your JSON, and write it beside the transcript as `<meeting-name>-ledger.html`. Change nothing else in the template.

Schema:

```
meta          { title, kind, source, sourceUrl?, clipUrl?, clipLabel?, start, end, headline }
                                                 start/end in seconds; the two URLs cite a
                                                 public transcript page and recording
participants  [ { name, avatar? } ]              order sets colour; speakerIndex points here
turns         [ [speakerIndex, seconds, wordCount] ]
topics        [ { label, segs:[[from,to,speakerIndex]], state, substantive, quote, who, ts } ]
openLoops     [ { at, question, instead } ]
commitments   [ { owner, what, at, firmness } ]
stances       [ { at, from, to, what, note } ]
notes         { timeline, ledger, openLoops, commitments, stances, airtime }
caveats       [ "..." ]
commitmentsNote / openLoopsNote                  one line each, shown under the stat band
```

`meta.headline` is three sentences at most: the findings that would surprise someone who sat in the room.

`participants[].avatar` is optional and off unless the user asks for it: a `data:image/…` URI or an
`https://` URL, rendered as a small circle beside the name. Never go looking for a photograph of a
real meeting participant — a name is not consent to put someone's face on a shareable page.

Abbreviated, to fix the shape:

```json
{
  "meta": {"title":"Where did we land?","kind":"Weekly sync","source":"Zoom .vtt",
           "start":0,"end":1380,
           "headline":"Twenty-three minutes, nine threads, three of them closed."},
  "participants": [{"name":"Dana Whitfield"},{"name":"Amir Haddad"}],
  "turns": [[0,0,14],[1,22,61],[0,95,8]],
  "topics": [{"label":"Pricing tiers","segs":[[0,240,0],[900,1020,1]],
              "state":"open","substantive":true,
              "quote":"We never actually said which tier the trial converts into.",
              "who":"Dana","ts":"4:12"}],
  "openLoops": [{"at":"4:12","question":"Which tier does the trial convert into?",
                 "instead":"Amir answered the discount question instead."}],
  "commitments": [{"owner":"Amir","what":"Draft the tier comparison","at":"16:40","firmness":"Firm"}],
  "stances": [{"at":"11:05","from":"Amir","to":"Dana","what":"Ship the annual plan first",
               "note":"Dana agreed without pushback."}],
  "notes": {"timeline":"…","ledger":"…","openLoops":"…","commitments":"…","stances":"…","airtime":"…"},
  "commitmentsNote":"Both are Amir's", "openLoopsNote":"Two are pricing questions",
  "caveats": ["Word counts computed with awk; turn splits left as Zoom emitted them."]
}
```

**Done when** the file exists on disk, opens with no error panel and bars in the topic timeline, and `scripts/check_ledger.py` on it exits 0.

### 6. Report

Give the user the file path, then lead with the number that answers *where did we land*, then the open loops. The ledger is already on the page — do not restate it in chat.
