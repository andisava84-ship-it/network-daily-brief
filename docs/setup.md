# Setup

Plan on a day to get the first draft out and a week of tuning. You can start with only the tracker export and add chat, confirmations and the Matrix later; every section that depends on a missing source is skipped and noted.

## What you need

- **A tracking platform with API access** (Affise, Everflow, TUNE, CAKE or similar) and a read-only key.
- **Google Workspace**: Drive for the exports and reference docs, Gmail for delivery.
- **Claude** with scheduled tasks and the Google Drive and Gmail connectors.
- **An automation tool for the exports** — Tasklet, Make, n8n, Zapier or a cron job. It must read your tracker (and chat, optionally) and write Google Docs.
- Optional: Microsoft Teams or Slack access for the chat export; monthly advertiser confirmation sheets for the confirmation status and the Matrix.

## 1. Create the Drive folder

```
Daily Brief/
├── exports/        tracker and chat export docs land here
└── reference/      Intelligence Reference, Matrix LIVE + archives, config, template
```

Restrict it to the people who already see the tracker and the chats.

## 2. Fill in the config

Copy `config/brief-config.example.yaml` to `skill/network-daily-brief/references/brief-config.yaml` and replace every `<placeholder>`:

- `network` and `schedule` — name, short code, time zone, tracker, chat tool, standup time.
- `delivery` — `mode: draft` to start; the mailbox that owns the draft; to / cc; subjects.
- `definitions` — **decide what "declined" means in your network.** If it is a payable cap-management status, keep it in revenue. If it means rejected, remove it.
- `attribution_delays` — every offer whose payable event arrives days later. This single list removes most false "payout bug" alarms.
- `test_offer_ids` — offers to ignore.
- `owners` — every person who receives actions, with what they own. The first matching rule wins.

## 3. Build the tracker export

Follow [`prompts/tracker-export-agent.md`](../prompts/tracker-export-agent.md) and the format in [`docs/data-contracts.md`](data-contracts.md) §1. Schedule it Monday–Friday at `schedule.tracker_export_at`. Run it once by hand and compare three numbers against the tracker UI: yesterday's approved revenue, one offer's conversions, one publisher's payout.

## 4. Build the chat export (optional)

Follow [`prompts/chat-export-agent.md`](../prompts/chat-export-agent.md). List every advertiser and publisher chat, the internal ops channel and the wishlist chat. Exclude personal and HR channels.

## 5. Create the Intelligence Reference

Copy [`templates/intelligence-reference.md`](../templates/intelligence-reference.md) into a Google Doc in `reference/`. On day one, fill **Parts 1, 8, 9 and 12** — definitions, scoring formula, failure patterns and brief rules need no history. Fill the tier, geo, vertical and profile parts once you have three closed months of confirmations (step 6 produces the numbers). Put its file ID in `sources.reference_doc`.

## 6. Create the Matrix (once you have confirmations)

Export three or more closed months of confirmations into the two CSVs described in the header of `scripts/matrix_compute.py`, then:

```bash
python3 scripts/matrix_compute.py --adv advertiser-confirmations.csv --pub publisher-payouts.csv --window 3
```

Paste the tables from `matrix_tables.md` into a Google Doc laid out like [`templates/campaign-matrix.md`](../templates/campaign-matrix.md), add the notes and the §8 strategic signals, and name it `{SHORT}_Campaign_Intelligence_Matrix_LIVE`. Put its file ID in `sources.matrix_doc`. From then on, [`prompts/matrix-refresh-runbook.md`](../prompts/matrix-refresh-runbook.md) keeps it current.

Try it first on the samples:

```bash
python3 scripts/matrix_compute.py --adv examples/sample-advertiser-confirmations.csv --pub examples/sample-publisher-payouts.csv
```

## 7. Install the brief and schedule it

Install `skill/network-daily-brief/` as a skill, or put its instructions in a Drive doc. Then create the scheduled task: [`prompts/scheduled-task.md`](../prompts/scheduled-task.md). Monday–Friday, at least an hour after the exports, written in your local time zone.

## 8. Run it by hand, then check

Run the task once while watching and check:

- [ ] The header date and weekday are right, and the subheader names the right period.
- [ ] Revenue in the KPI tile equals approved + declined + hold from the export, and the components are shown.
- [ ] Three random numbers in the brief trace back to the export.
- [ ] Every action has exactly one owner from the config.
- [ ] The draft renders in Gmail **and** in Outlook (dark headers, zebra rows, chips visible).
- [ ] If you save the HTML, `python3 scripts/check_email_html.py brief.html` passes.

## 9. Start the loop

Send the first brief and ask the team to **reply to it** with what they did. The second brief reads those replies; by the end of the first week the "What changed" section and the ages on each action are doing real work.

## Keeping it healthy

| When | What |
|---|---|
| Daily | Glance at the provenance line: both exports found, Reference and Matrix read by ID. |
| When a month closes | The Matrix refresh runs (or run the runbook by hand). |
| Quarterly | Refresh the Reference from the last three closed months; update geo and vertical scores and profiles. |
| When the team changes | Update `owners` in the config the same day. Stale routing is the fastest way to lose the team's trust. |
| When an alert is wrong twice | Fix the rule (an attribution delay, a test offer, a manual status) rather than ignoring it. |
