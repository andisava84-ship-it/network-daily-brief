# Scheduled task — the daily brief

The brief runs as a scheduled task in Claude with the **Google Drive** and **Gmail** connectors enabled. Keep the scheduled-task prompt short and keep the real instructions in one place you can edit without touching the schedule.

## Option A — the skill is installed (simplest)

Install `skill/network-daily-brief/` as a skill (with your filled-in `references/brief-config.yaml`), then use this as the scheduled-task prompt:

```text
Run the network-daily-brief skill for today. Follow it exactly, including the
weekday rules (exit without doing anything on Saturday and Sunday) and the
delivery mode in the config. If anything required is missing, say so at the
top of the brief rather than guessing.
```

## Option B — instructions live in Google Drive

1. Create a Google Doc `{SHORT} Daily Brief — Instructions` and paste the body of `skill/network-daily-brief/SKILL.md` into it.
2. Create a Google Doc `{SHORT} Daily Brief — Config` and paste your filled-in `brief-config.yaml` into it.
3. Upload `skill/network-daily-brief/references/email-template.html` to the same Drive folder.
4. Use this as the scheduled-task prompt (fill in the three file IDs):

```text
Open the Google Doc "{SHORT} Daily Brief — Instructions" (file ID {INSTRUCTIONS_ID})
and carry it out exactly as written for today. Wherever it refers to the config,
use the Google Doc "{SHORT} Daily Brief — Config" (file ID {CONFIG_ID}); wherever
it refers to references/email-template.html, use the Drive file with ID {TEMPLATE_ID}.
On Saturday and Sunday stop immediately without creating anything.
```

Editing the brief is then a document edit; the schedule never changes.

## Schedule

| Setting | Value |
|---|---|
| Days | Monday–Friday. Prefer a weekday-only schedule over a daily one that exits on weekends. |
| Time | At least 60 minutes after the export jobs (`schedule.brief_at` in the config). The reference setup: exports at 07:00, brief at 08:45, standup at 10:30. |
| Time zone | Write the schedule in your local time zone so daylight-saving changes do not shift it. A schedule written in UTC moves by an hour twice a year. |
| Connectors | Google Drive (read exports, Reference, Matrix, confirmation sheets), Gmail (read yesterday's brief and replies, create the draft). Nothing else is needed. |
| Model | A strong reasoning model. The brief does arithmetic, cross-references four sources and writes 40–90 KB of HTML in one pass. |
| Approval | The task only reads Drive and Gmail and creates a draft, so it can run without step-by-step approval. If you switch `delivery.mode` to `send`, decide deliberately whether runs should still ask first. |

## First week

- **Day 1:** run it by hand while watching. Check the dates in the header, that every number traces to the export, and that the draft renders in Gmail and Outlook.
- **First Monday:** check the weekend recap uses Fri, Sat and Sun from the 7-day block.
- **First Friday:** calibration run. Decide whether three strategic plays is the right number for your team.
- **All week:** ask the team to reply to the brief with status updates. The second brief onwards depends on those replies.
