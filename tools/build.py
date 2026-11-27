#!/usr/bin/env python3
"""Compose the 27 November 2026 front page and write entry.png beside the repo root.

Pillow only. The build asserts its own limits: canvas size, every text line fits
its box, and every text/background pair clears WCAG 4.5:1. Any violation raises.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"

PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (26, 26, 26)
MUTED = (84, 78, 68)
RED = (139, 26, 26)
WHITE = (255, 255, 255)

# (tag, headline, summary, source, tag colour)
STORIES = [
    ("UKRAINE WAR",
     "Trump says he asked Putin to pull back",
     "Speaking Thursday, the US president said he told Putin last week he wants Russia to "
     "pull back military aggression across Europe, hoping for a quick settlement.",
     "The Standard (HK)", (139, 26, 26)),
    ("EUROPE",
     "EU leaders wrestle over 2028-34 budget",
     "Summit leaders debated a budget proposal of nearly EUR 1.6 trillion and financing "
     "for Ukraine, aiming for a deal before a run of national elections next year.",
     "The Standard (HK)", (22, 76, 130)),
    ("DIPLOMACY",
     "Lithuania threatens Taiwan office status",
     "Vilnius says it will revoke the legal status of Taiwan's representative office "
     "unless Taipei changes the mission's name, as it seeks to normalise ties with China.",
     "The Standard (HK)", (92, 62, 120)),
    ("UNITED STATES",
     "Thanksgiving storm hits the East Coast",
     "Wind gusts up to 70 mph (112 kph) toppled trees and power lines, cutting power to "
     "hundreds of thousands of users and disrupting flights on the holiday.",
     "The Standard (HK), SBS News", (28, 96, 70)),
    ("ECONOMY",
     "Bank of England to cut capital rules",
     "The central bank said Thursday it will lower capital requirements for the largest "
     "UK-focused banks after a review found domestic lenders were hit disproportionately.",
     "The Standard (HK)", (120, 70, 14)),
    ("KOREAN PENINSULA",
     "North Korea pauses support for Russia",
     "Ukrainian intelligence says Pyongyang has temporarily suspended military support "
     "for Russia; analysts link it to Moscow's remarks on easing Korean tensions.",
     "SBS News (Seoul)", (60, 60, 66)),
]


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def need_contrast(fg, bg, what):
    ratio = contrast(fg, bg)
    assert ratio >= 4.5, f"contrast {ratio:.2f} < 4.5 for {what}"


def wrap(draw, text, font, max_w, max_lines, what):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            assert cur, f"{what}: single word '{w}' wider than box"
            lines.append(cur)
            cur = w
    lines.append(cur)
    assert len(lines) <= max_lines, f"{what}: {len(lines)} lines > {max_lines}"
    for ln in lines:
        assert draw.textlength(ln, font=font) <= max_w, f"{what}: line overflows"
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    assert img.size == (1024, 1024)

    f_title = ImageFont.truetype(SERIF_B, 62)
    f_date = ImageFont.truetype(SANS_B, 17)
    f_tag = ImageFont.truetype(SANS_B, 13)
    f_head = ImageFont.truetype(SERIF_B, 23)
    f_body = ImageFont.truetype(SANS, 15)
    f_lead = ImageFont.truetype(SERIF_B, 38)
    f_lead_body = ImageFont.truetype(SANS, 18)
    f_src = ImageFont.truetype(SANS, 14)
    f_foot = ImageFont.truetype(SANS, 13)

    M = 32
    # Masthead
    need_contrast(INK, PAPER, "masthead title")
    title = "THE WORLD TODAY"
    assert d.textlength(title, font=f_title) <= W - 2 * M, "title overflows"
    d.text((W // 2, 30), title, font=f_title, fill=INK, anchor="mt")
    d.rectangle([M, 108, W - M, 111], fill=INK)
    need_contrast(MUTED, PAPER, "date line")
    date = "FRIDAY 27 NOVEMBER 2026  |  SIX STORIES FROM THE DAY'S WORLD NEWS"
    assert d.textlength(date, font=f_date) <= W - 2 * M, "date overflows"
    d.text((W // 2, 120), date, font=f_date, fill=MUTED, anchor="mt")
    d.rectangle([M, 148, W - M, 149], fill=INK)

    # Layout: full-width lead, then a row of 3 and a row of 2.
    gap = 14
    top, bottom = 162, 960
    lead_h = 206
    row_h = (bottom - top - lead_h - 2 * gap) // 2
    full = W - 2 * M
    c3 = (full - 2 * gap) // 3
    c2 = (full - gap) // 2
    slots = [(M, top, full, lead_h, True)]
    y2 = top + lead_h + gap
    slots += [(M + k * (c3 + gap), y2, c3, row_h, False) for k in range(3)]
    y3 = y2 + row_h + gap
    slots += [(M + k * (c2 + gap), y3, c2, row_h, False) for k in range(2)]
    assert y3 + row_h <= bottom + 1, "cards overflow the page area"
    assert len(slots) == len(STORIES)

    need_contrast(INK, CARD, "headline/body")
    need_contrast(MUTED, CARD, "source")
    pad = 18
    bar = 8

    for i, ((tag, head, body, src, col), (x, y, w, h, lead)) in enumerate(zip(STORIES, slots)):
        d.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
        d.rectangle([x, y, x + w, y + bar], fill=col)  # colour-coded top bar
        need_contrast(WHITE, col, f"tag colour {tag}")
        fh = f_lead if lead else f_head
        fb = f_lead_body if lead else f_body
        lead_lh, body_lh = (44, 26) if lead else (29, 22)
        iw = w - 2 * pad
        tw = int(d.textlength(tag, font=f_tag)) + 16
        ty = y + bar + 14
        d.rectangle([x + pad, ty, x + pad + tw, ty + 22], fill=col)
        d.text((x + pad + 8, ty + 4), tag, font=f_tag, fill=WHITE)
        if lead:
            d.text((x + w - pad, ty + 4), "LEAD STORY", font=f_tag, fill=MUTED, anchor="ra")
        hl = wrap(d, head, fh, iw, 2 if lead else 3, f"headline {i}")
        cy = draw_lines(d, x + pad, ty + 34, hl, fh, INK, lead_lh)
        bl = wrap(d, body, fb, iw, 3 if lead else 6, f"body {i}")
        cy = draw_lines(d, x + pad, cy + 8, bl, fb, INK, body_lh)
        src_text = "Source: " + src
        assert d.textlength(src_text, font=f_src) <= iw, f"source {i} overflows"
        sy = y + h - pad - 14
        assert cy + 6 <= sy, f"card {i}: text collides with source line ({cy} > {sy})"
        d.rectangle([x + pad, sy - 8, x + w - pad, sy - 7], fill=(205, 198, 184))
        d.text((x + pad, sy), src_text, font=f_src, fill=MUTED)

    # Footer
    foot = "Compiled 27 Nov 2026 from The Standard (Hong Kong) and SBS News (Seoul). Events as reported Thu 26 Nov."
    need_contrast(MUTED, PAPER, "footer")
    assert d.textlength(foot, font=f_foot) <= W - 2 * M, "footer overflows"
    d.text((W // 2, 984), foot, font=f_foot, fill=MUTED, anchor="mt")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    assert size <= 1024 * 1024, f"PNG too large: {size}"
    print(f"wrote {os.path.normpath(out)} {img.size} {size} bytes")


if __name__ == "__main__":
    main()
