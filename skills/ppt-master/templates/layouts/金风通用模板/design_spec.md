# 金风通用模板 - Design Specification

## I. Template Overview

| Item | Value |
| --- | --- |
| Template ID | 金风通用模板 |
| Display Name | 金风通用模板 |
| Category | brand |
| Source Reference | 2024年工作策划——风资源创新研究部0322.pptx; 2026季度工作总结汇报样本 |
| Applicable Scenarios | 金风科技内部汇报、年度策划、工作计划、技术部门工作策划、培训汇报 |
| Design Tone | 克制、工程感、白底、深蓝标题、浅灰内容带、表格式信息组织 |

This template is reconstructed from the Goldwind 2024 work-planning deck and validated against multiple 2026 quarterly Goldwind report samples. It is a reusable PPT Master layout package, not a full slide conversion. The default production path is native editable PowerPoint (`goldwind_native_base.pptx` + `goldwind_native_deck.py`) so master/layout elements remain reliable in WPS and PowerPoint.

The reusable visual authority is limited to the true template elements: top-right Goldwind logo, left copyright rail, native cover/ending background, TOC left wind-turbine image, full-width dotted wave artwork where used by the layout, header/title structure, gray content bands, and teal table/tag blocks.

The dotted-wave assets are dimension-locked so the SVG finalizer cannot shrink them by aspect-ratio fitting: `bottom_wave.png` is 1280x390 for cover/ending SVG fallback pages. The native PPTX base owns the production background.

Explicit exclusions: `image5.png` from the imported PPTX is a content-specific simulation image and must not be treated as a reusable template asset. The imported wind/engineering figure is also not used by the cover or ending templates. The bottom-right three-stripe page-number block at `x=1204, y=620` is a misidentified non-template element and is forbidden.

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280x720 |
| viewBox | `0 0 1280 720` |
| Left Rail | x=72/73 vertical divider |
| Header Baseline | y=84 divider line |
| Content Safe Area | x=76, y=112, w=1140, h=508 |

## III. Color Scheme

| Role | HEX | Usage |
| --- | --- | --- |
| Background | `#FFFFFF` | Page background |
| Primary | `#063360` | Titles, chapter number, structural emphasis |
| Primary deep | `#023162` | Cover/ending accent bar |
| Body text | `#515151` | Main copy and TOC text |
| Secondary text | `#404040` | Cover metadata and ending subtitles |
| Tertiary text | `#A6A9AC` | Header line and footer notes |
| Border | `#DDDDDD` | Left rail and table borders |
| Gray band | `#E9EAEB` | Historical content summary band |
| Light gray | `#F1F1F1` | Auxiliary fills |
| Mid gray | `#848484` | Secondary labels |
| Tag teal | `#034F75` | Table headers and image tags |

## IV. Typography System

| Role | Font Stack | Size Guidance |
| --- | --- | --- |
| Cover title | `Arial, Microsoft YaHei, sans-serif` | 54-72px |
| Page title | `Arial, Microsoft YaHei, sans-serif` | 24-34px |
| Body | `Microsoft YaHei, Arial, sans-serif` | 16-20px |
| Annotation | `Arial, Microsoft YaHei, sans-serif` | 10-13px |

The original deck uses Arial/Helvetica/PingFang/微软雅黑-derived rendering. This template standardizes the editable SVG/PPT path to PPT-safe font stacks while preserving the original hierarchy.

## V. Page Structure

- Shared master: white background, left vertical copyright rail, top-right logo. Do not add the bottom-right three-block page-number marker.
- Content header: line from x=0 to x=328 at y=84, section number at x=84 y=66, quoted page/chapter title at x=138 y=66.
- Cover/ending: large title block aligned near x=344 for cover and x=186 for ending, vertical blue accent bar near x=73, native background/wave layer in the lower half.
- TOC: left full-height wind-turbine image plus right agenda list. Use `toc_wind_left.png` at `x=0, y=-0.006in, w=6.92in, h=7.506in`; right text box at `x=7.653in, y=0.187in, w=4.899in, h=6.614in`. Keep TOC to four primary entries only; do not add description rows or secondary explanatory lines on the TOC page.
- Content pages: wide gray band beginning near x=76 y=112 plus optional table/tag structures.
- Left rail copyright: final PPTX uses a native rotated PowerPoint object at `x=-2.376in, y=3.371in, w=5.512in, h=0.76in, rotation=270`, `font-size=8`. SVG fallback previews may use `matrix(0 -1.33 1.33 0 40.71 624.67)`, but the final Goldwind deck must not rely on SVG matrix export.

## VI. Page Types

| File | Purpose | Required Placeholders |
| --- | --- | --- |
| `01_cover.svg` | Cover | `{{TITLE}}`, `{{AUTHOR}}`, `{{DATE}}` |
| `02_toc.svg` | Table of contents | `{{TOC_ITEM_1_TITLE}}` ... `{{TOC_ITEM_4_TITLE}}` |
| `02_chapter.svg` | Chapter opener | `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`, `{{CHAPTER_DESC}}` |
| `03_content.svg` | Content page | `{{SECTION_NUM}}`, `{{PAGE_TITLE}}`, `{{CONTENT_AREA}}`, `{{SOURCE}}` |
| `04_ending.svg` | Ending | Editable element structure; default text may be changed on user request |
| `goldwind_native_base.pptx` | Native editable production base | Required for final Goldwind PPTX |
| `toc_wind_left.png` | Native TOC left image | Required on slide 2 TOC |

## VII. Layout Modes

- Cover / ending: dotted-wave anchor page.
- TOC: left full-height wind-turbine image plus right-aligned agenda list.
- Chapter opener: header plus full-width gray summary band.
- Dense content: rectangular gray bands, tables, two-column image/text, or screenshot blocks.
- Avoid modern rounded-card grids unless the user explicitly requests a different style.

## VIII. Spacing Specification

| Element | Coordinate / Size |
| --- | --- |
| Logo | x=1048, y=28, w=168, h=50 |
| Left rail | x=72/73, full height |
| Copyright (native PPTX) | x=-2.376in, y=3.371in, w=5.512in, h=0.76in, rotation=270, font-size=8 |
| Copyright (SVG fallback) | `matrix(0 -1.33 1.33 0 40.71 624.67)`, font-size=8 |
| Header line | x1=0, y=84, x2=328 |
| Content band | x=76, y=112, w=1140 |
| Footer source | x=84, y=700 |
| Forbidden marker | No gray/white/gray block at x=1204, y=620 |
| Cover/ending wave | `bottom_wave.png`, x=0, y=316, w=1280, h=390 |
| TOC left image | `toc_wind_left.png`, x=0, y=-0.006in, w=6.92in, h=7.506in |
| TOC text box | x=7.653in, y=0.187in, w=4.899in, h=6.614in |

## IX. SVG Technical Constraints

- Use `viewBox="0 0 1280 720"` for all templates.
- Use inline SVG attributes only; do not use `<style>`, CSS classes, scripts, or foreignObject.
- Image references must point to files in this template directory.
- Use `preserveAspectRatio` on every image.
- Keep placeholders visible and editable.
- Do not rasterize any structural page as one full-page image. Ending-page text, rail, accent bar, logo, and wave/background must remain separate editable/native PPT elements.
- For final `金风通用模板` delivery, build with `scripts/goldwind_native_deck.py` and validate with `scripts/goldwind_native_check.py` plus `scripts/pptx_visibility_check.py`.

## X. Placeholder Specification

Use the canonical placeholder contract:

- Cover: `{{TITLE}}`, `{{DATE}}`, `{{AUTHOR}}`; if the user gives a title, use it, otherwise generate the title from source content. Do not ask the user to edit any other cover text.
- Chapter: `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`, `{{CHAPTER_DESC}}`
- Content: `{{SECTION_NUM}}`, `{{PAGE_TITLE}}`, `{{CONTENT_AREA}}`, `{{SOURCE}}`
- Ending: current template text is the default value only. If the user asks to change it, replace the visible editable text while preserving the same element positions, typography scale, and visual hierarchy. Do not flatten the ending page into a screenshot or single image.
- TOC: `{{TOC_ITEM_1_TITLE}}` through `{{TOC_ITEM_4_TITLE}}` only. Use the native left-image layout and right agenda text box coordinates listed above. Do not add subtitles or secondary explanatory lines.
