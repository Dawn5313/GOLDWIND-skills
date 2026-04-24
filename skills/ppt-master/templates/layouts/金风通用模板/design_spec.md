# 金风通用模板 - Design Specification

## I. Template Overview

| Item | Value |
| --- | --- |
| Template ID | 金风通用模板 |
| Display Name | 金风通用模板 |
| Category | brand |
| Source Reference | 2024年工作策划——风资源创新研究部0322.pptx |
| Applicable Scenarios | 金风科技内部汇报、年度策划、工作计划、技术部门工作策划、培训汇报 |
| Design Tone | 克制、工程感、白底、深蓝标题、浅灰内容带、表格式信息组织 |

This template is reconstructed from the Goldwind 2024 work-planning deck. It is a reusable PPT Master layout package, not a full slide conversion. The reusable visual authority is limited to the true template elements: top-right Goldwind logo, left copyright rail, full-width dotted wave artwork, header/title structure, gray content bands, and teal table/tag blocks.

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
- Cover/ending: large title block aligned near x=344 for cover and x=186 for ending, vertical blue accent bar near x=73, full-width dotted wave layer in the lower half.
- TOC: full-width dotted wave layer (`x=0, y=120, w=1280, h=480`) behind the page, agenda list on right starting near x=736.
- Content pages: wide gray band beginning near x=76 y=112 plus optional table/tag structures.
- Left rail copyright: lock the original imported anchor `matrix(0 -1.33 1.33 0 40.71 624.67)`, `font-size=8`; do not approximate it with a rotated text box at another coordinate.

## VI. Page Types

| File | Purpose | Required Placeholders |
| --- | --- | --- |
| `01_cover.svg` | Cover | `{{TITLE}}`, `{{AUTHOR}}`, `{{DATE}}` |
| `02_toc.svg` | Table of contents | `{{TOC_ITEM_1_TITLE}}` ... `{{TOC_ITEM_4_DESC}}` |
| `02_chapter.svg` | Chapter opener | `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`, `{{CHAPTER_DESC}}` |
| `03_content.svg` | Content page | `{{SECTION_NUM}}`, `{{PAGE_TITLE}}`, `{{CONTENT_AREA}}`, `{{SOURCE}}` |
| `04_ending.svg` | Ending | Editable element structure; default text may be changed on user request |

## VII. Layout Modes

- Cover / ending: dotted-wave anchor page.
- TOC: left decorative wave plus right-aligned agenda list.
- Chapter opener: header plus full-width gray summary band.
- Dense content: rectangular gray bands, tables, two-column image/text, or screenshot blocks.
- Avoid modern rounded-card grids unless the user explicitly requests a different style.

## VIII. Spacing Specification

| Element | Coordinate / Size |
| --- | --- |
| Logo | x=1048, y=28, w=168, h=50 |
| Left rail | x=72/73, full height |
| Copyright | `matrix(0 -1.33 1.33 0 40.71 624.67)`, font-size=8 |
| Header line | x1=0, y=84, x2=328 |
| Content band | x=76, y=112, w=1140 |
| Footer source | x=84, y=700 |
| Forbidden marker | No gray/white/gray block at x=1204, y=620 |
| Cover/ending wave | x=0, y=316, w=1280, h=390 |
| TOC wave | x=0, y=120, w=1280, h=480 |

## IX. SVG Technical Constraints

- Use `viewBox="0 0 1280 720"` for all templates.
- Use inline SVG attributes only; do not use `<style>`, CSS classes, scripts, or foreignObject.
- Image references must point to files in this template directory.
- Use `preserveAspectRatio` on every image.
- Keep placeholders visible and editable.
- Do not rasterize any structural page as one full-page image. Ending-page text, rail, accent bar, logo, and wave must remain separate editable SVG/PPT elements.

## X. Placeholder Specification

Use the canonical placeholder contract:

- Cover: `{{TITLE}}`, `{{DATE}}`, `{{AUTHOR}}`; if the user gives a title, use it, otherwise generate the title from source content. Do not ask the user to edit any other cover text.
- Chapter: `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`, `{{CHAPTER_DESC}}`
- Content: `{{SECTION_NUM}}`, `{{PAGE_TITLE}}`, `{{CONTENT_AREA}}`, `{{SOURCE}}`
- Ending: current template text is the default value only. If the user asks to change it, replace the visible editable text while preserving the same element positions, typography scale, and visual hierarchy. Do not flatten the ending page into a screenshot or single image.
- TOC: `{{TOC_ITEM_1_TITLE}}`, `{{TOC_ITEM_1_DESC}}` through item 4
