# 02 — A messy two-party conversation

Tests the classification core: a thread that loops back, a real decision, a question asked out loud
and never answered, and a thread dropped mid-sentence on a topic switch. All four are present by
construction, so a run that finds only the decision has failed.

The transcript is in Otter's speaker-header shape — the one format verified against a real export.

## Prompt

> Where did we land on this? Save the page next to nothing, just write it to `./pricing-sync-ledger.html`.
>
> ```
> Dana Whitfield  0:04
> Morning. You good? I know it's been a week.
>
> Amir Haddad  0:09
> Yeah, fine. Bit fried, but fine.
>
> Dana Whitfield  0:14
> Okay so I want to get through pricing today because we keep, we keep circling it and then running out of time. The tiers. Where I've got to is three tiers, starter, team, business, and the middle one is the one everyone lands on. That's the whole design really. But I don't know if we're pricing team at forty or at fifty and honestly I've been going back and forth on that all week.
>
> Amir Haddad  0:41
> Fifty feels high for what's in it right now.
>
> Dana Whitfield  0:46
> It does, yeah. It does feel high. Although if we add the audit log before launch then it doesn't. So it kind of depends what ships.
>
> Amir Haddad  0:57
> Right.
>
> Dana Whitfield  1:02
> Anyway. Which tier does the trial convert into? Because at the moment the trial is basically business, everything switched on, and then on day fifteen they get dropped into whatever they picked, which for most people is going to be team, and that's a downgrade experience. That's a bad, that's genuinely a bad moment.
>
> Amir Haddad  1:28
> Well the discount's the bigger problem. If we're doing twenty percent annual and the trial's already free, the first invoice is going to look weird next to what they were seeing.
>
> Dana Whitfield  1:41
> Hm. Maybe.
>
> Amir Haddad  1:44
> I'd want to model that before we commit to twenty.
>
> Dana Whitfield  1:49
> Sure. Okay. So — the other thing, the onboarding emails. The copy in those is still the old positioning, it still says "workspace for teams" which we haven't used since March, and if someone signs up tomorrow that's the first thing they read.
>
> Amir Haddad  2:08
> Mm. Hey, did we ever decide about annual versus monthly for launch? Because that changes the whole billing build.
>
> Dana Whitfield  2:19
> Right, yes. My view is annual first. Just annual. We get the cash, the build is simpler, and we add monthly in Q3 when we actually understand churn.
>
> Amir Haddad  2:33
> I think that's right. Yeah. Let's do annual only at launch.
>
> Dana Whitfield  2:39
> Okay good, that's decided then. Annual only, monthly in Q3.
>
> Amir Haddad  2:45
> Agreed.
>
> Dana Whitfield  2:51
> That unblocks a lot actually. The billing thing was holding up the whole, the whole schema conversation.
>
> Amir Haddad  3:00
> It was.
>
> Dana Whitfield  3:04
> Right. So then who's writing the tier comparison table? Because sales are asking and I said end of week and I probably shouldn't have.
>
> Amir Haddad  3:15
> I'll do it. I've got the feature matrix already, it's mostly, it's mostly formatting at this point.
>
> Dana Whitfield  3:23
> Perfect. End of week?
>
> Amir Haddad  3:26
> End of week.
>
> Dana Whitfield  3:31
> Great. Um. What else. Oh — back to the tiers for a second, sorry. If we do annual only, does that change the forty versus fifty thing? Because annual at fifty is six hundred a year and that's a different conversation to forty.
>
> Amir Haddad  3:52
> It's a different conversation, yeah.
>
> Dana Whitfield  3:56
> So maybe we hold the number until you've modelled the discount.
>
> Amir Haddad  4:02
> That'd be my instinct.
>
> Dana Whitfield  4:06
> Fine. Fine. So pricing stays open, which is annoying because that's the third week running, but at least it's open for a reason now rather than just, you know, drift.
>
> Amir Haddad  4:20
> Better reason than last week.
>
> Dana Whitfield  4:24
> Ha. Yeah. Alright, I'll let you go. Thanks Amir.
>
> Amir Haddad  4:30
> See you.
> ```

## Pass rubric

**Acquisition and structure**

- [ ] Writes `./pricing-sync-ledger.html`; the page opens with no error panel and draws bars
- [ ] `skills/where-did-we-land/scripts/check_ledger.py ./pricing-sync-ledger.html` exits 0
- [ ] `turns[n][2]` are integers — no transcript text embedded
- [ ] Turn count is around 30, not 100+

**The four constructed cases** — each must be classified correctly

- [ ] **Pricing tiers** → `open`, with **two segments** on the timeline (0:14–1:02 and 3:31–4:20). A single continuous bar means the loop-back was missed
- [ ] **Annual versus monthly** → `decided` or `agreed`, receipt drawn from "Let's do annual only at launch" or "Annual only, monthly in Q3"
- [ ] **"Which tier does the trial convert into?"** → `unanswered`. Amir replies about the *discount*, never the tier. Marking this `agreed` or `closed` is a hard fail
- [ ] **Onboarding email copy** → `dropped`. Dana raises it at 1:49 and Amir switches to billing mid-thread; it never returns
- [ ] **Tier comparison table** → `action`, owner Amir, firmness firm, end of week

**Discipline**

- [ ] Every unresolved thread above appears in the open-loops table
- [ ] Receipts keep the disfluencies — "we keep, we keep circling it", "it's mostly, it's mostly formatting". A tidied quote is a fail even though it reads better
- [ ] Talk share is roughly 75/25 to Dana; both took a similar number of turns
- [ ] `stances` records that Amir agreed to annual-only, and that no disagreement occurred
- [ ] Small talk at 0:04 and the sign-off are marked `substantive: false`

## Runs
