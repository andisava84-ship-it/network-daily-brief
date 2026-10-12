#!/usr/bin/env python3
"""Check that a brief's HTML will survive Gmail and Outlook.

Usage:
    python3 scripts/check_email_html.py brief.html [more.html ...]

Exit code 0 = no errors (warnings may still be printed), 1 = errors found.

Errors (the brief will render broken):
  - a <style> block (Gmail strips it)
  - a background set on <tr> or <table> (Gmail drops it; set bgcolor on each <td>)
  - a <td> with an inline background but no bgcolor attribute
  - flexbox / grid layout
  - unbalanced <table>, <tr> or <td> tags
Warnings (worth a look):
  - HTML larger than ~100 KB (Gmail clips long messages behind "View entire message")
  - emoji (the visual system uses severity chips instead)
  - a bare "&" that is not an entity
  - external images (blocked by default in most clients)
"""
import re
import sys
from html.parser import HTMLParser

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")
BARE_AMP = re.compile(r"&(?![a-zA-Z]+;|#\d+;|#x[0-9a-fA-F]+;)")


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.errors, self.warnings = [], []
        self.stack = []
        self.counts = {"table": 0, "tr": 0, "td": 0}

    def where(self):
        line, _ = self.getpos()
        return f"line {line}"

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        style = a.get("style", "").lower().replace(" ", "")
        if tag == "style":
            self.errors.append(f"{self.where()}: <style> block — Gmail strips it; use inline styles")
        if tag in ("tr", "table") and ("background:" in style or "background-color:" in style):
            self.errors.append(f"{self.where()}: background on <{tag}> — move it to bgcolor on each <td>")
        if tag in ("tr", "table") and "bgcolor" in a:
            self.warnings.append(f"{self.where()}: bgcolor on <{tag}> is unreliable; put it on each <td>")
        if tag in ("td", "th") and ("background:" in style or "background-color:" in style) and "bgcolor" not in a:
            self.errors.append(f"{self.where()}: <{tag}> has an inline background but no bgcolor attribute")
        if "display:flex" in style or "display:grid" in style:
            self.errors.append(f"{self.where()}: flex/grid layout — use tables")
        if tag == "img" and a.get("src", "").startswith("http"):
            self.warnings.append(f"{self.where()}: external image — most clients block it by default")
        if tag in self.counts:
            self.counts[tag] += 1
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag not in self.counts:
            return
        # pop to the matching tag, reporting anything left open in between
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, line in self.stack[i + 1:]:
                    self.errors.append(f"line {line}: <{t}> not closed before </{tag}> at {self.where()}")
                del self.stack[i:]
                return
        self.errors.append(f"{self.where()}: </{tag}> without a matching <{tag}>")

    def handle_data(self, data):
        if EMOJI.search(data):
            self.warnings.append(f"{self.where()}: emoji in text — use a severity chip instead")


def check(path):
    raw = open(path, encoding="utf-8").read()
    c = Checker()
    c.feed(raw)
    c.close()
    for t, line in c.stack:
        c.errors.append(f"line {line}: <{t}> never closed")
    size = len(raw.encode("utf-8"))
    if size > 100_000:
        c.warnings.append(f"size {size:,} bytes — Gmail clips HTML over ~102 KB")
    body = re.sub(r"<[^>]+>", "", raw)
    n_amp = len(BARE_AMP.findall(body))
    if n_amp:
        c.warnings.append(f"{n_amp} bare '&' in text — write &amp;")
    print(f"{path}: {size:,} bytes, {c.counts['table']} tables, {c.counts['td']} cells")
    for e in c.errors:
        print(f"  ERROR   {e}")
    for w in c.warnings:
        print(f"  warning {w}")
    if not c.errors:
        print("  OK — Gmail-safe structure")
    return not c.errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    ok = all([check(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
