#!/usr/bin/env python3
"""
WRITTEN BY CLAUDE

Generates the theme-aware SVG assets used by README.md / README-ko.md.

Palette is lifted straight from junick.dev/styles/global.css so the GitHub
profile and the site read as one brand.

Usage:  python3 scripts/generate_assets.py
"""

import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# --- palette (mirrors junick.dev :root and its prefers-color-scheme block) ---
THEMES = {
    "light": {
        "bg": "#eef2ff", "surface": "#ffffff", "border": "#c7d3f0",
        "text": "#0f172a", "muted": "#4a5a80",
        "accent": "#3461e8", "accent_soft": "#dde8ff",
        "glow": "#3461e8", "glow_op": "0.06",
    },
    "dark": {
        "bg": "#0b1120", "surface": "#131c31", "border": "#2a3a5c",
        "text": "#e6ecfb", "muted": "#93a4c8",
        "accent": "#7d9dff", "accent_soft": "#1d2a48",
        "glow": "#7d9dff", "glow_op": "0.10",
    },
}

FONT = ("'Wanted Sans Variable','Wanted Sans','Pretendard',-apple-system,"
        "BlinkMacSystemFont,'Segoe UI','Apple SD Gothic Neo','Malgun Gothic',"
        "Helvetica,Arial,sans-serif")


def w(text, size, weight=400):
    """Rough advance-width estimate; CJK counts as full-width."""
    tot = 0.0
    for ch in text:
        if ord(ch) > 0x2E80:
            tot += size
        elif ch in "iljt.,'!|":
            tot += size * 0.28
        elif ch.isupper():
            tot += size * 0.62
        else:
            tot += size * 0.53
    return tot * (1.04 if weight >= 700 else 1.0)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- hero banner
def hero(t, tagline, chips, ko_size=27):
    """Name + tagline banner. Collapses to a shorter canvas when `chips` is empty."""
    W = 1000
    has_chips = bool(chips)
    H = 250 if has_chips else 190

    # decorative node graph (a nod to graph problems), fitted to the canvas height
    base = [(742, 74), (826, 48), (912, 88), (768, 152), (858, 130),
            (940, 176), (700, 118), (886, 196)]
    edges = [(0, 1), (1, 2), (0, 3), (0, 6), (1, 4), (2, 4), (3, 4),
             (4, 5), (3, 7), (5, 7), (6, 3)]
    squash = 1.0 if has_chips else 0.62
    nodes = [(x, H / 2 + (y - 122) * squash) for x, y in base]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-label="{esc(tagline)}">',
         "<defs>",
         f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0%" stop-color="{t["bg"]}"/>'
         f'<stop offset="100%" stop-color="{t["surface"]}"/></linearGradient>',
         f'<radialGradient id="glow" cx="50%" cy="50%" r="50%">'
         f'<stop offset="0%" stop-color="{t["glow"]}" stop-opacity="{t["glow_op"]}"/>'
         f'<stop offset="100%" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>',
         "</defs>",
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="url(#bg)" '
         f'stroke="{t["border"]}" stroke-width="1.5"/>',
         f'<circle cx="838" cy="{H/2:.0f}" r="230" fill="url(#glow)"/>',
         f'<rect x="1" y="1" width="5" height="{H-2}" rx="2.5" fill="{t["accent"]}" opacity="0.9"/>']

    for a, b in edges:
        x1, y1 = nodes[a]; x2, y2 = nodes[b]
        p.append(f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}" '
                 f'stroke="{t["accent"]}" stroke-width="1.4" opacity="0.28"/>')
    for i, (x, y) in enumerate(nodes):
        r, op = (7, 0.85) if i in (0, 4) else (5, 0.5)
        p.append(f'<circle cx="{x}" cy="{y:.1f}" r="{r}" fill="{t["accent"]}" opacity="{op}"/>')

    # name + korean name (ko_size lets the Korean build show 쮸닊 bigger)
    p.append(f'<text x="54" y="96" font-family="{FONT}" font-size="58" font-weight="800" '
             f'fill="{t["text"]}" letter-spacing="-1.5">_junick</text>')
    nx = 54 + w("_junick", 58, 800) + 20
    p.append(f'<text x="{nx:.0f}" y="96" font-family="{FONT}" font-size="{ko_size}" '
             f'font-weight="600" fill="{t["accent"]}">쮸닊</text>')
    p.append(f'<text x="56" y="134" font-family="{FONT}" font-size="20" font-weight="500" '
             f'fill="{t["muted"]}">{esc(tagline)}</text>')

    x = 56
    for c in chips:
        cw = w(c, 14, 600) + 30
        p.append(f'<rect x="{x:.0f}" y="164" width="{cw:.0f}" height="32" rx="16" '
                 f'fill="{t["accent_soft"]}" stroke="{t["border"]}" stroke-width="1"/>')
        p.append(f'<text x="{x + cw/2:.0f}" y="185" font-family="{FONT}" font-size="14" '
                 f'font-weight="600" fill="{t["accent"]}" text-anchor="middle">{esc(c)}</text>')
        x += cw + 10

    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------ highlights grid
def highlights(t, cards):
    W, GAP, COLS = 1000, 18, 3
    CW = (W - GAP * (COLS - 1)) / COLS
    CH = 132
    rows = (len(cards) + COLS - 1) // COLS
    H = rows * CH + (rows - 1) * GAP

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-label="Selected highlights">']

    n = len(cards)
    for i, (date, title, sub1, sub2) in enumerate(cards):
        row, col = divmod(i, COLS)
        in_row = min(COLS, n - row * COLS)          # cards on this row
        row_w = in_row * CW + (in_row - 1) * GAP
        cx = (W - row_w) / 2 + col * (CW + GAP)     # centred when the row is short
        cy = row * (CH + GAP)
        p.append(f'<rect x="{cx+0.75:.1f}" y="{cy+0.75:.1f}" width="{CW-1.5:.1f}" '
                 f'height="{CH-1.5:.1f}" rx="12" fill="{t["surface"]}" '
                 f'stroke="{t["border"]}" stroke-width="1.5"/>')
        p.append(f'<rect x="{cx+0.75:.1f}" y="{cy+22:.1f}" width="3.5" height="{CH-44:.1f}" '
                 f'rx="1.75" fill="{t["accent"]}"/>')
        tx = cx + 22
        p.append(f'<text x="{tx:.0f}" y="{cy+34:.0f}" font-family="{FONT}" font-size="11.5" '
                 f'font-weight="700" fill="{t["accent"]}" letter-spacing="1.1">{esc(date.upper())}</text>')
        p.append(f'<text x="{tx:.0f}" y="{cy+65:.0f}" font-family="{FONT}" font-size="19" '
                 f'font-weight="700" fill="{t["text"]}">{esc(title)}</text>')
        p.append(f'<text x="{tx:.0f}" y="{cy+91:.0f}" font-family="{FONT}" font-size="13.5" '
                 f'fill="{t["muted"]}">{esc(sub1)}</text>')
        if sub2:
            p.append(f'<text x="{tx:.0f}" y="{cy+111:.0f}" font-family="{FONT}" font-size="13.5" '
                     f'fill="{t["muted"]}">{esc(sub2)}</text>')

    p.append("</svg>")
    return "\n".join(p)



# ----------------------------------------------------------- profile cards
def profiles(t, cards):
    """Competitive-programming profile cards.

    Replaces the animated third-party badge SVGs, which lose all of their text
    when GitHub embeds them through <img> (their fonts/animations never run).
    """
    W, GAP, COLS = 1000, 18, 3
    CW = (W - GAP * (COLS - 1)) / COLS
    CH = 122
    H = CH

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-label="Competitive programming profiles">']

    for i, (platform, tier, line1, line2, tint) in enumerate(cards):
        cx = i * (CW + GAP)
        p.append(f'<rect x="{cx+0.75:.1f}" y="0.75" width="{CW-1.5:.1f}" height="{CH-1.5:.1f}" '
                 f'rx="12" fill="{t["surface"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
        p.append(f'<rect x="{cx+0.75:.1f}" y="0.75" width="{CW-1.5:.1f}" height="4" '
                 f'rx="2" fill="{tint}"/>')
        tx = cx + 22
        p.append(f'<circle cx="{tx+4:.0f}" cy="34" r="4.5" fill="{tint}"/>')
        p.append(f'<text x="{tx+18:.0f}" y="38" font-family="{FONT}" font-size="12.5" '
                 f'font-weight="700" fill="{t["muted"]}" letter-spacing="0.6">{esc(platform)}</text>')
        p.append(f'<text x="{tx:.0f}" y="70" font-family="{FONT}" font-size="21" '
                 f'font-weight="700" fill="{t["text"]}">{esc(tier)}</text>')
        p.append(f'<text x="{tx:.0f}" y="93" font-family="{FONT}" font-size="13.5" '
                 f'fill="{t["muted"]}">{esc(line1)}</text>')
        p.append(f'<text x="{tx:.0f}" y="111" font-family="{FONT}" font-size="12.5" '
                 f'fill="{t["muted"]}" opacity="0.85">{esc(line2)}</text>')

    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------- content
EN_TAGLINE = "a dev making random stuff"
KO_TAGLINE = "그때그때 만들고 싶은 거 만드는 개발자"

# EN_CHIPS = ["IOAI 2026 · Korean Representative", "USACO Platinum", "CF Expert · AtCoder Yellow"]
# KO_CHIPS = ["IOAI 2026 국가대표", "USACO Platinum", "CF Expert · AtCoder Yellow"]

EN_CHIPS = []
KO_CHIPS = []

EN_CARDS = [
    ("Jun 2026", "IOAI 2026", "Korean Representative", "3rd Int'l Olympiad in AI"),
    ("Feb 2026", "USACO Platinum", "Qualified; top division", "Bronze '24 · Silver '25 · Gold '26"),
    ("Jun 2026", "KOAI 2026 Silver", "4th place nationwide", "1st Korean Olympiad in AI"),
    ("2025–26", "Youth IT Gold ×3", "4th / 5th / 6th competitions", "Algorithm - 2nd nationwide"),
    ("2024–26", "Problem Writer", "UCPC 2025 & 2026 Prelim", "SUAPC 2024 Summer"),
]

KO_CARDS = [
    ("2026. 06", "IOAI 2026", "대한민국 국가대표", "제3회 국제인공지능올림피아드"),
    ("2026. 02", "USACO Platinum", "최상위 디비전 진출", "Bronze '24 · Silver '25 · Gold '26"),
    ("2026. 06", "KOAI 2026 은상", "전국 4위", "제1회 한국인공지능올림피아드"),
    ("2025–26", "청소년 IT 금상 3회", "제4·5·6회 대회", "알고리즘 부문 - 전국 2위"),
    ("2024–26", "문제 출제", "UCPC 2025 · 2026 예선", "SUAPC 2024 Summer"),
]



# Snapshot of the competitive profiles. Refresh with the live sources:
#   solved.ac   https://solved.ac/api/v3/user/show?handle=minjunnick
#   Codeforces  https://codeforces.com/api/user.info?handles=M1LLI0N_PP
#   AtCoder     https://atcoder.jp/users/junick_/history/json
SAC, CF, AC = "#00B4FC", "#2563EB", "#C9A700"

EN_PROFILES = [
    ("SOLVED.AC", "Diamond II", "Rating 2,568 · Class 7", "2,720 solved · @minjunnick", SAC),
    ("CODEFORCES", "Expert", "Rating 1,752 · Max 2,030", "Peak Candidate Master · @M1LLI0N_PP", CF),
    ("ATCODER", "Yellow · 1 Dan", "Rating 2,007 · Top 1.25%", "53 rated contests · @junick_", AC),
]

KO_PROFILES = [
    ("SOLVED.AC", "Diamond II", "레이팅 2,568 · 클래스 7", "2,720문제 해결 · @minjunnick", SAC),
    ("CODEFORCES", "Expert", "레이팅 1,752 · 최고 2,030", "최고 Candidate Master · @M1LLI0N_PP", CF),
    ("ATCODER", "Yellow · 1 Dan", "레이팅 2,007 · 상위 1.25%", "53회 참가 · @junick_", AC),
]

def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for name, theme in THEMES.items():
        t = THEMES[name]
        jobs.append((f"hero-{name}.svg", hero(t, EN_TAGLINE, EN_CHIPS)))
        jobs.append((f"hero-ko-{name}.svg", hero(t, KO_TAGLINE, KO_CHIPS, ko_size=40)))
        jobs.append((f"highlights-{name}.svg", highlights(t, EN_CARDS)))
        jobs.append((f"highlights-ko-{name}.svg", highlights(t, KO_CARDS)))
        jobs.append((f"profiles-{name}.svg", profiles(t, EN_PROFILES)))
        jobs.append((f"profiles-ko-{name}.svg", profiles(t, KO_PROFILES)))
    for fn, svg in jobs:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote assets/{fn}  ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
