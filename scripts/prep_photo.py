"""
prep_photo.py

Turns a normal portrait photo into a clean, high-contrast grayscale image
that converts nicely into ASCII art in the next step.

Why this matters: a flatly-lit face converts into a dark unreadable blob.
This script fixes that by:
  1. Cutting the background out (rembg) so only the subject remains.
  2. Applying CLAHE (adaptive local contrast) so the face has real
     highlights/shadows instead of one flat gray tone.
  3. Compositing onto a plain white canvas so the background maps to the
     empty end of the ASCII ramp.

Usage:
    pip install -r requirements.txt --break-system-packages
    python prep_photo.py my_photo.jpg
    -> writes prepped-source.png
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(input_path: str, output_path: str = "prepped-source.png") -> None:
    raw = Image.open(input_path).convert("RGBA")

    # cut the subject out from its background
    cutout = remove(raw)

    # composite the cutout onto solid white
    canvas = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    canvas.alpha_composite(cutout)
    flat_rgb = canvas.convert("RGB")

    # local contrast boost via CLAHE, done in grayscale
    gray = cv2.cvtColor(np.array(flat_rgb), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    Image.fromarray(boosted).save(output_path)
    print(f"prepped image written -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python prep_photo.py <input_photo>")
        sys.exit(1)
    prep(sys.argv[1])
