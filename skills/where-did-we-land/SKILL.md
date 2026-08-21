---
name: where-did-we-land
description: "Reconstruct a meeting or workshop transcript into a single self-contained HTML page: every thread, where it landed, what was left open, who committed to what, and who held the floor. Use when the user points at a transcript (Otter, Granola, Zoom, Teams, Fathom, raw notes) and asks where they landed, what was decided, what is still open, how the conversation went, or asks to visualise or reconstruct a conversation."
---

Address the underlying question: **where did we land, and what did we leave open?**

Here are two kinds of claims that appear on the page:

- **Measured Counts:** These are taken directly from the transcript, including turns, timings, and word counts.
- **Inferred States:** Each inferred state carries a **receipt**, the quote from the transcript it was read from. A state without a receipt does not ship.

Output is a plain `.html` file written to disk. No publishing step, no hosting, no server. The only capability this needs is reading and writing a file, so it runs identically in Claude Code, Cursor, Cowork and Codex.

## Run

### 0. Get the transcript, and check it is a conversation

**Go and find it.** The user should only be asked to paste if there's no other way to get the information. Typically, the system can get the information through a path, a share link, a download in the user's Downloads folder, or an MCP the session already has.

Work down the ladder in `reference/sources.md`: explicit input → local disk sweep → fetch a link → MCP adapters (Granola, Google Drive for Meet, Gmail for notetaker recaps) → ask. That file carries the filename patterns each tool writes, which share links are fetchable and which are auth-walled, and the exact searches for each MCP.

Before starting, check if there are at least two people speaking and taking turns. A recording with only one person speaking doesn't have different viewpoints, agreements, or unresolved topics between people. This would make the transcript seem empty and suggest a conversation occurred when it didn't. State this directly and provide a summary of what was said.

**Done when** you hold transcript text with at least two speakers alternating, or you stopped and told the user why. Name the rungs you already tried.

### 1. Normalise to turns

Emit one entry per speaker turn: `[speakerIndex, secondsFromStart, wordCount]`.

The transcript stays on the user's machine. Only word counts reach the page, so the charts and talk share stay exact. The only verbatim text on the page is the receipts selected in step 3.

Counting: where a shell is available, count exactly rather than by eye:

```bash
awk '{n+=NF} END {print n}' <<< "$turn_text"
```

Where no shell exists (Cowork), count each turn by hand. Turns average around 70 words so per-turn error stays small, and the method belongs in `caveats`.

Every tool on the market exports one of five shapes: speaker-header block, WebVTT, SRT, inline label, or JSON. **Read** `reference/formats.md` for how to recognise each one, what to do with the labels each tool emits, and which exports to reject outright.

The trap it exists to prevent: **cue-based formats (VTT, SRT) and per-utterance JSON are not turns.** One monologue arrives as forty cues. Merge consecutive entries by the same speaker before going further, or every count on the page is wrong by an order of magnitude.

Transcription tools also mis-split turns: one speaker's block swallowing the other's reply, a stray `Speaker 1`. Leave the split as the transcript has it and name each one in `caveats`, with what it does to the talk-share number.

Give an unattributable speaker index `-1`; the counts exclude those turns.

**Done when** every entry is one speaker's uninterrupted turn (a 20-minute two-person conversation lands around 40–120 of them), and you named every mis-split you noticed in a caveat.

### 2. Group turns into threads

A thread is one subject under discussion, not one topic sentence. Ten turns of call-and-response about the same decision are one thread.

A subject that comes back after the conversation moved on is the **same thread with a second segment**. Those gaps are the loop-backs the page draws. They are the most valuable thing on it, so keep them rather than merging a thread into one long bar.

Mark small talk, agenda-setting and sign-off as `substantive: false`; they stay on the timeline but drop out of the landed/open score.

**Done when** every turn belongs to a thread, and each thread's `segs` mark the stretches where it held the floor.

### 3. State each thread, with its receipt

| state        | what it means                                              |
| ------------ | ---------------------------------------------------------- |
| `decided`    | a choice was made and said out loud                        |
| `agreed`     | one party's position was taken up by the other             |
| `action`     | a named person owns a next step                            |
| `closed`     | a social or admin thread that ran its course               |
| `open`       | live, and explicitly unresolved                            |
| `partial`    | direction set, specifics missing                           |
| `ambiguous`  | addressed sideways; the question itself never got answered |
| `unanswered` | raised out loud, no response                               |
| `dropped`    | died mid-thread on a topic switch                          |

Pick the state, then copy the quote that shows it, **verbatim**, character for character.

Real speech is full of false starts and repetition: _"I've got a bunch of I think low-level updates"_, _"for the first the tasks improvement stuff"_. Tidying those is the easiest mistake to make and it quietly misrepresents what was said. Keep the disfluencies. Where a quote is too long, cut with an explicit `…` rather than smoothing over the join. `scripts/check_ledger.py` treats each side of an ellipsis as its own fragment and looks for both in the source.

Where the transcript will not support a firmer state, `ambiguous` is the honest answer and the page displays it.

**Done when** every thread has a state from this table and a `quote` a reader can check it against. Confirm it by running `scripts/check_ledger.py <page> <transcript>`.

### 4. Harvest the four registers

- `openLoops`: the question, and what happened instead of an answer.
- `commitments`: owner, what, when, and `firmness` read from the language used ("I'll do X" is firm; "we should probably" is not).
- `stances`: who agreed with whom, and any reversal. Someone changing their own earlier position is a finding. So is a meeting with no disagreement in it at all.
- `caveats`: what would make a reader wrong to trust this page.

**Done when** every thread stated `unanswered`, `dropped` or `ambiguous` appears in `openLoops`.

### 5. Write the news

The stat band carries the score: duration, threads landed, talk share, turns, commitments, and open loops. All of it is on screen before the reader reaches a word of prose. The prose carries the **news**: what someone who read every row knows and the score alone cannot show.

News comes from reading _across_ rows rather than off any single one:

- a subject raised, abandoned and raised again, and whether it ever closed
- which kind of subject lands, and which kind stays open
- who opens threads and who closes them
- the thread that held the floor longest, and where it ended
- a register that came back empty, or one person holding every commitment

Give each sentence a **receipt** of its own: the rows you read it from. A sentence you cannot point at rows for is an impression, and impressions do not ship. The same bar applies to the states.

**Report what this conversation did.** _"Neither man closes a thread he returns to"_ is a finding, checkable against the table in ten seconds. _"The most evenly balanced conversation you are likely to watch"_ ranks every conversation ever held on the strength of one measurement.

**Let numbers earn their place.** A number the tiles already display costs a second reading and returns nothing. Numbers the tiles cannot compute are news: how many threads came back, how many of those closed, how many commitments sit with one person.

Where the prose goes:

| field                               | carries                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------ |
| `meta.headline`                     | the news, three sentences at most                                              |
| `notes.*`                           | one line per section: what the reader is looking at, then what it shows _here_ |
| `commitmentsNote` / `openLoopsNote` | one line each, under the stat band                                             |

Recount every quantity as you write it. _"It happens twice here"_ is wrong the moment a third thread has two segments. On a page whose whole claim is measurement, a wrong count costs more than a dull sentence would.

**Done when** every sentence in `headline` and `notes` names rows you can point at, and you recounted every quantity in them against the JSON. No number in `headline` repeats one the stat band already shows.

### 6. Write the page

Copy `template.html` and replace the whole `<script type="application/json" id="convo">` block with your JSON. Write it beside the transcript as `<meeting-name>-ledger.html`. Change nothing else in the template.

Schema:

```
meta          { title, kind, source, date?, sourceUrl?, clipUrl?, clipLabel?, start, end, headline }
                                                 start/end in seconds; the two URLs cite a
                                                 public transcript page and recording; date is
                                                 an ISO string ("2026-08-21"), set only when a
                                                 date is visible anywhere in the transcript's own
                                                 content — never from the source filename, file
                                                 modification time, or by asking the user. Leave
                                                 it out when no such date exists.
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

`participants[].avatar` is optional and off unless the user asks for it: a `data:image/…` URI or an
`https://` URL, rendered as a small circle beside the name. Never go looking for a photograph of a
real meeting participant. A name is not consent to put someone's face on a shareable page.

Abbreviated, to fix the shape:

```json
{
  "meta": {"title":"Where did we land?","kind":"Weekly sync","source":"Zoom .vtt",
           "date":"2026-08-21","start":0,"end":1380,
           "headline":"Pricing came back at the end and is open for the third week running. The one question anyone asked outright got answered with a different question."},
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
  "notes": {"timeline":"One row per thread. Two bars mean the subject was left and came back. It happens once here, on the thread nobody closes.",
            "ledger":"…","openLoops":"…","commitments":"…","stances":"…","airtime":"…"},
  "commitmentsNote":"Both are Amir's", "openLoopsNote":"Two are pricing questions",
  "caveats": ["Word counts computed with awk; turn splits left as Zoom emitted them."]
}
```

**Done when** the file exists on disk, opens with no error panel and bars in the topic timeline, and `scripts/check_ledger.py` on it exits 0.

### 7. Report

Once step 6's Done-when bar is met, open the page in the system's default browser before reporting anything, where a shell is available. Set `page` to the file path you just wrote, then run:

```bash
case "$(uname)" in
  Darwin) open "$page" >/dev/null 2>&1 ;;
  Linux)  xdg-open "$page" >/dev/null 2>&1 ;;
  *)      cmd /c start "" "$page" >/dev/null 2>&1 ;;
esac
```

If the command fails (no display, headless session) or no shell exists at all (Cowork), skip it and move straight to the report below — no error, no extra message.

Give the user the file path, then lead with the number that answers _where did we land_, then the open loops. The ledger is already on the page. Do not restate it in chat.
