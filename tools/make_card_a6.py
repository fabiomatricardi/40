#!/usr/bin/env python3
"""Biglietto A6 da un solo foglio A4, piegato in 4 (quarter fold).

Un solo lato stampato: le quattro facciate (fronte, retro, interno sx, interno dx)
sono disposte sui quattro quadranti secondo la piega "quarter fold".
"""
from pathlib import Path
import qrcode
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "card-a6.pdf"
URL = "https://fabiomatricardi.github.io/40/"

PAPER = HexColor("#F6F1E7")
INK = HexColor("#17202A")
INK_SOFT = HexColor("#4A5560")
TEAL = HexColor("#0E5B57")
CLAY = HexColor("#B4552D")
LINE = Color(0.09, 0.13, 0.16, alpha=0.16)

FONTS = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Georgia", FONTS / "georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic", FONTS / "georgiai.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", FONTS / "georgiab.ttf"))
pdfmetrics.registerFont(TTFont("Segoe", FONTS / "segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Segoe-Bold", FONTS / "segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Segoe-Italic", FONTS / "segoeuii.ttf"))


def tracked(c, text, x, y, size, font, color, tracking=0.16, align="left"):
    c.setFont(font, size); c.setFillColor(color)
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    tr = size * tracking
    total = sum(widths) + tr * max(0, len(text) - 1)
    if align == "center": x -= total / 2
    elif align == "right": x -= total
    for ch, w in zip(text, widths):
        c.drawString(x, y, ch); x += w + tr
    return total


def para(c, text, x, y, width, style):
    p = Paragraph(text, style)
    w, h = p.wrapOn(c, width, 1000 * mm)
    p.drawOn(c, x, y - h)
    return h


def draw_qr(c, text, x, y, size, dark=INK):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=0)
    qr.add_data(text); qr.make(fit=True)
    m = qr.get_matrix(); n = len(m); cell = size / n
    for row, vals in enumerate(m):
        for col, on in enumerate(vals):
            if on:
                c.setFillColor(dark)
                c.rect(x + col * cell, y + (n - 1 - row) * cell, cell + .05, cell + .05, stroke=0, fill=1)


def paper(c):
    c.setFillColor(PAPER); c.rect(0, 0, 210 * mm, 297 * mm, stroke=0, fill=1)


def front(c, x, y, w, h):
    """Copertina. (x,y) = basso-sinistra del pannello."""
    bx, by, bw, bh = x + 6 * mm, y + 6 * mm, w - 12 * mm, h - 12 * mm
    c.setFillColor(TEAL)
    c.roundRect(bx, by, bw, bh, 3 * mm, stroke=0, fill=1)
    cx = bx + bw / 2
    iw = bw - 10 * mm

    tracked(c, "BUON COMPLEANNO", cx, by + bh - 11 * mm, 6.4, "Segoe-Bold",
            Color(1, 1, 1, alpha=.72), tracking=.3, align="center")
    c.setFont("Georgia-Italic", 21); c.setFillColor(PAPER)
    c.drawCentredString(cx, by + bh - 21 * mm, "Andrea,")

    c.saveState()
    c.setFillColor(Color(1, 1, 1, alpha=.10)); c.setFont("Georgia", 86)
    c.drawCentredString(cx, by + bh - 55 * mm, "40")
    c.restoreState()

    st = ParagraphStyle("t", fontName="Georgia", fontSize=9.2, leading=13.2,
                        textColor=Color(1, 1, 1, alpha=.95), alignment=1)
    para(c, "Un minuto per aprire il regalo.<br/><font name='Georgia-Italic'>Il resto della vita per usarlo bene.</font>",
         cx - iw / 2, by + bh - 60 * mm, iw, st)

    QR = 26 * mm; pad = 4 * mm; plate = QR + 2 * pad
    qx, qy = cx - plate / 2, by + 13 * mm
    c.setFillColor(PAPER); c.roundRect(qx, qy, plate, plate, 2 * mm, stroke=0, fill=1)
    draw_qr(c, URL, qx + pad, qy + pad, QR, dark=INK)

    tracked(c, "SCANSIONA QUI PER IL TUO REGALO", cx, by + 8 * mm, 5.4, "Segoe-Bold",
            Color(1, 1, 1, alpha=.85), tracking=.18, align="center")
    tracked(c, "EPUB \u00b7 ITALIANO \u00b7 SENZA DRM", cx, by + 4.4 * mm, 4.8, "Segoe",
            Color(1, 1, 1, alpha=.55), tracking=.16, align="center")


def back(c, x, y, w, h):
    c.setStrokeColor(Color(.05, .36, .34, alpha=.28)); c.setLineWidth(.8)
    c.circle(x + 20 * mm, y + h - 24 * mm, 9 * mm, stroke=1, fill=0)
    c.setFont("Georgia-Italic", 12.5); c.setFillColor(Color(.05, .36, .34, alpha=.55))
    c.drawCentredString(x + 20 * mm, y + h - 26.5 * mm, "1:00")

    q = ParagraphStyle("q", fontName="Georgia-Italic", fontSize=10.8, leading=16.5,
                       textColor=INK, alignment=1)
    para(c, "Regola n.1:<br/>i regali migliori si aprono in un minuto.",
         x + w / 2 - 40 * mm, y + h / 2 + 14 * mm, 80 * mm, q)
    c.setStrokeColor(LINE); c.setLineWidth(.5)
    c.line(x + w / 2 - 10 * mm, y + h / 2 + 6 * mm, x + w / 2 + 10 * mm, y + h / 2 + 6 * mm)
    s = ParagraphStyle("s", fontName="Segoe-Italic", fontSize=8, leading=11.5,
                       textColor=INK_SOFT, alignment=1)
    para(c, "Il libro \u00e8 tuo.<br/>Il minuto lo metti tu.",
         x + w / 2 - 40 * mm, y + h / 2 - 1 * mm, 80 * mm, s)
    tracked(c, "FABIO \u00b7 COREA DEL SUD \u00b7 2026", x + w / 2, y + 7 * mm,
            5.6, "Segoe", INK_SOFT, tracking=.2, align="center")


def inside_left(c, x, y, w, h):
    """Dedica."""
    dx = x + 9 * mm
    iw = w - 18 * mm
    dy = y + h - 14 * mm
    tracked(c, "PER I TUOI QUARANTA", dx, dy, 5.8, "Segoe-Bold", CLAY, tracking=.26)
    dy -= 8 * mm
    sty = ParagraphStyle("h", fontName="Georgia", fontSize=17, leading=20, textColor=INK)
    dy -= para(c, "Auguri,<br/>Andrea.", dx, dy, iw, sty)
    dy -= 2.5 * mm
    body = ParagraphStyle("b", fontName="Segoe", fontSize=8.6, leading=13, textColor=INK_SOFT)
    dy -= para(c, "40 anni, un cantiere in Corea del Sud e ancora voglia di crescere: "
                  "questo libro parla un po\u2019 di te.", dx, dy, iw, body)
    dy -= 4 * mm
    c.setStrokeColor(LINE); c.setLineWidth(.5); c.line(dx, dy, dx + 18 * mm, dy)
    dy -= 5 * mm
    ps = ParagraphStyle("p", fontName="Segoe-Italic", fontSize=7.8, leading=12, textColor=INK_SOFT)
    dy -= para(c, "P.S. Se in riunione senti \u201cfissiamo gli obiettivi\u201d,<br/>"
                  "non \u00e8 il libro: \u00e8 il cantiere.", dx, dy, iw, ps)
    dy -= 6 * mm
    c.setFont("Georgia-Italic", 12); c.setFillColor(TEAL)
    c.drawString(dx, dy, "\u2014 Fabio")


def inside_right(c, x, y, w, h):
    """Come aprirlo."""
    dx = x + 9 * mm
    iw = w - 18 * mm
    dy = y + h - 14 * mm
    tracked(c, "COME APRIRLO", dx, dy, 5.8, "Segoe-Bold", TEAL, tracking=.26)
    dy -= 7 * mm
    sty = ParagraphStyle("h2", fontName="Georgia", fontSize=12.5, leading=15, textColor=INK)
    dy -= para(c, "Due minuti,<br/>poi si legge.", dx, dy, iw, sty)
    dy -= 4 * mm

    head = ParagraphStyle("hd", fontName="Segoe-Bold", fontSize=7.4, leading=10, textColor=INK)
    txt = ParagraphStyle("tx", fontName="Segoe", fontSize=7.2, leading=10.5, textColor=INK_SOFT)
    steps = [
        ("iPhone / iPad", "Apri il file da File, tocca Condividi e scegli Libri."),
        ("Android", "Con Google Play Books: \u201cApri con\u201d e il libro \u00e8 in libreria."),
        ("E-reader", "Kobo, PocketBook o KOReader: copia l\u2019EPUB nella cartella libri."),
    ]
    for i, (hd, tx) in enumerate(steps, 1):
        c.setFont("Segoe-Bold", 7.6); c.setFillColor(CLAY)
        c.drawString(dx, dy - 2 * mm, f"0{i}")
        hh = para(c, hd, dx + 6 * mm, dy, iw - 6 * mm, head)
        hb = para(c, tx, dx + 6 * mm, dy - hh - .5 * mm, iw - 6 * mm, txt)
        dy -= hh + hb + 4.5 * mm

    c.setStrokeColor(LINE); c.setLineWidth(.5)
    c.line(dx, dy + 1.5 * mm, dx + iw, dy + 1.5 * mm)
    dy -= 2.5 * mm
    note = ParagraphStyle("n", fontName="Segoe-Italic", fontSize=6.6, leading=9.5, textColor=INK_SOFT)
    para(c, "Il QR non scade e il libro non ha DRM: si apre ovunque, oggi e fra dieci anni.",
         dx, dy, iw, note)

    c.setFont("Georgia-Italic", 8.6); c.setFillColor(TEAL)
    c.drawString(dx, y + 8 * mm, "Buon compleanno. E buon primo minuto.")


W, H = A4  # 210 x 297 mm
c = canvas.Canvas(str(OUT), pagesize=A4)
c.setTitle("Buon compleanno Andrea - 40 (A6, piega in 4)")
c.setAuthor("Fabio Matricardi")
paper(c)

PW, PH = W / 2, H / 2  # 105 x 148.5 mm

# esterno: riga in basso [retro | fronte]
back(c, 0, 0, PW, PH)
front(c, PW, 0, PW, PH)

# interno: riga in alto, ruotata di 180 (come richiede la piega in 4)
def rotated(x0, y0, fn):
    c.saveState()
    c.translate(x0 + PW, y0 + PH)
    c.rotate(180)
    fn(c, 0, 0, PW, PH)
    c.restoreState()

rotated(0, PH, inside_right)    # interno destro
rotated(PW, PH, inside_left)    # interno sinistro

# segni di piega sui bordi
c.setStrokeColor(Color(.09, .13, .16, alpha=.30)); c.setLineWidth(.4)
c.setDash(1.5, 2.5)
c.line(W / 2, 0, W / 2, 4 * mm); c.line(W / 2, H - 4 * mm, W / 2, H)
c.line(0, H / 2, 4 * mm, H / 2); c.line(W - 4 * mm, H / 2, W, H / 2)
c.setDash()

c.showPage(); c.save()
print("A6:", OUT, f"({W/mm:.0f}x{H/mm:.0f} mm, 1 pagina)")