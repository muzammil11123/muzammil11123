"""Prepare a photo for the ASCII portrait: python scripts/prep_photo.py photo.jpg

Removes the background, boosts local contrast, composites onto white, and writes
source-prepped.png. Run locally, once per photo.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/prep_photo.py <photo>")
    cutout = remove(Image.open(sys.argv[1]).convert("RGB")).convert("RGBA")
    pixels = np.asarray(cutout)
    gray = cv2.cvtColor(pixels[:, :, :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
    alpha = pixels[:, :, 3].astype(np.float32) / 255
    result = gray * alpha + 255 * (1 - alpha)
    Image.fromarray(result.astype(np.uint8)).save(ROOT / "source-prepped.png")
    print("Wrote source-prepped.png")


if __name__ == "__main__":
    main()
