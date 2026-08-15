#!/usr/bin/env python3
"""Structural checks on a generated ledger.

    python3 scripts/check_ledger.py <ledger.html> [transcript]

Reads the `#convo` JSON block out of the page and asserts the things that go wrong
in practice. No agent, no API key, no network. Exits non-zero on any failure.

With a transcript argument it also checks that every receipt appears verbatim in
the source — the one assertion that catches an invented quote.
"""
import json
import re
import sys
import unicodedata

STATES = {
    "decided", "agreed", "action", "closed", "open",
    "partial", "ambiguous", "unanswered", "dropped",
}
UNRESOLVED = {"unanswered", "dropped", "ambiguous"}

# A turn is a whole speaking turn, not a subtitle cue. Cue-based formats (VTT,
# SRT, per-utterance JSON) blow this up by 10-20x when the merge step is skipped.
TURNS_PER_MINUTE_MAX = 8.0
TURNS_PER_MINUTE_MIN = 0.8


class Report:
    def __init__(self):
        self.failed = False

    def ok(self, msg):
        print(f"  ✓ {msg}")

    def bad(self, msg):
        print(f"  ✗ {msg}")
        self.failed = True

    def note(self, msg):
        print(f"  · {msg}")


def load(path):
    html = open(path, encoding="utf-8").read()
    m = re.search(
        r'<script type="application/json" id="convo">(.*?)</script>', html, re.S
    )
    if not m:
        sys.exit(f"no #convo JSON block in {path} — is this a ledger page?")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f"#convo block is not valid JSON: {e}")


def check_no_transcript(d, r):
    """turns[n][2] must be a word count, never the words themselves."""
    leaked = [i for i, t in enumerate(d["turns"]) if not isinstance(t[2], int)]
    if leaked:
        sample = str(d["turns"][leaked[0]][2])[:60]
        r.bad(
            f"{len(leaked)} of {len(d['turns'])} turns carry text, not a count "
            f"— the transcript is embedded in the page (e.g. {sample!r})"
        )
    else:
        total = sum(t[2] for t in d["turns"])
        r.ok(f"turns are counts, not text ({total:,} words counted)")


def check_turn_count(d, r):
    """Catches an unmerged cue-based transcript, the loudest failure mode."""
    n = len(d["turns"])
    minutes = (d["meta"]["end"] - d["meta"]["start"]) / 60
    if minutes <= 0:
        r.bad(f"meta.end ({d['meta']['end']}) is not after meta.start")
        return
    lo, hi = TURNS_PER_MINUTE_MIN * minutes, TURNS_PER_MINUTE_MAX * minutes
    if n > hi:
        r.bad(
            f"{n} turns over {minutes:.0f} min ({n / minutes:.1f}/min) — far too many. "
            "Cue-based formats need consecutive same-speaker entries merged first; "
            "see reference/formats.md"
        )
    elif n < lo:
        r.bad(f"only {n} turns over {minutes:.0f} min — turns look under-split")
    else:
        r.ok(f"{n} turns over {minutes:.0f} min ({n / minutes:.1f}/min), plausible")


def check_receipts(d, r):
    """Every thread needs a state from the vocabulary and a non-empty quote."""
    bad_state = [t["label"] for t in d["topics"] if t.get("state") not in STATES]
    no_quote = [t["label"] for t in d["topics"] if not (t.get("quote") or "").strip()]
    if bad_state:
        r.bad(f"{len(bad_state)} thread(s) with an unknown state: {bad_state[:3]}")
    if no_quote:
        r.bad(f"{len(no_quote)} thread(s) with no receipt: {no_quote[:3]}")
    if not bad_state and not no_quote:
        r.ok(f"all {len(d['topics'])} threads carry a state and a receipt")


def check_open_loops(d, r):
    """Anything unresolved must surface in the open-loops table."""
    unresolved = [t for t in d["topics"] if t.get("state") in UNRESOLVED]
    listed = " ".join(
        f"{o.get('at', '')} {o.get('question', '')} {o.get('instead', '')}"
        for o in d["openLoops"]
    ).lower()
    missing = [
        t["label"]
        for t in unresolved
        if t.get("ts", "\0") not in listed
        and t["label"].lower()[:22] not in listed
    ]
    if missing:
        r.bad(
            f"{len(missing)} unresolved thread(s) never reached openLoops: {missing[:3]}"
        )
    else:
        r.ok(f"all {len(unresolved)} unresolved thread(s) appear in open loops")


def check_geometry(d, r):
    """Segments inside the meeting, speaker indices that resolve."""
    start, end = d["meta"]["start"], d["meta"]["end"]
    n_people = len(d["participants"])
    problems = []
    for t in d["topics"]:
        for a, b, sp in t["segs"]:
            if not (start <= a < b <= end):
                problems.append(f"{t['label']}: segment {a}-{b} outside {start}-{end}")
            if not (0 <= sp < n_people):
                problems.append(f"{t['label']}: speaker index {sp} has no participant")
    for i, turn in enumerate(d["turns"]):
        if not (start <= turn[1] <= end):
            problems.append(f"turn {i} at {turn[1]}s outside {start}-{end}")
        if turn[0] != -1 and not (0 <= turn[0] < n_people):
            problems.append(f"turn {i}: speaker index {turn[0]} has no participant")
    if problems:
        for p in problems[:4]:
            r.bad(p)
        if len(problems) > 4:
            r.note(f"... and {len(problems) - 4} more")
    else:
        r.ok("timeline geometry and speaker indices are sound")


_UNITS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
# "one" is left out on purpose: it is far commoner as an article than as a count,
# and flagging it would cost more false alarms than it is worth.


def _numbers_in(text):
    """Every quantity a reader would see in this sentence, digits or words."""
    found = {int(n) for n in re.findall(r"\d+", text)}
    words = re.split(r"[^a-z]+", text.lower())
    for i, w in enumerate(words):
        if w in _UNITS:
            # "twenty-three" reads as 23, not as 20 and 3
            if i and words[i - 1] in _TENS:
                continue
            found.add(_UNITS[w])
        elif w in _TENS:
            nxt = words[i + 1] if i + 1 < len(words) else ""
            found.add(_TENS[w] + _UNITS.get(nxt, 0))
    return found


def check_headline_news(d, r):
    """The stat band carries the score; the headline has to carry something else."""
    headline = d["meta"].get("headline", "")
    if not headline.strip():
        r.bad("meta.headline is empty — the page opens on nothing")
        return

    subst = [t for t in d["topics"] if t.get("substantive")] or d["topics"]
    landed = sum(1 for t in subst if t.get("state") in STATES - UNRESOLVED - {"open", "partial"})
    words = {}
    turns = {}
    for t in d["turns"]:
        words[t[0]] = words.get(t[0], 0) + t[2]
        turns[t[0]] = turns.get(t[0], 0) + 1
    total = sum(words.values()) or 1

    shown = {
        round((d["meta"]["end"] - d["meta"]["start"]) / 60): "the duration in the eyebrow",
        len(subst): "the thread count in Threads landed",
        landed: "the landed count in Threads landed",
        len(d["commitments"]): "the Commitments tile",
        len(d["openLoops"]): "the Open loops tile",
        len(d["turns"]): "the turn total in the footer",
    }
    for i, w in words.items():
        shown[round(100 * w / total)] = "a Talk share percentage"
        shown[turns[i]] = "a turn count under Talk share"

    clash = sorted(n for n in _numbers_in(headline) if n in shown and n > 1)
    if clash:
        for n in clash[:3]:
            r.bad(f"headline repeats {n}, already on screen as {shown[n]}")
        r.note("the headline's job is what the tiles cannot show — read across rows instead")
    else:
        r.ok("headline carries no number the stat band already shows")

    # Printed, not asserted: prose claims are not machine-checkable, but a wrong
    # count is the commonest way this page lies, so put the true ones in reach.
    loops = [f"T{i + 1:02d} ({t.get('state')})"
             for i, t in enumerate(d["topics"]) if len(t["segs"]) > 1]
    r.note(f"threads raised more than once: {len(loops)}"
           + (f" — {', '.join(loops)}" if loops else ""))


def _norm(s):
    """Fold smart quotes and whitespace so a receipt matches its source line."""
    s = unicodedata.normalize("NFKC", s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("–", "-"), ("…", "...")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def check_quotes_verbatim(d, transcript_path, r):
    """A receipt that is not in the source was invented."""
    source = _norm(open(transcript_path, encoding="utf-8").read())
    invented = []
    for t in d["topics"]:
        # Receipts may stitch two lines together with an ellipsis or a dash;
        # every fragment still has to exist in the source.
        parts = [p for p in re.split(r"\.\.\.|\s-\s", _norm(t["quote"])) if len(p) > 25]
        if not parts:
            continue
        if any(p not in source for p in parts):
            invented.append(t["label"])
    if invented:
        r.bad(f"{len(invented)} receipt(s) not found verbatim in the source: {invented[:3]}")
    else:
        r.ok(f"all {len(d['topics'])} receipts found verbatim in the transcript")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ledger = sys.argv[1]
    d = load(ledger)
    r = Report()

    print(f"\n{d['meta'].get('title', ledger)}")
    print(f"{ledger}\n")

    check_no_transcript(d, r)
    check_turn_count(d, r)
    check_receipts(d, r)
    check_open_loops(d, r)
    check_geometry(d, r)
    check_headline_news(d, r)

    if len(sys.argv) > 2:
        check_quotes_verbatim(d, sys.argv[2], r)
    else:
        r.note("no transcript given — skipping the verbatim-receipt check")

    print()
    sys.exit(1 if r.failed else 0)


if __name__ == "__main__":
    main()
