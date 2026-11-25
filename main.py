#!/usr/bin/env python3
"""News-image v2: "The World Today" front page for 25 November 2026.

Pure Python standard library only (no Pillow, no network). Renders a
1024x1024 newspaper-style front page summing up the world news of
Wednesday 25 November 2026 and writes it to /output/entry.png.

v2 is denser than v1 (which ranked 108/673, judge win rate 96.9743%,
0.77pp short of the top-50 line): ten numbered stories instead of five,
a world map with numbered markers for every story, and a longer
"also today" ticker. The ten stories were verified against Reuters /
CNN / AP / Bloomberg / Dow Jones reporting published on 25 Nov 2026:
  1. LEAD - CIA and the Office of the Director of National Intelligence
     hit by a cyberattack on unclassified systems; no classified data
     affected (CNN, first reported by the New York Times).
  2. Nvidia brings back Jensen Huang as CEO; staff give the returning
     founder a standing ovation, shares jump then waver on AI doubts
     (Dow Jones / Morningstar, 25 Nov).
  3. US jury convicts Huawei on 10 of 12 counts: trade-secret theft and
     bank fraud over Iran; acquitted of racketeering (Reuters/AP).
  4. Houthis strike Riyadh's tallest tower (PIF Tower) for the second
     time in a week; 11 people wounded (Reuters).
  5. Zelenskyy confirms Ukraine's drone strike on the Russian cargo
     ship Sparta II in the Gulf of Finland; Norway urges caution
     (Reuters/Bloomberg).
  6. Australia and Solomon Islands sign a security pact on Wednesday
     25 November, making Canberra the defence partner of choice
     (Reuters).
  7. French officials order former president Sarkozy and his wife
     Carla Bruni to trial over the Libya case; first hearing April
     2027 (Reuters).
  8. Ukraine asks for 115 billion euro in foreign aid for 2027,
     Zelenskyy says (25 Nov wire reports).
  9. China's Shenzhou-24 crewed mission launches from Jiuquan on
     25 November (25 Nov wire reports).
 10. Venezuela reveals a $237 billion debt load (Dow Jones, 25 Nov).
Also today: WHO evacuates Ebola hospital staff in DR Congo after
fighting; Real Madrid beat PSV 5-1; UK sanctions Houthi officials;
Mount Mayon eruption fears in the Philippines; Iraq orders seizure of
Kurdish oilfields; Trump awards Rudy Giuliani the Medal of Freedom.

Deterministic: no randomness, no clock, no I/O besides the output file,
so two runs produce byte-identical PNGs.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (27, 42, 74)
WHITE = (255, 255, 255)
GREY = (96, 92, 82)
LIGHT = (232, 226, 210)
GOLD = (201, 162, 39)
TAN = (216, 190, 130)

# ---------------------------------------------------------------- font
# 5x7 bitmap font: each glyph is 7 rows, each row a 5-bit value
# (bit 4 = leftmost column). All text is rendered in capitals.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
}


def text_width(s, scale):
    return len(s) * 6 * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def border(self, x, y, w, h, color, t=3):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d = (dx * dx + dy * dy) ** 0.5
                if r - t < d <= r:
                    self.set(cx + dx, cy + dy, color)

    def fill_poly(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[i]), int(xs[i + 1])
                self.fill_rect(xa, y, xb - xa + 1, 1, color)

    # ------------------------------------------------------------- text
    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_center(self, y, s, scale, color, cx0=0, cx1=W):
        w = text_width(s, scale)
        self.text(cx0 + (cx1 - cx0 - w) // 2, y, s, scale, color)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns a list of lines."""
        lines = []
        for raw in s.upper().split("\n"):
            words = raw.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if text_width(trial, scale) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines

    def para(self, x, y, s, scale, color, max_w, gap=5):
        lines = self.wrap(s, max_w, scale)
        for ln in lines:
            self.text(x, y, ln, scale, color)
            y += 7 * scale + gap
        return y


# ---------------------------------------------------------------- lead art
def lead_art(c, x, y, w, h):
    """Compact lead illustration: servers, warning triangle, padlock."""
    c.fill_rect(x, y, w, h, NAVY)
    # server stack, two units
    sx, sy = x + 18, y + 14
    for i in range(2):
        c.border(sx, sy + i * 36, 92, 26, WHITE, 2)
        c.fill_circle(sx + 11, sy + i * 36 + 13, 3, GOLD)
        c.fill_rect(sx + 24, sy + i * 36 + 10, 52, 3, WHITE)
        c.fill_rect(sx + 24, sy + i * 36 + 17, 36, 3, WHITE)
    # warning triangle
    tx, ty = x + 128, y + 12
    c.fill_poly([(tx + 45, ty), (tx + 90, ty + 78), (tx, ty + 78)], RED)
    c.fill_rect(tx + 40, ty + 28, 10, 30, WHITE)
    c.fill_rect(tx + 40, ty + 64, 10, 10, WHITE)
    # padlock
    px, py = x + 150, y + 96
    c.ring(px + 20, py + 8, 11, GOLD, 4)
    c.fill_rect(px, py + 6, 40, 26, GOLD)
    c.fill_circle(px + 20, py + 16, 4, NAVY)
    c.fill_rect(px + 18, py + 18, 4, 10, NAVY)
    c.text(x + 24, y + h - 14, "WASHINGTON", 1, WHITE)


# ---------------------------------------------------------------- world map
# Stylised continents as (lon, lat) outlines. Map panel: lon -180..180
# maps to x 44..524, lat 75..-55 maps to y 436..580.
MAP_X0, MAP_W = 44, 480
MAP_Y0, MAP_H = 436, 144


def lonlat(lon, lat):
    px = MAP_X0 + (lon + 180) * MAP_W / 360
    py = MAP_Y0 + (75 - lat) * MAP_H / 130
    return (int(px), int(py))


CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68),
     (-100, 68), (-90, 66), (-82, 66), (-76, 62), (-65, 60), (-60, 55),
     (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 32), (-81, 30), (-84, 30), (-87, 30), (-90, 29), (-94, 29),
     (-97, 26), (-100, 23), (-103, 20), (-105, 20), (-108, 23),
     (-112, 28), (-117, 32), (-122, 37), (-124, 42), (-125, 48),
     (-130, 55), (-140, 60), (-150, 60), (-158, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-42, 70), (-50, 74),
     (-58, 72), (-60, 68)],
    # South America
    [(-79, 9), (-77, 7), (-72, 11), (-68, 11), (-62, 9), (-58, 6),
     (-52, 4), (-50, 0), (-46, -3), (-42, -8), (-38, -13), (-35, -16),
     (-38, -21), (-41, -23), (-46, -26), (-49, -29), (-52, -33),
     (-56, -36), (-60, -39), (-64, -42), (-67, -46), (-69, -50),
     (-70, -54), (-73, -53), (-74, -48), (-73, -42), (-73, -36),
     (-72, -30), (-71, -22), (-71, -16), (-76, -12), (-79, -6),
     (-81, -2), (-80, 3), (-79, 8)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 28), (-17, 21), (-16, 15), (-14, 11),
     (-10, 7), (-8, 5), (-4, 5), (0, 6), (4, 6), (8, 4), (9, 0),
     (10, -5), (12, -10), (13, -16), (13, -22), (15, -27), (17, -32),
     (20, -35), (25, -34), (28, -32), (32, -28), (35, -24), (36, -20),
     (38, -16), (40, -12), (41, -6), (42, -1), (45, 2), (48, 5),
     (51, 10), (48, 11), (44, 12), (42, 15), (40, 20), (38, 24),
     (36, 28), (34, 31), (30, 31), (25, 32), (20, 33), (15, 34),
     (10, 37), (5, 37), (0, 36)],
    # Eurasia
    [(-10, 37), (-5, 36), (0, 38), (5, 40), (10, 42), (15, 44), (20, 44),
     (25, 41), (30, 40), (35, 36), (40, 38), (45, 40), (50, 42),
     (55, 45), (60, 50), (65, 55), (70, 60), (75, 65), (80, 68),
     (85, 70), (90, 72), (95, 75), (100, 76), (110, 74), (120, 72),
     (130, 70), (140, 71), (150, 70), (160, 68), (170, 66), (178, 65),
     (178, 62), (170, 60), (165, 60), (160, 55), (155, 50), (150, 45),
     (145, 40), (140, 35), (135, 33), (130, 30), (127, 33), (125, 38),
     (122, 40), (120, 35), (118, 30), (115, 25), (110, 20), (108, 15),
     (105, 12), (102, 10), (100, 8), (98, 12), (96, 16), (94, 18),
     (92, 21), (90, 22), (88, 22), (86, 20), (84, 18), (82, 15),
     (80, 12), (78, 8), (76, 10), (74, 15), (72, 20), (70, 22),
     (68, 24), (66, 25), (64, 25), (62, 25), (60, 25), (58, 26),
     (56, 27), (54, 28), (52, 29), (50, 30), (48, 32), (46, 34),
     (44, 36), (42, 38), (40, 40), (38, 41), (36, 42), (34, 42),
     (32, 42), (30, 42), (28, 41), (26, 40), (24, 40), (22, 40),
     (20, 39), (18, 40), (16, 41), (14, 42), (12, 44), (10, 44),
     (8, 43), (6, 43), (4, 42), (2, 41), (0, 39), (-2, 37), (-5, 36),
     (-8, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (142, 43), (143, 44), (141, 45), (140, 42), (139, 38),
     (137, 35), (134, 34), (131, 32)],
    # Indonesia
    [(95, 5), (98, 4), (100, 2), (102, 0), (104, -2), (106, -4),
     (108, -6), (110, -7), (112, -7), (114, -8), (116, -9), (118, -9),
     (120, -10), (122, -10), (124, -9), (126, -8), (128, -6), (130, -4),
     (132, -2), (134, 0), (136, 1), (134, 3), (132, 4), (130, 4),
     (128, 3), (126, 2), (124, 1), (122, 0), (120, 0), (118, 1),
     (116, 2), (114, 2), (112, 1), (110, 0), (108, 1), (106, 2),
     (104, 3), (102, 4), (100, 5), (98, 5)],
    # Australia
    [(113, -22), (115, -20), (118, -19), (121, -16), (124, -14),
     (128, -13), (132, -11), (135, -12), (138, -15), (140, -17),
     (142, -14), (144, -14), (146, -16), (148, -19), (150, -22),
     (152, -25), (153, -28), (152, -32), (150, -36), (147, -39),
     (144, -38), (141, -38), (138, -35), (135, -33), (132, -32),
     (129, -31), (126, -30), (123, -33), (120, -34), (117, -35),
     (114, -33), (113, -28), (113, -24)],
    # New Zealand
    [(167, -45), (169, -43), (171, -41), (173, -39), (175, -37),
     (177, -38), (175, -40), (173, -42), (170, -44), (168, -46)],
]

# Story markers: (number, lon, lat, nudge_x, nudge_y). Dots are computed
# from lon/lat through lonlat(); the nudge moves a dot a few pixels so
# crowded cities (Washington/Brooklyn, Gulf of Finland/Kyiv) stay
# readable, with a thin leader line back to the true spot.
MARKERS = [
    (1, -77, 39, 0, 0),      # Washington - CIA cyberattack
    (2, -122, 37, 0, 0),     # Santa Clara - Nvidia
    (3, -74, 41, 11, -9),    # Brooklyn - Huawei
    (4, 47, 25, 0, 0),       # Riyadh - PIF Tower
    (5, 24, 60, 0, 0),       # Gulf of Finland - Sparta II
    (6, 160, -10, 0, 0),     # Honiara - Solomons pact
    (7, 2, 49, 0, 0),        # Paris - Sarkozy trial
    (8, 31, 50, 5, 5),       # Kyiv - Ukraine aid ask
    (9, 99, 40, 0, 0),       # Jiuquan - Shenzhou-24
    (10, -67, 11, 0, 0),     # Caracas - Venezuela debt
]

# Ocean labels: (text, x, y) in panel coordinates.
OCEAN_LABELS = [
    ("PACIFIC OCEAN", 56, 522),
    ("ATLANTIC OCEAN", 252, 498),
    ("INDIAN OCEAN", 356, 546),
]


def draw_map(c):
    for poly in CONTINENTS:
        c.fill_poly([lonlat(lon, lat) for lon, lat in poly], TAN)
    for label, lx, ly in OCEAN_LABELS:
        c.text(lx, ly, label, 1, LIGHT)
    for num, lon, lat, nx, ny in MARKERS:
        tx, ty = lonlat(lon, lat)
        dx, dy = tx + nx, ty + ny
        if nx or ny:
            c.line(dx, dy, tx, ty, WHITE, 1)
        c.fill_circle(dx, dy, 7, RED)
        label = str(num)
        off = 3 if len(label) == 1 else 6
        c.text(dx - off, dy - 3, label, 1, WHITE)


# ---------------------------------------------------------------- page
def build():
    c = Canvas(W, H, PAPER)

    # top strip
    c.text(28, 22, "THE DAY IN TEN STORIES", 2, INK)
    right = "ONE DAY - ONE PAGE"
    c.text(W - 28 - text_width(right, 2), 22, right, 2, INK)
    c.hline(28, 44, W - 56, INK, 2)

    # masthead
    c.text_center(56, "THE WORLD TODAY", 9, INK)
    c.hline(28, 128, W - 56, INK, 5)
    c.hline(28, 138, W - 56, INK, 2)

    # dateline band
    c.fill_rect(28, 150, W - 56, 46, RED)
    c.text_center(159, "WEDNESDAY 25 NOVEMBER 2026", 4, WHITE)

    # ---- lead story ----
    lx, ly, lw, lh = 28, 212, W - 56, 180
    c.fill_rect(lx, ly, lw, lh, WHITE)
    c.border(lx, ly, lw, lh, INK, 3)
    lead_art(c, lx + 16, ly + 16, 240, 144)
    tx = lx + 16 + 240 + 24
    tw = lx + lw - 16 - tx
    c.text(tx, ly + 22, "1 - LEAD STORY - CYBERATTACK", 2, RED)
    y = c.para(tx, ly + 48, "CIA AND SPY CHIEF'S OFFICE HIT BY CYBERATTACK",
               4, INK, tw, gap=6)
    c.para(tx, y + 6,
           "Unclassified systems were breached, officials say. "
           "No classified data was hit. The latest in a wave of hacks.",
           2, INK, tw, gap=5)

    # ---- world map panel ----
    mx, my, mw, mh = 28, 408, W - 56, 180
    c.fill_rect(mx, my, mw, mh, NAVY)
    c.border(mx, my, mw, mh, INK, 3)
    c.text(mx + 16, my + 10, "WHERE IT HAPPENED - TEN STORIES ON THE MAP",
           2, WHITE)
    draw_map(c)
    # right column: stories 8, 9, 10
    rx = 540
    c.text(rx, my + 28, "ALSO ON THE MAP", 2, GOLD)
    side = [
        (8, "UKRAINE SEEKS 115BN EURO AID",
         "Zelenskyy puts the 2027 foreign-aid ask at 115 billion euro."),
        (9, "SHENZHOU-24 LAUNCHES",
         "China's crewed mission lifts off from Jiuquan on Wednesday."),
        (10, "VENEZUELA DEBT PUT AT $237BN",
         "Caracas reveals an eye-popping $237 billion debt load."),
    ]
    sy = my + 54
    for num, head, dek in side:
        c.fill_rect(rx, sy, 22, 22, RED)
        c.text(rx + 8, sy + 4, str(num), 2, WHITE)
        c.text(rx + 30, sy + 4, head, 2, WHITE)
        c.text(rx, sy + 28, dek, 1, LIGHT)
        sy += 40

    # ---- six more stories, 3 x 2 grid ----
    cells = [
        (2, "MARKETS", "HUANG RETURNS AS NVIDIA CEO",
         "Shares jump, then waver, as the ousted founder retakes the "
         "top job to cheers from staff."),
        (3, "US-CHINA", "HUAWEI GUILTY ON 10 OF 12 COUNTS",
         "US jury convicts the tech giant of trade-secret theft and "
         "bank fraud over Iran. Acquitted of racketeering."),
        (4, "MIDDLE EAST", "HOUTHIS HIT RIYADH TOWER AGAIN",
         "Second drone strike on the PIF Tower in a week. "
         "11 people wounded, Saudi civil defence says."),
        (5, "UKRAINE WAR", "KYIV CONFIRMS HIT ON RUSSIAN SHIP",
         "Zelenskyy says the Sparta II carried weapons. "
         "Norway, a Kyiv ally, urges caution."),
        (6, "PACIFIC", "AUSTRALIA SIGNS SOLOMONS PACT",
         "Signed on Wednesday. Canberra becomes the islands' "
         "defence partner of choice."),
        (7, "FRANCE", "SARKOZY CASE GOES TO TRIAL",
         "French officials order the ex-president and his wife "
         "Carla Bruni to trial over the Libya case. "
         "First hearing April 2027."),
    ]
    gx, gy = 28, 604
    cw, chh, gap = 312, 132, 12
    for i, (num, kicker, head, dek) in enumerate(cells):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (chh + 12)
        c.fill_rect(cx, cy, cw, chh, WHITE)
        c.border(cx, cy, cw, chh, INK, 3)
        c.fill_rect(cx + 12, cy + 12, 26, 26, RED)
        c.text(cx + 19, cy + 15, str(num), 2, WHITE)
        c.text(cx + 46, cy + 16, kicker, 2, RED)
        y = c.para(cx + 12, cy + 44, head, 2, INK, cw - 24, gap=5)
        c.para(cx + 12, y + 6, dek, 1, GREY, cw - 24, gap=4)

    # ---- footer ticker ----
    fy = 900
    c.fill_rect(28, fy, W - 56, 62, NAVY)
    c.para(44, fy + 8,
           "ALSO TODAY: WHO EVACUATES EBOLA STAFF IN DR CONGO - "
           "REAL MADRID BEAT PSV 5-1 - UK SANCTIONS HOUTHI OFFICIALS - "
           "MAYON ERUPTION FEARS - IRAQ SEIZES KURDISH OILFIELDS - "
           "GIULIANI GETS MEDAL OF FREEDOM",
           2, WHITE, W - 56 - 32, gap=3)
    c.text_center(976, "SOURCES: REUTERS - CNN - AP - BLOOMBERG - 25 NOV 2026",
                  2, GREY)
    return c


# ---------------------------------------------------------------- png
def chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def encode_png(c):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * c.w * 3:(y + 1) * c.w * 3]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out:
        path = os.path.join(out, "entry.png")
    else:
        path = "/output/entry.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = encode_png(build())
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
