#!/usr/bin/env python3
"""Genera QR e biglietto A5 pieghevole per il regalo dei 40 anni di Andrea."""
from pathlib import Path
import math

import qrcode
import qrcode.image.svg
from PIL import Image
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
OUT = ASSETS / "card-a5.pdf"

URL = "https://fabiomatricardi.github.io/40/"

# ---------------------------------------------------------------- colors
PAPER = HexColor("#F6F1E7")
INK = HexColor("#17202A")
INK_SOFT = HexColor("#4A5560")
TEAL = HexColor("#0E5B57")
TEAL_SOFT = HexColor("#13736D")
CLAY = HexColor("#B4552D")
LINE = Color(0.09, 0.13, 0.16, alpha=0.16)

# ---------------------------------------------------------------- fonts
FONTS = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Georgia", FONTS / "georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic", FONTS / "georgiai.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", FONTS / "georgiab.ttf"))
pdfmetrics.registerFont(TTFont("Segoe", FONTS / "segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Segoe-Bold", FONTS / "segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Segoe-Italic", FONTS / "segoeuii.ttf"))


def tracked(c, text, x, y, size, font, color, tracking=0.16, align="left"):
    """Testo con spaziatura tra le lettere (in em)."""
    c.setFont(font, size)
    c.setFillColor(color)
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    track = size * tracking
    total = sum(widths) + track * max(0, len(text) - 1)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    for ch, w in zip(text, widths):
        c.drawString(x, y, ch)
        x += w + track
    return total


def para(c, text, x, y, width, style):
    p = Paragraph(text, style)
    w, h = p.wrapOn(c, width, 1000 * mm)
    p.drawOn(c, x, y - h)
    return h


def draw_qr(c, text, x, y, size, dark=INK):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=0)
    qr.add_data(text)
    qr.make(fit=True)
    m = qr.get_matrix()
    n = len(m)
    cell = size / n
    for row, values in enumerate(m):
        for col, on in enumerate(values):
            if on:
                c.setFillColor(dark)
                c.rect(x + col * cell, y + (n - 1 - row) * cell, cell + 0.05, cell + 0.05, stroke=0, fill=1)
    return n


# ---------------------------------------------------------------- QR assets
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=1, border=4)
qr.add_data(URL)
qr.make(fit=True)
modules = len(qr.get_matrix())
print(f"URL: {URL} ({len(URL)} caratteri) -> QR {modules}x{modules} moduli (EC Q)")

svg = qrcode.make(URL, image_factory=qrcode.image.svg.SvgPathImage,
                  error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4)
svg.save(ASSETS / "qr.svg")

box = max(1, 2048 // modules)
img = qrcode.make(URL, error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4, box_size=box)
img = img.get_image().convert("L").resize((2048, 2048), Image.NEAREST)
img.save(ASSETS / "qr.png", dpi=(600, 600))
print("QR: assets/qr.png (2048px), assets/qr.svg")

# ---------------------------------------------------------------- page setup
W, H = landscape(A4)          # 297 x 210 mm
PW = W / 2                    # pannello A5
M = 10 * mm                   # margine di sicurezza

c = canvas.Canvas(str(OUT), pagesize=(W, H))
c.setTitle("Buon compleanno Andrea - 40")
c.setAuthor("Fabio Matricardi")
c.setSubject("Biglietto A5 pieghevole con QR")

def paper_bg():
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)

def fold_ticks():
    c.setStrokeColor(Color(0.09, 0.13, 0.16, alpha=0.35))
    c.setLineWidth(0.5)
    c.setDash(1, 2)
    c.line(W / 2, H - 5 * mm, W / 2, H)
    c.line(W / 2, 0, W / 2, 5 * mm)
    c.setDash()

# ================================================================ PAGE 1 — esterno
paper_bg()

# ---- back cover (pannello sinistro)
c.setStrokeColor(Color(0.05, 0.36, 0.34, alpha=0.28))
c.setLineWidth(0.9)
c.circle(M + 13 * mm, H - 34 * mm, 12 * mm, stroke=1, fill=0)
c.setFont("Georgia-Italic", 20)
c.setFillColor(Color(0.05, 0.36, 0.34, alpha=0.55))
c.drawCentredString(M + 13 * mm, H - 36.5 * mm, "1:00")

sty = ParagraphStyle("q", fontName="Georgia-Italic", fontSize=15.5, leading=24,
                     textColor=INK, alignment=1)
para(c, "Regola n.1:<br/>i regali migliori si aprono in un minuto.", 
     PW / 2 - 52 * mm, H / 2 + 22 * mm, 104 * mm, sty)

c.setStrokeColor(LINE)
c.setLineWidth(0.6)
c.line(PW / 2 - 14 * mm, H / 2 + 6 * mm, PW / 2 + 14 * mm, H / 2 + 6 * mm)

sub = ParagraphStyle("sub", fontName="Segoe-Italic", fontSize=10.6, leading=16,
                     textColor=INK_SOFT, alignment=1)
para(c, "Il libro \u00e8 tuo.<br/>Il minuto lo metti tu.", PW / 2 - 52 * mm, H / 2 - 2 * mm, 104 * mm, sub)

tracked(c, "FABIO \u00b7 COREA DEL SUD \u00b7 2026", PW / 2, M + 2 * mm,
        7.6, "Segoe", INK_SOFT, tracking=0.2, align="center")

# ---- front cover (pannello destro)
BX0, BY0, BX1, BY1 = PW + 9 * mm, 9 * mm, W - 9 * mm, H - 9 * mm
c.setFillColor(TEAL)
c.roundRect(BX0, BY0, BX1 - BX0, BY1 - BY0, 3.5 * mm, stroke=0, fill=1)

cx = (BX0 + BX1) / 2
iw = BX1 - BX0 - 16 * mm

tracked(c, "BUON COMPLEANNO", cx, BY1 - 17 * mm, 8.4, "Segoe-Bold", Color(1, 1, 1, alpha=0.72),
        tracking=0.34, align="center")

c.setFont("Georgia-Italic", 34)
c.setFillColor(PAPER)
c.drawCentredString(cx, BY1 - 33 * mm, "Andrea,")

# grande 40 in filigrana
c.saveState()
c.setFillColor(Color(1, 1, 1, alpha=0.11))
c.setFont("Georgia", 150)
c.drawCentredString(cx, BY1 - 100 * mm, "40")
c.restoreState()

tag = ParagraphStyle("tag", fontName="Georgia", fontSize=15, leading=22,
                     textColor=Color(1, 1, 1, alpha=0.95), alignment=1)
para(c, "Un minuto per aprire il regalo.<br/><font name='Georgia-Italic'>Il resto della vita per usarlo bene.</font>",
     cx - iw / 2, BY1 - 112 * mm, iw, tag)

# QR su placca chiara
QR = 31 * mm
pad = 5 * mm
plate = QR + 2 * pad
qx = cx - plate / 2
qy = BY0 + 21 * mm
c.setFillColor(PAPER)
c.roundRect(qx, qy, plate, plate, 2.5 * mm, stroke=0, fill=1)
draw_qr(c, URL, qx + pad, qy + pad, QR, dark=INK)

tracked(c, "SCANSIONA QUI PER IL TUO REGALO", cx, BY0 + 12 * mm, 7.4, "Segoe-Bold",
        Color(1, 1, 1, alpha=0.85), tracking=0.22, align="center")
tracked(c, "EPUB \u00b7 ITALIANO \u00b7 SENZA DRM", cx, BY0 + 7 * mm, 6.6, "Segoe",
        Color(1, 1, 1, alpha=0.55), tracking=0.18, align="center")

fold_ticks()
c.showPage()

# ================================================================ PAGE 2 — interno
paper_bg()

# ---- sinistra: dedica
dx = M + 4 * mm
dy = H - 26 * mm
c.setFillColor(CLAY)
tracked(c, "PER I TUOI QUARANTA", dx, dy, 8, "Segoe-Bold", CLAY, tracking=0.28)
dy -= 13 * mm

h1 = ParagraphStyle("h1", fontName="Georgia", fontSize=27, leading=31, textColor=INK)
dy -= para(c, "Auguri, Andrea.", dx, dy, PW - 2 * (M + 4 * mm), h1)

dy -= 4 * mm
body = ParagraphStyle("body", fontName="Segoe", fontSize=12.6, leading=19.5, textColor=INK_SOFT)
dy -= para(c, "40 anni, un cantiere in Corea del Sud e ancora voglia di crescere: "
               "questo libro parla un po\u2019 di te.", dx, dy, PW - 2 * (M + 4 * mm), body)

dy -= 5 * mm
c.setStrokeColor(LINE)
c.setLineWidth(0.6)
c.line(dx, dy, dx + 26 * mm, dy)
dy -= 7 * mm

ps = ParagraphStyle("ps", fontName="Segoe-Italic", fontSize=11.4, leading=17.5, textColor=INK_SOFT)
dy -= para(c, "P.S. Se in riunione senti \u201cfissiamo gli obiettivi\u201d,<br/>"
               "non \u00e8 il libro: \u00e8 il cantiere.", dx, dy,
           PW - 2 * (M + 4 * mm), ps)

dy -= 10 * mm
c.setFont("Georgia-Italic", 17)
c.setFillColor(TEAL)
c.drawString(dx, dy, "\u2014 Fabio")

# blocco libro in basso
by = M + 6 * mm
c.setStrokeColor(LINE)
c.setLineWidth(0.6)
c.line(dx, by + 24 * mm, dx + PW - 2 * (M + 4 * mm), by + 24 * mm)
tracked(c, "IL TUO REGALO", dx, by + 17 * mm, 7.4, "Segoe-Bold", CLAY, tracking=0.26)
c.setFont("Georgia-Italic", 14.5)
c.setFillColor(INK)
c.drawString(dx, by + 9 * mm, "La self leadership e l\u2019One Minute Manager")
tracked(c, "KEN BLANCHARD \u00b7 SUSAN FOWLER \u00b7 LAURENCE HAWKINS", dx, by + 3 * mm,
        6.8, "Segoe", INK_SOFT, tracking=0.14)

# ---- destra: come aprirlo
rx = PW + M + 4 * mm
ry = H - 26 * mm
c.setFillColor(TEAL)
tracked(c, "COME APRIRLO", rx, ry, 8, "Segoe-Bold", TEAL, tracking=0.28)
ry -= 11 * mm

h2 = ParagraphStyle("h2", fontName="Georgia", fontSize=17.5, leading=22, textColor=INK)
ry -= para(c, "Due minuti, poi si legge.", rx, ry, PW - 2 * (M + 4 * mm), h2)
ry -= 7 * mm

step_head = ParagraphStyle("sh", fontName="Segoe-Bold", fontSize=10.6, leading=14, textColor=INK)
step_body = ParagraphStyle("sb", fontName="Segoe", fontSize=10.4, leading=15, textColor=INK_SOFT)

steps = [
    ("iPhone / iPad", "Apri il file dall\u2019app File, tocca Condividi e scegli Libri."),
    ("Android", "Va benissimo Google Play Books: \u201cApri con\u201d e il libro \u00e8 in libreria."),
    ("E-reader", "Kobo, PocketBook o KOReader: copia l\u2019EPUB nella cartella dei libri."),
]
for i, (head, txt) in enumerate(steps, start=1):
    c.setFont("Segoe-Bold", 11)
    c.setFillColor(CLAY)
    c.drawString(rx, ry - 3.2 * mm, f"0{i}")
    hh = para(c, f"<b>{head}</b>", rx + 10 * mm, ry, PW - 2 * (M + 4 * mm) - 10 * mm, step_head)
    hb = para(c, txt, rx + 10 * mm, ry - hh - 0.8 * mm,
              PW - 2 * (M + 4 * mm) - 10 * mm, step_body)
    ry -= hh + hb + 8 * mm

c.setStrokeColor(LINE)
c.setLineWidth(0.6)
c.line(rx, ry + 2 * mm, rx + PW - 2 * (M + 4 * mm), ry + 2 * mm)
ry -= 4 * mm
note = ParagraphStyle("note", fontName="Segoe-Italic", fontSize=10, leading=15, textColor=INK_SOFT)
para(c, "Il QR non scade e il libro non ha DRM: si apre su qualsiasi dispositivo, oggi e fra dieci anni.",
     rx, ry, PW - 2 * (M + 4 * mm), note)

c.setFont("Georgia-Italic", 14)
c.setFillColor(TEAL)
c.drawString(rx, M + 10 * mm, "Buon compleanno. E buon primo minuto.")

fold_ticks()
c.showPage()
c.save()
print(f"Biglietto: {OUT} (2 pagine A4 orizzontale, piega centrale)")