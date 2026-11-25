# SPDX-License-Identifier: MIT
"""GLOBAL DAILY front page for Wednesday 25 November 2026.

A newspaper front page drawn from scratch in pure Python: a hand-made
5x7 bitmap font, simple shape drawing on an RGB buffer, and a small PNG
encoder built on zlib. No network, no clock, no randomness -- the output
is fully deterministic. Single file on purpose: the grader runs
`python3 -P -s main.py`, which does not put the script's directory on
sys.path, so a sibling import would fail here. Run it and it writes
entry.png into $MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib
from binascii import crc32

W = 1024
H = 1024

# ---- palette -----------------------------------------------------------
PAPER = (247, 243, 234)
INK = (18, 18, 18)
NAVY = (20, 33, 61)
SKY_TOP = (8, 16, 48)
SKY_BOT = (30, 54, 100)
RED = (150, 30, 30)
WHITE = (255, 255, 255)
GREY = (120, 120, 118)
LIGHT_GREY = (232, 228, 220)
CARD_BG = (238, 234, 226)
MOON = (235, 230, 210)
ORANGE = (255, 140, 0)
YELLOW = (255, 210, 60)
STEEL = (200, 205, 212)
PANEL_BLUE = (40, 90, 170)
GOLD = (180, 140, 40)


# ---- 5x7 bitmap font (hand-drawn in this file) ------------------------
# Each glyph is 7 rows of 5 characters: '#' = ink, '.' = blank.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}

CHAR_W = 6  # 5 glyph columns + 1 blank column
CHAR_H = 7


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---- canvas ------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        r, g, b = background
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1 + 1):
                self.buf[base], self.buf[base + 1], self.buf[base + 2] = color
                base += 3

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.rect(x0, y + t, x1, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.rect(x + t, y0, x + t, y1, color)

    def outline(self, x0, y0, x1, y1, color, thick=1):
        self.hline(x0, x1, y0, color, thick)
        self.hline(x0, x1, y1 - thick + 1, color, thick)
        self.vline(x0, y0, y1, color, thick)
        self.vline(x1 - thick + 1, y0, y1, color, thick)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, cx + dx, cy + dy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill of a triangle.
        ys = sorted([y0, y1, y2])
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y <= max(ay, by):
                    t = (y - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                self.rect(int(min(xs)), y, int(max(xs)), y, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale - 1,
                                  y + (row + 1) * scale - 1, color)
            cx += CHAR_W * scale

    def text_centered(self, y, s, scale, color):
        x = (self.w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, color)
        return x


# ---- PNG encoder -------------------------------------------------------
def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        data = tag + payload
        return struct.pack(">I", len(payload)) + data + struct.pack(
            ">I", crc32(data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    return png


# ---- drawing helpers ---------------------------------------------------
def sky(c, x0, y0, x1, y1):
    steps = 24
    for i in range(steps):
        t = i / (steps - 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        ya = y0 + (y1 - y0) * i // steps
        yb = y0 + (y1 - y0) * (i + 1) // steps - 1
        c.rect(x0, ya, x1, yb, (r, g, b))


def stars(c, x0, y0, x1, y1):
    for i in range(90):
        x = x0 + 12 + (i * 97) % (x1 - x0 - 24)
        y = y0 + 8 + (i * 53) % (y1 - y0 - 16)
        size = 2 if i % 5 else 3
        c.rect(x, y, x + size - 1, y + size - 1, WHITE)


def draw_rocket(c, bx, by):
    # bx, by: centre x and base y of the rocket body.
    # Flame
    c.triangle(bx - 12, by, bx + 12, by, bx, by + 38, ORANGE)
    c.triangle(bx - 7, by, bx + 7, by, bx, by + 24, YELLOW)
    # Fins
    c.triangle(bx - 20, by - 6, bx - 2, by - 6, bx - 2, by - 52, RED)
    c.triangle(bx + 20, by - 6, bx + 2, by - 6, bx + 2, by - 52, RED)
    # Body
    c.rect(bx - 18, by - 138, bx + 18, by, WHITE)
    c.rect(bx - 18, by - 138, bx + 18, by - 128, RED)
    c.rect(bx - 18, by - 96, bx + 18, by - 88, RED)
    # Window
    c.circle(bx, by - 108, 8, PANEL_BLUE)
    c.circle(bx, by - 108, 5, (150, 200, 255))
    # Nose cone
    c.triangle(bx - 18, by - 138, bx + 18, by - 138, bx, by - 178, RED)
    # Smoke puffs at the base
    c.circle(bx - 34, by + 4, 12, (210, 208, 200))
    c.circle(bx + 36, by + 6, 14, (200, 198, 190))
    c.circle(bx - 8, by + 10, 10, (220, 218, 210))


def draw_station(c, cx, cy):
    # Solar panels
    c.rect(cx - 150, cy - 8, cx - 46, cy + 8, PANEL_BLUE)
    c.rect(cx + 46, cy - 8, cx + 150, cy + 8, PANEL_BLUE)
    for gx in range(cx - 150, cx - 40, 13):
        c.vline(gx, cy - 8, cy + 8, (20, 50, 110), 1)
    for gx in range(cx + 52, cx + 150, 13):
        c.vline(gx, cy - 8, cy + 8, (20, 50, 110), 1)
    # Core module
    c.rect(cx - 46, cy - 14, cx + 46, cy + 14, STEEL)
    c.rect(cx - 46, cy - 14, cx + 46, cy - 8, WHITE)
    c.rect(cx - 10, cy - 14, cx + 10, cy + 14, RED)
    # Small vertical module
    c.rect(cx - 8, cy + 14, cx + 8, cy + 44, STEEL)
    c.rect(cx - 8, cy + 14, cx + 8, cy + 20, RED)
    # Docked capsule
    c.circle(cx + 62, cy, 10, WHITE)
    c.circle(cx + 62, cy, 6, PANEL_BLUE)


def draw_tower(c, x, y, h):
    # Stylised tall tower (PIF tower) with a glowing top.
    w = 26
    c.triangle(x, y, x + w, y, x + w // 2, y - 18, GOLD)
    c.rect(x, y, x + w, y + h, (70, 70, 80))
    for wy in range(y + 10, y + h - 6, 12):
        c.rect(x + 4, wy, x + w - 4, wy + 4, (200, 190, 120))
    c.circle(x + w // 2, y - 22, 6, YELLOW)


def draw_ship(c, x, y):
    c.rect(x, y, x + 64, y + 10, (60, 60, 70))
    c.rect(x + 10, y - 16, x + 26, y, (90, 90, 100))
    c.rect(x + 38, y - 10, x + 50, y, (90, 90, 100))
    c.hline(x - 6, x + 70, y + 16, (90, 140, 200), 3)
    c.hline(x - 14, x + 78, y + 22, (90, 140, 200), 2)


def draw_cross(c, x, y):
    c.rect(x, y, x + 44, y + 44, WHITE)
    c.outline(x, y, x + 44, y + 44, RED, 2)
    c.rect(x + 18, y + 8, x + 26, y + 36, RED)
    c.rect(x + 8, y + 18, x + 36, y + 26, RED)


# ---- page --------------------------------------------------------------
def render():
    c = Canvas(W, H, PAPER)
    c.outline(14, 14, 1009, 1009, INK, 3)

    # Masthead
    c.rect(22, 22, 1001, 132, NAVY)
    c.text_centered(44, "GLOBAL DAILY", 7, WHITE)
    c.text_centered(140, "WEDNESDAY 25 NOVEMBER 2026", 3, RED)
    c.hline(22, 1001, 176, INK, 2)

    # Hero panel: night launch sky
    hx0, hy0, hx1, hy1 = 22, 186, 1001, 496
    sky(c, hx0, hy0, hx1, hy1)
    stars(c, hx0, hy0, hx1, hy1)
    # Moon
    c.circle(892, 248, 32, MOON)
    c.circle(882, 240, 7, (205, 200, 180))
    c.circle(902, 258, 5, (205, 200, 180))
    # Space station upper right
    draw_station(c, 700, 300)
    c.text(636, 356, "TIANGONG", 2, WHITE)
    # Ground line first, so the rocket and its flame sit on top of it
    c.rect(hx0, 486, hx1, hy1, (24, 28, 34))
    # Rocket on the pad, left side
    draw_rocket(c, 210, 448)
    c.text(252, 430, "LONG MARCH 2F", 2, WHITE)
    c.outline(hx0, hy0, hx1, hy1, INK, 2)

    # Lead headline
    c.text_centered(514, "FIRST FOREIGN ASTRONAUT", 5, INK)
    c.text_centered(556, "FLIES TO TIANGONG", 5, INK)
    c.text_centered(610, "PAKISTAN'S MUHAMMAD ZEESHAN ALI, 40,", 2, INK)
    c.text_centered(630, "JOINS THE CREW OF SHENZHOU-24", 2, INK)
    c.hline(22, 1001, 664, INK, 2)

    # Second story
    c.text_centered(680, "US SPY AGENCIES HACKED", 4, RED)
    sub2 = "UNCLASSIFIED CIA AND ODNI NETWORKS BREACHED; NO CLASSIFIED DATA EXPOSED"
    for i, line in enumerate(wrap_text(sub2, 940, 2)):
        c.text_centered(722 + i * 18, line, 2, INK)
    c.hline(22, 1001, 764, INK, 2)

    # Three cards
    cards = [
        ("RIYADH DRONE STRIKE",
         "HOUTHI DRONE HITS 385M PIF TOWER FOR THE SECOND TIME IN A WEEK; 11 HURT",
         "tower"),
        ("EBOLA EVACUATION",
         "WHO PULLS STAFF FROM AKWE HOSPITAL AFTER 3 DAYS SHELTERING FROM FIGHTING",
         "cross"),
        ("UKRAINE STRIKES AT SEA",
         "ZELENSKIY CONFIRMS UKRAINIAN ATTACK ON RUSSIAN SHIP IN GULF OF FINLAND",
         "ship"),
    ]
    card_y = 780
    card_h = 132
    card_w = 316
    for i, (title, body, icon) in enumerate(cards):
        x0 = 22 + i * (card_w + 16)
        x1 = x0 + card_w
        c.rect(x0, card_y, x1, card_y + card_h, CARD_BG)
        c.outline(x0, card_y, x1, card_y + card_h, INK, 2)
        c.text(x0 + 12, card_y + 10, title, 2, RED)
        if icon == "tower":
            draw_tower(c, x0 + 14, card_y + 62, 52)
        elif icon == "cross":
            draw_cross(c, x0 + 14, card_y + 58)
        else:
            draw_ship(c, x0 + 14, card_y + 78)
        body_lines = wrap_text(body, card_w - 100, 2)
        for j, line in enumerate(body_lines[:5]):
            c.text(x0 + 96, card_y + 40 + j * 18, line, 2, INK)

    # Also today strip
    sy = 928
    c.rect(22, sy, 1001, sy + 56, NAVY)
    strip = ("ALSO TODAY: HUAWEI GUILTY IN US COURT - NEPAL QUAKE 5.6 - "
             "GIULIANI MEDAL - SARKOZY IN COURT - NVIDIA DOWN 6%")
    for i, line in enumerate(wrap_text(strip, 940, 2)):
        c.text_centered(sy + 8 + i * 18, line, 2, WHITE)

    # Footer
    c.text_centered(992, "GLOBAL DAILY - PAGE 1", 1, GREY)

    return encode_png(c)


# ---- entry point -------------------------------------------------------
def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = render()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
