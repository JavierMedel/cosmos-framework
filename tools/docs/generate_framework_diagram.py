# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: OpenMDW-1.1

"""Render the README workflow GIF with Pillow (python tools/docs/generate_framework_diagram.py).

Install Pillow separately; this illustration does not require the training environment.
Use --font-dir to select a directory containing DejaVuSans.ttf and DejaVuSans-Bold.ttf
on systems without Segoe UI. The GIF is fully legible even when animation is disabled.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, SCALE = 1100, 650, 2
GREEN = (118, 185, 0)  # NVIDIA green, #76B900.
WHITE = (241, 244, 237)
MUTED = (167, 177, 160)
BACKGROUND = (7, 10, 7)


def mix(a, b, amount):
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def render(phase, font_dir):
    canvas = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    def box(bounds, fill, outline, radius=16, width=1):
        draw.rounded_rectangle(
            tuple(round(v * SCALE) for v in bounds),
            radius=radius * SCALE,
            fill=fill,
            outline=outline,
            width=width * SCALE,
        )

    def line(points, fill, width=1):
        draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill, width * SCALE)

    def label(text, x, y, size, color=WHITE, bold=False):
        name = (
            ("segoeuib.ttf" if bold else "segoeui.ttf")
            if font_dir is None
            else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
        )
        path = Path("C:/Windows/Fonts" if font_dir is None else font_dir) / name
        font = ImageFont.truetype(str(path), size * SCALE)
        draw.text((x * SCALE, y * SCALE), text, font=font, anchor="mm", fill=color)

    def dot(x, y, radius, color):
        draw.ellipse(
            ((x - radius) * SCALE, (y - radius) * SCALE, (x + radius) * SCALE, (y + radius) * SCALE),
            fill=color,
        )

    box((12, 12, 1088, 638), BACKGROUND, (39, 49, 34), radius=24)
    label("NVIDIA COSMOS", 550, 45, 13, GREEN, bold=True)

    # A small model/checkpoint icon, drawn as vectors to keep every frame crisp.
    box((533, 70, 567, 101), (18, 27, 14), GREEN, radius=7)
    for x in (542, 550, 558):
        line([(x, 79), (x, 92)], GREEN, 2)
    label("Existing pretrained model", 550, 126, 25, bold=True)
    label("Example integrations: Cosmos3 / GR00T / Alpamayo / Qwen / π0.5", 550, 159, 16, MUTED)

    def flow(top, bottom, offset):
        line([(550, top), (550, bottom)], (57, 82, 36), 2)
        line([(545, bottom - 6), (550, bottom), (555, bottom - 6)], GREEN, 2)
        y = top + ((phase + offset) % 1) * (bottom - top - 8)
        dot(550, y, 8, (22, 39, 11))
        dot(550, y, 3, GREEN)

    flow(184, 214, 0)
    box((38, 230, 1062, 469), (11, 18, 10), (45, 66, 32), radius=18)
    label("NVIDIA Cosmos Framework", 550, 257, 26, bold=True)
    label("Optional paths; support varies by model, hardware and backend", 550, 285, 13, MUTED)
    cards = [
        (56, 299, 543, 369, "Supervised fine-tuning", "Learn from task examples"),
        (557, 299, 1044, 369, "Reinforcement learning", "Optimize against rewards"),
        (56, 383, 543, 453, "Distillation", "Transfer knowledge from a teacher"),
        (557, 383, 1044, 453, "Quantization", "Use supported lower-precision formats"),
    ]
    # Each card gently brightens once per cycle; all labels remain visible.
    for index, (left, top, right, bottom, title, subtitle) in enumerate(cards):
        distance = abs(((phase - index / 4 + 0.5) % 1) - 0.5)
        strength = max(0, 1 - distance / 0.22)
        strength = strength * strength * (3 - 2 * strength)
        box(
            (left, top, right, bottom),
            mix((21, 28, 19), (30, 48, 16), strength),
            mix((49, 65, 39), GREEN, strength),
            radius=11,
        )
        line([(left + 17, top + 21), (left + 17, bottom - 21)], mix((63, 92, 37), GREEN, strength), 3)
        label(title, (left + right) / 2, top + 24, 21, bold=True)
        label(subtitle, (left + right) / 2, top + 51, 15, MUTED)

    flow(481, 511, 0.5)
    box((533, 527, 567, 553), (18, 27, 14), GREEN, radius=7)
    dot(544, 540, 2, GREEN)
    dot(556, 540, 2, GREEN)
    line([(550, 521), (550, 527)], GREEN, 2)
    label("Adapted / optimized checkpoint", 550, 579, 25, bold=True)
    label("Evaluate task quality and runtime performance before deployment", 550, 612, 16, MUTED)
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "images/cosmos-framework.gif")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    first = render(0, args.font_dir)
    palette = first.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames = [palette]
    for frame in range(1, 80):
        frames.append(render(frame / 80, args.font_dir).quantize(palette=palette, dither=Image.Dither.NONE))
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"Created {args.output}: {WIDTH}x{HEIGHT}, 80 frames, 6.4-second loop")


if __name__ == "__main__":
    main()
