#!/usr/bin/env python3
"""Generate the My Day paper route sheet (Letter PDF) from private/data.json (decrypt first: python3 tools/encrypt.py --decrypt).

Usage: python3 make_pdf.py [path-to-data.json]
Writes private/my-day-<date>.pdf next to the data file (local only: the site is
locked, so never publish a plain PDF to docs/). Empty tick boxes
throughout, for pen use on the dash.
"""
import json
import os
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

NAVY = HexColor("#264387")
DNAVY = HexColor("#1a2f61")
GOLD = HexColor("#F0A846")
INK = HexColor("#1d2433")
GRAY = HexColor("#5b6478")
LINE = HexColor("#dfe4ee")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "private", "data.json")


def box(c, x, y, s=9):
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.rect(x, y, s, s, stroke=1, fill=0)


def main():
    d = json.load(open(DATA))
    stops = d.get("stops", [])
    out = os.path.join(os.path.dirname(DATA), "my-day-%s.pdf" % d.get("date", "day"))
    W, H = LETTER
    c = canvas.Canvas(out, pagesize=LETTER)
    L, R = 0.5 * inch, W - 0.5 * inch
    y = H - 0.55 * inch

    # Header
    logo = os.path.join(HERE, "docs", "logo.png")
    if os.path.exists(logo):
        c.drawImage(logo, L, y - 32, width=150, height=32.3, mask="auto", preserveAspectRatio=True)
    c.setFillColor(DNAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawRightString(R, y - 12, "MY DAY")
    c.setFillColor(GOLD)
    c.rect(L, y - 40, R - L, 2.2, stroke=0, fill=1)
    y -= 58
    c.setFillColor(DNAVY)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(L, y, d.get("dayLabel", ""))
    y -= 15
    total_drive = sum(s.get("driveFromPrev") or 0 for s in stops)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9.5)
    c.drawString(L, y, "%d stops · %d min driving%s" % (
        len(stops), total_drive, (" · first stop " + stops[0]["start"]) if stops else ""))
    y -= 10
    c.setStrokeColor(LINE)
    c.line(L, y, R, y)
    y -= 16

    def need(h):
        nonlocal y
        if y - h < 0.55 * inch:
            c.showPage()
            y = H - 0.55 * inch

    # Start
    if d.get("start"):
        need(34)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(L, y, "START")
        y -= 13
        c.setFillColor(INK)
        c.setFont("Helvetica", 11)
        c.drawString(L, y, d["start"])
        y -= 20

    # Today's inspections
    insps = d.get("inspections") or []
    if insps:
        need(30 + 26 * len(insps))
        c.setFillColor(DNAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(L, y, "Today's Inspections")
        y -= 4
        c.setFillColor(GOLD)
        c.rect(L, y, R - L, 1.6, stroke=0, fill=1)
        y -= 15
        for x in insps:
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 10.5)
            head = "%s  %s — %s" % (x.get("time", ""), x.get("type", ""),
                                    (x.get("address") or "").split(",")[0])
            c.drawString(L, y, head)
            y -= 12
            meta = " · ".join(v for v in [
                "#" + x["permit"] if x.get("permit") else "",
                ("Inspector " + x["inspector"]) if x.get("inspector") else "",
                x.get("contact") or "",
                x.get("note") or ""] if v)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 9.5)
            c.drawString(L, y, meta)
            y -= 14
        c.setStrokeColor(LINE)
        c.line(L, y, R, y)
        y -= 16

    # Load the Truck (two columns)
    counts = {}
    for s in stops:
        for m in s.get("materials") or []:
            counts[m] = counts.get(m, 0) + 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if items:
        need(30 + 15 * ((len(items) + 1) // 2))
        c.setFillColor(DNAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(L, y, "Load the Truck")
        y -= 4
        c.setFillColor(GOLD)
        c.rect(L, y, R - L, 1.6, stroke=0, fill=1)
        y -= 15
        colw = (R - L) / 2
        half = (len(items) + 1) // 2
        top = y
        for idx, (name, n) in enumerate(items):
            cx = L if idx < half else L + colw
            cy = top - 15 * (idx if idx < half else idx - half)
            box(c, cx, cy - 2)
            c.setFillColor(INK)
            c.setFont("Helvetica", 9.5)
            label = name + ("  ×%d" % n if n > 1 else "")
            c.drawString(cx + 14, cy, label)
        y = top - 15 * half - 8
        c.setStrokeColor(LINE)
        c.line(L, y, R, y)
        y -= 16

    # Stops
    for i, s in enumerate(stops):
        mats = s.get("materials") or []
        need(44 + 13.5 * len(mats))
        if s.get("driveFromPrev"):
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 8.5)
            c.drawCentredString((L + R) / 2, y, "— %d min drive —" % s["driveFromPrev"])
            y -= 14
        box(c, L, y - 3, 11)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        tstr = "%s – %s" % (s.get("start", ""), s.get("end", ""))
        c.drawString(L + 18, y, tstr)
        street = (s.get("address") or "").split(",")[0]
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(L + 26 + c.stringWidth(tstr, "Helvetica-Bold", 10.5), y, street)
        y -= 13.5
        job = s["title"].split(" — ")[1] if " — " in s.get("title", "") else s.get("title", "")
        meta = " · ".join(x for x in [job, s.get("who") or "",
                                      ",".join((s.get("address") or "").split(",")[1:]).strip()] if x)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 9.5)
        c.drawString(L + 18, y, meta)
        y -= 12
        if s.get("note"):
            c.drawString(L + 18, y, s["note"])
            y -= 12
        if s.get("trackUrl"):
            c.setFillColor(NAVY)
            c.setFont("Helvetica", 8.5)
            c.drawString(L + 18, y, "Job page: " + s["trackUrl"])
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 9.5)
            y -= 12
        for m in mats:
            box(c, L + 18, y - 2, 8)
            c.setFillColor(INK)
            c.setFont("Helvetica", 9.5)
            c.drawString(L + 31, y, m)
            y -= 13.5
        y -= 6
        c.setStrokeColor(LINE)
        c.line(L, y, R, y)
        y -= 14

    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8.5)
    c.drawString(L, 0.45 * inch, "Sharma Electric & HVAC · EC13013924 · CAC1823596 · TUG install 30 min · Underground 45 min · Drive time included")
    c.save()
    print("wrote", out)


if __name__ == "__main__":
    main()
