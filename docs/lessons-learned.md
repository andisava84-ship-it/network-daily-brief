# Lessons learned

The brief went through more than a dozen prompt versions and four visual systems in production. These are the fixes that mattered, roughly in the order we hit them. Most are one line in the skill; each cost at least one broken morning.

## Rendering

**Gmail drops backgrounds set on `<tr>`.** The first briefs rendered as plain black-on-white text in Gmail: no dark headers, no zebra rows. Gmail strips CSS backgrounds on table rows and ignores `<style>` blocks. The fix is mechanical: every background goes on the `<td>` as the `bgcolor` attribute, with a matching inline `background:` as a fallback. `scripts/check_email_html.py` catches it.

**Write the HTML directly into the draft tool call.** Generating the email to a file and reading it back for the Gmail draft overflowed the context, failed halfway and left several partial drafts. Composing the full HTML inside the create-draft call works every time.

**Stay under ~100 KB.** Gmail clips longer messages behind "View entire message", and most readers never click it. Cut sections that have nothing to say rather than shrinking fonts.

**No emoji.** Coloured-dot emoji for priority rendered differently in every client and could not carry a label. A 3px coloured left border plus a small text chip ("OVERDUE — 5d") reads the same everywhere.

**Colour by meaning, not by sign.** A red "−3% clicks" scared people when the drop was junk traffic tapering off. Benign declines are grey with a note ("junk tapered", "cap-managed"); red is reserved for genuinely bad news.

## Dates

**Compute the weekday; never let the model guess it.** An early brief labelled a Tuesday as Monday and ran the weekend template. The skill now states the rule explicitly and gives the day-to-template table.

**Name exports by the date the data covers.** The tracker export is named for yesterday; the chat export for today. Mixing these up made the brief read the wrong day's numbers twice.

**Monday needs no special exports.** The 7-day block in Sunday night's export already contains Friday, Saturday and Sunday. Weekend chat windows run 60+ hours and are usually quiet — the brief must not report that as a data gap.

**Write schedules in local time.** A schedule in UTC moves by an hour twice a year relative to the standup.

## False alarms

**Declare your manual statuses.** Declined and hold are set by hand in the reference network. Until the brief was told, it flagged "$0 declined" as a broken API every morning. Now `$0` in a manual status is the normal state.

**Keep a delayed-attribution list.** Subscription and deposit offers pay days after the install. Without the list, every one of them showed up as a "payout bug". With it, the brief says "NORMAL — 6-day attribution delay" and only flags rows outside the window.

**Exclude test offers by ID.** Otherwise the zero-traffic section opens with the test postback offer every day.

**Handle duplicate exports.** Automation tools occasionally write the same export twice. The brief takes the newest file whose "Generated at" is today and ignores titles starting with `DUPLICATE`.

## Trust

**A person sends it.** Drafts, not sends. The ops lead catches the occasional wrong number before the team acts on it. That review is quick because the provenance line says exactly what was read.

**Every number must come from a source.** The brief may only use figures from the export, the Reference, the Matrix or the confirmation sheet, and must say when something does not reconcile. The same rule applies to the Matrix refresh: every figure comes from the script output.

**Read documents by file ID, not title.** Title search picked up archived copies and stale duplicates in the Drive root. The brief now reads the Reference and the Matrix by ID, falls back to title only if the ID fails, and says so. The Matrix keeps one LIVE document with a fixed ID; versions are archived beside it.

**Keep the long prompt out of the schedule.** Editing a 10,000-character prompt inside a scheduled task invites mistakes, and the version running in the schedule drifted from the version people thought was live. Keep the instructions in one place (the skill or a Drive doc) and have the scheduled task point at it.

## Making it useful

**Score every new campaign individually.** "Review the new campaigns" got ignored. A verdict per campaign (ACCEPT 84, suggested publishers with their numbers) gets acted on in the standup.

**Cite evidence for every suggestion.** "Pub Alpha (3-mo: $6,900 / 1% deduction)" persuades; "Pub Alpha" alone doesn't.

**Hard filters before scoring.** A handful of rules (tiny budgets, deposit requirements, blocked verticals) decide most declines instantly and keep the formula honest.

**Age every open item and drop it at day 10.** Without the ladder, the brief repeated the same requests for weeks and people stopped reading. Dropping an item after ten days ("assume a conscious decision") keeps the list short enough to act on.

**One owner per action, at most five each.** Actions without an owner don't happen; more than five per person don't either.

**Ask for replies.** The single biggest improvement came from asking the team to reply to the brief with what they did. The next morning's brief reads those replies, marks items fixed and moves on.

**Keep routing current.** When people change roles, update the owners the same day. Actions routed to someone who has left are the fastest way to lose the team's trust in everything else the brief says.
