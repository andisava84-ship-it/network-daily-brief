# {NETWORK} Campaign Intelligence Matrix — v{N} ({m1} + {m2} + {m3}, confirmed)

Updated: {date} · Supersedes: v{N−1} · Status: LIVE · Source: confirmation sheets {list}, computed with `scripts/matrix_compute.py`
Definitions: scrub % = (tracked − confirmed) ÷ tracked · deduction % = deducted ÷ payout before deduction · margin = confirmed − net publisher payout · Currency: {USD; EUR lines summed at face value}

> The daily brief cites this document by section number (§1, §4, §5, §6, §7, §8). Keep the numbering. Every number comes from the script output — paste the tables from `matrix_tables.md` and add notes.

## Restatements vs v{N−1} (read first)

Changes over $100, or any tier change, in months that both versions cover, with the reason from the sheet notes. "None" if there are none.

| Month | Line | Was | Now | Reason |
|---|---|---|---|---|

## Topline (six months + window total)

| Month | Tracked | Confirmed | Scrub | Publisher payout | Margin | Margin % | Closed |
|---|---|---|---|---|---|---|---|

## §1 Advertiser tiers

| Advertiser | {m1} confirmed / scrub | {m2} | {m3} | Window tier | Latest | Share of last month | Notes |
|---|---|---|---|---|---|---|---|

Concentration: top advertiser = {x}% of {m3}.

## §2 Geo

| Geo | Tracked (window) | Scrub | Trend | Notes |
|---|---|---|---|---|

## §3 Vertical

| Vertical | Tracked (window) | Scrub | Trend | Notes |
|---|---|---|---|---|

## §4 Publisher quality tiers

| Publisher | {m1} payout / deduction | {m2} | {m3} | Window tier | Share of last month | Clean markets | Notes |
|---|---|---|---|---|---|---|---|

Note any one-off pass-through (an advertiser-wide scrub) that distorts a publisher's rate.

## §5 Dormant publishers

Clean publishers (GOLD/SILVER historically) with no payout in the latest month.

| Publisher | Last active | Tier | Avg monthly payout | Markets | Re-pitch hook |
|---|---|---|---|---|---|

## §6 Untapped publisher × offer matches

Clean publishers not running clean offers in markets they already convert in ("same market"), then expansion candidates ("same vertical, new geo").

| Publisher | Offer | Fit | Evidence |
|---|---|---|---|

**Single-publisher offers** (Pattern 7):

| Offer | Advertiser | Publisher | Tracked |
|---|---|---|---|

## §7 Win-back advertisers

Clean advertisers with no revenue in the latest month. Mark any that must not be re-pitched.

| Advertiser | Last active | Tier | What they ran | Re-pitch? |
|---|---|---|---|---|

## §8 Strategic signals (compute-free, for "Money left on table")

Short, specific signals the brief can apply to yesterday's numbers without recomputing anything:

- {e.g. "Offer #118 caps out most afternoons; every capped day ≈ $X — ask for a higher cap."}
- {e.g. "Finance ES is 0% scrub but depends on one advertiser — pre-pitch a second ES finance advertiser."}
- {e.g. "VPN CPS is no longer automatically clean — enforce sub-IDs before adding publishers."}

## §9 Refresh cadence

Rebuilt when a confirmation month closes (see `prompts/matrix-refresh-runbook.md`). Next candidate month: {month}.
