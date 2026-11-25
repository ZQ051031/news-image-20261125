#!/usr/bin/env python3
"""News-image entry: "The World Today" front page for 25 November 2026.

Pure Python standard library only (no Pillow, no network). Renders a
1024x1024 newspaper-style front page summing up the world news of
Wednesday 25 November 2026 and writes it to /output/entry.png.

The five stories were verified against Reuters / CNN / AP / Bloomberg
reporting published on 25 November 2026 (events of 24-25 Nov, in any
time zone):
  1. CIA and the Office of the Director of National Intelligence hit by
     a cyberattack on unclassified systems; no classified data affected
     (CNN, first reported by the New York Times).
  2. US jury convicts Huawei on 10 of 12 counts: trade-secret theft and
     bank fraud over Iran; acquitted of racketeering (Reuters/AP).
  3. Houthis strike Riyadh's tallest tower (PIF Tower) for the second
     time in a week; 11 people wounded (Reuters).
  4. Zelenskyy confirms Ukraine's drone strike on the Russian cargo
     ship Sparta II in the Gulf of Finland; Norway urges caution
     (Reuters/Bloomberg).
  5. Australia and Solomon Islands sign a security pact on Wednesday
     25 November, making Canberra the defence partner of choice
     (Reuters).
Also noted: WHO evacuates Ebola hospital staff in DR Congo after
fighting; Real Madrid beat PSV 5-1; US inflation data due.

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


# ---------------------------------------------------------------- icons
def icon_scales(c, x, y, s):
    """Scales of justice, white on navy, inside a s x s box at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    c.vline(cx, cy - 20, 40, WHITE, 3)
    c.hline(cx - 20, cy - 20, 40, WHITE, 3)
    c.fill_circle(cx, cy - 24, 4, WHITE)
    for sx in (-20, 20):
        c.line(cx + sx, cy - 20, cx + sx - 8, cy - 2, WHITE, 2)
        c.line(cx + sx, cy - 20, cx + sx + 8, cy - 2, WHITE, 2)
        c.fill_poly([(cx + sx - 10, cy - 2), (cx + sx + 10, cy - 2),
                     (cx + sx, cy + 10)], WHITE)


def icon_tower(c, x, y, s):
    """Skyscraper with a strike flash, white/gold on navy."""
    cx = x + s // 2
    c.fill_rect(cx - 11, y + 14, 22, s - 22, WHITE)
    c.fill_rect(cx - 11, y + 8, 22, 6, WHITE)
    for wy in range(y + 20, y + s - 10, 9):
        for wx in (cx - 7, cx + 1):
            c.fill_rect(wx, wy, 5, 5, NAVY)
    c.fill_poly([(x + s - 12, y + 2), (x + s - 2, y + 8),
                 (x + s - 12, y + 14), (x + s - 4, y + 8)], GOLD)
    c.fill_circle(x + s - 8, y + 8, 3, GOLD)


def icon_ship(c, x, y, s):
    """Cargo ship on waves, white/red on navy."""
    cy = y + s // 2 + 4
    c.fill_poly([(x + 6, cy), (x + s - 6, cy), (x + s - 14, cy + 14),
                 (x + 14, cy + 14)], WHITE)
    c.fill_rect(x + s // 2 - 2, cy - 22, 4, 22, WHITE)
    c.fill_poly([(x + s // 2 + 2, cy - 22), (x + s // 2 + 18, cy - 16),
                 (x + s // 2 + 2, cy - 10)], RED)
    for wy in (cy + 20, cy + 26):
        c.line(x + 6, wy, x + s - 6, wy, WHITE, 2)


def icon_pact(c, x, y, s):
    """Shield with a star: a signed pact, white/gold on navy."""
    cx, cy = x + s // 2, y + s // 2
    c.fill_poly([(cx - 18, cy - 20), (cx + 18, cy - 20), (cx + 18, cy + 2),
                 (cx, cy + 22), (cx - 18, cy + 2)], WHITE)
    c.fill_poly([(cx - 16, cy - 18), (cx + 16, cy - 18), (cx + 16, cy + 1),
                 (cx, cy + 19), (cx - 16, cy + 1)], NAVY)
    c.fill_circle(cx, cy - 2, 7, GOLD)
    c.line(cx - 12, cy + 8, cx - 4, cy + 14, GOLD, 3)
    c.line(cx - 4, cy + 14, cx + 13, cy - 4, GOLD, 3)


def lead_art(c, x, y, w, h):
    """Lead illustration: servers, warning triangle and padlock."""
    c.fill_rect(x, y, w, h, NAVY)
    # server stack
    sx, sy = x + 24, y + 26
    for i in range(3):
        c.border(sx, sy + i * 34, 96, 26, WHITE, 2)
        c.fill_circle(sx + 12, sy + i * 34 + 13, 3, GOLD)
        c.fill_rect(sx + 24, sy + i * 34 + 10, 52, 3, WHITE)
        c.fill_rect(sx + 24, sy + i * 34 + 17, 36, 3, WHITE)
    # warning triangle
    tx, ty = x + 150, y + 30
    c.fill_poly([(tx + 55, ty), (tx + 110, ty + 92), (tx, ty + 92)], RED)
    c.fill_rect(tx + 50, ty + 30, 10, 36, WHITE)
    c.fill_rect(tx + 50, ty + 74, 10, 10, WHITE)
    # padlock
    px, py = x + 52, y + 150
    c.ring(px + 30, py + 22, 20, GOLD, 5)
    c.fill_rect(px, py + 20, 60, 48, GOLD)
    c.fill_circle(px + 30, py + 38, 6, NAVY)
    c.fill_rect(px + 27, py + 40, 6, 16, NAVY)
    c.text(x + 24, y + h - 34, "WASHINGTON", 2, WHITE)


# ---------------------------------------------------------------- page
def build():
    c = Canvas(W, H, PAPER)

    # top strip
    c.text(28, 22, "THE DAY IN FIVE STORIES", 2, INK)
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
    lx, ly, lw, lh = 28, 212, W - 56, 296
    c.fill_rect(lx, ly, lw, lh, WHITE)
    c.border(lx, ly, lw, lh, INK, 3)
    lead_art(c, lx + 16, ly + 16, 280, lh - 32)
    tx = lx + 16 + 280 + 24
    tw = lx + lw - 16 - tx
    c.text(tx, ly + 22, "LEAD STORY - CYBERATTACK", 2, RED)
    y = c.para(tx, ly + 50, "CIA AND SPY CHIEF'S OFFICE HIT BY CYBERATTACK",
               4, INK, tw, gap=6)
    y = c.para(tx, y + 12,
               "Unclassified systems were breached, officials say. "
               "No classified data was hit. The latest in a wave of "
               "hacks after the FBI crime database breach.",
               2, INK, tw, gap=5)
    c.hline(tx, ly + lh - 52, tw, LIGHT, 2)
    c.text(tx, ly + lh - 38, "REPORTED BY CNN AND THE NEW YORK TIMES",
           2, GREY)

    # ---- four more stories, 2 x 2 grid ----
    cells = [
        ("2 - US-CHINA - COURT",
         "HUAWEI GUILTY ON 10 OF 12 COUNTS",
         "US jury convicts Huawei of trade-secret theft and bank "
         "fraud over Iran. Acquitted of racketeering.",
         icon_scales),
        ("3 - MIDDLE EAST",
         "HOUTHIS HIT RIYADH'S TALLEST TOWER AGAIN",
         "Drone strike is the second on the PIF Tower in a week. "
         "11 people wounded.",
         icon_tower),
        ("4 - UKRAINE WAR",
         "KYIV CONFIRMS HIT ON RUSSIAN SHIP",
         "Zelenskyy says the Sparta II carried weapons. "
         "Norway urges caution.",
         icon_ship),
        ("5 - PACIFIC",
         "AUSTRALIA SIGNS PACT WITH SOLOMONS",
         "Signed on Wednesday. Canberra becomes the islands' "
         "defence partner of choice.",
         icon_pact),
    ]
    gx, gy = 28, 524
    cw, chh, gap = 474, 176, 20
    for i, (kicker, head, dek, icon) in enumerate(cells):
        cx = gx + (i % 2) * (cw + gap)
        cy = gy + (i // 2) * (chh + 8)
        c.fill_rect(cx, cy, cw, chh, WHITE)
        c.border(cx, cy, cw, chh, INK, 3)
        # icon box, top right
        ix, iy, isz = cx + cw - 76, cy + 14, 60
        c.fill_rect(ix, iy, isz, isz, NAVY)
        icon(c, ix, iy, isz)
        pad = 16
        c.text(cx + pad, cy + 16, kicker, 2, RED)
        y = c.para(cx + pad, cy + 44, head, 3, INK,
                   cw - pad - 92, gap=6)
        c.para(cx + pad, y + 6, dek, 2, INK, cw - 2 * pad, gap=4)

    # ---- footer ticker ----
    fy = 900
    c.fill_rect(28, fy, W - 56, 62, NAVY)
    c.para(44, fy + 10,
           "ALSO TODAY: WHO EVACUATES EBOLA HOSPITAL STAFF IN DR CONGO "
           "AFTER FIGHTING - REAL MADRID BEAT PSV 5-1 - US INFLATION "
           "DATA DUE TODAY",
           2, WHITE, W - 56 - 32, gap=4)
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
