#!/usr/bin/env python3
"""Post-export PPTX visibility and packaging checks."""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def slide_sort_key(name: str) -> tuple[int, str]:
    match = re.search(r"slide(\d+)\.xml$", name)
    return (int(match.group(1)) if match else 10_000, name)


def relationship_targets(zf: zipfile.ZipFile, slide_name: str) -> dict[str, str]:
    rels_name = slide_name.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
    if rels_name not in zf.namelist():
        return {}
    root = ET.fromstring(zf.read(rels_name))
    targets: dict[str, str] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        if rel_id:
            targets[rel_id] = target
    return targets


def normalize_target(slide_name: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    base = Path(slide_name).parent
    return posixpath.normpath((base / target).as_posix())


def check_pptx(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        slides = sorted(
            (name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml")),
            key=slide_sort_key,
        )
        if not slides:
            return ["no slide XML files found"]

        for idx, slide_name in enumerate(slides, start=1):
            root = ET.fromstring(zf.read(slide_name))
            text_nodes = [node.text or "" for node in root.findall(".//a:t", NS)]
            text_count = sum(1 for text in text_nodes if text.strip())
            image_count = len(root.findall(".//a:blip", NS))
            shape_count = len(root.findall(".//p:sp", NS))
            if text_count == 0 and image_count == 0 and shape_count <= 1:
                errors.append(f"slide {idx}: appears blank or nearly blank")

            rels = relationship_targets(zf, slide_name)
            for blip in root.findall(".//a:blip", NS):
                rel_id = blip.attrib.get(f"{{{NS['r']}}}embed")
                if not rel_id:
                    continue
                target = rels.get(rel_id)
                if not target:
                    errors.append(f"slide {idx}: image relationship {rel_id} is missing")
                    continue
                target_path = normalize_target(slide_name, target)
                if target_path not in names:
                    errors.append(f"slide {idx}: media target missing from package: {target_path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check exported PPTX for blank slides and missing media.")
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()

    pptx = args.pptx.resolve()
    if not pptx.exists():
        print(f"PPTX visibility check FAILED: file not found: {pptx}")
        return 1
    if pptx.suffix.lower() != ".pptx":
        print(f"PPTX visibility check FAILED: expected .pptx, got: {pptx.name}")
        return 1

    try:
        errors = check_pptx(pptx)
    except zipfile.BadZipFile:
        print(f"PPTX visibility check FAILED: not a valid PPTX zip: {pptx}")
        return 1

    if errors:
        print("PPTX visibility check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PPTX visibility check PASSED")
    print(f"- file: {pptx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
