"""Render favicon.ico from the SkillForge mark.

The mark is a 270-degree readiness gauge arc with a swept needle and a forge
spark at the ready end, in the ember accent. This redraws that geometry with
Pillow at high resolution, then downsamples to 16, 32, and 48 px so the icon
stays crisp in a browser tab. Run with Pillow available, for example:

    uvx --with pillow python frontend/scripts/make_favicon.py

It writes frontend/public/favicon.ico and a 64 px PNG preview next to it.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

EMBER = (255, 122, 24, 255)
AMBER = (255, 194, 75, 255)

# Geometry in a 32-unit canvas, matching frontend/public/favicon.svg.
UNIT = 32
CENTER = (16.0, 16.0)
ARC_R = 11.5
ARC_W = 3.4
NEEDLE_TIP = (22.3, 10.3)
NEEDLE_W = 2.6
HUB_R = 2.2
SPARK = (23.0, 10.0)
SPARK_OUT = 3.8
SPARK_IN = 1.1


def _round_line(draw: ImageDraw.ImageDraw, p0, p1, width, fill, s) -> None:
    draw.line([(p0[0] * s, p0[1] * s), (p1[0] * s, p1[1] * s)], fill=fill, width=int(width * s))
    rr = (width * s) / 2
    for px, py in (p0, p1):
        draw.ellipse([px * s - rr, py * s - rr, px * s + rr, py * s + rr], fill=fill)


def _star(cx, cy, outer, inner, s):
    pts = []
    for i in range(8):
        ang = math.radians(i * 45) - math.pi / 2
        rad = outer if i % 2 == 0 else inner
        pts.append(((cx + rad * math.cos(ang)) * s, (cy + rad * math.sin(ang)) * s))
    return pts


def render(scale: int) -> Image.Image:
    s = scale
    img = Image.new("RGBA", (UNIT * s, UNIT * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gauge arc: 270 degrees, open at the bottom, round caps.
    cx, cy = CENTER
    box = [(cx - ARC_R) * s, (cy - ARC_R) * s, (cx + ARC_R) * s, (cy + ARC_R) * s]
    # SVG opens the arc between the two lower 45-degree points; in Pillow's
    # clockwise-from-3-o'clock degrees that is the sweep from 135 to 45 (the long way).
    draw.arc(box, start=135, end=45, fill=EMBER, width=int(ARC_W * s))
    # Round caps at the arc ends.
    rr = (ARC_W * s) / 2
    for ang in (135, 45):
        ex = cx + ARC_R * math.cos(math.radians(ang))
        ey = cy + ARC_R * math.sin(math.radians(ang))
        draw.ellipse([ex * s - rr, ey * s - rr, ex * s + rr, ey * s + rr], fill=EMBER)

    _round_line(draw, CENTER, NEEDLE_TIP, NEEDLE_W, EMBER, s)
    draw.ellipse(
        [(cx - HUB_R) * s, (cy - HUB_R) * s, (cx + HUB_R) * s, (cy + HUB_R) * s], fill=EMBER
    )
    draw.polygon(_star(SPARK[0], SPARK[1], SPARK_OUT, SPARK_IN, s), fill=AMBER)
    return img


def main() -> None:
    public = Path(__file__).resolve().parent.parent / "public"
    public.mkdir(exist_ok=True)

    master = render(scale=16)  # 512 px master for clean downsampling
    sizes = [16, 32, 48]
    frames = [master.resize((n, n), Image.LANCZOS) for n in sizes]
    ico_path = public / "favicon.ico"
    frames[0].save(ico_path, format="ICO", sizes=[(n, n) for n in sizes], append_images=frames[1:])
    print(f"wrote {ico_path} with sizes {sizes}")


if __name__ == "__main__":
    main()
