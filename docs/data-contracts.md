# Data contracts

The brief reads three inputs every morning and two slow-moving documents. The daily inputs are plain-text Google Docs written by an export job. Any tool can write them (Tasklet, Make, n8n, Zapier, a cron job calling your tracker's API); the brief only cares that the format below is respected.

Why Google Docs and not JSON or CSV? The brief runs through a Drive connector that reads Docs as text reliably, a person can open the export and check it in seconds, and a missing or half-written export is obvious at a glance.

---

## 1. Tracker export — `{short}_tracker_{data_date}`

- **Written:** every workday before the brief runs (07:00 in the reference setup).
- **Named for the data date** (yesterday), not the run date. On Tuesday 2026-05-13 the file is `nwm_tracker_2026-05-12`.
- **Folder:** `sources.drive_folder` from the config.
- **One file per day.** If the job retries, it must replace or rename the earlier file. The brief takes the newest file whose `Generated at` is today and ignores any title starting with `DUPLICATE`.

### Required sections, in this order

```
{NETWORK} TRACKER DAILY EXPORT — {data_date}
Generated at: {YYYY-MM-DD HH:MM TZ}
Period: {data_date − 6 days} to {data_date}

=== DAILY STATS (7 days) ===
Day: {YYYY-MM-DD}
Clicks: {n} | Unique: {n}
Approved: cv={n}, charge=${x}, payout=${x}, margin=${x}
Hold: cv={n}, charge=${x}, payout=${x}
Declined: cv={n}, charge=${x}, payout=${x}
Pending: cv={n}, charge=${x}
Total: cv={n}, charge=${x}, payout=${x}, margin=${x}
(repeat for each of the 7 days, oldest first)

=== OFFER STATS (yesterday) ===
Offer: {id} | {offer name}
Advertiser: {advertiser name}
Clicks: {n} | Trafficback: {n}
Approved: cv={n}, charge=${x}, payout=${x}
Hold: cv={n}, charge=${x}, payout=${x}
Declined: cv={n}, charge=${x}, payout=${x}
Pending: cv={n}, charge=${x}
Total: cv={n}, charge=${x}, payout=${x}
(one block per offer with any clicks or conversions yesterday)

=== AFFILIATE STATS (yesterday) ===
Affiliate: {id} | {publisher name}
Offer: {id} | {offer name}
Clicks: {n}
Approved: cv={n}, charge=${x}, payout=${x}
Hold: cv={n}, charge=${x}, payout=${x}
Declined: cv={n}, charge=${x}, payout=${x}
(one block per publisher × offer)

=== ALL OFFERS ===
ID: {id} | {offer name} | Advertiser: {name} | Status: {active|suspended|...} | Privacy: {public|protected|private}

=== ZERO-TRAFFIC ACTIVE OFFERS ===
ID: {id} | {offer name} | Advertiser: {name} | Status: active | Yesterday clicks: 0 | Affiliates assigned: {n|N/A}

=== PAUSED/STOPPED OFFERS ===
ID: {id} | {offer name} | Advertiser: {name} | Status: {suspended|stopped}
```

### Field notes

| Field | Meaning |
|---|---|
| `charge` | What the advertiser pays you (Affise calls it charge; others call it revenue). |
| `payout` | What you pay the publisher. |
| `margin` | charge − payout for that status. The brief recomputes margin from the config definition; this field is a cross-check. |
| `payout` on Hold and Declined | Needed to compute margin as "revenue minus all payouts". Without it the brief can only show the approved margin (approved charge − approved payout) and must label it that way. |
| `Declined` | Conversions moved out of approved. In the reference network this is manual cap management and still payable. Say what it means for you in `definitions` in the config. |
| `Trafficback` | Clicks redirected because of caps, targeting or a paused offer. A high trafficback with low clicks on an active offer is a cap or targeting problem. |
| Monday | The 7-day block must contain Fri, Sat and Sun as separate days. The brief builds the weekend recap from it; no separate weekend files are needed. |
| Offer naming | If your offer names carry platform, geo and model (`Lumen Bank - Android - ES (CPA)`), the brief and the matrix script can infer geo and pricing model. Otherwise add them to the offer map. |

Fictional example: [`examples/sample-tracker-export.md`](../examples/sample-tracker-export.md).

---

## 2. Chat export — `{short}_chat_{run_date}`

- **Named for the run date.** Window: the last 24 hours, cut at the export time. On Monday: Friday afternoon to Monday morning.
- Covers every chat and channel where advertisers, publishers and the team talk business. At least: advertiser group chats, publisher group chats, the internal ops channel and any "wishlist" chat where publishers ask for offers.

```
{NETWORK} CHAT EXPORT — {run_date}
Exported at: {YYYY-MM-DD HH:MM TZ}
Period: {start} to {end}
Day type: {weekday | monday-weekend}
Chats checked: {n}
Chats with messages in window: {n}
Total messages in window: {n}

=== MESSAGES IN WINDOW ===
--- CHAT: [{group|channel|oneOnOne|meeting}] {chat name} ---
{YYYY-MM-DD HH:MM TZ} | {sender name} | {message text}
(chronological; keep the full text, including numbers, payouts, geos and caps)

=== CHATS WITH NO MESSAGES IN WINDOW ===
[{type}] {chat name}

=== INACCESSIBLE CHATS/CHANNELS ===
{name and reason, or "None"}
```

Listing silent and inaccessible chats matters: it lets the brief say "quiet weekend" with confidence instead of guessing whether the export failed.

Fictional example: [`examples/sample-chat-export.md`](../examples/sample-chat-export.md).

---

## 3. Yesterday's brief and its replies (Gmail)

No export needed. The brief searches the delivery mailbox for the most recent message with any of the three subjects, reads its open items and their ages, then reads the replies in that thread. Ask the team to **reply to the brief** with status updates ("paused #183", "added Pub Echo to #245"). That reply thread is how the brief learns what was done.

---

## 4. Monthly confirmations — `{short} NC {Month} {Year}` (optional)

A Google Sheet per month with at least two tabs. Column names can differ; tell the brief which is which in the Reference (Part 1).

**Advertiser tab** — one row per advertiser × offer:
`AM | Advertiser | Currency | Offer ID | Offer | Total CV | Approved CV | Tracked revenue | Confirmed revenue | Scrub amount | Status | Scrub method | Notes`

Status values: `Confirmed`, `Part Scrub`, `Scrubbed` (terminal) and `Pending`, `Disputed` (open).

**Publisher tab** — one row per publisher × offer:
`Publisher | Advertiser | Offer ID | Offer | CV | Payout before deduction | Approved payout | Deducted | Scrub method | Status`

Status values as above. `Scrub method = Proportional (estimated)` marks payouts split by estimate rather than by the advertiser's line items.

---

## 5. Inputs for `scripts/matrix_compute.py`

Two CSVs exported from the monthly confirmation sheets (one row per month × offer, and one per month × publisher × offer). The column list is in the script's header and the fictional samples are in `examples/`:

- [`examples/sample-advertiser-confirmations.csv`](../examples/sample-advertiser-confirmations.csv)
- [`examples/sample-publisher-payouts.csv`](../examples/sample-publisher-payouts.csv)
- Output: [`examples/sample-matrix-tables.md`](../examples/sample-matrix-tables.md)
