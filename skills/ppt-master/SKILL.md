---
name: ppt-master
description: >
  Goldwind-oriented PPT production workflow. On first invocation, always enters
  an official intake mode, asking for a reference style deck, source materials,
  and online research preference before continuing to the native Goldwind PPTX
  or SVG-to-PPTX pipeline.
  Use when user asks to "create PPT", "make presentation", "生成PPT", "做PPT",
  "制作演示文稿", or mentions "ppt-master".
---

# PPT Master Skill

> AI-driven Goldwind PPT production system. Converts source materials into a native editable Goldwind PPTX when `金风通用模板` is selected, and keeps the SVG-to-PPTX pipeline for non-native templates and reference previews.

**Core Pipeline**: `Source Document → Create Project → Template Option → Strategist → [Image_Generator] → Executor → Native Goldwind PPTX or SVG Post-processing → Export`

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order; the output of each step is the input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require a full stop; the AI MUST wait for an explicit user response before proceeding and MUST NOT make any decisions on behalf of the user
> 3. **NO CROSS-PHASE BUNDLING** — Cross-phase bundling is FORBIDDEN. (Note: the Eight Confirmations in Step 4 are ⛔ BLOCKING — the AI MUST present recommendations and wait for explicit user confirmation before proceeding. Once the user confirms, all subsequent non-BLOCKING steps — design spec output, SVG generation, speaker notes, and post-processing — may proceed automatically without further user confirmation)
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE) listed at the top; these MUST be verified before starting that Step
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN (e.g., writing SVG code during the Strategist phase)
> 6. **NO SUB-AGENT SVG GENERATION** — Executor Step 6 SVG generation is context-dependent and MUST be completed by the current main agent end-to-end. Delegating page SVG generation to sub-agents is FORBIDDEN
> 7. **SEQUENTIAL PAGE GENERATION ONLY** — In Executor Step 6, after the global design context is confirmed, SVG pages MUST be generated sequentially page by page in one continuous pass. Grouped page batches (for example, 5 pages at a time) are FORBIDDEN
> 8. **SPEC_LOCK RE-READ PER PAGE** — Before generating each SVG page, Executor MUST `read_file <project_path>/spec_lock.md`. All colors / fonts / icons / images MUST come from this file — no values from memory or invented on the fly. Executor MUST also look up the current page's `page_rhythm` tag and apply the matching layout discipline (`anchor` / `dense` / `breathing` — see executor-base.md §2.1). This rule exists to resist context-compression drift on long decks and to break the uniform "every page is a card grid" default
> 9. **GOLDWIND TEMPLATE MIMIC FIRST** — When a historical Goldwind PPT or `金风通用模板` is provided/selected, template extraction, reference-SVG reading, coordinate/title/font anchor locking, and template-mimic validation MUST happen before content design or SVG generation. Skipping this is a workflow failure.

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **Response language**: Always match the language of the user's input and provided source materials. For example, if the user asks in Chinese, respond in Chinese; if the source material is in English, respond in English.
> - **Explicit override**: If the user explicitly requests a specific language (e.g., "请用英文回答" or "Reply in Chinese"), use that language instead.
> - **Template format**: The `design_spec.md` file MUST always follow its original English template structure (section headings, field names), regardless of the conversation language. Content values within the template may be in the user's language.

> [!IMPORTANT]
> ## 🔌 Compatibility With Generic Coding Skills
>
> - `ppt-master` is a repository-specific workflow skill, not a general application scaffold
> - Do NOT create or require `.worktrees/`, `tests/`, branch workflows, or other generic engineering structure by default
> - If another generic coding skill suggests repository conventions that conflict with this workflow, follow this skill first unless the user explicitly asks otherwise

> [!CAUTION]
> ## 🏢 Goldwind Intake Gate (HIGHEST PRIORITY)
>
> This skill is customized for **Goldwind Technology PPT production**.
>
> **When this skill is invoked in a thread for the first time, regardless of the user's first sentence, the AI MUST NOT start analysis, planning, conversion, template extraction, or generation immediately.**
>
> Instead, the AI MUST reply with **only** the following official startup notice in Chinese (minor punctuation polishing is allowed, but the meaning and structure must remain the same):
>
> ```text
> 启动成功。现已进入金风科技PPT制作流程。为确保版式风格、内容整理及扩展资料准备准确无误，请您依次提供以下四项资料：
> 1. PPT样式参考：请发送一份您过往汇报中使用的PPT或历史模板文件，我将自动提取版式与视觉风格，并按该风格进行临摹制作；也可以选择使用本技能包中自带的金风通用模板。
> 2. 内容素材资料：您可以直接发送文字内容，也可以发送一个或多个文件；我将自动完成整理、提炼与结构化处理，并用于后续PPT编排。
> 3. 联网扩展需求：如需我联网补充资料，请明确说明希望扩展的是PPT内图片素材、Icon素材，还是内容资料；我将按您的要求执行扩展搜索与整理。如无需联网，也请直接说明。
> 4. 图标素材需求：如您有企业图标素材库，请一并发送；如需AI生成自定义图标，请明确说明，确认后我可在正文页素材中使用AI生成的自定义图标；未说明时默认使用本技能包内置SVG图标库。
> ```
>
> Mandatory behavior:
>
> 1. On the first invocation, output **only** the startup notice above. Do not append workflow explanation, recommendations, confirmations, or any extra analysis.
> 2. Even if the user already included files, links, or detailed requirements in the first triggering message, still output only the startup notice in that turn. Do not process those materials yet.
> 3. After the startup notice has been sent once in the thread, the AI may continue the workflow on subsequent turns using:
>    - materials already present in the conversation
>    - newly uploaded historical PPT style references
>    - newly provided text/files
>    - the user's explicit联网搜索 preference
> 4. Before entering the normal PPT Master pipeline, verify whether the following intake items are sufficiently covered:
>    - `style_reference`: historical PPT / reference style deck / brand style sample
>    - `content_materials`: text, documents, spreadsheets, PDFs, PPTs, or other source content
>    - `research_preference`: no search / search images-icons / search content / search both
>    - `icon_asset_preference`: built-in SVG library / user-provided icon library / AI-generated custom icons
> 5. If one or more required intake items are still missing after the first startup reply (`style_reference`, `content_materials`, `research_preference`), the AI must stay in intake mode and ask only for the missing items in a concise, official tone. Do not skip ahead to Step 1.
> 6. `icon_asset_preference` is non-blocking: if the user does not answer it, default to the built-in SVG icon library. If the user explicitly chooses AI-generated custom icons, those icons may be used as正文页素材 and must follow the Icon Generation Policy below.
> 7. Once the intake items are sufficiently covered, continue into the standard pipeline below in strict serial order.

## Goldwind Intake Checklist

Before entering the standard workflow, the AI should internally normalize the user's intake into the following structure:

```text
style_reference:
- provided / missing
- file paths or links
- notes on expected style similarity

content_materials:
- provided / missing
- text summary or file list

research_preference:
- no_search / images_icons / content / both
- optional keyword or scope notes

icon_asset_preference:
- built_in_svg / user_provided_library / ai_custom_icons
- notes on provided icon files or requested custom icon style
```

Recommended intake follow-up rules after the startup notice:

- If only the style reference is missing, ask only for the historical PPT / style reference.
- If only the content materials are missing, ask only for the source materials to fill into the deck.
- If only the research preference is missing, ask whether联网搜索 is needed and what should be searched.
- If only the icon asset preference is missing, do not block; default to the built-in SVG icon library unless the user later requests a user-provided icon library or AI-generated custom icons.
- If the required style reference, content materials, and research preference are available, do not ask redundant intake questions; proceed directly to Step 1. Missing icon asset preference defaults to the built-in SVG icon library.

Goldwind customization rule:

- If the user provides a historical PPT / PPTX style reference, the AI MUST treat it as the primary visual authority for this project.
- Do not default to generic free design when a Goldwind historical PPT is available.
- Extract and summarize the historical PPT style before writing the project `design_spec.md`.
- The extracted style should guide colors, typography, page rhythm, header/footer treatment, logo placement, decorative motifs, chart styling, and image usage.
- If the user explicitly says `金风通用模板`, `工作策划模板`, or asks to use the 2024 work-planning style as a reusable template, select the built-in optional template `金风通用模板`.
- For `金风通用模板`, the default deliverable MUST be a native editable PPTX built from `templates/layouts/金风通用模板/goldwind_native_base.pptx` via `scripts/goldwind_native_deck.py`. The SVG templates remain the visual/reference fallback, not the primary export path.
- For `金风通用模板`, the user-facing final output MUST be exactly one PPTX with a Chinese filename derived from the deck title. Do not attach or list QA decks, preview images, exported SVG PPTX files, design docs, or scripts unless the user explicitly asks for them.
- For `金风通用模板`, the cover page has only three dynamic text slots: `{{TITLE}}`, `{{AUTHOR}}`, and `{{DATE}}`. Use a user-provided title when present; otherwise auto-generate a title from the source material. Do not ask the user to edit any other cover text.
- For `金风通用模板`, the ending page MUST remain editable PowerPoint elements that match the Goldwind cover/ending layout structure, coordinates, typography, logo/rail/wave/accent placement, and visual hierarchy. The current ending copy is the default value only; it may be changed when the user requests different wording. Never rasterize the ending page as a full-page image.
- After building a native Goldwind PPTX, run `python3 ${SKILL_DIR}/scripts/goldwind_native_check.py <output.pptx>` and `python3 ${SKILL_DIR}/scripts/pptx_visibility_check.py <output.pptx>`. Any failure is blocking.

## Main Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | Documents to Markdown — native Python for DOCX/HTML/EPUB/IPYNB, pandoc fallback for legacy formats (.doc/.odt/.rtf/.tex/.rst/.org/.typ) |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PowerPoint to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | Web page to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.cjs` | Node.js fallback for WeChat / TLS-blocked sites (use only if `curl_cffi` is unavailable; `web_to_md.py` now handles WeChat when `curl_cffi` is installed) |
| `${SKILL_DIR}/scripts/project_manager.py` | Project init / validate / manage |
| `${SKILL_DIR}/scripts/analyze_images.py` | Image analysis |
| `${SKILL_DIR}/scripts/image_gen.py` | AI image generation (multi-provider) |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG quality check |
| `${SKILL_DIR}/scripts/layout_sanity_check.py` | SVG layout collision check for image/text overlaps |
| `${SKILL_DIR}/scripts/template_mimic_check.py` | Goldwind template-mimic gate check |
| `${SKILL_DIR}/scripts/goldwind_native_deck.py` | Build an editable native PPTX from the built-in Goldwind PowerPoint master/layout package |
| `${SKILL_DIR}/scripts/goldwind_native_check.py` | Native Goldwind PPTX gate check for TOC image, layout binding, rotated copyright, and media integrity |
| `${SKILL_DIR}/scripts/total_md_split.py` | Speaker notes splitting |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | Export to PPTX |
| `${SKILL_DIR}/scripts/pptx_compat_export.py` | Export a raster compatibility PPTX via Chrome-rendered full-slide PNGs for WPS / older Office blank-slide fallback |
| `${SKILL_DIR}/scripts/pptx_visibility_check.py` | Post-export PPTX blank-slide / missing-media check |
| `${SKILL_DIR}/scripts/update_spec.py` | Propagate a `spec_lock.md` color / font_family change across all generated SVGs |

For complete tool documentation, see `${SKILL_DIR}/scripts/README.md`.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layout templates | `${SKILL_DIR}/templates/layouts/layouts_index.json` | Query available page layout templates |
| Visualization templates | `${SKILL_DIR}/templates/charts/charts_index.json` | Query available visualization SVG templates (charts, infographics, diagrams, frameworks) |
| Icon library | `${SKILL_DIR}/templates/icons/` | Search icons on demand: `ls templates/icons/<library>/ \| grep <keyword>` (libraries: `chunk/`, `tabler-filled/`, `tabler-outline/`) |

## Icon Generation Policy

- Standard PPT icons MUST come from the bundled SVG icon libraries in `${SKILL_DIR}/templates/icons/` and be embedded by `finalize_svg.py` / `embed_icons.py`. They do not use any image model.
- Do not route ordinary UI icons, KPI icons, process-step icons, bullet icons, or card icons through `image_gen.py`.
- `image_gen.py` is only for raster image assets such as backgrounds, photos, illustrations, decorative patterns, or large diagram-style images. It is not the default icon pipeline.
- If a user explicitly requests a custom AI-generated icon or a required metaphor cannot be found after searching the approved icon library, treat it as an image asset, record it in the Image Resource List, and document the active backend/model from `python3 ${SKILL_DIR}/scripts/image_gen.py --list-backends` or the runtime `IMAGE_BACKEND` / provider model variables. Do not call it generically "image2".
- For Goldwind/engineering/internal reporting decks, prefer the `chunk` icon library unless the design spec deliberately chooses another single library. One presentation still uses exactly one icon library.

## Standalone Workflows

| Workflow | Path | Purpose |
|----------|------|---------|
| `create-template` | `workflows/create-template.md` | Standalone template creation workflow |

---

## Workflow

### Step 0: Goldwind Intake

🚧 **GATE**: This step runs before all other steps whenever the skill is newly invoked in a thread.

Rules:

1. First invocation in thread: output the official startup notice from **Goldwind Intake Gate** and hard stop.
2. Subsequent turns: collect and verify `style_reference`, `content_materials`, and `research_preference`.
3. Do not enter Step 1 until the intake is sufficiently complete.
4. If the user requests联网搜索 after intake, treat the selected scope as part of the project inputs and carry it forward into Strategist / Image / asset selection decisions.

**✅ Checkpoint — Proceed to Step 1 only when intake is sufficiently complete.**

### Step 0.5: Goldwind Style Reference Preparation

🚧 **GATE**: Step 0 complete; `style_reference` is available.

When the style reference includes a historical `.pptx` file, prepare it before normal content processing:

```bash
python3 ${SKILL_DIR}/scripts/pptx_template_import.py "<style_reference.pptx>" -o "<project_or_output_path>/style_reference_import"
```

Use the generated import package as the primary style evidence:

- `manifest.json` for slide size, theme colors, fonts, assets, and page candidates
- `master_layout_analysis.md` for reusable master/layout structure
- `analysis.md` for page-type and content-pattern hints
- `reference_svg_selection.json` and selected `svg/slide_*.svg` files for page rhythm, spacing, and visual motifs
- extracted `assets/` for reusable logos, backgrounds, and brand imagery

Hard mimic requirements:

1. Read every SVG file listed in `reference_svg_selection.json` before writing `design_spec.md`.
2. Produce a project-level template mimic contract in `design_spec.md` (or a companion `<project_path>/template_mimic.md`) covering page-type mapping, title hierarchy, font plan, logo coordinates, left copyright rail, cover/TOC/ending structure, and reusable asset exclusions.
3. Only promote true reusable template elements. Content-specific figures, including the simulation/arrow figure previously misidentified from the 2024 work-planning deck, MUST NOT be treated as template assets.
4. For `金风通用模板`, the bottom-right three-stripe page-number block (`x=1204, y=620, w=76, h=60`) is a forbidden non-template artifact. Do not generate it on any page.
5. If `金风通用模板` is used, preserve its cover and ending contracts exactly: cover title/name/date only; ending page element structure is locked to the native Goldwind cover/ending layout, while ending text uses current defaults unless the user asks to modify it. The ending page must stay editable and must not be delivered as one flattened image.
6. Use the native Goldwind pathway by default: `python3 ${SKILL_DIR}/scripts/goldwind_native_deck.py --spec <deck_spec.json> -o <output.pptx>`. This avoids SVG matrix/rotation loss in WPS and keeps logo, rail, wave/background, and master/layout elements editable or natively inherited.
7. Name the final PPTX in Chinese, preferably from the deck title (for example `金风科技2025股东回报.pptx`). User-facing delivery must list only this one PPTX. Internal QA decks, preview PNGs, SVG reference decks, logs, scripts, and design docs may be created for checking but must not be presented as final outputs unless requested.
8. Preserve the dotted wave background as a full-width template layer on cover/ending and other wave-background layouts. In SVG fallback only, use `bottom_wave.png` at `x=0, y=316, w=1280, h=390`. Do not crop it to a local decoration.
9. Preserve the TOC page as the native left-image agenda layout, not a dotted-wave substitute: use `toc_wind_left.png` at `x=0, y=-0.006in, w=6.92in, h=7.506in`, with the right TOC text box at `x=7.653in, y=0.187in, w=4.899in, h=6.614in`. Keep four primary entries only; no description rows or secondary explanatory lines.
10. Preserve content-page titles by filling the native top title placeholder; do not add a second title text box over the placeholder.
11. Preserve the left rail copyright as a native rotated PowerPoint object when exporting PPTX: `x=-2.376in, y=3.371in, w=5.512in, h=0.76in, rotation=270`, `font-size=8`. In SVG fallback previews, retain the imported `matrix(0 -1.33 1.33 0 40.71 624.67)` anchor, but do not use SVG fallback as the primary Goldwind deliverable.
12. Run `goldwind_native_check.py` and `pptx_visibility_check.py` on the final native PPTX; any missing TOC left image, duplicate title, unfilled title placeholder, top-left horizontal copyright text, missing media, or wrong layout binding is a blocking failure.

If the reference is screenshots or images rather than PPTX, preserve them as style evidence and summarize visible style cues before Step 4.

**✅ Checkpoint — Style reference prepared and summarized; proceed to Step 1.**

### Step 1: Source Content Processing

🚧 **GATE**: Step 0 and Step 0.5 complete; user has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

When the user provides non-Markdown content, convert immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office document | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| PPTX / PowerPoint deck | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / other | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`; falls back to `node web_to_md.cjs <URL>` only if that package is unavailable) |
| Markdown | Read directly |

**✅ Checkpoint — Confirm source content is ready, proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format>
```

Format options: `ppt169` (default), `ppt43`, `xhs`, `story`, etc. For the full format list, see `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User provided text directly in conversation | No import needed — content is already in conversation context; subsequent steps can reference it directly |

> ⚠️ **MUST use `--move`**: All source files (original PDF / MD / images) MUST be **moved** (not copied) into `sources/` for archiving.
> - Markdown files generated in Step 1, original PDFs, original MDs — **all** must be moved into the project via `import-sources --move`
> - Intermediate artifacts (e.g., `_files/` directories) are handled automatically by `import-sources`
> - After execution, source files no longer exist at their original location

**✅ Checkpoint — Confirm project structure created successfully, `sources/` contains all source files, converted materials are ready. Proceed to Step 3.**

---

### Step 3: Template Option

🚧 **GATE**: Step 2 complete; project directory structure is ready.

**Default path — free design, no question asked.** Proceed directly to Step 4. Do NOT query `layouts_index.json` and do NOT ask the user an A/B template-vs-free-design question. Free design is the standard mode: the AI tailors structure and style to the specific content.

**Template flow is opt-in.** Enter it only when one of these explicit triggers appears in the user's prior messages:

1. User names a specific template (e.g., "用 mckinsey 模板" / "use the academic_defense template")
2. User names a style / brand reference that maps to a template (e.g., "McKinsey 那种" / "Google style" / "学术答辩样式")
3. User explicitly asks what templates exist (e.g., "有哪些模板可以用")

Only when a trigger fires: read `${SKILL_DIR}/templates/layouts/layouts_index.json`, resolve the match (or list available options for trigger 3), and copy template files to the project directory:

```bash
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.svg <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/<template_name>/design_spec.md <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.png <project_path>/templates/ 2>/dev/null || true
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.jpg <project_path>/templates/ 2>/dev/null || true
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.png <project_path>/images/ 2>/dev/null || true
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.jpg <project_path>/images/ 2>/dev/null || true
```

When `<template_name>` is `金风通用模板`, immediately run:

```bash
python3 ${SKILL_DIR}/scripts/template_mimic_check.py "${SKILL_DIR}/templates/layouts/金风通用模板" --tolerance 0
```

The check must pass before Step 4.

**Soft hint (non-blocking, optional).** Before Step 4, if the user's content is an obvious strong match for an existing template (e.g., clearly an academic defense, a government report, a McKinsey-style consulting deck) AND the user has given no template signal, the AI MAY emit a single-sentence notice and continue without waiting:

> Note: the library has a template `<name>` that matches this scenario closely. Say the word if you want to use it; otherwise I'll continue with free design.

This is a hint, not a question — do NOT block, do NOT require an answer. Skip the hint entirely when the match is weak or ambiguous.

> To create a new global template, read `workflows/create-template.md`

**✅ Checkpoint — Default path proceeds to Step 4 without user interaction. If a template trigger fired, template files are copied before advancing.**

---

### Step 4: Strategist Phase (MANDATORY — cannot be skipped)

🚧 **GATE**: Step 3 complete; default free-design path taken, or (if triggered) template files copied into the project.

First, read the role definition:
```
Read references/strategist.md
```

> ⚠️ **Mandatory gate in `strategist.md`**: Before writing `design_spec.md`, Strategist MUST `read_file templates/design_spec_reference.md` and produce the spec following its full I–XI section structure. See `strategist.md` Section 1 for the explicit gate rule.

**Must complete the Eight Confirmations** (full template structure in `templates/design_spec_reference.md`):

⛔ **BLOCKING**: The Eight Confirmations MUST be presented to the user as a bundled set of recommendations, and you MUST **wait for the user to confirm or modify** before outputting the Design Specification & Content Outline. This is the single core confirmation point in the workflow. Once confirmed, all subsequent script execution and slide generation should proceed fully automatically.

1. Canvas format
2. Page count range
3. Target audience
4. Style objective
5. Color scheme
6. Icon usage approach
7. Typography plan
8. Image usage approach

If the user has provided images, run the analysis script **before outputting the design spec** (do NOT directly read/open image files — use the script output only):
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **Image handling rule**: The AI must NEVER directly read, open, or view image files (`.jpg`, `.png`, etc.). All image information must come from the `analyze_images.py` script output or the Design Specification's Image Resource List.

**Output**:
- `<project_path>/design_spec.md` — human-readable design narrative
- `<project_path>/spec_lock.md` — machine-readable execution contract (distilled from the decisions in design_spec.md; Executor re-reads this before every page). See `templates/spec_lock_reference.md` for the skeleton.
- If a historical PPT or `金风通用模板` is used, the design spec / lock MUST record template mimic anchors and page mapping before generation.

**✅ Checkpoint — Phase deliverables complete, auto-proceed to next step**:
```markdown
## ✅ Strategist Phase Complete
- [x] Eight Confirmations completed (user confirmed)
- [x] Design Specification & Content Outline generated
- [x] Execution lock (spec_lock.md) generated
- [ ] **Next**: Auto-proceed to [Image_Generator / Executor] phase
```

---

### Step 5: Image_Generator Phase (Conditional)

🚧 **GATE**: Step 4 complete; Design Specification & Content Outline generated and user confirmed.

> **Trigger condition**: Image approach includes "AI generation". If not triggered, skip directly to Step 6 (Step 6 GATE must still be satisfied).

Read `references/image-generator.md`

1. Extract all images with status "pending generation" from the design spec
2. Generate prompt document → `<project_path>/images/image_prompts.md`
3. Generate images (CLI tool recommended):
   ```bash
   python3 ${SKILL_DIR}/scripts/image_gen.py "prompt" --aspect_ratio 16:9 --image_size 1K -o <project_path>/images
   ```

**✅ Checkpoint — Confirm all images are ready, proceed to Step 6**:
```markdown
## ✅ Image_Generator Phase Complete
- [x] Prompt document created
- [x] All images saved to images/
```

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete; all prerequisite deliverables are ready.

Read the role definition based on the selected style:
```
Read references/executor-base.md          # REQUIRED: common guidelines
Read references/executor-general.md       # General flexible style
Read references/executor-consultant.md    # Consulting style
Read references/executor-consultant-top.md # Top consulting style (MBB level)
```

> Only need to read executor-base + one style file.

**Design Parameter Confirmation (Mandatory)**: Before generating the first SVG, the Executor MUST review and output key design parameters from the Design Specification (canvas dimensions, color scheme, font plan, body font size) to ensure spec adherence. See executor-base.md Section 2 for details.

**Per-page spec_lock re-read (Mandatory)**: Before generating **each** SVG page, Executor MUST `read_file <project_path>/spec_lock.md` and use only the colors / fonts / icons / images listed there. This resists context-compression drift on long decks. See executor-base.md §2.1 for details.

> ⚠️ **Main-agent only rule**: SVG generation in Step 6 MUST remain with the current main agent because page design depends on full upstream context (source content, design spec, template mapping, image decisions, and cross-page consistency). Do NOT delegate any slide SVG generation to sub-agents.
> ⚠️ **Generation rhythm rule**: After confirming the global design parameters, the Executor MUST generate pages sequentially, one page at a time, while staying in the same continuous main-agent context. Do NOT split Step 6 into grouped page batches such as 5 pages per batch.

**Visual Construction Phase**:
- Generate SVG pages sequentially, one page at a time, in one continuous pass → `<project_path>/svg_output/`

**Quality Check Gate (Mandatory)** — after all SVGs are generated and BEFORE speaker notes:
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```
- Any `error` (banned SVG features, viewBox mismatch, spec_lock drift, etc.) MUST be fixed on the offending page before proceeding — go back to Visual Construction, re-generate that page, re-run the check.
- `warning` entries (e.g., low-resolution image, non-PPT-safe font tail) should be reviewed and fixed when straightforward; may be acknowledged and released otherwise.
- Running the checker against `svg_output/` is required — running it only after `finalize_svg.py` is too late (finalize rewrites SVG and some violations get masked).

If `金风通用模板` or a Goldwind historical reference is used, also run:

```bash
python3 ${SKILL_DIR}/scripts/template_mimic_check.py <project_path> --tolerance 0
```

Any failure must be fixed before speaker notes or export.

Run the layout sanity check before speaker notes. Any image/text overlap failure must be fixed by resizing, moving, or splitting the affected content before export:

```bash
python3 ${SKILL_DIR}/scripts/layout_sanity_check.py <project_path>
```

**Logic Construction Phase**:
- Generate speaker notes → `<project_path>/notes/total.md`

**✅ Checkpoint — Confirm all SVGs and notes are fully generated and quality-checked. Proceed directly to Step 7 post-processing**:
```markdown
## ✅ Executor Phase Complete
- [x] All SVGs generated to svg_output/
- [x] svg_quality_checker.py passed (0 errors)
- [x] Speaker notes generated at notes/total.md
```

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; all SVGs generated to `svg_output/`; speaker notes `notes/total.md` generated.

> ⚠️ The following three sub-steps MUST be **executed individually one at a time**. Each command must complete and be confirmed successful before running the next.
> ❌ **NEVER** put all three commands in a single code block or single shell invocation.

**Step 7.1** — Split speaker notes:
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
# Output: exports/<project_name>_<timestamp>.pptx + exports/<project_name>_<timestamp>_svg.pptx
# Use --only native  to skip SVG reference version
# Use --only legacy  to only generate SVG image version
```

> ❌ **NEVER** use `cp` as a substitute for `finalize_svg.py` — it performs multiple critical processing steps
> ❌ **NEVER** export directly from `svg_output/` — MUST use `-s final` to export from `svg_final/`
> ❌ **NEVER** add extra flags like `--only`

**Step 7.4** — Verify the native editable PPTX before delivery:
```bash
python3 ${SKILL_DIR}/scripts/pptx_visibility_check.py <project_path>/exports/<native_output>.pptx
```

If the SVG reference deck (`*_svg.pptx`) is produced without PNG fallback support, treat it as an internal layout reference only. The native editable PPTX is the deliverable for WPS/PowerPoint viewing.

---

## Role Switching Protocol

Before switching roles, you **MUST first read** the corresponding reference file — skipping is FORBIDDEN. Output marker:

```markdown
## [Role Switch: <Role Name>]
📖 Reading role definition: references/<filename>.md
📋 Current task: <brief description>
```

---

## Reference Resources

| Resource | Path |
|----------|------|
| Shared technical constraints | `references/shared-standards.md` |
| Canvas format specification | `references/canvas-formats.md` |
| Image layout specification | `references/image-layout-spec.md` |
| SVG image embedding | `references/svg-image-embedding.md` |

---

## Notes

- Do NOT add extra flags like `--only` to the post-processing commands — run them as-is
- Local preview: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: If the user encounters issues during generation (layout overflow, export errors, blank images, etc.), recommend checking `docs/faq.md` — it contains known solutions sourced from real user reports and is continuously updated
