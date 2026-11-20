#!/usr/bin/env python3
"""THE WORLD TODAY - front page summing up Friday 20 November 2026.

Draws a 1024x1024 PNG newspaper front page with a hand-built stroke-vector
letterform renderer (glyphs are polylines on a 5x7 grid, stroked with round
caps) and a pure-stdlib PNG encoder. No network, no randomness, no clock:
two runs write byte-identical files.

Headlines below were collected from reports published on 20 Nov 2026
(Reuters, BBC, AP, The Guardian, MarketWatch, Space, and wire digests).
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 40, 75)
RED = (176, 42, 30)
GREEN = (28, 88, 58)
PURPLE = (88, 48, 108)
ORANGE = (168, 78, 18)
GREY = (120, 114, 104)
LIGHT = (226, 221, 210)
WHITE = (250, 248, 243)

# ---------------------------------------------------------------- font
# Each glyph: strokes separated by "|", each stroke a run of "x,y" points
# on a 5-wide (0..4) by 7-tall (0..6) grid. A zero-length stroke is a dot.
FONT = {
    "A": "0,6 2,0 4,6|1,4 3,4",
    "B": "0,0 0,6|0,0 3,0 4,1 4,2 3,3 0,3|0,3 3,3 4,4 4,5 3,6 0,6",
    "C": "4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5",
    "D": "0,0 0,6 3,6 4,5 4,1 3,0 0,0",
    "E": "4,0 0,0 0,6 4,6|0,3 3,3",
    "F": "0,6 0,0 4,0|0,3 3,3",
    "G": "4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5 4,3|4,3 2,3",
    "H": "0,0 0,6|4,0 4,6|0,3 4,3",
    "I": "2,0 2,6|1,0 3,0|1,6 3,6",
    "J": "2,0 2,5 1,6 0,5|1,0 3,0",
    "K": "0,0 0,6|4,0 0,3 4,6",
    "L": "0,0 0,6 4,6",
    "M": "0,6 0,0 2,3 4,0 4,6",
    "N": "0,6 0,0 4,6 4,0",
    "O": "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0",
    "P": "0,6 0,0 3,0 4,1 4,2 3,3 0,3",
    "Q": "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0|3,4 4,6",
    "R": "0,6 0,0 3,0 4,1 4,2 3,3 0,3|2,3 4,6",
    "S": "4,1 3,0 1,0 0,1 0,2 1,3 3,3 4,4 4,5 3,6 1,6 0,5",
    "T": "0,0 4,0|2,0 2,6",
    "U": "0,0 0,5 1,6 3,6 4,5 4,0",
    "V": "0,0 2,6 4,0",
    "W": "0,0 1,6 2,3 3,6 4,0",
    "X": "0,0 4,6|4,0 0,6",
    "Y": "0,0 2,3 4,0|2,3 2,6",
    "Z": "0,0 4,0 0,6 4,6",
    "0": "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0|1,5 3,1",
    "1": "1,1 2,0 2,6|1,6 3,6",
    "2": "1,0 3,0 4,1 4,2 2,4 0,6 4,6",
    "3": "1,0 3,0 4,1 4,2 3,3 1,3|3,3 4,4 4,5 3,6 1,6 0,5",
    "4": "0,4 3,0 3,6|0,4 4,4",
    "5": "4,0 0,0 0,3 3,3 4,4 4,5 3,6 1,6 0,5",
    "6": "3,0 1,0 0,2 0,5 1,6 3,6 4,5 4,4 3,3 0,3",
    "7": "0,0 4,0 2,6",
    "8": "1,0 3,0 4,1 4,2 3,3 1,3 0,2 0,1 1,0|1,3 3,3 4,4 4,5 3,6 1,6 0,5 0,4",
    "9": "0,5 0,2 1,0 3,0 4,1 4,4 3,6 1,6 0,5|1,3 3,3 4,2",
    " ": "",
    ".": "2,6 2,6",
    ",": "2,5 2,6 1,6",
    ":": "2,2 2,2|2,5 2,5",
    ";": "2,2 2,2|2,4 2,5 1,6",
    "!": "2,0 2,4|2,6 2,6",
    "?": "1,1 2,0 3,0 4,1 4,2 3,3 2,3|2,6 2,6",
    "'": "2,0 2,2",
    "-": "0,3 4,3",
    "(": "3,0 2,1 2,5 3,6",
    "$": "4,1 3,0 1,0 0,1 0,2 1,3 3,3 4,4 4,5 3,6 1,6 0,5|2,0 2,6",
    ")": "1,0 2,1 2,5 1,6",
    "/": "4,6 0,0",
    "%": "0,0 1,0 1,1 0,1|4,6 3,6 3,5 4,5|4,0 0,6",
    "+": "2,1 2,5|0,3 4,3",
    "=": "0,2 4,2|0,4 4,4",
    '"': "1,0 1,2|3,0 3,2",
    "*": "2,0 2,6|0,2 4,4|4,2 0,4",
    "[": "3,0 1,0 1,6 3,6",
    "]": "1,0 3,0 3,6 1,6",
    "|": "2,0 2,6",
}

GLYPHS = {}
for _ch, _spec in FONT.items():
    _strokes = []
    for _part in _spec.split("|"):
        _pts = []
        for _tok in _part.split():
            _x, _y = _tok.split(",")
            _pts.append((int(_x), int(_y)))
        if _pts:
            _strokes.append(_pts)
    GLYPHS[_ch] = _strokes


def sanitize(text):
    """Map fancy punctuation to the glyph set; fail loudly on the unknown."""
    text = text.upper()
    repl = {"\u2014": "-", "\u2013": "-", "\u2019": "'", "\u201c": '"',
            "\u201d": '"', "\u2022": "|", "\u00a0": " ", "\u00d7": "X"}
    out = []
    for ch in text:
        ch = repl.get(ch, ch)
        if ch not in GLYPHS:
            raise ValueError("no glyph for %r in %r" % (ch, text))
        out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def disc(self, cx, cy, r, color):
        r = max(1, int(round(r)))
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for x in range(cx - dx, cx + dx + 1):
                self.put(x, cy + dy, color)

    def segment(self, x0, y0, x1, y1, width, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x0 + (x1 - x0) * t))
            y = int(round(y0 + (y1 - y0) * t))
            self.disc(x, y, width / 2.0, color)

    def polyline(self, pts, width, color):
        for a, b in zip(pts, pts[1:]):
            self.segment(a[0], a[1], b[0], b[1], width, color)
        if len(pts) == 1:
            self.disc(pts[0][0], pts[0][1], width / 2.0, color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, color)

    def hline(self, x0, x1, y, width, color):
        self.rect(x0, y - width // 2, x1 - x0, width, color)

    def circle(self, cx, cy, r, width, color):
        # polyline approximation of a circle outline
        import math
        pts = []
        n = 64
        for k in range(n + 1):
            a = 2 * math.pi * k / n
            pts.append((int(round(cx + r * math.cos(a))),
                        int(round(cy + r * math.sin(a)))))
        self.polyline(pts, width, color)

    def ellipse(self, cx, cy, rx, ry, width, color):
        import math
        pts = []
        n = 72
        for k in range(n + 1):
            a = 2 * math.pi * k / n
            pts.append((int(round(cx + rx * math.cos(a))),
                        int(round(cy + ry * math.sin(a)))))
        self.polyline(pts, width, color)

    # -- text ------------------------------------------------------
    def char_advance(self, scale):
        return 6.0 * scale + scale * 0.35

    def text_width(self, text, scale):
        text = sanitize(text)
        return len(text) * self.char_advance(scale) - scale * 0.35

    def draw_text(self, x, y, text, scale, color, weight):
        """Draw text with top-left at (x, y); returns width drawn."""
        text = sanitize(text)
        cx = float(x)
        for ch in text:
            for stroke in GLYPHS[ch]:
                pts = [(int(round(cx + px * scale)),
                        int(round(y + py * scale))) for px, py in stroke]
                self.polyline(pts, weight, color)
            cx += self.char_advance(scale)
        return int(round(cx - x - scale * 0.35))

    def text_centered(self, cx, y, text, scale, color, weight):
        w = self.text_width(text, scale)
        return self.draw_text(int(round(cx - w / 2)), y, text, scale, color, weight)

    def wrap(self, text, scale, max_w):
        """Greedy word wrap; returns list of lines."""
        words = sanitize(text).split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- content
# (kicker, headline, summary) - every item verified in reports published
# on 20 November 2026 (see module docstring).
LEAD = ("TOP STORY - WASHINGTON",
        "TRUMP: NO RUSH ON IRAN",
        "DECISION AFTER JANUARY 1",
        "President says he will \"see what happens\" in the new year; "
        "the Senate rejects a bid to block a strike on Iran.")

WORLD = [
    ("THE HAGUE",
     "COURT: MYANMAR COMMITTED GENOCIDE",
     "First state ever found guilty of genocide."),
    ("KYIV",
     "RUSSIAN STRIKES HIT KYIV EMBASSIES",
     "Austrian and Dutch missions damaged overnight."),
    ("BRUSSELS",
     "EUROPE READY FOR TALKS WITH RUSSIA",
     "Leaders say they are open to talks to end the war."),
    ("SHENZHEN",
     "TRUMP, XI, PUTIN ISSUE PEACE PLEDGE",
     "Historic summit ends with a pledge on nuclear risk."),
    ("RIYADH",
     "HOUTHIS STRIKE AT RIYADH TOWER",
     "Saudi wealth fund tower damaged in a Houthi attack."),
    ("ODISHA, INDIA",
     "CYCLONE AKVAN: 300,000 EVACUATED",
     "Storm nears Odisha; 423 rescue teams deployed."),
    ("SUVA",
     "FIJI DECLARES DROUGHT DISASTER",
     "El Nino dries up water supplies across the islands."),
    ("SEOUL",
     "COURT CLEARS EX-PM HAN DUCK-SOO",
     "Court overturns conviction tied to 2024 martial law."),
    ("VIENNA",
     "NORTH KOREA EXPANDS ENRICHMENT",
     "UN watchdog: Pyongyang enlarging its Yongbyon plant."),
    ("CARACAS",
     "US, VENEZUELA RESTORE MILITARY TIES",
     "Defence deal signed after months of tension."),
]

MARKETS = [
    ("NEW YORK",
     "ANTHROPIC DEBUTS AT $1.3 TRILLION",
     "AI firm closes day one near $97; biggest IPO ever."),
    ("NEW YORK",
     "NVIDIA LOSES $669BN IN SIX DAYS",
     "Chip giant's slide deepens as AI stocks give up gains."),
    ("NEW YORK",
     "STOCKS FACE WORST WEEK SINCE APRIL",
     "US indexes slide as recession trades emerge."),
    ("TOKYO",
     "BANK OF JAPAN SIGNALS MORE HIKES",
     "Ueda: rates will keep rising; 1.50% expected in Dec."),
    ("TOKYO",
     "JAPAN INFLATION HITS YEAR HIGH",
     "Core prices jump as energy subsidies expire."),
    ("WASHINGTON",
     "FED MINUTES FLAG HIKE RISK",
     "J.P. Morgan sees hikes at the next three meetings."),
    ("WASHINGTON",
     "NVIDIA FACES CHIP PROBE",
     "California AG subpoenas Nvidia over chip diversion."),
    ("WASHINGTON",
     "879,000 AI CHIPS CLEARED FOR CHINA",
     "Commerce approved sales to Chinese firms in 6 months."),
    ("GENEVA",
     "IMF WARNS ON 4.7% INFLATION",
     "Georgieva: many economies must keep policy tight."),
]

SCIENCE = [
    ("SPACE",
     "VOYAGER 1 PASSES ONE LIGHT-DAY",
     "NASA: probe now more than a light-day from Earth."),
    ("TOKYO",
     "HAYABUSA2 DROPS ASTEROID LANDING",
     "Engine trouble forces Japan's probe to change plans."),
    ("LOS ANGELES",
     "GTA 6 SALES PASS $1.8BN ODYSSEY",
     "Rockstar hit overtakes the film's global run."),
    ("ANTALYA",
     "COP31 NEARS END, 21 ISSUES OPEN",
     "Climate talks enter final two days with disputes open."),
    ("NEW YORK",
     "TRUMP PARDONS PETE ROSE",
     "Baseball's banned hits king pardoned posthumously."),
]

SPORT = [
    ("WELLINGTON",
     "NICHOLLS 113* SAVES NEW ZEALAND",
     "Hosts reach 273 for 5 on day one of the first Test."),
    ("JOHANNESBURG",
     "SOUTH AFRICA TOP WORLD TEST TABLE",
     "Proteas beat Bangladesh; Harmer takes 6 for 51."),
    ("RAWALPINDI",
     "SRI LANKA LEAD PAKISTAN BY 82",
     "Visitors 309 for 9 at stumps on day three."),
    ("SYDNEY",
     "THUNDER BEAT HEAT IN SIX-WICKET WIN",
     "Harris and Learoyd star in a Big Bash thriller."),
    ("LONDON",
     "GILL IN DRS ROW WITH UMPIRE",
     "India captain argues a review call on day one."),
]

SECTIONS = [
    ("WORLD", NAVY, WORLD),
    ("MARKETS + TECH", GREEN, MARKETS),
    ("SCIENCE + CULTURE", PURPLE, SCIENCE),
    ("SPORT", ORANGE, SPORT),
]


# ---------------------------------------------------------------- drawing
def draw_globe(cv, cx, cy, r):
    """Wireframe globe: outline, meridians, parallels, orbit ring."""
    cv.circle(cx, cy, r, 3, NAVY)
    cv.ellipse(cx, cy, int(r * 0.45), r, 2, NAVY)
    cv.ellipse(cx, cy, r, int(r * 0.45), 2, NAVY)
    cv.hline(cx - r, cx + r, cy, 2, NAVY)
    cv.hline(cx - int(r * 0.86), cx + int(r * 0.86), cy - int(r * 0.5), 2, NAVY)
    cv.hline(cx - int(r * 0.86), cx + int(r * 0.86), cy + int(r * 0.5), 2, NAVY)
    cv.ellipse(cx, cy, r + 14, int((r + 14) * 0.32), 2, RED)


def draw_section_header(cv, x, y, w, title, color):
    cv.rect(x, y, w, 24, color)
    cv.draw_text(x + 10, y + 5, title, 1.9, WHITE, 3)
    return y + 24


def draw_item(cv, x, y, w, kicker, headline, summary, color):
    """One story block; returns y just below it."""
    cv.draw_text(x, y, kicker, 1.15, color, 2)
    y += 11
    for line in cv.wrap(headline, 2.0, w):
        cv.draw_text(x, y, line, 2.0, INK, 2)
        y += 15
    for line in cv.wrap(summary, 1.35, w):
        cv.draw_text(x, y, line, 1.35, (74, 70, 62), 2)
        y += 11
    return y + 3


def build():
    cv = Canvas(W, H, PAPER)
    mx = 36
    col_w = (W - 2 * mx - 24) // 2  # 464
    right_x = mx + col_w + 24

    # ---- masthead ----
    cv.text_centered(W // 2, 18, "THE WORLD TODAY", 4.6, NAVY, 5)
    cv.hline(mx, W - mx, 62, 2, NAVY)
    cv.rect(mx, 70, W - 2 * mx, 36, RED)
    cv.text_centered(W // 2, 79, "FRIDAY, 20 NOVEMBER 2026", 2.3, WHITE, 3)
    cv.text_centered(W // 2, 116,
                     "THE DAY'S NEWS FROM EVERY REGION AND EVERY FIELD - IN ONE PICTURE",
                     1.25, GREY, 2)
    cv.hline(mx, W - mx, 140, 3, NAVY)

    # ---- lead story ----
    y = 156
    kicker, h1, h2, summ = LEAD
    cv.draw_text(mx, y, kicker, 1.3, RED, 2)
    y += 16
    cv.draw_text(mx, y, h1, 2.9, INK, 4)
    y += 24
    cv.draw_text(mx, y, h2, 2.9, INK, 4)
    y += 26
    for line in cv.wrap(summ, 1.55, 640):
        cv.draw_text(mx, y, line, 1.55, (74, 70, 62), 2)
        y += 14
    draw_globe(cv, 880, 208, 52)
    cv.text_centered(880, 272, "ONE DAY - ONE WORLD", 1.1, NAVY, 2)
    y = max(y, 292)
    cv.hline(mx, W - mx, y, 2, NAVY)
    y += 12

    # ---- two columns ----
    # left: WORLD then SPORT ; right: MARKETS then SCIENCE
    left_plan = [("WORLD", NAVY, WORLD), ("SPORT", ORANGE, SPORT)]
    right_plan = [("MARKETS + TECH", GREEN, MARKETS),
                  ("SCIENCE + CULTURE", PURPLE, SCIENCE)]
    col_end = {}
    for x, plan in ((mx, left_plan), (right_x, right_plan)):
        yy = y
        for title, color, items in plan:
            yy = draw_section_header(cv, x, yy, col_w, title, color)
            yy += 6
            for k, hd, sm in items:
                yy = draw_item(cv, x, yy, col_w, k, hd, sm, color)
                cv.hline(x, x + col_w, yy - 2, 1, LIGHT)
        col_end[x] = yy
    y = max(col_end.values())

    # ---- footer ----
    cv.hline(mx, W - mx, 986, 2, NAVY)
    cv.text_centered(W // 2, 994,
                     "COMPILED FROM REPORTS PUBLISHED ON 20 NOVEMBER 2026",
                     1.15, GREY, 2)
    print("layout: columns end left=%d right=%d footer=986" % (
        col_end[mx], col_end[right_x]))
    print("stories: lead 1 + world %d + markets %d + science %d + sport %d = %d"
          % (len(WORLD), len(MARKETS), len(SCIENCE), len(SPORT),
             1 + len(WORLD) + len(MARKETS) + len(SCIENCE) + len(SPORT)))
    return cv


# ---------------------------------------------------------------- png
def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    path = out_dir if out_dir.endswith(".png") else os.path.join(out_dir, "entry.png")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = encode_png(build())
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
