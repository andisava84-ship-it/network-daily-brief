# Matrix refresh runbook (monthly)

The daily brief scores today's traffic against what advertisers actually confirmed in recent months. That memory lives in the **Campaign Intelligence Matrix** and it does not update itself: when a confirmation month closes, the Matrix is rebuilt. Run this runbook as a weekly scheduled task (it stops at step 1 most weeks) or by hand once a month.

Save it as a Google Doc and point a scheduled task at it:

```text
Open the Google Doc "{SHORT} Matrix Refresh Runbook" (file ID {ID}) and carry it
out exactly as written. Most runs end at step 1; in that case stop without
emailing anyone. Only email {OWNER_EMAIL} when a new Matrix version goes live or a
step fails.
```

---

## 0. Sources of truth

- **LIVE Matrix** — Google Doc `{SHORT}_Campaign_Intelligence_Matrix_LIVE` (file ID `{MATRIX_ID}`). The daily brief reads this ID. Never create a new LIVE doc and never change its ID.
- **Archive** — `{SHORT}_Campaign_Intelligence_Matrix_vN_{months}` in the same folder. The latest archive's layout is the template for the next.
- **Compute script** — `scripts/matrix_compute.py` from this repository (Python 3, standard library only).
- **Offer map** (optional) — a sheet of offer ID → vertical, geo, pricing model. Manual overrides always win.
- **Confirmation sheets** — `{SHORT} NC {Month} {Year}`, one per month, in their month folders. Use only the copy in the month folder; ignore stray copies elsewhere.

## 1. Check (every run, about two minutes)

1. Read the LIVE Matrix header. Its newest month is M; the candidate is M + 1.
2. If the candidate month has not ended, stop.
3. Find the candidate's confirmation sheet. If it does not exist, stop.
4. Export its advertiser and publisher tabs to the two CSV formats in the script header and run `matrix_compute.py`. If the candidate month shows `closed=False` (a Pending or Disputed row with money remains), stop. Do not email.

## 2. Rebuild (only when the candidate month is closed)

1. Export the candidate and the previous months (at least six for the topline) to the two CSVs and run:
   `python3 matrix_compute.py --adv adv.csv --pub pub.csv --window 3`
2. Every number in the new version comes from `matrix.json` / `matrix_tables.md`. Never type a number that is not in the output.
3. Write version N+1 in the layout of [`templates/campaign-matrix.md`](../templates/campaign-matrix.md), keeping the section numbers (the brief cites §1, §4, §5, §6, §7, §8):
   - **Restatements vs vN (read first):** compare the overlapping months with the previous version; list every change over $100 or any tier change, with the reason from the sheet's notes. If there are none, say so.
   - Topline, §1 advertiser tiers, §2 geo, §3 vertical, §4 publisher tiers, §5 dormant publishers, §6 untapped matches + single-publisher offers, §7 win-back advertisers, §8 strategic signals, §9 refresh cadence.
   - Where a one-off event distorts a rate (an advertiser-wide scrub passed through to every publisher), explain it in the notes. If something does not reconcile, say so. Never guess.
4. Publish:
   - Create the archive doc `{SHORT}_Campaign_Intelligence_Matrix_vN+1_{months}`.
   - Replace the entire body of the LIVE doc with the same text. Keep its ID.
   - Read the LIVE doc back and confirm the header shows the new months.
5. Append any new offers from the script output to the offer map with blank override columns.
6. Email the owner: subject `{SHORT} Matrix vN+1 live — {months}`, at most eight lines: biggest tier moves, new and dormant accounts, top-advertiser share of the latest month, restatements, unclassified offers to fix, links to LIVE and archive.

## 3. Never

Edit a confirmation sheet, the CRM, the Intelligence Reference or the daily-brief scheduled task. Overwrite or delete an archive version. Send any email other than the one in step 2.6.

## 4. If something fails

Leave the LIVE doc untouched, email the owner one short message with the error and the step, and stop.

---

## The Intelligence Reference is different

The Reference (scoring formula, geo and vertical scores, success profiles, failure patterns, routing) changes slowly. Refresh it by hand once a quarter from the last three closed months, or when the team changes. The Matrix carries the month-to-month tier changes in between, and wins when the two disagree on a tier.
