#!/usr/bin/env python3
"""Build a Goldwind-standard PPTX using native PowerPoint layouts.

This path intentionally avoids SVG-to-PPTX for Goldwind decks. It starts from a
real Goldwind PPTX base file so master/layout elements such as logo, side rail,
rotated copyright text, page-number placeholders, and background artwork are
kept as PowerPoint-native objects. Generated content remains editable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.util import Inches, Pt
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit("python-pptx is required. Install with: python3 -m pip install python-pptx") from exc


PRIMARY = RGBColor(0x06, 0x33, 0x60)
PRIMARY_DEEP = RGBColor(0x02, 0x31, 0x62)
BODY = RGBColor(0x51, 0x51, 0x51)
MUTED = RGBColor(0x84, 0x84, 0x84)
TEAL = RGBColor(0x03, 0x4F, 0x75)
GRAY = RGBColor(0xE9, 0xEA, 0xEB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xDD, 0xDD, 0xDD)

SLIDE_W = 13.333333
SLIDE_H = 7.5
TEXT_FONT = "微软雅黑"
LATIN_FONT = "Arial"
COPYRIGHT_TEXT = "GOLDWIND SCIENCE"


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def template_dir() -> Path:
    return skill_dir() / "templates" / "layouts" / "金风通用模板"


def default_base() -> Path:
    return template_dir() / "goldwind_native_base.pptx"


def default_toc_image() -> Path:
    return template_dir() / "toc_wind_left.png"


def inches(value: float):
    return Inches(value)


def clear_slides(prs: Presentation) -> None:
    sld_id_lst = prs.slides._sldIdLst  # noqa: SLF001 - python-pptx has no public delete API.
    for sld_id in list(sld_id_lst):
        r_id = sld_id.rId
        prs.part.drop_rel(r_id)
        sld_id_lst.remove(sld_id)


def get_layout(prs: Presentation, name_fragment: str):
    for layout in prs.slide_layouts:
        if name_fragment in layout.name:
            return layout
    raise SystemExit(f"Cannot find slide layout containing: {name_fragment}")


def find_copyright_element(prs: Presentation):
    for slide in prs.slides:
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False) and COPYRIGHT_TEXT in shape.text.upper() and "©" in shape.text:
                return deepcopy(shape._element)  # noqa: SLF001 - cloning original PPT XML preserves native rendering.
    for layout in prs.slide_layouts:
        for shape in layout.shapes:
            if getattr(shape, "has_text_frame", False) and COPYRIGHT_TEXT in shape.text.upper() and "©" in shape.text:
                return deepcopy(shape._element)  # noqa: SLF001
    return None


def clone_shape_to_slide(slide, element) -> None:
    if element is None:
        add_copyright(slide)
        return
    cloned = deepcopy(element)
    max_id = max((shape.shape_id for shape in slide.shapes), default=1)
    for node in cloned.iter():
        if node.tag.endswith("}cNvPr"):
            node.set("id", str(max_id + 1))
            node.set("name", "Goldwind Side Copyright")
            break
    slide.shapes._spTree.insert_element_before(cloned, "p:extLst")  # noqa: SLF001


def set_text_style(run, size: float, color=BODY, bold: bool = False, font: str = TEXT_FONT) -> None:
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def display_len(text: str) -> float:
    """Approximate visual length for adaptive PPT-safe font sizing."""
    return sum(1.7 if ord(ch) > 127 else 1.0 for ch in str(text))


def adaptive_size(text: str, base: float, minimum: float, steps: tuple[tuple[float, float], ...]) -> float:
    length = display_len(text)
    size = base
    for threshold, decrement in steps:
        if length > threshold:
            size -= decrement
    return max(minimum, size)


def text_box(slide, x, y, w, h, text="", size=18, color=BODY, bold=False, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(inches(x), inches(y), inches(w), inches(h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_text_style(run, size, color, bold)
    return shape


def top_title_placeholder(slide):
    for shape in slide.shapes:
        if not getattr(shape, "is_placeholder", False) or not getattr(shape, "has_text_frame", False):
            continue
        if shape.top <= Inches(1.0) and shape.left <= Inches(1.0):
            return shape
    return None


def remove_top_title_placeholder(slide) -> None:
    shape = top_title_placeholder(slide)
    if shape is not None:
        shape._element.getparent().remove(shape._element)  # noqa: SLF001 - remove unused placeholder prompt.


def set_title_placeholder(slide, text: str) -> None:
    shape = top_title_placeholder(slide)
    if shape is None:
        text_box(slide, 0.763, 0.276, 6.8, 0.50, text, 20, PRIMARY, True)
        return
    shape.left = inches(0.763)
    shape.top = inches(0.276)
    shape.width = inches(6.8)
    shape.height = inches(0.50)
    tf = shape.text_frame
    tf.clear()
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    set_text_style(run, 20, PRIMARY, True)


def rect_text(slide, x, y, w, h, text="", fill=WHITE, line=BORDER, size=16, color=BODY, bold=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x), inches(y), inches(w), inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = inches(0.16)
    tf.margin_right = inches(0.16)
    tf.margin_top = inches(0.10)
    tf.margin_bottom = inches(0.08)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    set_text_style(run, size, color, bold)
    return shape


def normalize_bullet(item) -> tuple[str, str]:
    if isinstance(item, dict):
        heading = str(item.get("heading", "") or item.get("title", "")).strip()
        body = item.get("body", "")
        if isinstance(body, list):
            body = "；".join(str(part).strip() for part in body if str(part).strip())
        return heading, str(body).strip()
    return str(item).strip(), ""


def normalize_items(items: list) -> list[tuple[str, str]]:
    return [normalize_bullet(item) for item in items if normalize_bullet(item)[0]]


def item_meta(item, *keys: str, default: str = "") -> str:
    if not isinstance(item, dict):
        return default
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def density_grid(count: int) -> dict:
    """Return a Goldwind-native dense layout contract for 100-inch projection."""
    if count <= 4:
        return {
            "columns": 2,
            "rows": 2,
            "x": 0.92,
            "y": 2.02,
            "card_w": 5.55,
            "card_h": 1.30,
            "gap_x": 0.47,
            "gap_y": 0.36,
            "heading_size": 14.0,
            "body_size": 11.5,
            "body_min": 9.8,
        }
    if count <= 6:
        return {
            "columns": 3,
            "rows": 2,
            "x": 0.92,
            "y": 1.96,
            "card_w": 3.62,
            "card_h": 1.38,
            "gap_x": 0.34,
            "gap_y": 0.38,
            "heading_size": 12.8,
            "body_size": 10.8,
            "body_min": 9.2,
        }
    if count <= 9:
        return {
            "columns": 3,
            "rows": 3,
            "x": 0.92,
            "y": 1.83,
            "card_w": 3.62,
            "card_h": 1.08,
            "gap_x": 0.34,
            "gap_y": 0.22,
            "heading_size": 11.7,
            "body_size": 9.4,
            "body_min": 8.1,
        }
    if count <= 12:
        return {
            "columns": 4,
            "rows": 3,
            "x": 0.92,
            "y": 1.78,
            "card_w": 2.72,
            "card_h": 1.15,
            "gap_x": 0.25,
            "gap_y": 0.25,
            "heading_size": 10.4,
            "body_size": 8.3,
            "body_min": 7.2,
        }
    if count <= 16:
        return {
            "columns": 4,
            "rows": 4,
            "x": 0.92,
            "y": 1.75,
            "card_w": 2.72,
            "card_h": 0.92,
            "gap_x": 0.25,
            "gap_y": 0.17,
            "heading_size": 9.5,
            "body_size": 7.5,
            "body_min": 6.7,
        }
    return {
        "columns": 3,
        "rows": 6,
        "x": 0.92,
        "y": 1.75,
        "card_w": 3.62,
        "card_h": 0.68,
        "gap_x": 0.34,
        "gap_y": 0.11,
        "heading_size": 8.6,
        "body_size": 6.8,
        "body_min": 6.2,
    }


def add_dense_cards(slide, bullets: list) -> None:
    items = normalize_items(bullets)
    if not items:
        return
    grid = density_grid(len(items))
    capacity = grid["columns"] * grid["rows"]
    for i, (heading, body) in enumerate(items[:capacity]):
        col = i % grid["columns"]
        row = i // grid["columns"]
        x = grid["x"] + col * (grid["card_w"] + grid["gap_x"])
        y = grid["y"] + row * (grid["card_h"] + grid["gap_y"])
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x), inches(y), inches(grid["card_w"]), inches(grid["card_h"]))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x), inches(y), inches(grid["card_w"]), inches(0.10))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL
        bar.line.fill.background()

        heading_size = adaptive_size(heading, grid["heading_size"], grid["heading_size"] - 1.2, ((18, 0.4), (28, 0.5)))
        body_size = adaptive_size(body, grid["body_size"], grid["body_min"], ((36, 0.5), (52, 0.6), (72, 0.8), (96, 0.7)))
        text_box(slide, x + 0.15, y + 0.20, grid["card_w"] - 0.30, 0.24, heading, heading_size, PRIMARY, True)
        if body:
            text_box(slide, x + 0.15, y + 0.46, grid["card_w"] - 0.30, max(0.20, grid["card_h"] - 0.52), body, body_size, BODY, False)


def add_process_flow(slide, bullets: list) -> None:
    items = normalize_items(bullets)[:12]
    if not items:
        return
    lanes = [
        ("输入", [item for item in bullets if item_meta(item, "phase", "stage").startswith("输入")]),
        ("计算", [item for item in bullets if item_meta(item, "phase", "stage").startswith("计算")]),
        ("校核", [item for item in bullets if item_meta(item, "phase", "stage").startswith("校核")]),
        ("输出", [item for item in bullets if item_meta(item, "phase", "stage").startswith("输出")]),
    ]
    if not any(group for _, group in lanes):
        lanes = [
            ("输入", bullets[:3]),
            ("处理", bullets[3:6]),
            ("校核", bullets[6:9]),
            ("输出", bullets[9:12]),
        ]
    x0, y0, w, lane_h, gap = 0.92, 1.76, 11.58, 0.86, 0.20
    for lane_idx, (lane_title, group) in enumerate(lanes):
        y = y0 + lane_idx * (lane_h + gap)
        band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x0), inches(y), inches(w), inches(lane_h))
        band.fill.solid()
        band.fill.fore_color.rgb = RGBColor(0xF6, 0xF7, 0xF8)
        band.line.color.rgb = BORDER
        tag = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x0), inches(y), inches(0.82), inches(lane_h))
        tag.fill.solid()
        tag.fill.fore_color.rgb = PRIMARY
        tag.line.fill.background()
        text_box(slide, x0 + 0.10, y + 0.28, 0.62, 0.18, lane_title, 9.5, WHITE, True, PP_ALIGN.CENTER)
        group_items = normalize_items(group)[:4]
        if not group_items:
            continue
        step_w = (w - 1.25) / 4
        for idx, (heading, body) in enumerate(group_items):
            sx = x0 + 1.02 + idx * step_w
            text_box(slide, sx, y + 0.12, step_w - 0.18, 0.18, heading, 9.6, PRIMARY, True)
            text_box(slide, sx, y + 0.36, step_w - 0.18, 0.32, body, adaptive_size(body, 6.8, 6.0, ((38, 0.3), (56, 0.4))), BODY, False)
            if idx < len(group_items) - 1:
                text_box(slide, sx + step_w - 0.24, y + 0.31, 0.12, 0.16, "→", 12, TEAL, True, PP_ALIGN.CENTER)


def add_timeline(slide, bullets: list) -> None:
    items = normalize_items(bullets)[:16]
    if not items:
        return
    top_items = items[:8]
    bottom_items = items[8:16]
    x0, y0, w = 0.92, 2.00, 11.55
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x0 + 0.18), inches(3.58), inches(w - 0.36), inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = TEAL
    line.line.fill.background()
    for idx, (heading, body) in enumerate(top_items):
        cx = x0 + idx * (w / max(1, len(top_items) - 1))
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, inches(cx), inches(3.47), inches(0.22), inches(0.22))
        dot.fill.solid()
        dot.fill.fore_color.rgb = TEAL if idx % 2 == 0 else PRIMARY
        dot.line.fill.background()
        card_y = y0 if idx % 2 == 0 else 3.88
        text_box(slide, cx - 0.10, 3.18 if idx % 2 == 0 else 3.73, 0.42, 0.18, item_meta(bullets[idx], "period", default=f"W{idx+1}"), 8, PRIMARY, True, PP_ALIGN.CENTER)
        box_x = min(max(0.82, cx - 0.58), SLIDE_W - 1.58)
        text_box(slide, box_x + 0.06, card_y, 1.35, 0.20, heading, 8.8, PRIMARY, True, PP_ALIGN.CENTER)
        text_box(slide, box_x, card_y + 0.24, 1.48, 0.52, body, adaptive_size(body, 6.5, 5.8, ((32, 0.3), (48, 0.4))), BODY, False, PP_ALIGN.CENTER)
    if bottom_items:
        panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(0.92), inches(5.45), inches(11.55), inches(1.02))
        panel.fill.solid()
        panel.fill.fore_color.rgb = RGBColor(0xF8, 0xF9, 0xFA)
        panel.line.color.rgb = BORDER
        cols = 4
        cell_w = 11.25 / cols
        for idx, (heading, body) in enumerate(bottom_items[:4]):
            x = 1.05 + idx * cell_w
            text_box(slide, x, 5.62, cell_w - 0.18, 0.18, heading, 8.8, PRIMARY, True)
            text_box(slide, x, 5.86, cell_w - 0.18, 0.34, body, adaptive_size(body, 6.4, 5.7, ((34, 0.3), (50, 0.4))), BODY, False)


def add_risk_matrix(slide, bullets: list) -> None:
    raw = bullets[:12]
    items = normalize_items(raw)
    if not items:
        return
    x0, y0, w, h = 0.92, 1.78, 11.55, 4.78
    cols = [1.35, 2.35, 2.35, 2.35, 2.35]
    headers = ["等级", "风险项", "触发信号", "应对动作", "关闭证据"]
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x0), inches(y0), inches(w), inches(0.36))
    header.fill.solid()
    header.fill.fore_color.rgb = PRIMARY
    header.line.fill.background()
    cx = x0
    for width, title in zip(cols, headers):
        text_box(slide, cx + 0.06, y0 + 0.09, width - 0.12, 0.14, title, 8.2, WHITE, True, PP_ALIGN.CENTER)
        cx += width
    row_h = (h - 0.36) / len(items)
    for idx, (heading, body) in enumerate(items):
        y = y0 + 0.36 + idx * row_h
        fill = RGBColor(0xFB, 0xFC, 0xFC) if idx % 2 == 0 else WHITE
        row = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x0), inches(y), inches(w), inches(row_h))
        row.fill.solid()
        row.fill.fore_color.rgb = fill
        row.line.color.rgb = BORDER
        risk_level = item_meta(raw[idx], "level", "risk_level", default=("高" if idx < 3 else "中" if idx < 8 else "低"))
        signal = item_meta(raw[idx], "signal", "trigger", default=body.split("；")[0] if body else "")
        action = item_meta(raw[idx], "action", default=body.split("；")[-1] if body else "")
        evidence = item_meta(raw[idx], "evidence", default="日志/截图/纪要留痕")
        values = [risk_level, heading, signal, action, evidence]
        cx = x0
        for width, value in zip(cols, values):
            color = RGBColor(0xC9, 0x4A, 0x3A) if risk_level == "高" and width == cols[0] else BODY
            text_box(slide, cx + 0.07, y + 0.08, width - 0.14, row_h - 0.12, value, adaptive_size(value, 6.6, 5.7, ((32, 0.3), (48, 0.4))), color, width == cols[0], PP_ALIGN.CENTER if width == cols[0] else PP_ALIGN.LEFT)
            cx += width


def add_section_summary(slide, bullets: list) -> None:
    items = normalize_items(bullets)[:10]
    if not items:
        return
    left = items[:4]
    right = items[4:10]
    rect_text(slide, 0.92, 1.82, 4.08, 3.72, left[0][0] if left else "核心结论", fill=PRIMARY, line=PRIMARY, size=18, color=WHITE, bold=True)
    if left:
        text_box(slide, 1.14, 2.50, 3.62, 0.90, left[0][1], adaptive_size(left[0][1], 12.5, 9.5, ((80, 0.8), (120, 0.8))), WHITE, False)
    for idx, (heading, body) in enumerate(left[1:4]):
        y = 3.72 + idx * 0.58
        text_box(slide, 1.14, y, 1.05, 0.18, heading, 8.5, WHITE, True)
        text_box(slide, 2.08, y, 2.62, 0.22, body, 6.8, WHITE, False)
    for idx, (heading, body) in enumerate(right):
        y = 1.86 + idx * 0.73
        bullet = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(5.42), inches(y + 0.09), inches(0.16), inches(0.16))
        bullet.fill.solid()
        bullet.fill.fore_color.rgb = TEAL
        bullet.line.fill.background()
        text_box(slide, 5.75, y, 2.05, 0.18, heading, 9.2, PRIMARY, True)
        text_box(slide, 7.60, y, 4.75, 0.30, body, adaptive_size(body, 7.1, 6.2, ((46, 0.3), (66, 0.4))), BODY, False)


def image_path_from_page(page: dict) -> Path | None:
    raw = page.get("image_path") or page.get("image")
    if isinstance(raw, dict):
        raw = raw.get("path")
    if not raw:
        return None
    path = Path(str(raw)).expanduser()
    if not path.exists():
        raise SystemExit(f"Page image does not exist: {path}")
    return path


def image_box_from_page(page: dict) -> tuple[float, float, float, float]:
    raw = page.get("image")
    if isinstance(raw, dict) and isinstance(raw.get("box"), dict):
        box = raw["box"]
        return (
            float(box.get("x", 0.90)),
            float(box.get("y", 1.92)),
            float(box.get("w", 7.00)),
            float(box.get("h", 3.94)),
        )
    return (0.90, 1.92, 7.00, 3.94)


def image_annotation_items(page: dict, bullets: list) -> list[tuple[str, str]]:
    raw_items = page.get("image_annotations") or page.get("image_labels") or []
    items: list[tuple[str, str]] = []
    for item in raw_items:
        heading, body = normalize_bullet(item)
        if heading:
            items.append((heading, body))
    if items:
        return items[:6]
    return [normalize_bullet(item) for item in bullets if normalize_bullet(item)[0]][:6]


def add_image_annotations(slide, page: dict, bullets: list, box: tuple[float, float, float, float]) -> None:
    items = image_annotation_items(page, bullets)
    if not items:
        return
    x, y, w, h = box
    cols = 3 if len(items) >= 5 else 2
    rows = 2 if cols == 3 else ((len(items) + 1) // 2)
    gap_x = 0.13
    gap_y = 0.11
    card_w = (w - 0.44 - gap_x * (cols - 1)) / cols
    card_h = 0.46 if rows <= 2 else 0.39
    start_x = x + 0.22
    start_y = y + h - 0.24 - rows * card_h - (rows - 1) * gap_y
    for idx, (heading, body) in enumerate(items[: cols * rows]):
        col = idx % cols
        row = idx // cols
        cx = start_x + col * (card_w + gap_x)
        cy = start_y + row * (card_h + gap_y)
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(cx), inches(cy), inches(card_w), inches(card_h))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(cx), inches(cy), inches(0.06), inches(card_h))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL
        bar.line.fill.background()
        heading_size = adaptive_size(heading, 8.8, 7.3, ((12, 0.4), (18, 0.5), (24, 0.5)))
        body_size = adaptive_size(body, 6.9, 5.9, ((24, 0.3), (36, 0.4), (50, 0.4)))
        text_box(slide, cx + 0.11, cy + 0.06, card_w - 0.17, 0.15, heading, heading_size, PRIMARY, True)
        if body:
            text_box(slide, cx + 0.11, cy + 0.23, card_w - 0.17, card_h - 0.25, body, body_size, BODY, False)


def add_image_panel(slide, page: dict, bullets: list) -> bool:
    path = image_path_from_page(page)
    if path is None:
        return False
    x, y, w, h = image_box_from_page(page)
    frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(x), inches(y), inches(w), inches(h))
    frame.fill.solid()
    frame.fill.fore_color.rgb = WHITE
    frame.line.color.rgb = BORDER
    frame.shadow.inherit = False
    slide.shapes.add_picture(str(path), inches(x + 0.06), inches(y + 0.06), width=inches(w - 0.12), height=inches(h - 0.12))
    add_image_annotations(slide, page, bullets, (x + 0.06, y + 0.06, w - 0.12, h - 0.12))
    caption = page.get("image_caption") or ""
    if caption:
        text_box(slide, x, y + h + 0.10, w, 0.24, caption, 8.5, MUTED, False, PP_ALIGN.CENTER)
    return True


def add_side_cards(slide, bullets: list) -> None:
    items = [normalize_bullet(item) for item in bullets if normalize_bullet(item)[0]][:10]
    if not items:
        return
    x = 8.18
    y = 1.82
    w = 4.48
    if len(items) <= 5:
        cols = 1
        rows = len(items)
        card_w = w
        card_h = 0.72 if len(items) >= 5 else 0.86
        gap_x = 0
        gap_y = 0.16
    else:
        cols = 2
        rows = min(5, (len(items) + 1) // 2)
        gap_x = 0.14
        gap_y = 0.13
        card_w = (w - gap_x) / 2
        card_h = 0.82 if len(items) <= 8 else 0.69
    for idx, (heading, body) in enumerate(items):
        col = idx % cols
        row = idx // cols
        cx = x + col * (card_w + gap_x)
        cy = y + row * (card_h + gap_y)
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(cx), inches(cy), inches(card_w), inches(card_h))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(cx), inches(cy), inches(0.08), inches(card_h))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL
        bar.line.fill.background()
        heading_base = 10.8 if cols == 1 else 8.7
        body_base = 8.5 if cols == 1 else 6.8
        heading_size = adaptive_size(heading, heading_base, heading_base - 1.4, ((14, 0.4), (22, 0.5), (30, 0.5)))
        body_size = adaptive_size(body, body_base, body_base - 1.2, ((24, 0.3), (38, 0.4), (54, 0.5)))
        text_box(slide, cx + 0.18, cy + 0.07, card_w - 0.30, 0.18, heading, heading_size, PRIMARY, True)
        if body:
            text_box(slide, cx + 0.18, cy + 0.28, card_w - 0.30, max(0.18, card_h - 0.33), body, body_size, BODY, False)


def add_copyright(slide) -> None:
    # Match the native Goldwind report samples: rotated rectangle, not SVG matrix text.
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(-2.376), inches(3.371), inches(5.512), inches(0.76))
    shape.rotation = 270
    shape.fill.background()
    shape.line.fill.background()
    tf = shape.text_frame
    tf.clear()
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "© GOLDWIND SCIENCE & TECHNOLOGY CO., LTD."
    set_text_style(run, 8, BODY, False, LATIN_FONT)


def add_accent(slide, y=2.67):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inches(0.76), inches(y), inches(0.028), inches(0.787))
    shape.fill.solid()
    shape.fill.fore_color.rgb = PRIMARY
    shape.line.fill.background()


def add_cover(slide, spec: dict) -> None:
    # Side copyright, logo, and wave/background are inherited from the native layout.
    add_accent(slide, 2.67)
    title = spec.get("title") or "金风科技专题汇报"
    subtitle = spec.get("subtitle") or ""
    author = spec.get("author") or "汇报人 - Codex"
    report_date = spec.get("date") or date.today().strftime("%Y-%m-%d")
    text_box(slide, 0.60, 1.55, 12.2, 0.62, title, 33, PRIMARY, True, PP_ALIGN.CENTER)
    if subtitle:
        text_box(slide, 0.60, 2.18, 12.2, 0.48, subtitle, 24, PRIMARY, True, PP_ALIGN.CENTER)
    text_box(slide, 2.15, 4.24, 9.44, 0.39, author, 18, BODY, False, PP_ALIGN.CENTER)
    text_box(slide, 6.17, 4.71, 2.35, 0.38, report_date, 18, BODY, False, PP_ALIGN.CENTER)


def add_toc(slide, items: list[str], toc_image: Path) -> None:
    remove_top_title_placeholder(slide)
    slide.shapes.add_picture(str(toc_image), inches(0), inches(-0.006), width=inches(6.92), height=inches(7.506))
    box = slide.shapes.add_textbox(inches(7.653), inches(0.187), inches(4.899), inches(6.614))
    tf = box.text_frame
    tf.clear()
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = "目录"
    set_text_style(r, 28, BODY, True)
    for idx, title in enumerate(items[:4], start=1):
        p = tf.add_paragraph()
        p.level = 0
        p.space_before = Pt(20)
        p.line_spacing = 2.0
        p.text = f"{idx}.  {title}"
        for run in p.runs:
            set_text_style(run, 20, BODY, True)


def add_content(slide, page: dict, section_num: str) -> None:
    title = page.get("title") or "页面标题"
    lead = page.get("lead") or ""
    bullets = page.get("bullets") or []
    source = page.get("source") or ""
    set_title_placeholder(slide, f"{section_num}「{title}」")
    if lead:
        lead_size = adaptive_size(lead, 14.0, 11.8, ((70, 0.6), (100, 0.8), (130, 0.8)))
        rect_text(slide, 0.763, 1.02, 12.107, 0.66, lead, fill=GRAY, line=GRAY, size=lead_size, color=BODY, bold=True)
    if add_image_panel(slide, page, bullets):
        side_cards = page.get("side_cards") or bullets[6:] or bullets
        add_side_cards(slide, side_cards)
    else:
        layout = str(page.get("layout") or "").strip().lower()
        if layout == "process_flow":
            add_process_flow(slide, bullets)
        elif layout == "timeline":
            add_timeline(slide, bullets)
        elif layout == "risk_matrix":
            add_risk_matrix(slide, bullets)
        elif layout == "section_summary":
            add_section_summary(slide, bullets)
        else:
            add_dense_cards(slide, bullets)
    if source:
        text_box(slide, 0.84, 7.10, 8.0, 0.18, f"Source: {source}", 8.5, RGBColor(0xA6, 0xA9, 0xAC), False)


def add_ending(slide, spec: dict) -> None:
    # Side copyright, logo, and wave/background are inherited from the native layout.
    add_accent(slide, 1.784)
    text_box(slide, 1.94, 0.69, 8.27, 1.58, spec.get("ending_title", "THANKS"), 78, PRIMARY_DEEP, False)
    lines = spec.get(
        "ending_lines",
        [
            "金风科技股份有限公司",
            "GOLDWIND SCIENCE & TECHNOLOGY CO., LTD",
            "北京金风科创风电设备有限公司",
            "BEIJING GOLDWIND SCIENCE & CREATION WINDPOWER EQUIPMENT CO., LTD",
        ],
    )
    y_positions = [2.70, 3.21, 4.01, 4.52]
    sizes = [19, 17, 19, 17]
    for text, y, size in zip(lines[:4], y_positions, sizes):
        text_box(slide, 1.95, y, 10.7, 0.42, text, size, BODY, size == 19)


def load_spec(path: Path | None) -> dict:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "title": "金风科技2025股东回报",
        "subtitle": "年度价值创造观察",
        "author": "汇报人 - Codex",
        "date": "2026-04-24",
        "toc": ["回报框架", "业绩兑现", "增长基础", "治理与ESG"],
        "pages": [
            {
                "title": "股东回报框架",
                "lead": "股东回报不是单点分红，而是经营质量、现金创造、分配纪律和透明沟通的连续闭环。",
                "bullets": [
                    {"heading": "经营质量", "body": "收入、利润、ROE决定长期回报的基本盘。"},
                    {"heading": "现金创造", "body": "经营现金流与货币资金决定分配安全边际。"},
                    {"heading": "增长基础", "body": "订单、全球化和服务容量支撑后续兑现。"},
                    {"heading": "治理沟通", "body": "信息披露和ESG实践影响长期信任。"},
                    {"heading": "资本配置", "body": "分红、回购、投资节奏共同影响股东收益。"},
                    {"heading": "风险边界", "body": "交付、价格和汇率波动需要纳入回报判断。"},
                ],
                "source": "Goldwind 2025 Annual Results Report",
            },
            {
                "title": "2025年度业绩兑现",
                "lead": "2025年收入、归母净利润和ROE同步提升，股东回报的经营底座明显增强。",
                "bullets": [
                    {"heading": "营业收入 730.23亿", "body": "年度规模继续提升。"},
                    {"heading": "归母净利润 27.74亿", "body": "盈利恢复支撑回报能力。"},
                    {"heading": "综合毛利率 14.18%", "body": "业务质量持续修复。"},
                    {"heading": "加权ROE 7.08%", "body": "较2024年继续改善。"},
                    {"heading": "费用纪律", "body": "费用率变化决定利润修复能否沉淀。"},
                    {"heading": "分红能力", "body": "盈利与现金共同约束可持续分配。"},
                ],
                "source": "Goldwind 2025 Annual Results Report",
            },
            {
                "title": "订单与全球化支撑",
                "lead": "订单、销售容量和国际化布局决定利润修复能否转化为跨周期回报能力。",
                "bullets": [
                    {"heading": "对外销售容量 26,626MW", "body": "同比增长65.9%。"},
                    {"heading": "在手订单 53.7GW", "body": "截至2025年底。"},
                    {"heading": "全球累计装机 165GW", "body": "业务基础持续扩张。"},
                    {"heading": "海外订单 9,270.17MW", "body": "国际业务提供增量线索。"},
                    {"heading": "服务收入", "body": "存量机组运维带来更平滑的现金贡献。"},
                    {"heading": "区域组合", "body": "国内外需求分散有助于平滑周期波动。"},
                ],
                "source": "Goldwind 2025 Annual Results Report",
            },
            {
                "title": "现金质量与回报约束",
                "lead": "股东回报不能只看利润，还要看经营现金流、货币资金和已执行分红节奏。",
                "bullets": [
                    {"heading": "经营现金流 35.43亿", "body": "现金流恢复增强分配空间。"},
                    {"heading": "货币资金 103.23亿", "body": "年末资金安全垫。"},
                    {"heading": "已执行分红", "body": "2024年度末期股息每股0.14元。"},
                    {"heading": "后续观察", "body": "结合资本开支和订单交付节奏评估。"},
                    {"heading": "偿债能力", "body": "债务结构影响分红安全边际。"},
                    {"heading": "营运周转", "body": "应收、存货和预付款决定现金回笼速度。"},
                ],
                "source": "Goldwind 2025 Annual Results Report",
            },
            {
                "title": "治理与ESG长期信任",
                "lead": "治理质量和ESG兑现会影响资本市场对长期现金流的稳定性判断。",
                "bullets": [
                    {"heading": "信息披露考核A", "body": "治理透明度保持较高水平。"},
                    {"heading": "绿色电力占比99%", "body": "全球生产及运营活动绿电使用。"},
                    {"heading": "供应链协同", "body": "主要零部件供应商绿电使用比例达100%。"},
                    {"heading": "投资者关系", "body": "持续强化业绩沟通与价值传递。"},
                    {"heading": "评级认可", "body": "外部评级强化长期责任经营背书。"},
                    {"heading": "长期沟通", "body": "定期披露和互动提升资本市场预期稳定性。"},
                ],
                "source": "Goldwind 2025 Annual Results Report",
            },
        ],
    }


def safe_output_name(spec: dict) -> str:
    title = str(spec.get("title") or "金风科技汇报").strip()
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]+', "", title)
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = cleaned[:36] or "金风科技汇报"
    return f"{cleaned}.pptx"


def build(spec: dict, output: Path, base: Path, toc_image: Path) -> Path:
    prs = Presentation(str(base))
    prs.slide_width = inches(SLIDE_W)
    prs.slide_height = inches(SLIDE_H)
    cover_layout = get_layout(prs, "60_")
    content_layout = get_layout(prs, "8_")
    copyright_element = find_copyright_element(prs)
    clear_slides(prs)

    cover = prs.slides.add_slide(cover_layout)
    clone_shape_to_slide(cover, copyright_element)
    add_cover(cover, spec)

    toc = prs.slides.add_slide(content_layout)
    add_toc(toc, spec.get("toc") or [page.get("title", "") for page in spec.get("pages", [])[:4]], toc_image)

    pages = spec.get("pages") or []
    for idx, page in enumerate(pages, start=1):
        slide = prs.slides.add_slide(content_layout)
        add_content(slide, page, f"{idx:02d}")

    ending = prs.slides.add_slide(cover_layout)
    clone_shape_to_slide(ending, copyright_element)
    add_ending(ending, spec)

    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a native editable Goldwind-standard PPTX.")
    parser.add_argument("--spec", type=Path, help="JSON deck spec. If omitted, builds a bundled demo deck.")
    parser.add_argument("-o", "--output", type=Path, help="Output PPTX path")
    parser.add_argument("--base", type=Path, default=default_base())
    parser.add_argument("--toc-image", type=Path, default=default_toc_image())
    args = parser.parse_args()

    spec = load_spec(args.spec)
    output = args.output or Path.cwd() / safe_output_name(spec)
    build(spec, output, args.base, args.toc_image)
    print(f"Goldwind native deck built: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
