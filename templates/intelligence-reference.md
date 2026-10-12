# {NETWORK} Daily Brief — Intelligence Reference

Last updated: {date} · Data coverage: {months of confirmed data} · Next refresh: {quarter}

The daily brief reads this document every morning before it writes anything. It is the brief's long-term memory: what your numbers mean, who is clean, what has worked before, how to score a new campaign and who owns what. Write it once, refresh it quarterly. The Campaign Intelligence Matrix carries the month-to-month tier changes in between; where the two disagree on a tier, the Matrix is newer and wins.

> How to fill this in: start with Parts 1, 8, 9 and 12 — they work on day one with no history. Fill Parts 2–7 and 11 from three closed months of confirmations (`scripts/matrix_compute.py` produces most of the numbers). Every figure you write here should come from your confirmation sheets, never from memory.

---

## Part 1 — Definitions (non-negotiable)

- **Approved Revenue** = approved charge + hold charge + declined charge. {Say why declined counts, or remove it: "Declined = manual cap management. We decline excess conversions to stay inside advertiser caps; they are still payable."}
- **Profit Margin** = Approved Revenue − all publisher payouts (approved + hold + declined payout). **Margin %** = Profit Margin ÷ Approved Revenue × 100.
- Words: "Profit Margin", never "earnings". "{declined}", never "{throttled}".
- **Confirmed revenue (for confirmations)** = {which conversions count: e.g. approved with charge > 0, plus declined with the comment "Rejected by a manager"}.
- **Publisher payout (for confirmations)** = {where it comes from: the payout field in tracker stats, never config payout × conversions}.
- **Upside rule:** if an advertiser confirms more than you tracked, the difference is network profit; publisher payouts stay on tracked numbers. {Adjust to your policy.}

## Part 2 — Advertiser scrub tiers

Tiers by scrub % (scrub ÷ tracked) over the last three closed months:

| Tier | Scrub |
|---|---|
| CLEAN | < 5% |
| ACCEPTABLE | 5–15% |
| WATCH | 15–25% |
| HIGH RISK | 25–50% |
| SCRUBBED | > 50% |

For each active advertiser: confirmed revenue by month, scrub by month, current tier (reflecting the latest trend), the offers that drive the tier, the owning AM.

```
{Advertiser} | ${confirmed 3 months} ({m1} / {m2} / {m3}) | {s1}% / {s2}% / {s3}% | {TIER — trend}
{one line: which offers are clean, which are dirty, anything structural (upside pattern, concentration)}. AM: {name}
```

**Dormant advertisers** (no revenue in the window) with last known tier — these feed the win-back list.

**Block list** — advertisers whose new campaigns are auto-declined, with the reason (e.g. "100% scrub two months running").

**Offer-level blocks** — specific offers or offer types blocked even when the advertiser is otherwise fine.

## Part 3 — Publisher quality tiers

Tiers by deduction % (deducted ÷ payout before deduction):

| Tier | Deduction |
|---|---|
| GOLD | < 5% |
| SILVER | 5–15% |
| WATCH | 15–25% |
| RISKY | 25–50% |
| BLOCK | > 50% |

For each publisher: payout over the window, deduction %, number of advertisers, main geos, "best for" verticals. Note when a one-off advertiser-wide scrub passed through and distorts the rate. End with publisher concentration (top two publishers' share of the latest month).

## Part 4 — Geo scores (0–20)

One line per geo you run: score, tracked revenue over the window, scrub by month, top publishers, clean and dirty offers. Start everyone at 10 and move the score with evidence:

- Clean at scale (< 5% scrub on meaningful volume) → 16–20
- Mixed (5–25%) → 10–15
- Mostly scrubbed (25–50%) → 5–9
- Fully scrubbed or no publisher coverage → 0–4

## Part 5 — Vertical scores (0–20)

Same method as Part 4, per vertical (Finance, Shopping, VPN, Gaming, Health/Fitness, …). Mark verticals you will not accept (score 0, auto-decline) and say why.

## Part 6 — Pricing model comparison

Confirmed revenue, scrub % and offer count by model (CPA, CPI, CPR, CPS). Write the rule each row implies, e.g. "If an advertiser offers CPA with a deposit event, ask whether a registration (CPR) version exists."

## Part 7 — Historical success profiles

**The strongest single predictor for a new campaign.** A profile is a combination of vertical + geo (+ pricing model). Success rate = share of offer-months with scrub under 25%, from confirmed data. `matrix_compute.py` produces this table.

```
{Vertical} + {Geo} + {Model} | {success}% ({wins} of {n}{, thin}) | ${tracked} | {scrub}% scrub
{one line: which advertisers/offers, the verdict (ACCEPT / TEST / DECLINE), best publishers}
```

Mark profiles with three or fewer offer-months as thin and say so when citing them.

## Part 8 — Scoring formula

**Total = Profile match + Vertical + Geo + Payable event + Payout + KPI modifiers + Performance modifier + Same-advertiser bonus**

Profile match (Part 7):

| Success rate | Points |
|---|---|
| > 60% | +25 |
| 40–60% | +10 |
| 20–39% | −5 |
| < 20% | −15 |
| 0% | −25 |
| No profile (new combination) | 0 |
| Same advertiser succeeded before | +10 |
| Same advertiser failed before | −10 |

Base dimensions:
- Vertical: 0–20 (Part 5) · Geo: 0–20 (Part 4)
- Payable event: CPI 15 · CPR 12 · CPS 10 · CPA registration 8 · CPA purchase 5 · CPA deposit $50+ 2 · CPA deposit $100+ 0
- Payout: inside the geo's normal range 8–10 · below the floor 0 · suspiciously high 5

KPI modifiers: no KPIs +10 · day-7 retention > 30% −5 · day-7 retention > 45% −15 · day-14 return on ad spend > 100% −20 · > 200% −35 · deposit $100+ −40

Performance modifier (campaigns with 3+ days of data): > $20/day for 7+ days +20 · > $20/day for 3–6 days +10 · conversion rate > 0.5% +10 · conversion rate < 0.01% on 10K+ clicks −25

Score → action: 80+ ACCEPT (3–4 publishers) · 60–79 TEST (2–3 publishers, 7 days) · 40–59 RISKY (1 publisher) · 20–39 WEAK (decline unless strategic) · 0–19 DECLINE.

**Hard auto-decline filters** (override every score):
1. Daily budget under ${25}
2. Monthly cap under {50} conversions
3. CPA with a deposit of ${100}+
4. {A geo with a history of heavy scrub} from an advertiser you have not worked with
5. {Verticals you never accept, e.g. casino}
6. Day-14 return-on-ad-spend requirement over 200%

## Part 9 — Failure pattern library

Check every campaign against these. Name the pattern in the brief when you see it.

1. **Click graveyard** — 10K+ clicks, conversion rate < 0.05% after 3+ days. → Pause the publisher on that offer.
2. **Install but no event** — CPS/CPR/CPA offer with 50+ installs and 0 payable events. → Pause the publisher; check the postback.
3. **Advertiser ghost** — no reply to confirmations for 30+ days. → Escalate; send no new traffic.
4. **Payout mismatch** — publisher paid while charge is $0, or charge $0 with real conversions. → Check the offer configuration and fix payout/charge.
5. **Cap starvation** — daily cap under 10, filled in the first hour. → Ask for a cap increase.
6. **Multi-geo trap** — one geo converts, the rest are dead. → Split into single-geo offers; kill the dead geos.
7. **Single-publisher dependency** — > 80% of an offer's revenue from one publisher. → Add two or more publishers.
8. **Advertiser portfolio death** — an advertiser with 3+ campaigns all at $0. → Decline its new campaigns (same-advertiser −10).
9. **Zombie** — active offer, no traffic for 7+ days. → Assign publishers or pause.
10. **Scrub spiral** — a publisher's deduction rate rising month over month on the same offer. → Pause the publisher on that offer; check quality.
11. **Payout race to the bottom** — the same campaign at many networks, payout falling every month. → Check competitiveness; renegotiate or drop.
12. **Event impossibility** — CPA with a $100+ deposit or day-14 return on ad spend over 200%. → Auto-decline.

{Add your own patterns with one line of evidence each. Evidence is what makes the brief trust the pattern.}

## Part 10 — Routing notes

Owners, emails and portfolios live in the config (`owners`). Use this part only for exceptions the config cannot express, e.g. "The CRM still lists a former AM on 30 advertisers — route them to {name} and do not raise it as an action item."

## Part 11 — Publisher-to-vertical map

When the brief suggests publishers for a campaign, it uses this map. Format:

```
{Publisher} → {Vertical Geo} ${payout} {deduction}% · {Vertical Geo} … · Block: {verticals to keep them off}
```

Then list **open slots** — clean publisher × clean offer pairs not running together — and the **do-not-assign** list.

## Part 12 — Brief rules

- Tables are sorted by revenue, never by conversion count.
- Every claim is backed by data: tracker stats, confirmation records or a chat quote.
- Publisher suggestions always carry evidence (conversions, $ amount, deduction rate).
- New campaigns are always scored, one by one, with a verdict.
- Flag concentration when one offer, publisher or advertiser is above {30}% of daily revenue.
- Zero-traffic offers: check the payable event before calling it a problem.
- Do not suggest the same publishers for the same offer two days in a row.
- Anti-repetition: day 3 amber, day 5 red, day 10 drop (assume a conscious decision).
- Auto-detect resolutions: more publishers on an offer than yesterday = the publisher was added.

## Part 13 — Data freshness

What this document is built from and when:

- Confirmation months used: {list}, with topline per month (tracked / confirmed / payout / margin % / scrub %).
- Older history used for profiles: {source and range}.
- CRM / team snapshot date: {date}.
- Open confirmation month: {month} ({what is still pending}).
- Next refresh: {quarter}.
