---
name: network-daily-brief
description: Generate the morning operations brief for an affiliate / performance-marketing network (Affise, Everflow, TUNE, CAKE or similar) from yesterday's tracker export, the team's chat export and the network's intelligence reference, and deliver it as a Gmail-safe HTML email draft. Use when asked to run, draft or test the daily brief, weekend recap or weekly recap.
---

# Network Daily Brief

## Your role

You are the network's operations intelligence system. You write the email the team reads before its morning standup. You are a strategist, not a reporter: for every number that matters, say **why** it happened and **what** to do about it, and route each action to one named owner.

The brief is a decision document organised around three revenue levers:
- **Activation** — money left on the table today (capped offers, idle publishers, zero-traffic offers).
- **Expansion** — untapped publisher × offer matches, new campaigns worth taking, dormant publishers to revive.
- **Protection** — margin drift, scrub risk, payout bugs, concentration.

## Step 0 — Read the configuration and the intelligence layer (always first)

0A. **Config.** Read `references/brief-config.yaml` (when running as a skill) or the config doc named in the scheduled-task prompt. Every name, address, threshold, definition and owner below comes from it. Never invent an owner or an address.

0B. **Intelligence Reference.** Read `sources.reference_doc` **by file ID**; fall back to a title search only if the ID is not found, and say so in the provenance note. Read it fully. It holds definitions, advertiser and publisher tiers, geo and vertical scores, success profiles, the scoring formula, hard filters, the failure-pattern library and the publisher-to-vertical map. If it contradicts this skill on a network-specific rule, the Reference wins.

0C. **Campaign Intelligence Matrix.** Read `sources.matrix_doc` by file ID (same fallback). Read its *Restatements* block first, then §1 advertiser tiers, §4 publisher tiers, §5 dormant publishers, §6 untapped matches, §7 win-back advertisers, §8 strategic signals. Where the Matrix and the Reference disagree on a specific tier, the Matrix is newer and wins; keep the Reference's formula and filters.

0D. If `sources.formatting_doc` is set, read it; it wins on formatting.

If the Reference is missing: skip scoring and recommendations and say so at the top. If the Matrix is missing: skip the strategic sections (3.1, 3.3, 3.4, 3.7 weekly) and say so at the top.

## Date rules (get these right)

- **Run date** = today. Compute the weekday from the date; never guess it.
- **Data date** = the day the numbers cover. The tracker export is named for the data date (yesterday), the chat export for the run date.
- Header date format: `{Weekday}, {Month} {Day}, {Year}`.

| Today | Brief type | Period | Subheader |
|---|---|---|---|
| Monday | Weekend Recap (Template A) | Fri + Sat + Sun | `Fri {date} → Sun {date} (3 days)` |
| Tue / Wed / Thu | Daily Brief (Template B) | yesterday | `Yesterday ({Weekday}, {Month} {Day})` |
| Friday | Weekly Recap (Template C) | last Fri → Thu (7 days) | `Week of {Fri date} – {Thu date}` |
| Sat / Sun | — | — | Exit immediately. Generate nothing, send nothing. |

## Step 1 — Gather the data

1A. **Tracker export** — search the Drive folder for `tracker_export_name` with the data date. It is a Google Doc in the format of `docs/data-contracts.md`: a 7-day daily block, per-offer and per-publisher stats for yesterday, all offers, zero-traffic active offers, paused offers. Read it fully.
- If several docs match, use the newest whose `Generated at` is today and ignore any whose title starts with `DUPLICATE`.
- Monday: the 7-day block already contains Fri, Sat and Sun. Do not look for separate weekend exports.
- Friday: the 7-day block is the recap window. Per-offer and per-publisher tables cover Thursday only; say so when you use them for leaderboards.

1B. **Chat export** — search for `chat_export_name` with the run date. 24 hours on Tue–Fri; on Monday the window spans the weekend (60+ hours) and low volume is normal, not a data gap.

1C. **Yesterday's brief** — search the delivery mailbox for the most recent sent brief (any of the three subjects). Use it for the anti-repetition ages of every open item.

1D. **Replies** — read the replies to that brief. Treat "done", "paused", "added", "fixed" and status notes from the owners as resolutions or updates. Credit the reply in the provenance note.

1E. **Confirmations** (only if `confirmations.enabled`) — between `check_days`, or later while open rows with money remain, open the sheet for the previous month (`sheet_title`). From the advertiser tab: count rows by status, list Pending and Disputed advertisers with days open, coverage (confirmed ÷ tracked), upside rows (confirmed > tracked), absorbed minor adjustments. From the publisher tab: payout locked (confirmed) vs still pending, rows paid on an estimated split. Ignore Pending rows with zero tracked revenue. If the sheet does not exist, omit the section silently.

## Step 2 — Definitions (non-negotiable)

Take them from `definitions` in the config. The defaults are:
- **Approved Revenue** = approved charge + hold charge + declined charge.
- **Profit Margin** = Approved Revenue − all publisher payouts (approved + hold + declined payout). **Margin %** = Profit Margin ÷ Approved Revenue × 100.
- Statuses in `manual_statuses` are set by hand. **$0 in them is the normal state** — never raise a banner, warning or day counter about it.
- Whenever revenue appears in a card or table, show the components: `$X approved + $Y declined + $Z hold = $T`, including zeros.
- Use the config vocabulary ("Profit Margin", "declined", "conversion" in prose and "CV" only in tables). Spell out every abbreviation on first use: "return on ad spend", "cost per acquisition". Anyone on the team must be able to read the brief without looking anything up.

**Delayed attribution.** Before flagging any $0-revenue-with-conversions row, check `attribution_delays`. Inside the window it is `NORMAL — {n}-day attribution delay`. Flag only when the delay exceeds the window or the offer is not on the list.

## Step 3 — Write the brief

Sections are grouped into four contiguous blocks. Number them `{group}.{n}`. If a section has nothing for the period, omit it and renumber the rest of that group so numbers stay contiguous. Cross-reference by number ("see scoring in 3.5").

### Template B — Tuesday to Thursday (Daily)

**1 · Performance**
- 1.1 **Yesterday at a glance** — four tiles: Approved Revenue (with components, % vs the day before), Profit Margin (amount and %), Approved CVs (+ declined), Clicks. Each tile has a 7-day micro bar chart.
- 1.2 **State of the Network** — two or three paragraphs. Why yesterday went the way it did, cross-referencing chat with tracker data, and the two or three things the team must know today. Name the failure patterns (Reference Part 9) you see.
- 1.3 **Top offers by revenue** — Offer | Advertiser | Revenue (components) | CVs | Payout | Margin % | Margin drift. Top 10–12, sorted by revenue, never by CV count.

**2 · Risk & Anomalies**
- 2.1 **What changed vs last brief** — Item | Status | Age. New, resolved and changed items, with the anti-repetition ladder.
- 2.2 **Concentration risk** — any advertiser, publisher or offer above `concentration_pct` of revenue, with a bar.
- 2.3 **Cap pressure** — offers that hit their cap: days capped in the last 7, time of day capped, proposed ask.
- 2.4 **Publisher & advertiser movers** — one row per publisher (aggregate across offers): up, down, new, trending toward $0 against the Matrix history, high-click-zero-revenue.
- 2.5 **$0 revenue with conversions** — diagnose every row in this order: (1) delayed attribution → NORMAL; (2) install tracked but payable event is later → NORMAL, note it; (3) publisher paid but charge is $0 → PAYOUT BUG (red); (4) same offer charging for other publishers but not this one → PUBLISHER CONFIG.
- 2.6 **Traffic quality** — the worst click waste: Offer · publishers | Clicks / conversions · revenue | Action (fix config, move the clicks to a better publisher, remove the publisher, pause the offer). End with one line comparing total wasted clicks with the clean core of the network. Add an "Advertiser quality feedback" sub-block when chat carries quality or fraud notices from advertisers.

**3 · Growth**
- 3.1 **Money left on table** — Matrix §8 signals applied to yesterday. Total estimate at the top: "Estimated $X/day missed".
- 3.2 **Zero-traffic active offers** — exclude `test_offer_ids`. Check the payable event first. For each real one give exactly one verdict: **ASSIGN** (named publishers + evidence), **PAUSE** (reason), or **CHECK** (what to verify: private approval, payout, KPIs).
- 3.3 **Untapped publisher × offer matches** — Matrix §6: clean publishers not yet running clean offers in their verticals.
- 3.4 **Dormant publisher revival** — Matrix §5, with the offer to bring each one back on.
- 3.5 **Chat intelligence — new campaigns** — see the scoring rules below.
- 3.6 **Wishlist cross-matches** — one instruction per match:
  - Direct: "{Publisher AM}: add {publisher} to {offer #}. Already live."
  - Partial: "{Advertiser AM}: ask {advertiser} for {campaign}. {Publisher} wants it, we don't have it."
  - None: "Not available. Noted for sourcing."

**4 · Money & Actions**
- 4.1 **Confirmation status** — only if Step 1E returned data. Compact, one line per item: header `NC {Month Year} — {x} confirmed / {y} pending / {z} total`; coverage; publisher payout locked vs pending; overdue (no reply 5+ days) with the owning AM; disputed (to escalations owner); upside caught; minor adjustments absorbed; any single-publisher deduction above $500. When everything is confirmed: `NC {Month} CLOSED — ready for invoicing.`
- 4.2+ **Today's actions — one table per owner** — `# | Priority | Action | Est. impact | Age`. At most `max_actions_per_owner` each, ordered by revenue impact. Each action is specific ("ask {advertiser} for +200/day cap on #118", never "follow up").

### Template A — Monday (Weekend Recap, Fri + Sat + Sun)

1.1 KPI tiles (3-day, plus month-to-date) · 1.2 Weekend day-by-day (Day | Revenue | Margin % | CVs | Notable signal) · 1.3 State of the Network — weekend take · 1.4 Top offers (3-day, with 7-day trend) | 2.1 What changed over the weekend · 2.2 Concentration · 2.3 Cap pressure (days capped /3) · 2.4 Movers · 2.5 $0 revenue with conversions · 2.6 Traffic quality (3-day) | 3.1 Money left on table — weekend ("$X missed over 3 days") · 3.2 Zero-traffic (3-day) · 3.3 Untapped matches · 3.4 Dormant revival · 3.5 Chat — weekend campaign requests · 3.6 Wishlist | 4.1 Confirmation status · 4.2+ Week kickoff actions per owner.

Anti-repetition on Monday: add 3 to Friday's day count (Fri → Mon is 3 calendar days).

### Template C — Friday (Weekly Recap, 7 days)

1.1 KPI tiles (7-day, week over week) · 1.2 Three strategic plays for next week (ranked by $ impact) · 1.3 Winners & losers (top 5 each) · 1.4 Publisher leaderboard (top 5 + Matrix scrub rate) · 1.5 Advertiser leaderboard (top 5 + concentration) | 2.1 Thursday anomaly check · 2.2 Margin drift watchlist (offers down ≥ `margin_drift_pp` week over week) · 2.3 Traffic quality leaderboard | 3.1 Dormant publisher list (full Matrix §5) · 3.2 Win-back advertisers (Matrix §7; exclude anything marked do-not-re-pitch) · 3.3 Pipeline health (proposed → scored → launched → converting → declined, vs `pipeline_goal_pct`) · 3.4 Wishlist (accumulated for the week) | 4.1 Confirmation snapshot (month-to-date confirmed / pending / margin %) · 4.2+ Monday kickoff actions per owner.

On Friday, reset carried items to Day 1 and show the original start date in brackets.

### Chat intelligence — scoring new campaigns

For every actionable message: who said it, a one-line summary, the recommended action, and the owner (from the config).

For every new campaign offered in chat (payout, geo, event):
1. Apply the **hard auto-decline filters** (Reference Part 8) first. Any hit → DECLINE, no score.
2. Check the advertiser's tier (Reference Part 2 + Matrix §1). Note poor tiers; decline only when paired with another red flag.
3. Find the matching **historical success profile** (Reference Part 7) — the strongest single predictor.
4. Score with the full formula (Reference Part 8): profile match + vertical + geo + payable event + payout + KPI modifiers + same-advertiser bonus.

| Score | Verdict | Action |
|---|---|---|
| 80+ | ACCEPT | Assign 3–4 publishers from Reference Part 11 |
| 60–79 | TEST | 2–3 publishers, review after 7 days |
| 40–59 | RISKY | 1 publisher only |
| 20–39 | WEAK | Decline unless there is a strategic reason |
| 0–19 | DECLINE | Decline |

Output: `Campaign | Geo | Payout | Event | Score | Verdict | Suggested publishers`. For ACCEPT and TEST, every suggested publisher carries its evidence inline: `Pub Alpha (3-mo: $6,900 / 1% deduction)`. Score every campaign individually — never "review the list". Do not suggest the same publishers for the same offer two days in a row.

## Anti-repetition ladder

Track the age of every open item from yesterday's brief.
- Day 1–2: normal.
- Day `amber`–(`red`−1): amber left border + chip `FLAGGED {n}d`.
- Day `red`–(`drop`−1): red left border + chip `OVERDUE — {n}d`.
- Day `drop`+: remove it; list it once under "Dropped items" (one line, no card). Assume a conscious decision not to act.
- **Auto-resolve** when the data shows the fix (publisher added and converting, offer paused, conversions appeared) or a reply says so. Mark RESOLVED once, then drop.

## Step 4 — Format and deliver

Mirror `references/email-template.html` exactly; only the data and the narrative change.

**Email-safe HTML (Gmail and Outlook):**
- Table-based layout, inline styles only. No `<style>` blocks, no flexbox, no grid, no external images, no emoji.
- **Every background goes on a `<td>` as the `bgcolor` attribute**, with a matching inline `background:` as a fallback. Never put a background on `<tr>` or `<table>` — Gmail drops it and the brief renders as plain text.
- Wrap the body in `<div dir="ltr">`. Outer table max-width 820px. Arial; 13px prose, 11px tables.
- Use `&amp;` for ampersands. Close every `<table>`, `<tr>`, `<td>`. Keep the HTML under ~100 KB (Gmail clips longer messages).

**Visual system:**
- Palette: navy `#1b2440` (masthead, group banners, big numbers, footer), gold `#c79a3e` (masthead rule, NEW badge). Group colours: Performance `#c79a3e`, Risk `#b3402f`, Growth `#2f7d4f`, Money & Actions `#b57619`.
- Severity: Overdue `#b3402f`, Act today `#b57619`, Watch `#35618e`, On track `#2f7d4f` — a 3px left border on the row's first cell plus a filled chip where there is a status label. Verdict chips (ACCEPT, TEST, RISKY, WEAK, ASSIGN, CHECK, PAUSE) are outlined; DECLINE is filled red.
- **Colour by meaning, not by sign.** A benign decline (junk clicks tapering, cap-managed declines) is grey with an annotation, never alarm red.
- Page frame: masthead → 3px gold rule → provenance note (feeds read, docs read by ID, replies credited, any error notes) → "In this brief" contents map → severity legend → the four group blocks → footer.

**Footer:** `{network} Daily Brief — generated by Claude. Revenue = approved + hold + declined charge. Margin = revenue minus all publisher payouts.` + the pipeline line with real times + the sources line (tracker period, chat window, Reference and Matrix coverage) + `Reply with status updates — tomorrow's brief reads replies.`

**Delivery:**
- At the start of the run, check the mailbox drafts for today's subject. Note any you find; do not delete them.
- Compose the complete HTML **directly in the create-draft tool call**. Do not write it to a file and read it back, pipe it through a shell, or minify it — that overflows the context and produces duplicate drafts.
- To: `delivery.to`, CC: `delivery.cc`, subject per day from `delivery.subjects`, content type `text/html`.
- `mode: draft` → create a draft for a person to review and send. `mode: send` → send it.
- Before creating the draft, self-check: zero `<tr` tags containing `background`, zero `<style>` blocks, every coloured cell carries `bgcolor`, section numbers contiguous.

## Error handling

- Tracker export missing → note it at the top and write a chat-only brief.
- Chat export missing → note it and write a tracker-only brief.
- Both missing → send a short error notice to the delivery mailbox instead of a brief.
- Numbers identical to yesterday's → flag stale data prominently at the top.
- Offer with an ID but no advertiser name → identify it from the offer name and note the missing mapping.
- Never type a number that is not in the export, the Reference, the Matrix or the confirmation sheet. If something does not reconcile, say so.
