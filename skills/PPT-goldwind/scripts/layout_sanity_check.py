#!/usr/bin/env python3
"""Lightweight SVG layout sanity checks for generated PPT pages.

This is intentionally conservative: it catches obvious image/text collisions
that survive syntactic SVG validation but become unreadable in PowerPoint/WPS.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


DECORATIVE_IMAGE_HINTS = ("logo", "toc_wave", "background", "wave")
SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


@dataclass(frozen=True)
class Box:
    kind: str
    label: str
    x: float
    y: float
    w: float
    h: float

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)


def to_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    return float(match.group(0)) if match else default


def image_boxes(root: ET.Element) -> list[Box]:
    boxes: list[Box] = []
    for elem in root.iter():
        if elem.tag != f"{SVG_NS}image":
            continue
        href = elem.attrib.get("href") or elem.attrib.get(XLINK_HREF) or ""
        x = to_float(elem.attrib.get("x"))
        y = to_float(elem.attrib.get("y"))
        w = to_float(elem.attrib.get("width"))
        h = to_float(elem.attrib.get("height"))
        if any(hint in href for hint in DECORATIVE_IMAGE_HINTS):
            continue
        # After finalize_svg.py embeds images as data URIs, filenames disappear.
        # Goldwind cover/TOC/ending decorative waves are large background-like
        # images; skip those so intentional text-on-wave layouts do not fail.
        if (w >= 900 and h >= 250 and y >= 250) or (w >= 600 and h >= 250 and x <= 100):
            continue
        label = "embedded-image" if href.startswith("data:image/") else (href or "image")
        boxes.append(
            Box(
                "image",
                label,
                x,
                y,
                w,
                h,
            )
        )
    return boxes


def text_content(elem: ET.Element) -> str:
    return "".join(elem.itertext()).strip()


def estimate_text_width(text: str, font_size: float) -> float:
    latin = sum(1 for char in text if ord(char) < 128)
    cjk = max(0, len(text) - latin)
    return latin * font_size * 0.55 + cjk * font_size


def text_boxes(root: ET.Element) -> list[Box]:
    boxes: list[Box] = []
    for elem in root.iter():
        if elem.tag != f"{SVG_NS}text":
            continue
        text = text_content(elem)
        if not text:
            continue
        font_size = to_float(elem.attrib.get("font-size"), 16.0)
        x = to_float(elem.attrib.get("x"))
        y = to_float(elem.attrib.get("y"))
        width = estimate_text_width(text, font_size)
        height = max(font_size * 1.2, font_size)
        anchor = elem.attrib.get("text-anchor")
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        boxes.append(Box("text", text[:48], x, y - font_size, width, height))
    return boxes


def intersection(a: Box, b: Box) -> float:
    left = max(a.x, b.x)
    top = max(a.y, b.y)
    right = min(a.x + a.w, b.x + b.w)
    bottom = min(a.y + a.h, b.y + b.h)
    return max(0.0, right - left) * max(0.0, bottom - top)


def check_svg(svg_path: Path, min_overlap_ratio: float) -> list[str]:
    try:
        root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        return [f"{svg_path.name}: invalid SVG XML: {exc}"]

    errors: list[str] = []
    images = image_boxes(root)
    texts = text_boxes(root)
    for image in images:
        for text in texts:
            overlap = intersection(image, text)
            if overlap <= 0 or text.area <= 0:
                continue
            ratio = overlap / max(1.0, min(image.area, text.area))
            if ratio >= min_overlap_ratio and overlap >= 160:
                errors.append(
                    f"{svg_path.name}: image '{image.label}' overlaps text '{text.label}' "
                    f"(overlap={math.ceil(overlap)}px^2, ratio={ratio:.2f})"
                )
    return errors


def find_svgs(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".svg":
        return [path]
    if (path / "svg_output").exists():
        return sorted((path / "svg_output").glob("*.svg"))
    return sorted(path.glob("*.svg"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated SVGs for obvious layout collisions.")
    parser.add_argument("path", type=Path, help="Project directory, SVG directory, or SVG file")
    parser.add_argument("--min-overlap-ratio", type=float, default=0.18)
    args = parser.parse_args()

    svgs = find_svgs(args.path.resolve())
    if not svgs:
        print(f"Layout sanity check FAILED: no SVG files found at {args.path}")
        return 1

    errors: list[str] = []
    for svg in svgs:
        errors.extend(check_svg(svg, args.min_overlap_ratio))

    if errors:
        print("Layout sanity check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Layout sanity check PASSED")
    print(f"- files checked: {len(svgs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
