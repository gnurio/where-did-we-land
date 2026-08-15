# Getting hold of a transcript

Asking the user to copy-paste is the last resort, not the first move. Work down this ladder and stop
at the first rung that yields text.

## The ladder

| # | Rung | Needs |
|---|---|---|
| 1 | **Explicit input** — a path, a URL, or pasted text in the request | nothing |
| 2 | **Local disk sweep** — the folders these tools write into | filesystem |
| 3 | **A link** — fetch a share URL | web fetch |
| 4 | **MCP adapters** — Granola, Google Drive, Gmail | that MCP connected |
| 5 | **Ask** — name the formats and the folders you already checked | — |

---

## 2 · Local disk sweep

Most transcripts arrive as a download and are never moved. Sweep for files modified in the last ~14
days, newest first, and offer the matches:

```
~/Downloads          *.vtt *.srt *transcript* *Transcript* *.txt recently modified
~/Documents/Zoom/    per-meeting folders from local recordings
~/Desktop
```

Filename patterns worth recognising:

| Pattern | Tool |
|---|---|
| `GMT20240101-120000_Recording.transcript.vtt` | **Zoom** cloud transcript download |
| `GMT…_Recording*.m4a` / `.mp4` beside it | Zoom recording — transcript may sit next to it |
| `<Meeting title>.docx` or `.vtt` | **Teams** — the `.vtt` is the better input, take it over the `.docx` |
| `<Note title>.txt` | **Otter** export |
| `<meeting-code> (YYYY-MM-DD HH:MM …)` | **Google Meet** recording, from a synced Drive folder |

If Google Drive for Desktop is mounted, also sweep
`~/Google Drive/My Drive/Meet Recordings/` and `~/Library/CloudStorage/GoogleDrive-*/My Drive/Meet Recordings/`.

**Granola stores locally too:** `~/Library/Application Support/Granola/granola.db` is SQLite, and
`cache-v6.json.enc` holds the encrypted cache. Both are undocumented and reverse-engineered — prefer
the MCP (rung 4). Reach for the database only when there is no MCP, and tell the user it is an
unofficial path that may break.

## 3 · A link

| Link shape | Fetchable? |
|---|---|
| `otter.ai/u/…` | Only if the note was shared publicly. Otter's "share notes" emails carry this link. |
| `fathom.video/share/…` | Usually public. |
| `grain.com/share/…`, `tldv.io/…` | Usually public. |
| `docs.google.com/document/…` | Use the **Drive MCP** (rung 4), not a raw fetch — it is auth-walled. |
| `zoom.us/rec/share/…` | Passcode-gated. Expect it to fail; ask for the downloaded `.vtt` instead. |
| Teams / SharePoint `…sharepoint.com/…` | Auth-walled. Ask for the downloaded `.vtt`. |

A fetched share page is usually the rendered transcript, so it normally reads as shape A or D in
`formats.md`. Verify speakers survived the fetch before trusting it — some share pages render only
the AI summary.

## 4 · MCP adapters

### Granola
`list_meetings` over the recent range → show titles → `get_meeting_transcript` on the chosen id.
Granola labels speakers `Me` / `Them` when the meeting had no speaker tags; see `formats.md`.

### Google Drive — the Meet path
Google Workspace deposits Meet transcripts as Google Docs, and recordings into a `Meet Recordings`
folder. Two searches find them:

```
title contains 'Transcript'
mimeType = 'application/vnd.google-apps.document' and title contains 'Transcript'
```

Then `read_file_content` on the file id. A Meet transcript Doc reads as shape A — speaker name and
timestamp above the speech.

Note the asymmetry: a Meet **recording** in that folder is an `.mp4` with no transcript. Video with no
transcript Doc beside it means transcription was off for that meeting — say so rather than offering
the video.

### Gmail — the notetaker recap path
Most notetakers email a recap containing a link to the full transcript. Search for the senders, then
follow the link via rung 3:

```
from:no-reply@otter.ai subject:"Meeting Summary"
from:fireflies.ai OR from:fathom.video OR from:read.ai OR from:tldv.io
subject:"meeting recap" OR subject:"meeting notes" OR subject:"transcript"
```

The email body itself is the AI summary, not the transcript — follow the link, do not parse the email.

## 5 · Ask

Only after the rungs above come up empty. Say what you already checked, and name what will work:

> Nothing in `~/Downloads` from the last two weeks and no Granola meeting matches. Paste the
> transcript, give me a file path, or share the link — Otter, Zoom `.vtt`, Teams `.vtt`, Granola,
> Fathom, Fireflies, tl;dv, Grain, Descript and Krisp all work.
