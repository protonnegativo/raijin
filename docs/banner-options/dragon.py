"""Original lightning dragon, drawn procedurally (no third-party artwork)."""
import math
import random

from PIL import Image, ImageDraw


def bolt(d, x0, y0, x1, y1, width, rnd, depth=0, jag=12):
    """A jagged lightning segment from (x0,y0) to (x1,y1), with occasional branches."""
    pts = [(x0, y0)]
    n = max(3, int(math.hypot(x1 - x0, y1 - y0) / 14))
    for i in range(1, n):
        t = i / n
        x = x0 + (x1 - x0) * t + rnd.uniform(-jag, jag)
        y = y0 + (y1 - y0) * t + rnd.uniform(-jag, jag)
        pts.append((x, y))
        if depth < 1 and rnd.random() < 0.18:
            a = math.atan2(y1 - y0, x1 - x0) + rnd.choice([-1, 1]) * rnd.uniform(0.6, 1.1)
            L = rnd.uniform(25, 55)
            bolt(d, x, y, x + L * math.cos(a), y + L * math.sin(a), max(1, width - 2), rnd, depth + 1, jag * 0.6)
    pts.append((x1, y1))
    d.line(pts, fill=255, width=width, joint="curve")


def dragon(w=560, h=340, seed=7):
    rnd = random.Random(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)

    # serpentine body from the head (left) to the tail (right)
    path = []
    for i in range(240):
        t = i / 239
        x = 215 + 300 * t
        y = 170 + 62 * math.sin(2 * math.pi * (1.25 * t) + 0.4) * (0.55 + 0.45 * t)
        path.append((x, y, t))
    for x, y, t in path:
        r = 27 * (1 - t) ** 0.7 + 4
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)

    # electric cracks across the body (scales made of lightning)
    for k in range(18):
        x, y, t = path[int(k * 239 / 18)]
        r = 27 * (1 - t) ** 0.7 + 4
        if r < 8:
            continue
        d.line([(x - r * 0.7, y - r * 0.6), (x + rnd.uniform(-3, 3), y), (x - r * 0.4, y + r * 0.7)], fill=0, width=4)

    # spines along the back
    for k in range(4, 40, 2):
        x, y, t = path[int(k * 239 / 42)]
        r = 27 * (1 - t) ** 0.7 + 4
        nx, ny = path[min(239, int(k * 239 / 42) + 2)][:2]
        a = math.atan2(ny - y, nx - x) - math.pi / 2
        L = r * 1.0 + 12
        d.polygon([(x + r * 0.6 * math.cos(a + 0.5), y + r * 0.6 * math.sin(a + 0.5)),
                   (x + (r + L) * math.cos(a), y + (r + L) * math.sin(a)),
                   (x + r * 0.6 * math.cos(a - 0.5), y + r * 0.6 * math.sin(a - 0.5))], fill=255)

    # head: open jaws facing left
    hx, hy = path[0][0], path[0][1]
    S = 1.45
    P = lambda dx, dy: (hx + dx * S, hy + dy * S)
    d.polygon([P(+8, -26), P(-30, -22), P(-62, -12), P(-58, -4), P(-24, -6), P(+10, +2)], fill=255)  # upper jaw
    d.polygon([P(+8, +6), P(-22, +10), P(-50, +22), P(-46, +28), P(-14, +24), P(+12, +20)], fill=255)  # lower jaw
    for k in range(5):  # teeth
        tx = -52 + k * 9
        d.polygon([P(tx, -6), P(tx + 4, 1), P(tx + 7, -6)], fill=255)
    d.ellipse((*P(-22, -21), *P(-13, -13)), fill=0)  # eye
    d.polygon([P(-4, -24), P(+30, -58), P(+40, -54), P(+8, -20)], fill=255)  # horn
    d.polygon([P(+2, -18), P(+46, -36), P(+50, -30), P(+8, -12)], fill=255)  # second horn

    # whiskers and breath: lightning
    bolt(d, hx - 85, hy - 14, hx - 150, hy - 50, 5, rnd)
    bolt(d, hx - 70, hy + 34, hx - 140, hy + 75, 5, rnd)
    bolt(d, hx - 88, hy + 8, hx - 135, hy + 10, 6, rnd, jag=6)

    # claws: small bolts under the body
    for k in (60, 120):
        x, y, t = path[k]
        bolt(d, x, y + 18, x - 18, y + 58, 5, rnd, depth=1, jag=7)

    # bolts flying off the tail and around the body
    tx, ty = path[-1][0], path[-1][1]
    bolt(d, tx, ty, tx + 20, ty - 70, 5, rnd)
    bolt(d, tx - 40, ty - 10, tx - 10, ty + 80, 4, rnd)
    return im.crop(im.getbbox())


def thunderbird(w=360, h=300, seed=3):
    """Symmetric thunderbird: wings with lightning feather edges, bolt tail."""
    rnd = random.Random(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    cx = w // 2
    for side in (-1, 1):
        pts = [(cx, 105)]
        # upper wing edge rising to the tip
        pts += [(cx + side * 40, 80), (cx + side * 95, 50), (cx + side * 150, 30), (cx + side * 172, 40)]
        # jagged feather edge coming back (lightning teeth)
        for k in range(7):
            x = cx + side * (165 - k * 21)
            pts += [(x, 70 + k * 12), (x - side * 10, 95 + k * 10)]
        pts += [(cx + side * 22, 175), (cx, 165)]
        d.polygon(pts, fill=255)
    d.ellipse((cx - 24, 95, cx + 24, 185), fill=255)  # body
    d.ellipse((cx - 17, 52, cx + 17, 90), fill=255)  # head
    d.polygon([(cx - 6, 84), (cx, 104), (cx + 6, 84)], fill=255)  # beak
    d.ellipse((cx - 9, 64, cx - 3, 70), fill=0)
    d.ellipse((cx + 3, 64, cx + 9, 70), fill=0)
    d.polygon([(cx - 14, 56), (cx - 30, 22), (cx - 6, 50)], fill=255)  # crest
    d.polygon([(cx + 14, 56), (cx + 30, 22), (cx + 6, 50)], fill=255)
    # tail: three bolts
    bolt(d, cx, 180, cx - 40, 285, 6, rnd, depth=1, jag=10)
    bolt(d, cx, 180, cx, 295, 7, rnd, depth=1, jag=10)
    bolt(d, cx, 180, cx + 40, 285, 6, rnd, depth=1, jag=10)
    # lightning in the talons
    bolt(d, cx - 18, 175, cx - 85, 230, 3, rnd)
    bolt(d, cx + 18, 175, cx + 85, 230, 3, rnd)
    return im


if __name__ == "__main__":
    import pathlib
    here = pathlib.Path(__file__).parent
    dragon().save(here / "dragon_mask.png")
    thunderbird().save(here / "bird_mask.png")


def thunderbird_v(w=440, h=340, seed=11):
    """Wings raised in a V: broad wings with a lightning-tooth trailing edge, bolts in the talons."""
    rnd = random.Random(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    cx = w // 2
    for side in (-1, 1):
        tip = (cx + side * 205, 10)
        pts = [(cx + side * 8, 120), (cx + side * 70, 70), tip]
        # trailing edge: big lightning teeth from the tip back to the body
        n = 7
        for k in range(1, n + 1):
            t = k / n
            x = tip[0] + (cx + side * 20 - tip[0]) * t
            y = tip[1] + (175 - tip[1]) * t
            pts += [(x + side * 6, y + 34), (x - side * 14, y + 6)]
        pts += [(cx + side * 20, 190), (cx + side * 4, 180)]
        d.polygon(pts, fill=255)
        # one dark feather line per wing so it reads as a wing, not a blob
        d.line([(cx + side * 40, 120), (cx + side * 160, 40)], fill=0, width=4)
    d.ellipse((cx - 28, 110, cx + 28, 225), fill=255)  # body
    d.ellipse((cx - 20, 66, cx + 20, 112), fill=255)  # head
    d.polygon([(cx - 9, 102), (cx, 132), (cx + 9, 102)], fill=255)  # beak
    d.ellipse((cx - 11, 80, cx - 3, 88), fill=0)
    d.ellipse((cx + 3, 80, cx + 11, 88), fill=0)
    for s_ in (-1, 1):
        d.polygon([(cx + s_ * 12, 72), (cx + s_ * 34, 26), (cx + s_ * 4, 66)], fill=255)
    for dx in (-32, 0, 32):
        d.polygon([(cx - 12, 215), (cx + dx - 16, 285), (cx + dx, 270), (cx + dx + 16, 285), (cx + 12, 215)], fill=255)
    for s_ in (-1, 1):
        bolt(d, cx + s_ * 18, 222, cx + s_ * 130, 335, 6, rnd, jag=12)
    return im.crop(im.getbbox())


def thunderbird_storm(w=460, h=340, seed=3):
    """The original thunderbird with bolts striking out of the wingtips."""
    rnd = random.Random(seed)
    base = thunderbird(w=360, h=300, seed=seed)
    im = Image.new("L", (w, h), 0)
    im.paste(base, ((w - 360) // 2, 20))
    d = ImageDraw.Draw(im)
    cx = w // 2
    for side in (-1, 1):
        tipx = cx + side * 172
        bolt(d, tipx, 60, tipx + side * 40, 0, 4, rnd, jag=8)
        bolt(d, tipx, 70, tipx + side * 55, 170, 4, rnd, jag=10)
        bolt(d, cx + side * 120, 150, cx + side * 150, 260, 3, rnd, jag=8)
    return im.crop(im.getbbox())


def thunderbird_totem(w=420, h=320):
    """Geometric Northwest-coast style: symmetric blocks, eyes on the wings."""
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    cx = w // 2
    for s in (-1, 1):
        # wing as stacked blocks stepping outwards
        for k in range(5):
            x0 = cx + s * (30 + k * 34)
            y0 = 100 + k * 10
            d.rectangle(sorted([x0, x0 + s * 32])[:1] + [y0] + sorted([x0, x0 + s * 32])[1:] + [y0 + 90 - k * 12], fill=255)
            d.rectangle(sorted([x0 + s * 6, x0 + s * 26])[:1] + [y0 + 8] + sorted([x0 + s * 6, x0 + s * 26])[1:] + [y0 + 20], fill=0)
        # wing eye (ovoid)
        ex = cx + s * 95
        d.ellipse((ex - 26, 112, ex + 26, 150), fill=0)
        d.ellipse((ex - 18, 118, ex + 18, 144), fill=255)
        d.ellipse((ex - 8, 124, ex + 8, 138), fill=0)
        # feather tips at the bottom of the wing
        for k in range(5):
            x = cx + s * (40 + k * 34)
            d.polygon([(x, 190 - k * 2), (x + s * 16, 230 - k * 6), (x + s * 30, 190 - k * 2)], fill=255)
    # head with curved beak and crest
    d.rectangle((cx - 28, 40, cx + 28, 110), fill=255)
    d.polygon([(cx - 28, 40), (cx, 0), (cx + 28, 40)], fill=255)
    d.ellipse((cx - 20, 55, cx - 6, 69), fill=0)
    d.ellipse((cx + 6, 55, cx + 20, 69), fill=0)
    d.polygon([(cx - 10, 80), (cx + 10, 80), (cx + 4, 108), (cx - 4, 108)], fill=0)
    # body and tail
    d.rectangle((cx - 26, 110, cx + 26, 240), fill=255)
    d.rectangle((cx - 14, 130, cx + 14, 150), fill=0)
    d.rectangle((cx - 14, 170, cx + 14, 190), fill=0)
    for dx in (-26, 0, 26):
        d.polygon([(cx + dx - 13, 240), (cx + dx, 300), (cx + dx + 13, 240)], fill=255)
    return im.crop(im.getbbox())
