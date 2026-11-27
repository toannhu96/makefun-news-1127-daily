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
    f_head = ImageFont.truetype(SERIF_B, 24)
    f_body = ImageFont.truetype(SANS, 16)
    f_src = ImageFont.truetype(SANS, 13)
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

    # Cards: 2 columns x 3 rows
    gap = 16
    cw = (W - 2 * M - gap) // 2
    top, bottom = 164, 962
    ch = (bottom - top - 2 * gap) // 3
    pad = 16
    need_contrast(INK, CARD, "headline")
    need_contrast(MUTED, CARD, "body/source")
    need_contrast(WHITE, RED, "tag")

    for i, (tag, head, body, src, col) in enumerate(STORIES):
        x = M + (i % 2) * (cw + gap)
        y = top + (i // 2) * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=INK, width=2)
        need_contrast(WHITE, col, f"tag colour {tag}")
        tw = int(d.textlength(tag, font=f_tag)) + 16
        d.rectangle([x + pad, y + pad, x + pad + tw, y + pad + 22], fill=col)
        d.text((x + pad + 8, y + pad + 4), tag, font=f_tag, fill=WHITE)
        iw = cw - 2 * pad
        hl = wrap(d, head, f_head, iw, 2, f"headline {i}")
        cy = draw_lines(d, x + pad, y + pad + 32, hl, f_head, INK, 30)
        bl = wrap(d, body, f_body, iw, 4, f"body {i}")
        cy = draw_lines(d, x + pad, cy + 4, bl, f_body, INK, 21)
        need_contrast(INK, CARD, "body")
        src_text = "Reported by " + src
        assert d.textlength(src_text, font=f_src) <= iw, f"source {i} overflows"
        sy = y + ch - pad - 15
        assert cy <= sy, f"card {i}: text collides with source line ({cy} > {sy})"
        d.text((x + pad, sy), src_text, font=f_src, fill=MUTED)

    # Footer
    foot = "Compiled 27 Nov 2026 from The Standard (Hong Kong) and SBS News (Seoul) reports. Events as reported Thursday 26 Nov."
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
