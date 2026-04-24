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
}
FORBIDDEN_TEMPLATE_ASSETS = {"image5.png", "cover_wind.jpg"}
FORBIDDEN_PAGE_MARKER_PATTERNS = {
    "legacy bottom-right page-marker top stripe": r'<rect[^>]+x="1204"[^>]+y="620"[^>]+width="76"',
    "legacy bottom-right page-marker middle stripe": r'<rect[^>]+x="1204"[^>]+y="638"[^>]+width="76"',
    "legacy bottom-right page-marker bottom stripe": r'<rect[^>]+x="1204"[^>]+y="656"[^>]+width="76"',
    "legacy bottom-right page-marker number": r'<text[^>]+x="1242"[^>]+y="675"',
}
ENDING_FIXED_TEXT = [
    "THANKS",
    "金风科技股份有限公司",
    "GOLDWIND SCIENCE &amp; TECHNOLOGY CO., LTD",
    "北京金风科创风电设备有限公司",
    "BEIJING GOLDWIND SCIENCE &amp; CREATION WINDPOWER EQUIPMENT CO., LTD.",
]


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


def check_shared_anchors(svg_name: str, svg: str, errors: list[str]) -> None:
    anchors = {
        "top-right logo at x=1048 y=28": r'<image[^>]+x="1048"[^>]+y="28"[^>]+logo\.png',
        "left rail x=72/73": r'<line[^>]+x1="7[23]"[^>]+y1="0"[^>]+y2="720"',
        "copyright rail text": r'GOLDWIND SCIENCE &amp; TECHNOLOGY CO\., LTD\.',
    }
    for label, pattern in anchors.items():
        if not contains_exact_anchor(svg, pattern):
            errors.append(f"{svg_name}: missing anchor: {label}")
    check_no_legacy_page_marker(svg_name, svg, errors)


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
    if "toc_wave.png" not in svg:
        errors.append("01_cover.svg: cover must use dotted wave artwork toc_wave.png")


def check_ending(template_dir: Path, errors: list[str]) -> None:
    svg = read_text(template_dir / "04_ending.svg")
    check_shared_anchors("04_ending.svg", svg, errors)
    if "{{" in svg or "}}" in svg:
        errors.append("04_ending.svg: ending page must be fixed text; placeholders are forbidden")
    for text in ENDING_FIXED_TEXT:
        if text not in svg:
            errors.append(f"04_ending.svg: fixed ending text missing or changed: {text}")
    if "toc_wave.png" not in svg:
        errors.append("04_ending.svg: ending must use dotted wave artwork toc_wave.png")


def check_content_templates(template_dir: Path, errors: list[str]) -> None:
    for name in ("02_toc.svg", "02_chapter.svg", "03_content.svg"):
        path = template_dir / name
        if path.exists():
            svg = read_text(path)
            check_shared_anchors(name, svg, errors)
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
    if "toc_wave.png" not in first and "reference_toc_wave.png" not in first:
        errors.append(f"{svgs[0].name}: first slide must keep Goldwind dotted wave cover structure")
    for text in ENDING_FIXED_TEXT:
        if text not in last:
            errors.append(f"{svgs[-1].name}: fixed ending text missing or changed: {text}")


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
