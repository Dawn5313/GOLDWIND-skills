#!/usr/bin/env python3
"""Check Goldwind template-mimic gates for built-in templates and projects."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_TEMPLATE_ID = "金风通用模板"
REQUIRED_TEMPLATE_FILES = {
    "01_cover.svg",
    "02_toc.svg",
    "02_chapter.svg",
    "03_content.svg",
    "04_ending.svg",
    "design_spec.md",
    "logo.png",
    "toc_wave.png",
    "bottom_wave.png",
}
FORBIDDEN_TEMPLATE_ASSETS = {"image5.png", "cover_wind.jpg"}
FORBIDDEN_PAGE_MARKER_PATTERNS = {
    "legacy bottom-right page-marker top stripe": r'<rect[^>]+x="1204"[^>]+y="620"[^>]+width="76"',
    "legacy bottom-right page-marker middle stripe": r'<rect[^>]+x="1204"[^>]+y="638"[^>]+width="76"',
    "legacy bottom-right page-marker bottom stripe": r'<rect[^>]+x="1204"[^>]+y="656"[^>]+width="76"',
    "legacy bottom-right page-marker number": r'<text[^>]+x="1242"[^>]+y="675"',
}
ENDING_TEXT_ANCHORS = {
    "ending headline text anchor x=186 y=170": r'<text[^>]+x="186"[^>]+y="170"',
    "ending first CN line x=188 y=300": r'<text[^>]+x="188"[^>]+y="300"',
    "ending first EN line x=188 y=342": r'<text[^>]+x="188"[^>]+y="342"',
    "ending second CN line x=188 y=426": r'<text[^>]+x="188"[^>]+y="426"',
    "ending second EN line x=188 y=466": r'<text[^>]+x="188"[^>]+y="466"',
}
TOC_TEXT_ANCHORS = {
    "TOC title x=736 y=184": r'<text[^>]+x="736"[^>]+y="184"[^>]*>目录</text>',
    "TOC row 1 number x=736 y=251": r'<text[^>]+x="736"[^>]+y="251"[^>]*>1\.</text>',
    "TOC row 1 title x=784 y=251": r'<text[^>]+x="784"[^>]+y="251"',
    "TOC row 2 number x=736 y=326": r'<text[^>]+x="736"[^>]+y="326"[^>]*>2\.</text>',
    "TOC row 2 title x=784 y=326": r'<text[^>]+x="784"[^>]+y="326"',
    "TOC row 3 number x=736 y=401": r'<text[^>]+x="736"[^>]+y="401"[^>]*>3\.</text>',
    "TOC row 3 title x=784 y=401": r'<text[^>]+x="784"[^>]+y="401"',
    "TOC row 4 number x=736 y=475": r'<text[^>]+x="736"[^>]+y="475"[^>]*>4\.</text>',
    "TOC row 4 title x=784 y=475": r'<text[^>]+x="784"[^>]+y="475"',
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_template_dir(target: Path, template_id: str) -> Path:
    if target.name == template_id and (target / "01_cover.svg").exists():
        return target
    if (target / "templates" / "01_cover.svg").exists():
        return target / "templates"
    if (target / "templates" / template_id / "01_cover.svg").exists():
        return target / "templates" / template_id
    candidate = skill_dir() / "templates" / "layouts" / template_id
    if candidate.exists():
        return candidate
    return target


def check_template_index(template_id: str, errors: list[str]) -> None:
    index_path = skill_dir() / "templates" / "layouts" / "layouts_index.json"
    if not index_path.exists():
        errors.append(f"missing layouts index: {index_path}")
        return
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"layouts_index.json is invalid JSON: {exc}")
        return
    if template_id not in index:
        errors.append(f"template '{template_id}' is not registered in layouts_index.json")


def contains_exact_anchor(svg: str, pattern: str) -> bool:
    return re.search(pattern, svg) is not None


def check_required_files(template_dir: Path, errors: list[str]) -> None:
    missing = sorted(name for name in REQUIRED_TEMPLATE_FILES if not (template_dir / name).exists())
    if missing:
        errors.append(f"missing template files/assets: {', '.join(missing)}")
    present_forbidden = sorted(name for name in FORBIDDEN_TEMPLATE_ASSETS if (template_dir / name).exists())
    if present_forbidden:
        errors.append(f"forbidden non-template assets present: {', '.join(present_forbidden)}")
    check_png_dimensions(template_dir / "toc_wave.png", 1280, 480, errors)
    check_png_dimensions(template_dir / "bottom_wave.png", 1280, 390, errors)


def check_png_dimensions(path: Path, expected_width: int, expected_height: int, errors: list[str]) -> None:
    if not path.exists():
        return
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append(f"cannot read PNG asset {path.name}: {exc}")
        return
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
        errors.append(f"{path.name}: expected PNG asset")
        return
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (expected_width, expected_height):
        errors.append(
            f"{path.name}: expected {expected_width}x{expected_height}, got {width}x{height}; "
            "wave assets must match SVG boxes to prevent finalize-time shrinking"
        )


def check_shared_anchors(svg_name: str, svg: str, errors: list[str]) -> None:
    anchors = {
        "top-right logo at x=1048 y=28": r'<image[^>]+x="1048"[^>]+y="28"[^>]+logo\.png',
        "left rail x=72/73": r'<line[^>]+x1="7[23]"[^>]+y1="0"[^>]+y2="720"',
        "copyright rail text": r'GOLDWIND SCIENCE &amp; TECHNOLOGY CO\., LTD\.',
        "copyright rail original transform": r'transform="matrix\(0 -1\.33 1\.33 0 40\.71 624\.67\)"',
    }
    for label, pattern in anchors.items():
        if not contains_exact_anchor(svg, pattern):
            errors.append(f"{svg_name}: missing anchor: {label}")
    check_no_legacy_page_marker(svg_name, svg, errors)


def check_wave_anchor(svg_name: str, svg: str, errors: list[str], variant: str) -> None:
    if variant == "toc":
        pattern = r'<image[^>]+x="0"[^>]+y="120"[^>]+width="1280"[^>]+height="480"[^>]+toc_wave\.png'
        label = "full-width TOC dotted wave at x=0 y=120 w=1280 h=480"
    else:
        pattern = r'<image[^>]+x="0"[^>]+y="316"[^>]+width="1280"[^>]+height="390"[^>]+bottom_wave\.png'
        label = "full-width lower dotted wave at x=0 y=316 w=1280 h=390"
    if not contains_exact_anchor(svg, pattern):
        errors.append(f"{svg_name}: missing anchor: {label}")


def check_no_fullpage_raster(svg_name: str, svg: str, errors: list[str]) -> None:
    for image_tag in re.findall(r'<image\b[^>]*>', svg):
        width_match = re.search(r'width="([0-9.]+)"', image_tag)
        height_match = re.search(r'height="([0-9.]+)"', image_tag)
        if not width_match or not height_match:
            continue
        width = float(width_match.group(1))
        height = float(height_match.group(1))
        if width >= 1200 and height >= 650:
            errors.append(f"{svg_name}: structural page appears flattened as a full-page image")


def check_ending_structure(svg_name: str, svg: str, errors: list[str]) -> None:
    if not contains_exact_anchor(svg, r'<rect[^>]+x="73"[^>]+y="170"[^>]+width="3"[^>]+height="76"'):
        errors.append(f"{svg_name}: missing ending accent bar at x=73 y=170 w=3 h=76")
    for label, pattern in ENDING_TEXT_ANCHORS.items():
        if not contains_exact_anchor(svg, pattern):
            errors.append(f"{svg_name}: missing anchor: {label}")
    if len(re.findall(r'<text\b', svg)) < 6:
        errors.append(f"{svg_name}: ending page must use editable text elements, not a flattened image")
    check_no_fullpage_raster(svg_name, svg, errors)


def check_toc_structure(svg_name: str, svg: str, errors: list[str]) -> None:
    for label, pattern in TOC_TEXT_ANCHORS.items():
        if not contains_exact_anchor(svg, pattern):
            errors.append(f"{svg_name}: missing anchor: {label}")
    if "TOC_ITEM_1_DESC" in svg or re.search(r'TOC_ITEM_\d+_DESC', svg):
        errors.append(f"{svg_name}: TOC description placeholders are forbidden in 金风通用模板")
    if len(re.findall(r'<text\b', svg)) > 10:
        errors.append(f"{svg_name}: TOC must keep the historical four-entry agenda structure without description rows")


def check_no_legacy_page_marker(svg_name: str, svg: str, errors: list[str]) -> None:
    for label, pattern in FORBIDDEN_PAGE_MARKER_PATTERNS.items():
        if contains_exact_anchor(svg, pattern):
            errors.append(f"{svg_name}: forbidden non-template element found: {label}")
    if "{{PAGE_NUM}}" in svg:
        errors.append(f"{svg_name}: PAGE_NUM placeholder is forbidden in 金风通用模板")


def check_cover(template_dir: Path, errors: list[str]) -> None:
    svg = read_text(template_dir / "01_cover.svg")
    check_shared_anchors("01_cover.svg", svg, errors)
    for placeholder in ("{{TITLE}}", "{{AUTHOR}}", "{{DATE}}"):
        if placeholder not in svg:
            errors.append(f"01_cover.svg: missing required cover placeholder {placeholder}")
    for forbidden in ("{{SUBTITLE}}", "{{AUTHOR_EN}}", "{{PRESENTER}}"):
        if forbidden in svg:
            errors.append(f"01_cover.svg: forbidden cover placeholder {forbidden}; only title/author/date may vary")
    check_wave_anchor("01_cover.svg", svg, errors, "lower")


def check_ending(template_dir: Path, errors: list[str]) -> None:
    svg = read_text(template_dir / "04_ending.svg")
    check_shared_anchors("04_ending.svg", svg, errors)
    check_wave_anchor("04_ending.svg", svg, errors, "lower")
    check_ending_structure("04_ending.svg", svg, errors)


def check_content_templates(template_dir: Path, errors: list[str]) -> None:
    for name in ("02_toc.svg", "02_chapter.svg", "03_content.svg"):
        path = template_dir / name
        if path.exists():
            svg = read_text(path)
            check_shared_anchors(name, svg, errors)
            if name == "02_toc.svg":
                check_wave_anchor(name, svg, errors, "toc")
                check_toc_structure(name, svg, errors)
    content = read_text(template_dir / "03_content.svg")
    for token in ("{{SECTION_NUM}}", "{{PAGE_TITLE}}", "{{CONTENT_AREA}}"):
        if token not in content:
            errors.append(f"03_content.svg: missing content placeholder {token}")


def check_project_outputs(project_dir: Path, errors: list[str]) -> None:
    output_svgs = sorted((project_dir / "svg_output").glob("*.svg")) if (project_dir / "svg_output").exists() else []
    final_svgs = sorted((project_dir / "svg_final").glob("*.svg")) if (project_dir / "svg_final").exists() else []
    # Prefer svg_output because this gate runs before finalize_svg.py in the
    # normal pipeline; svg_final may still contain stale files from a prior run.
    svgs = output_svgs or final_svgs
    if not svgs:
        return
    for svg_path in svgs:
        check_no_legacy_page_marker(svg_path.name, read_text(svg_path), errors)
    first = read_text(svgs[0])
    last = read_text(svgs[-1])
    if "bottom_wave.png" not in first and "toc_wave.png" not in first and "reference_toc_wave.png" not in first:
        errors.append(f"{svgs[0].name}: first slide must keep Goldwind dotted wave cover structure")
    check_ending_structure(svgs[-1].name, last, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Goldwind template-mimic hard gates.")
    parser.add_argument("path", type=Path, help="Project path or template directory")
    parser.add_argument("--template-id", default=DEFAULT_TEMPLATE_ID)
    parser.add_argument("--tolerance", default="0", help="Reserved for future coordinate tolerance; current anchors are exact")
    args = parser.parse_args()

    errors: list[str] = []
    target = args.path.resolve()
    template_dir = resolve_template_dir(target, args.template_id)

    if not template_dir.exists():
        errors.append(f"template/project path does not exist: {template_dir}")
    else:
        check_template_index(args.template_id, errors)
        check_required_files(template_dir, errors)
        if (template_dir / "01_cover.svg").exists():
            check_cover(template_dir, errors)
        if (template_dir / "04_ending.svg").exists():
            check_ending(template_dir, errors)
        if (template_dir / "03_content.svg").exists():
            check_content_templates(template_dir, errors)
        if target.is_dir() and (target / "svg_output").exists():
            check_project_outputs(target, errors)

    if errors:
        print("Template mimic check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Template mimic check PASSED")
    print(f"- template_id: {args.template_id}")
    print(f"- template_dir: {template_dir}")
    print(f"- tolerance: {args.tolerance}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
