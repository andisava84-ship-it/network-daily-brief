#!/usr/bin/env python3
"""Campaign Intelligence Matrix — compute step.

Turns your monthly advertiser confirmations (what each advertiser confirmed vs
what you tracked) and publisher payouts into the numbers the daily brief scores
against: advertiser and publisher tiers, geo / vertical scrub, success
profiles, dormant publishers, win-back advertisers, single-publisher offers and
untapped publisher x offer matches.

Every number in the Matrix doc should come from this script's output. Never
type a figure by hand.

Usage:
    python3 scripts/matrix_compute.py \
        --adv examples/sample-advertiser-confirmations.csv \
        --pub examples/sample-publisher-payouts.csv \
        [--window 3] [--out matrix.json] [--md matrix_tables.md]

Input 1 — advertiser confirmations (one row per month x offer):
    month,advertiser,offer_id,offer_name,vertical,geo,model,tracked,confirmed,status
    month      YYYY-MM (the month being confirmed)
    vertical   e.g. Finance, Shopping, VPN (optional; blank = Unclassified)
    geo        primary country code, e.g. ES (optional; parsed from the name if blank)
    model      CPA / CPI / CPR / CPS (optional)
    tracked    revenue your tracker recorded
    confirmed  revenue the advertiser confirmed (what you invoice)
    status     Confirmed / Part Scrub / Scrubbed / Pending / Disputed

Input 2 — publisher payouts (one row per month x publisher x offer):
    month,publisher,advertiser,offer_id,payout,deducted
    payout     payout before deductions
    deducted   amount withheld after the advertiser's scrub

Definitions:
    scrub %     = (tracked - confirmed, floored at 0) / tracked
    deduction % = deducted / payout
    margin      = confirmed - (payout - deducted)
    A month is CLOSED when no row with tracked > 0 is still Pending or Disputed.
"""
import argparse
import csv
import json
import re
from collections import defaultdict

ADV_TIERS = [(5, "CLEAN"), (15, "ACCEPTABLE"), (25, "WATCH"), (50, "HIGH RISK"), (101, "SCRUBBED")]
PUB_TIERS = [(5, "GOLD"), (15, "SILVER"), (25, "WATCH"), (50, "RISKY"), (101, "BLOCK")]
OPEN_STATUSES = {"pending", "disputed"}
SUCCESS_SCRUB_PCT = 25  # an offer-month "succeeds" when scrub is below this


def num(v):
    if v is None:
        return 0.0
    s = str(v).replace("$", "").replace("€", "").replace(",", "").replace("%", "").strip()
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def pct(part, whole):
    return round(part / whole * 100, 1) if whole else None


def tier(rate, table):
    if rate is None:
        return "—"
    for limit, name in table:
        if rate < limit:
            return name
    return table[-1][1]


def guess_geo(offer_name):
    m = re.search(r"-\s*([A-Z]{2})(?:[/\s(]|$)", offer_name or "")
    return m.group(1) if m else "?"


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{k.strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adv", required=True, help="advertiser confirmations CSV")
    ap.add_argument("--pub", required=True, help="publisher payouts CSV")
    ap.add_argument("--window", type=int, default=3, help="months in the detail window (default 3)")
    ap.add_argument("--out", default="matrix.json")
    ap.add_argument("--md", default="matrix_tables.md")
    args = ap.parse_args()

    adv_rows = load(args.adv)
    pub_rows = load(args.pub)
    for r in adv_rows:
        r["tracked"], r["confirmed"] = num(r.get("tracked")), num(r.get("confirmed"))
        r["open"] = r.get("status", "").lower() in OPEN_STATUSES
        # an open row has no scrub yet: it is excluded from scrub, tiers and margin until it closes
        r["scrub"] = 0.0 if r["open"] else max(r["tracked"] - r["confirmed"], 0.0)
        r["vertical"] = r.get("vertical") or "Unclassified"
        r["geo"] = r.get("geo") or guess_geo(r.get("offer_name"))
        r["model"] = (r.get("model") or "").upper()
    open_keys = {(r["month"], r["offer_id"]) for r in adv_rows if r["open"]}
    for r in pub_rows:
        r["payout"], r["deducted"] = num(r.get("payout")), num(r.get("deducted"))
        r["open"] = (r["month"], r["offer_id"]) in open_keys
    closed_adv = [r for r in adv_rows if not r["open"]]
    closed_pub = [r for r in pub_rows if not r["open"]]

    months = sorted({r["month"] for r in adv_rows} | {r["month"] for r in pub_rows})
    window = months[-args.window:]
    last = months[-1]
    offer_info = {r["offer_id"]: r for r in adv_rows}

    # ── topline and month status
    topline = []
    for m in months:
        A = [r for r in closed_adv if r["month"] == m]
        P = [r for r in closed_pub if r["month"] == m]
        t, c, s = sum(r["tracked"] for r in A), sum(r["confirmed"] for r in A), sum(r["scrub"] for r in A)
        pay, ded = sum(r["payout"] for r in P), sum(r["deducted"] for r in P)
        open_rows = [(r["advertiser"], r["offer_id"], r["tracked"], r["status"]) for r in adv_rows
                     if r["month"] == m and r["open"] and r["tracked"] > 0]
        margin = c - (pay - ded)
        topline.append(dict(month=m, tracked=round(t, 2), confirmed=round(c, 2), scrub_pct=pct(s, t),
                            payout=round(pay - ded, 2), margin=round(margin, 2), margin_pct=pct(margin, c),
                            pending_tracked=round(sum(o[2] for o in open_rows), 2),
                            closed=not open_rows, open_rows=open_rows))

    # ── advertisers
    adv = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))  # adv -> month -> [tracked, confirmed, scrub]
    for r in closed_adv:
        a = adv[r["advertiser"]][r["month"]]
        a[0] += r["tracked"]; a[1] += r["confirmed"]; a[2] += r["scrub"]
    advertisers = []
    for name, by_m in adv.items():
        wt = sum(by_m[m][0] for m in window); ws = sum(by_m[m][2] for m in window)
        all_t = sum(v[0] for v in by_m.values()); all_s = sum(v[2] for v in by_m.values())
        latest = next((m for m in reversed(months) if by_m[m][0] > 0), None)
        advertisers.append(dict(
            advertiser=name,
            confirmed={m: (round(by_m[m][1], 2) if by_m[m][0] else None) for m in window},
            scrub_pct={m: pct(by_m[m][2], by_m[m][0]) for m in window},
            window_confirmed=round(sum(by_m[m][1] for m in window), 2),
            window_tier=tier(pct(ws, wt), ADV_TIERS),
            latest_tier=tier(pct(by_m[latest][2], by_m[latest][0]), ADV_TIERS) if latest else "—",
            all_time_tier=tier(pct(all_s, all_t), ADV_TIERS),
            last_active=latest))
    advertisers.sort(key=lambda r: -r["window_confirmed"])
    last_total = sum(r["confirmed"] for r in closed_adv if r["month"] == last)
    for a in advertisers:
        a["share_last_month_pct"] = pct(adv[a["advertiser"]][last][1], last_total)

    # ── geo, vertical
    def dim(key):
        d = defaultdict(lambda: [0.0, 0.0])
        for r in closed_adv:
            if r["month"] in window and r["tracked"] > 0:
                d[r[key]][0] += r["tracked"]; d[r[key]][1] += r["scrub"]
        return sorted([dict(name=k, tracked=round(v[0], 2), scrub_pct=pct(v[1], v[0])) for k, v in d.items()],
                      key=lambda x: -x["tracked"])

    # ── success profiles: vertical + geo (+ model), share of offer-months with scrub < 25%
    prof = defaultdict(lambda: [0, 0, 0.0, 0.0])  # n, wins, tracked, scrub
    for r in adv_rows:
        if r["month"] in window and r["tracked"] > 0 and not r["open"]:
            key = " + ".join(x for x in (r["vertical"], r["geo"], r["model"]) if x)
            p = prof[key]
            p[0] += 1; p[2] += r["tracked"]; p[3] += r["scrub"]
            if pct(r["scrub"], r["tracked"]) < SUCCESS_SCRUB_PCT:
                p[1] += 1
    profiles = sorted([dict(profile=k, offer_months=v[0], successes=v[1], success_pct=pct(v[1], v[0]),
                            tracked=round(v[2], 2), scrub_pct=pct(v[3], v[2]), thin=v[0] <= 3)
                       for k, v in prof.items()], key=lambda x: (-x["success_pct"], -x["tracked"]))

    # ── publishers
    pub = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))  # pub -> month -> [payout, deducted]
    pub_offers_last = defaultdict(set)
    pub_markets = defaultdict(set)  # clean (vertical, geo) pairs per publisher
    for r in pub_rows:
        if r["payout"] > 0 and r["month"] == last:
            pub_offers_last[r["publisher"]].add(r["offer_id"])
        if r["open"]:
            continue
        p = pub[r["publisher"]][r["month"]]
        p[0] += r["payout"]; p[1] += r["deducted"]
        if r["payout"] > 0 and r["month"] in window and r["deducted"] / r["payout"] < 0.15:
            o = offer_info.get(r["offer_id"], {})
            pub_markets[r["publisher"]].add((o.get("vertical", "Unclassified"), o.get("geo", "?")))
    publishers = []
    for name, by_m in pub.items():
        wp = sum(by_m[m][0] for m in window); wd = sum(by_m[m][1] for m in window)
        latest = next((m for m in reversed(months) if by_m[m][0] > 0), None)
        all_p = sum(v[0] for v in by_m.values()); all_d = sum(v[1] for v in by_m.values())
        publishers.append(dict(
            publisher=name,
            payout={m: (round(by_m[m][0] - by_m[m][1], 2) if by_m[m][0] else None) for m in window},
            deduction_pct={m: pct(by_m[m][1], by_m[m][0]) for m in window},
            window_payout=round(wp - wd, 2),
            window_tier=tier(pct(wd, wp), PUB_TIERS),
            all_time_tier=tier(pct(all_d, all_p), PUB_TIERS),
            avg_monthly_payout=round((all_p - all_d) / max(1, len([m for m in by_m if by_m[m][0] > 0])), 2),
            last_active=latest,
            clean_markets=sorted(f"{v} {g}" for v, g in pub_markets[name]),
            clean_verticals=sorted({v for v, _ in pub_markets[name]})))
    publishers.sort(key=lambda r: -r["window_payout"])
    last_payout = sum(r["payout"] - r["deducted"] for r in closed_pub if r["month"] == last)
    for p in publishers:
        p["share_last_month_pct"] = pct(pub[p["publisher"]][last][0] - pub[p["publisher"]][last][1], last_payout)

    good_pub = {"GOLD", "SILVER"}
    good_adv = {"CLEAN", "ACCEPTABLE"}
    dormant = [dict(publisher=p["publisher"], last_active=p["last_active"], tier=p["all_time_tier"],
                    avg_monthly_payout=p["avg_monthly_payout"], verticals=p["clean_markets"])
               for p in publishers if p["last_active"] and p["last_active"] != last and p["all_time_tier"] in good_pub]
    winback = [dict(advertiser=a["advertiser"], last_active=a["last_active"], tier=a["all_time_tier"])
               for a in advertisers if a["last_active"] and a["last_active"] != last and a["all_time_tier"] in good_adv]

    # ── offers live last month: publishers on each, single-publisher offers, untapped matches
    last_offers = {}
    for r in adv_rows:
        if r["month"] == last and r["tracked"] > 0:
            last_offers[r["offer_id"]] = dict(offer_id=r["offer_id"], offer=r["offer_name"], advertiser=r["advertiser"],
                                              vertical=r["vertical"], geo=r["geo"], tracked=round(r["tracked"], 2),
                                              scrub_pct=pct(r["scrub"], r["tracked"]),
                                              publishers=sorted(p for p, offs in pub_offers_last.items() if r["offer_id"] in offs))
    single = [o for o in last_offers.values() if len(o["publishers"]) == 1]
    untapped = []
    for o in last_offers.values():
        if o["scrub_pct"] is None or o["scrub_pct"] >= 15:
            continue
        for p in publishers:
            if p["window_tier"] not in good_pub or p["publisher"] in o["publishers"]:
                continue
            if f"{o['vertical']} {o['geo']}" in p["clean_markets"]:
                fit = "same market"
            elif o["vertical"] in p["clean_verticals"]:
                fit = "same vertical, new geo"
            else:
                continue
            untapped.append(dict(publisher=p["publisher"], publisher_tier=p["window_tier"], fit=fit,
                                 offer_id=o["offer_id"], offer=o["offer"], vertical=o["vertical"], geo=o["geo"],
                                 evidence=f"{p['window_tier']}, clean in {', '.join(p['clean_markets'])}; "
                                          f"offer scrub {o['scrub_pct']:.0f}% last month"))
    untapped.sort(key=lambda u: (u["fit"] != "same market", u["publisher"]))

    out = dict(months=months, window=window, last_month=last, topline=topline, advertisers=advertisers,
               geo=dim("geo"), vertical=dim("vertical"), profiles=profiles, publishers=publishers,
               dormant_publishers=dormant, winback_advertisers=winback,
               single_publisher_offers=single, untapped_matches=untapped)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    # ── markdown tables, ready to paste into the Matrix doc
    def money(v):
        return "–" if v is None else f"${v:,.0f}"

    def p_(v):
        return "–" if v is None else f"{v:.0f}%"

    L = [f"# Matrix tables — window {window[0]} → {window[-1]} (generated by matrix_compute.py)\n",
         "Closed rows only. Pending / Disputed rows are excluded until they close.\n",
         "## Topline", "| Month | Tracked | Confirmed | Scrub | Publisher payout | Margin | Margin % | Still open | Closed |",
         "|---|---|---|---|---|---|---|---|---|"]
    for t in topline:
        L.append(f"| {t['month']} | {money(t['tracked'])} | {money(t['confirmed'])} | {p_(t['scrub_pct'])} | "
                 f"{money(t['payout'])} | {money(t['margin'])} | {p_(t['margin_pct'])} | "
                 f"{money(t['pending_tracked']) if t['pending_tracked'] else '–'} | {'yes' if t['closed'] else 'NO'} |")
    L += ["", "## §1 Advertiser tiers", "| Advertiser | " + " | ".join(f"{m} confirmed / scrub" for m in window)
          + " | Window tier | Latest | Share of last month |", "|---|" + "---|" * (len(window) + 3)]
    for a in advertisers:
        cells = " | ".join(f"{money(a['confirmed'][m])} / {p_(a['scrub_pct'][m])}" for m in window)
        L.append(f"| {a['advertiser']} | {cells} | {a['window_tier']} | {a['latest_tier']} | {p_(a['share_last_month_pct'])} |")
    for title, rows_ in (("§2 Geo", out["geo"]), ("§3 Vertical", out["vertical"])):
        L += ["", f"## {title}", "| Name | Tracked (window) | Scrub |", "|---|---|---|"]
        L += [f"| {r['name']} | {money(r['tracked'])} | {p_(r['scrub_pct'])} |" for r in rows_]
    L += ["", "## Success profiles (share of offer-months with scrub < 25%)",
          "| Profile | Success | Offer-months | Tracked | Scrub |", "|---|---|---|---|---|"]
    L += [f"| {r['profile']} | {p_(r['success_pct'])} ({r['successes']} of {r['offer_months']}{', thin' if r['thin'] else ''}) | "
          f"{r['offer_months']} | {money(r['tracked'])} | {p_(r['scrub_pct'])} |" for r in profiles]
    L += ["", "## §4 Publisher tiers", "| Publisher | " + " | ".join(f"{m} payout / deduction" for m in window)
          + " | Window tier | Share of last month | Clean markets |", "|---|" + "---|" * (len(window) + 3)]
    for p in publishers:
        cells = " | ".join(f"{money(p['payout'][m])} / {p_(p['deduction_pct'][m])}" for m in window)
        L.append(f"| {p['publisher']} | {cells} | {p['window_tier']} | {p_(p['share_last_month_pct'])} | "
                 f"{', '.join(p['clean_markets']) or '–'} |")
    L += ["", "## §5 Dormant publishers", "| Publisher | Last active | Tier | Avg monthly payout | Verticals |", "|---|---|---|---|---|"]
    L += [f"| {d['publisher']} | {d['last_active']} | {d['tier']} | {money(d['avg_monthly_payout'])} | {', '.join(d['verticals']) or '–'} |"
          for d in dormant] or ["| none | | | | |"]
    L += ["", "## §6 Untapped publisher × offer matches", "| Publisher | Offer | Fit | Evidence |", "|---|---|---|---|"]
    L += [f"| {u['publisher']} | #{u['offer_id']} {u['offer']} | {u['fit']} | {u['evidence']} |" for u in untapped] or ["| none | | | |"]
    L += ["", "### Single-publisher offers (last month)", "| Offer | Advertiser | Publisher | Tracked |", "|---|---|---|---|"]
    L += [f"| #{o['offer_id']} {o['offer']} | {o['advertiser']} | {o['publishers'][0]} | {money(o['tracked'])} |"
          for o in single] or ["| none | | | |"]
    L += ["", "## §7 Win-back advertisers", "| Advertiser | Last active | Tier |", "|---|---|---|"]
    L += [f"| {w['advertiser']} | {w['last_active']} | {w['tier']} |" for w in winback] or ["| none | | |"]
    with open(args.md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    for t in topline:
        print(f"{t['month']}: tracked {money(t['tracked'])}  confirmed {money(t['confirmed'])}  scrub {p_(t['scrub_pct'])}  "
              f"margin {money(t['margin'])} ({p_(t['margin_pct'])})  closed={t['closed']}")
    print(f"advertisers {len(advertisers)} · publishers {len(publishers)} · dormant {len(dormant)} · "
          f"win-back {len(winback)} · single-publisher offers {len(single)} · untapped matches {len(untapped)}")
    print(f"wrote {args.out} and {args.md}")


if __name__ == "__main__":
    main()
