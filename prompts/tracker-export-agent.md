# Export job 1 — tracker → Google Doc

This job pulls yesterday's numbers from your tracking platform and writes them to a Google Doc in the format of [`docs/data-contracts.md`](../docs/data-contracts.md) §1. The reference setup runs it in **Tasklet** (an AI automation agent with Affise API access and Google Drive). Make, n8n, Zapier or a small script on a cron work just as well. If you use a script, follow the contract and skip the prompt.

**Schedule:** Monday–Friday, 07:00 local time (`schedule.tracker_export_at`).
**Access:** a read-only API key for the tracker; write access to the Drive folder.

## Prompt for an AI automation agent

```text
You are the tracker export job for {NETWORK}. Every weekday at {07:00 TZ} you
pull yesterday's statistics from {TRACKER} and write ONE Google Doc to the Drive
folder "{FOLDER}". You only read from {TRACKER}; never change anything there.

FILE
- Title: {short_lower}_tracker_{DATA_DATE}, where DATA_DATE = yesterday (YYYY-MM-DD).
- If a doc with that title already exists, overwrite its content. Never create a
  second doc with the same title.
- First lines:
  {NETWORK} TRACKER DAILY EXPORT — {DATA_DATE}
  Generated at: {now, YYYY-MM-DD HH:MM TZ}
  Period: {DATA_DATE minus 6 days} to {DATA_DATE}

SECTIONS (exactly these headers, in this order)
1. === DAILY STATS (7 days) ===
   For each of the last 7 days, oldest first:
   Day / Clicks + Unique / Approved (cv, charge, payout, margin) /
   Hold (cv, charge, payout) / Declined (cv, charge, payout) / Pending (cv, charge) /
   Total (cv, charge, payout, margin).
   On Monday this block must contain Friday, Saturday and Sunday as separate days.
2. === OFFER STATS (yesterday) ===
   One block per offer with any clicks or conversions yesterday: Offer id | name,
   Advertiser, Clicks | Trafficback, then Approved / Hold / Declined / Pending / Total
   with cv, charge and payout.
3. === AFFILIATE STATS (yesterday) ===
   One block per publisher x offer: Affiliate id | name, Offer id | name, Clicks,
   Approved / Hold / Declined with cv, charge and payout.
4. === ALL OFFERS ===  one line per offer: ID | name | Advertiser | Status | Privacy | Affiliates.
5. === ZERO-TRAFFIC ACTIVE OFFERS ===  active offers with 0 clicks yesterday.
6. === PAUSED/STOPPED OFFERS ===  offers whose status is not active.

RULES
- Money with 2 decimals and a $ sign; counts as plain integers. Use the account
  currency.
- Use the tracker's own status names for approved / hold / declined / pending.
- Keep offer names exactly as in the tracker (they carry platform, geo and model).
- If an offer has no advertiser name, write the advertiser ID and continue.
- If the API fails, retry twice 5 minutes apart. If it still fails, write the doc
  with the header and a single line "EXPORT FAILED: {reason}" so the brief can say so.
- Write nothing else to Drive and message no one.
```

## Platform notes

- **Affise:** the stats API can slice by day, by offer and by affiliate; the offers API gives status and privacy. Charge = what the advertiser pays, payout = what the publisher earns, "declined" in Affise is the status the brief calls declined.
- **Everflow / TUNE / CAKE:** map revenue → `charge`, payout → `payout`, and your rejected/pending statuses to the four status lines. Tell the brief in the config (`definitions`) whether rejected conversions are payable.
- **Trafficback** is Affise-specific. If your tracker has no equivalent, write `Trafficback: n/a`.
