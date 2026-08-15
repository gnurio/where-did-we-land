# Transcript formats

Every meeting tool on the market exports one of **five shapes**. Identify the shape from the first
~30 lines, then normalise to turns: `[speakerIndex, secondsFromStart, wordCount]` — the spoken text is
counted, not carried, so it never reaches the page.

## A · Speaker-header block

Speaker and timestamp on their own line, speech on the lines beneath.

```
Thor Galle 0:49
Okay, that's a good point already.

Unknown Speaker 1:02
Yeah, I think so too.
```

**From:** Otter `.txt` (the best-documented plain text on the market), Google Meet transcript Docs,
Descript when configured for speaker headers.
**Parse:** header line = `^(.+?)\s+(\d+):(\d{2})(:(\d{2}))?\s*$`. Everything until the next header is
one turn. This is already one turn per speaker — no merging needed.

## B · WebVTT

```
WEBVTT

1
00:00:05.790 --> 00:00:13.514
Christina: Lorem ipsum dolor sit amet
```

Teams puts the speaker in a voice tag instead:

```
00:00:05.000 --> 00:00:08.000
<v John Smith>Hello everyone.</v>
```

**From:** Zoom cloud recordings (the canonical Zoom artifact), Microsoft Teams, Avoma, Grain, Descript
subtitles.
**Parse:** cue time = the `-->` line, start only. Speaker = text before the first `: ` **or** the
`<v Name>` tag. Then **merge — see below.**

## C · SRT

Same cue structure as VTT; comma decimal separator and no `WEBVTT` header.

```
1
00:00:05,790 --> 00:00:13,514
Christina: Lorem ipsum dolor sit amet
```

**From:** Otter, Fireflies, Grain, Descript.
**Parse:** as VTT. Then **merge.**

## D · Inline label

Speaker, timestamp and speech on one line. Punctuation varies by exporter.

```
[00:05:32] Alice: Let's revisit the budget allocations.
**Sarah (00:00):** Thanks for joining.
00:05:32  Alice  Let's revisit the budget allocations.
```

**From:** Granola community exporters, Fireflies Markdown, tl;dv Transcript Grabber, Krisp `.txt`.
**Parse:** timestamp and a speaker name before a `:` separator, in either order. Consecutive lines by
the same speaker are usually already one turn, but check — some exporters emit one line per sentence,
in which case **merge.**

## E · JSON

Every API on the market converges on the same three fields.

```json
{"speaker": "Alice", "text": "Let's revisit the budget.", "start_time": 332.4}
```

**From:** Granola API, Fathom API, Circleback webhook, Fireflies, Read.ai, tl;dv.
**Parse:** direct. Field names vary — `speaker` / `speaker_name` / `speaker.display_name`,
`start_time` / `startTime` / `timestamp`, seconds or `HH:MM:SS`. One object is usually one utterance,
not one turn, so **merge.**

---

## The merge rule

**Cue-based formats destroy turns.** VTT and SRT emit a cue every few seconds, so one 400-word
monologue becomes forty cues. Feed those straight in and every count on the page is wrong: turn totals
inflate by 10–20×, average turn length collapses, and the airtime chart shows a flat comb instead of
the monologues that are the point of it.

**Merge consecutive entries by the same speaker into one turn.** Keep the first entry's timestamp as
the turn start and join the text with a space. Break the merge only when the speaker changes. Count
words **after** merging, then discard the text — merging first is what makes the count a turn length
rather than a cue length.

Sanity check after merging: a 20-minute two-person conversation lands around 40–120 turns. Several
hundred means the merge did not happen.

## Speaker labels to normalise

| Label seen | Comes from | Do |
|---|---|---|
| `Me` / `Them` | Granola without speaker tags | Ask the user who is who, or use them as-is and say so in `caveats` |
| `Unknown Speaker` | Otter | Keep as its own participant; note it in `caveats` |
| `Speaker 0` / `Speaker 1` | Supernormal, generic diarisation | Ask for real names — the ledger's stance rows are unreadable otherwise |
| A name appearing two ways | Otter re-identification mid-file | Merge to one participant, note it |

## Reject these

- **Teams plain-text via Graph** (`application/vnd.microsoft.graph.transcript+text`) keeps timestamps
  but **strips speaker attribution entirely.** Nothing on the page can be built from it. Ask for the
  `.vtt` or `.docx` instead.
- **Supernormal imported recordings** are monologue-formatted with no speaker separation.
- **Granola "Copy Notes"** copies the AI summary, not the transcript. Ask for the transcript.
- **Grain `.md` bulk export** is an enriched document — summary, action items, participant history —
  not a raw transcript. Extract the transcript section or use the API.
