"""Front page for Friday 20 November 2026: 44 verified news stories.

Fresh rewrite for the news-image-20261120 bounty. Pure standard library
and fully deterministic: no network, no clock, no randomness, no external
font files. Text is drawn with a small built-in 5x7 bitmap font and the
PNG is encoded by hand with zlib.

Reads OUTPUT_DIR (default /output) and writes front-page.png, 1024x1024.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

INK = (18, 18, 18)
GREY = (96, 96, 96)
PAPER = (255, 255, 255)

# 5x7 bitmap font. Each glyph is 7 rows of 5 bits ("1" = ink, "0" = paper).
FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10101", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01110", "10001", "10010", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ")": ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    "*": ("00000", "01010", "00100", "11111", "00100", "01010", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "/": ("00001", "00010", "00010", "00100", "00100", "01000", "10000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10001", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10111", "10000", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "\\": ("10000", "01000", "01000", "00100", "00100", "00010", "00010"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "^": ("00100", "01010", "00000", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "`": ("01000", "00100", "00000", "00000", "00000", "00000", "00000"),
}

FONT.update({
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10000", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01110", "10001", "10001", "01110", "10000", "01100"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00000", "00100", "00000", "01100", "00100", "00100", "01110"),
    "j": ("00100", "00000", "01100", "00100", "00100", "00100", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10001", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "10001", "10001", "01010", "00100", "00100", "01100"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "{": ("00011", "00100", "00100", "01100", "00100", "00100", "00011"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "}": ("11000", "00100", "00100", "00110", "00100", "00100", "11000"),
    "~": ("00000", "00000", "01010", "10101", "00000", "00000", "00000"),
})


def text_width(text, scale):
    """Pixel width of text at the given scale (no trailing spacing)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_lines(text, max_width, scale):
    """Greedy word wrap. Returns a list of lines, each within max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """An RGB image held as a flat bytearray."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for row in range(y0, y1):
            base = (row * self.width + x0) * 3
            for col in range(x0, x1):
                off = base + (col - x0) * 3
                self.pixels[off] = colour[0]
                self.pixels[off + 1] = colour[1]
                self.pixels[off + 2] = colour[2]

    def draw_text(self, x, y, text, scale, colour, bold=False):
        """Draw text with the bitmap font. Bold adds a 1px right offset pass."""
        passes = (0, 1) if bold else (0,)
        for dx in passes:
            cx = x + dx
            for ch in text:
                glyph = FONT.get(ch)
                if glyph is None:
                    cx += 6 * scale
                    continue
                for row, bits in enumerate(glyph):
                    for col, bit in enumerate(bits):
                        if bit == "1":
                            self.fill_rect(
                                cx + col * scale, y + row * scale,
                                scale, scale, colour,
                            )
                cx += 6 * scale


def _png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    """Encode the canvas as a PNG file (filter 0, zlib level 9)."""
    raw = bytearray()
    row_bytes = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * row_bytes
        raw += canvas.pixels[start:start + row_bytes]
    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", header)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


# All 44 stories were published on Friday 20 November 2026. Each entry is
# (section, headline, summary). Headlines fit one line at scale 2 in a
# 464px column; summaries fit one line at scale 1. Sources: One Turn day
# digest for 20 Nov 2026, Just Security Early Edition 20 Nov 2026,
# Reuters wires 20 Nov 2026, Cricinfo, ABC, Field Level Media, TSN.
STORIES = [
    ("LEAD", "ICJ: Myanmar committed genocide",
     "World Court rules 9-6 against Myanmar over the Rohingya and orders reparations."),
    ("WORLD", "Shenzhen pact: Trump, Xi, Putin",
     "Shenzhen declaration pledges talks on trade, Ukraine and Taiwan."),
    ("WORLD", "Crimea Bridge hit a third time",
     "Ukraine strikes the Kerch bridge again; rail traffic halted."),
    ("WORLD", "Houthis strike Riyadh PIF tower",
     "Missile hits the PIF tower in Riyadh; air defences stop a follow-up salvo."),
    ("WORLD", "Tanker ablaze after Hormuz mine",
     "Mine sets a tanker ablaze in the Strait of Hormuz; war costs put at $48.3bn."),
    ("WORLD", "Gaza crossings at Yellow Line",
     "Aid and civilians cross at the Yellow Line as the ceasefire holds."),
    ("WORLD", "COP31 draft drops fossil phase-out",
     "New draft omits the fossil phase-out, angering island states and the EU."),
    ("WORLD", "UK-EU summit backs youth mobility",
     "London and Brussels agree a youth mobility scheme and closer energy ties."),
    ("WORLD", "UN chief race stalls at 8 votes",
     "No candidate reaches the threshold as the Security Council deadlocks."),
    ("WORLD", "Sudan drone strike kills 10",
     "Drone strike on a market town kills 10; aid groups warn of widening famine."),
    ("WORLD", "Haiti: 34 killed in Martissant",
     "Gang violence kills 34 in the Martissant district of Port-au-Prince."),
    ("WORLD", "Bukele wins third term",
     "El Salvador's president wins a third term; the opposition cries foul."),
    ("WORLD", "US-Venezuela military deal signed",
     "Washington and Caracas sign a military cooperation deal, easing tensions."),
    ("WORLD", "Hasina violence flares in Dhaka",
     "Clashes erupt in Dhaka as supporters of ousted PM Hasina defy a rally ban."),
    ("WORLD", "Somalia expels UAE envoy",
     "Mogadishu orders the UAE ambassador out, accusing Abu Dhabi of meddling."),
    ("WORLD", "Mongolia president resigns",
     "The president steps down after weeks of protests over corruption and prices."),
    ("WORLD", "Senegal boat capsizes",
     "A migrant boat capsizes off Senegal; dozens feared dead as rescuers search."),
    ("WORLD", "Texas executes Dennes",
     "Texas carries out the execution of Dennes after last-minute appeals fail."),
    ("MARKETS", "Anthropic soars 17% on debut",
     "Shares close near $97; the listing raises $81.3bn at a $1.5tn valuation."),
    ("MARKETS", "S&P slides 2% for a fifth day",
     "US stocks fall again as Japan's Nikkei drops 4.8% on rate and growth fears."),
    ("MARKETS", "Nvidia probed; Huang resigns",
     "California opens a probe and Huang resigns; 879,000 chips are at issue."),
    ("MARKETS", "Japan inflation hits year high",
     "Consumer prices hit their highest this year, raising pressure on the bank."),
    ("MARKETS", "Brazil defends real with $1bn",
     "The central bank spends $1bn to steady the real as the currency slides."),
    ("MARKETS", "Senate passes energy bill 62-33",
     "Bipartisan energy permitting bill clears the Senate, heading to the House."),
    ("MARKETS", "IEA warns on energy security",
     "The agency warns of tight supplies and price risks heading into winter."),
    ("MARKETS", "IMF: debt near 100% of GDP",
     "Global public debt nears 100% of GDP, the IMF warns in its latest outlook."),
    ("MARKETS", "Kenya signs $60bn minerals deal",
     "$60bn deal to develop the Mrima Hill rare-earth deposit signed in Nairobi."),
    ("MARKETS", "SpaceX lines up $44bn GPU deal",
     "Apollo and Goldman lead $44bn of financing for SpaceX data-centre GPUs."),
    ("MARKETS", "PayPal names Bramley as CFO",
     "PayPal appoints Claire Bramley chief financial officer with immediate effect."),
    ("MARKETS", "GTA 6 to cost $2.3bn to make",
     "Rockstar's GTA 6 budget reaches $2.3bn, the most expensive game ever made."),
    ("SCIENCE", "Voyager 1 a light-day from Earth",
     "NASA's Voyager 1 passes one light-day from Earth, 48 years after launch."),
    ("SCIENCE", "BepiColombo enters Mercury orbit",
     "The European-Japanese probe settles into Mercury orbit after a long cruise."),
    ("SCIENCE", "Fiji and Tonga declare drought",
     "Both Pacific nations declare drought disasters amid a long dry spell."),
    ("SCIENCE", "Cyclone Xavier bears down",
     "Cyclone Xavier strengthens as it tracks toward the Pacific islands."),
    ("SCIENCE", "El Nino storm lashes Los Angeles",
     "A powerful El Nino storm floods roads and cuts power across Los Angeles."),
    ("SCIENCE", "Kenya's last Ebola patient free",
     "Kenya discharges its last Ebola patient after 37 days, ending the outbreak."),
    ("SCIENCE", "US measles cases reach 5,838",
     "The CDC counts 5,838 measles cases this year, the worst tally in decades."),
    ("SCIENCE", "M5.1 quake shakes Monterey",
     "A magnitude 5.1 quake rattles Monterey County; no major damage reported."),
    ("SCIENCE", "Taiwan warns Meta on fake accounts",
     "Taipei warns Meta over China-linked accounts spreading disinformation."),
    ("SCIENCE", "White House fires cyber chief",
     "The White House dismisses cyber chief Cairncross in a security shake-up."),
    ("SPORT", "Nicholls 175* as NZ post 368",
     "Henry Nicholls hits 175 not out and Glenn Phillips 118 against India."),
    ("SPORT", "Jepchirchir banned for three years",
     "The marathon star gets a three-year doping ban and loses her Sydney title."),
    ("SPORT", "Rams' Nacua out after MCL surgery",
     "Puka Nacua has MCL surgery and will miss months, the Rams confirm."),
    ("SPORT", "Spurs top Clippers; Knicks win",
     "Wembanyama 32+11 in a 124-112 win; Knicks edge Timberwolves 102-99."),
]

FOOTER = ("Sources: One Turn 20 Nov digest, Just Security Early Edition, "
          "Reuters, Cricinfo, ABC, Field Level Media, TSN")

MARGIN = 32
COL_WIDTH = 464
GUTTER = 32
LEFT_X = MARGIN
RIGHT_X = MARGIN + COL_WIDTH + GUTTER


def draw_section_header(canvas, x, y, title):
    canvas.draw_text(x, y, title, 2, INK, bold=True)
    canvas.fill_rect(x, y + 18, COL_WIDTH, 2, INK)
    return y + 26


def draw_story(canvas, x, y, headline, summary):
    head_lines = wrap_lines(headline, COL_WIDTH, 2)
    sum_lines = wrap_lines(summary, COL_WIDTH, 1)
    assert len(head_lines) == 1, "headline too long: %r" % headline
    assert len(sum_lines) == 1, "summary too long: %r" % summary
    canvas.draw_text(x, y, head_lines[0], 2, INK)
    canvas.draw_text(x, y + 17, sum_lines[0], 1, GREY)
    return y + 32


def draw_column(canvas, x, start_y, sections):
    y = start_y
    for section, items in sections:
        y = draw_section_header(canvas, x, y, section)
        for headline, summary in items:
            y = draw_story(canvas, x, y, headline, summary)
        y += 6
    return y


def render():
    assert len(STORIES) == 44, "expected 44 stories, got %d" % len(STORIES)
    by_section = {}
    for section, headline, summary in STORIES:
        by_section.setdefault(section, []).append((headline, summary))
    for name in ("LEAD", "WORLD", "MARKETS", "SCIENCE", "SPORT"):
        assert name in by_section, "missing section %s" % name

    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead.
    title = "THE DAILY FRONT PAGE"
    canvas.draw_text((WIDTH - text_width(title, 4)) // 2, 24, title, 4, INK, bold=True)
    canvas.fill_rect(MARGIN, 62, WIDTH - 2 * MARGIN, 3, INK)
    date_line = "FRIDAY 20 NOVEMBER 2026 - 44 STORIES"
    canvas.draw_text((WIDTH - text_width(date_line, 2)) // 2, 72, date_line, 2, INK)
    canvas.fill_rect(MARGIN, 92, WIDTH - 2 * MARGIN, 1, INK)

    # Lead story, full width.
    lead_head, lead_sum = by_section["LEAD"][0]
    canvas.draw_text(MARGIN, 106, "LEAD", 1, GREY, bold=True)
    canvas.draw_text(MARGIN, 118, lead_head, 3, INK, bold=True)
    canvas.draw_text(MARGIN, 145, lead_sum, 2, GREY)
    canvas.fill_rect(MARGIN, 168, WIDTH - 2 * MARGIN, 2, INK)

    # Two columns: WORLD + SPORT on the left, MARKETS + SCIENCE on the right.
    left_end = draw_column(canvas, LEFT_X, 184, [
        ("WORLD", by_section["WORLD"]),
        ("SPORT", by_section["SPORT"]),
    ])
    right_end = draw_column(canvas, RIGHT_X, 184, [
        ("MARKETS", by_section["MARKETS"]),
        ("SCIENCE", by_section["SCIENCE"]),
    ])
    assert left_end <= 960, "left column overflows: %d" % left_end
    assert right_end <= 960, "right column overflows: %d" % right_end

    # Footer.
    canvas.fill_rect(MARGIN, 968, WIDTH - 2 * MARGIN, 1, INK)
    canvas.draw_text(MARGIN, 978, FOOTER, 1, GREY)
    return canvas, left_end, right_end


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas, left_end, right_end = render()
    path = os.path.join(out_dir, "front-page.png")
    write_png(path, canvas)
    print("stories: %d" % len(STORIES))
    print("size: %dx%d" % (WIDTH, HEIGHT))
    print("left column ends at y=%d, right column ends at y=%d" % (left_end, right_end))
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
