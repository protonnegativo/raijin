"""Generates 5 Raijin banner options: braille art + block name + HUD, rendered to PNG and plain text."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SYM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
CJK = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 16)
CELL_W, CELL_H, PAD = 10, 20, 24
BG = (10, 10, 14)


# ---------- braille ----------
def to_braille(img_1bit):
    """img_1bit: PIL '1' image, white = dot. Returns list of braille strings (2x4 dots per char)."""
    w, h = img_1bit.size
    px = img_1bit.load()
    bits = [(0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (0, 3, 0x40), (1, 3, 0x80)]
    rows = []
    for cy in range(0, h - h % 4, 4):
        row = ""
        for cx in range(0, w - w % 2, 2):
            v = 0
            for dx, dy, b in bits:
                if px[cx + dx, cy + dy]:
                    v |= b
            row += chr(0x2800 + v) if v else " "
        rows.append(row.rstrip())
    width = max(len(r) for r in rows)
    return [r.ljust(width) for r in rows]


def dither(img, cols, contrast=1.8, invert=False, thresh=None):
    g = ImageOps.grayscale(img)
    if invert:
        g = ImageOps.invert(g)
    g = ImageEnhance.Contrast(g).enhance(contrast)
    w = cols * 2
    h = int(g.height * w / g.width) // 4 * 4
    g = g.resize((w, h), Image.LANCZOS)
    if thresh is not None:
        return g.point(lambda p: 255 if p > thresh else 0).convert("1")
    return g.convert("1")  # Floyd-Steinberg


def masked(img, dotfn, cols, smooth=5):
    """Dense fill: a dot wherever dotfn(h, s, v, l) is true (after a median filter), empty elsewhere."""
    from PIL import ImageFilter
    rgb = img.convert("RGB")
    hsv = rgb.convert("HSV").load()
    L = rgb.convert("L").load()
    w, h = rgb.size
    m = Image.new("L", (w, h))
    pm = m.load()
    for y in range(h):
        for x in range(w):
            hh, ss, vv = hsv[x, y]
            pm[x, y] = 255 if dotfn(hh, ss, vv, L[x, y]) else 0
    m = m.filter(ImageFilter.MedianFilter(smooth))
    W = cols * 2
    H = int(h * W / w) // 4 * 4
    return m.resize((W, H), Image.LANCZOS).point(lambda p: 255 if p > 100 else 0).convert("1")


# ---------- block letters (half blocks) ----------
def block_text(text, size=22, font=MONO_B):
    f = ImageFont.truetype(font, size)
    l, t, r, b = f.getbbox(text)
    im = Image.new("L", (r - l + 2, b - t + 2), 0)
    ImageDraw.Draw(im).text((-l + 1, -t + 1), text, font=f, fill=255)
    im = im.point(lambda p: 255 if p > 110 else 0)
    w, h = im.size
    if h % 2:
        im = ImageOps.expand(im, (0, 0, 0, 1))
        h += 1
    px = im.load()
    rows = []
    for y in range(0, h, 2):
        s = ""
        for x in range(w):
            top, bot = px[x, y] > 0, px[x, y + 1] > 0
            s += "█" if top and bot else "▀" if top else "▄" if bot else " "
        rows.append(s.rstrip())
    rows = [r for r in rows if r.strip()]
    width = max(len(r) for r in rows)
    return [r.ljust(width) for r in rows]


# ---------- color helpers ----------
def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Canvas:
    """Lines of (char, color) for rendering."""

    def __init__(self):
        self.lines = []

    def add(self, text, color):
        self.lines.append([(ch, color(i) if callable(color) else color) for i, ch in enumerate(text)])

    def add_segments(self, segs):
        import unicodedata
        line = []
        for text, color in segs:
            for ch in text:
                line.append((ch, color))
                if unicodedata.east_asian_width(ch) in "WF":
                    line.append(("", color))
        self.lines.append(line)

    def plain(self):
        return "\n".join("".join(c for c, _ in l).rstrip() for l in self.lines)

    def png(self, path):
        cols = max(len(l) for l in self.lines)
        img = Image.new("RGB", (cols * CELL_W + 2 * PAD, len(self.lines) * CELL_H + 2 * PAD), BG)
        d = ImageDraw.Draw(img)
        for y, line in enumerate(self.lines):
            for x, (ch, color) in enumerate(line):
                if ch and ch.strip():
                    font = SYM if 0x2800 <= ord(ch) <= 0x28FF or ch in "⚡" else CJK if ord(ch) > 0x2E80 else MONO
                    d.text((PAD + x * CELL_W, PAD + y * CELL_H), ch, font=font, fill=color)
        img.save(path, optimize=True)


def side_by_side(left, right, top=0, gap=3):
    """left/right: lists of segment-lists. Returns combined segment lists."""
    lw = max(sum(len(t) for t, _ in l) for l in left)
    out = []
    for i in range(max(len(left), len(right) + top)):
        segs = list(left[i]) if i < len(left) else []
        used = sum(len(t) for t, _ in segs)
        segs.append((" " * (lw - used), BG))
        j = i - top
        if 0 <= j < len(right):
            segs.append((" " * gap, BG))
            segs += right[j]
        out.append(segs)
    return out


def colored(rows, c1, c2, vertical=True):
    n = len(rows)
    out = []
    for i, r in enumerate(rows):
        if vertical:
            out.append([(r, mix(c1, c2, i / max(1, n - 1)))])
        else:
            w = len(r)
            out.append([(ch, mix(c1, c2, x / max(1, w - 1))) for x, ch in enumerate(r)])
    return out


def framed(art_rows, c1, c2, frame, label):
    w = len(art_rows[0])
    lines = [[("┏━━" + " " * (w - 2) + "━━┓", frame)]]
    mid = len(art_rows) // 2
    for i, row in enumerate(art_rows):
        side = "╋" if i == mid else "┃" if i < 2 or i > len(art_rows) - 3 else " "
        lines.append([(side + " ", frame), (row, mix(c1, c2, i / len(art_rows))), (" " + side, frame)])
    lines.append([("┗━━" + " " * (w - 2) + "━━┛", frame)])
    lines.append([(" " + label, c2)])
    return lines


def hud(rows, title, c_frame, c_text, c_bar, width=50):
    out = [[("╭─ " + title + " " + "─" * (width - len(title) - 3) + "╮", c_frame)]]
    for text, kind in rows:
        color = c_bar if kind == "bar" else c_text
        import unicodedata
        dw = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
        out.append([("│ " + text + " " * (width - 1 - dw) + "│", color)])
    out.append([("╰" + "─" * width + "╯", c_frame)])
    return out


def hud_rows():
    return [
        ("ID ........ RAIJIN // 雷神", "t"),
        ("CLASS ..... thunder god · AI-native · offensive", "t"),
        ("SIGNAL .... " + "█" * 18 + "░░ 90%", "bar"),
        ("NOISE ..... ░░░░░░░░░░░░░░░░░░░░ ~0", "t"),
        ("OUTPUT .... Raijin Schema · JSON", "t"),
        ("BUILD ..... v0.1.0", "t"),
    ]


ACRONYM = "AI-native offensive security tools."
MOTTO = "Signal, not noise."


def save(name, lines):
    c = Canvas()
    for segs in lines:
        c.add_segments(segs)
    c.png(OUT / f"{name}.png")
    (OUT / f"{name}.txt").write_text(c.plain() + "\n")
    print(name, "cols=", max(len(l) for l in c.lines), "rows=", len(c.lines))


# ---------- sources ----------
import sys
sys.path.insert(0, str(HERE))
from dragon import dragon, thunderbird, thunderbird_v, thunderbird_storm, thunderbird_totem

NAME = block_text("RAIJIN", 15)
CYAN, VIOLET, BLUE, WHITE = (80, 220, 255), (170, 90, 255), (60, 140, 255), (235, 240, 255)
GOLD, AMBER, ORANGE, YELLOW = (255, 205, 80), (255, 170, 0), (255, 110, 0), (255, 240, 120)


def mask_art(im, cols):
    return to_braille(dither(im.convert("RGB"), cols, contrast=1.0, thresh=128))

RED = (230, 50, 40)
VA = mask_art(thunderbird_v(), 40)
VB = mask_art(thunderbird_storm(), 44)
VC = mask_art(thunderbird_totem(), 38)

# 3A: wings raised, target-lock HUD, cyan -> violet
left = framed(VA, CYAN, VIOLET, (120, 200, 255), "TGT-LOCK ▸ 0x" + b"RAIJIN".hex())
right = colored(NAME, CYAN, VIOLET, vertical=False) + [[("", BG)]] + hud(hud_rows(), "TARGET", (120, 200, 255), (190, 225, 255), CYAN)
save("3a-thunderbird-hud", side_by_side(left, right, top=2) + [[(ACRONYM, (200, 225, 255))], [(MOTTO, VIOLET)]])

# 3B: storm (bolts from the wingtips), amber -> orange, HUD
left = colored(VB, YELLOW, ORANGE)
right = colored(NAME, YELLOW, ORANGE, vertical=False) + [[("", BG)]] + hud(hud_rows(), "TARGET", AMBER, (255, 215, 150), ORANGE)
save("3b-thunderbird-storm", side_by_side(left, right, top=2) + [[(ACRONYM, (255, 215, 150))], [(MOTTO, ORANGE)]])

# 3C: totem, gold -> red, name underneath
lines = colored(VC, GOLD, RED)
lines += [[("", BG)]] + [[(" " * 2, BG)] + seg for seg in colored(NAME, GOLD, RED, vertical=False)]
lines += [[("  " + ACRONYM + " " + MOTTO, (255, 220, 160))]]
save("3c-thunderbird-totem", lines)
