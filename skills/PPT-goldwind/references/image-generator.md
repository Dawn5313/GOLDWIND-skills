# Image_Generator Reference Manual

> This file is the streamlined reference for the Image_Generator role. Common standards (SVG technical constraints, canvas formats, post-processing pipeline, etc.) are in [shared-standards.md](./shared-standards.md).

## Core Mission

Receive the "Image Resource List" from the Design Specification & Content Outline output by the Strategist, create optimized prompts for each image pending generation, generate images with the default `image2` / `gpt-image-2` backend, and save them to the project's `images/` directory.

**Trigger condition**: When AI image generation is needed (standalone use or invoked within pipeline), including proactive Strategist decisions for visual table, process, architecture, mechanism, or diagram assets.

> **Icon boundary**: The Image_Generator is not the default icon generator. Standard PPT icons must use the bundled SVG icon libraries in `templates/icons/` and are embedded by `finalize_svg.py`. Use Image_Generator for raster backgrounds, photos, illustrations, decorative patterns, large diagram-style images, visually rich process diagrams, architecture visuals, and table-to-infographic treatments. Only generate a custom icon here when the user explicitly asks for AI-generated icons or when no approved SVG library icon fits after documented search; in that case, record the active backend/model.

| Mode | Trigger | Description |
|------|---------|-------------|
| **Standalone** | Directly describe image needs | Generate single or multiple AI images |
| **In-pipeline** | Image Resource List contains `Pending generation` assets | Batch-generate `gpt-image-2` assets for a project |

> Next step in pipeline: Executor generates SVGs

---

## 1. Input & Output

### Input

- **Design Specification & Content Outline** (from Strategist): project theme, target audience, design style, color scheme, canvas format
- **Image Resource List** (key input):

  | Filename | Dimensions | Purpose | Type | Status | Generation Description |
  |----------|-----------|---------|------|--------|----------------------|
  | cover_bg.png | 1920x1080 | Cover background | Background | Pending | Modern tech abstract background, deep blue gradient |

### Output

| Deliverable | Path / Description | Requirements |
|------------|-------------------|--------------|
| Prompt document | `project/images/image_prompts.md` | **Must** be saved using file write tool — cannot just be output in conversation |
| Optimized prompts | Individual prompt per image | Directly usable with AI image generation tools; doubles as alt text |
| Image files | `project/images/` directory | Named per the resource list filenames |
| Updated list | Status changes | "Pending" → "Generated" |

---

## 2. Unified Prompt Structure

### 2.1 Standard Output Format

Every image must be output in the following format:

```markdown
### Image N: {filename}

| Attribute | Value |
| --------- | ----- |
| Purpose   | {which page / what function} |
| Type      | {Background / Illustration / Photography / Diagram / Architecture visual / Table-to-infographic / Decorative} |
| Dimensions | {width}x{height} ({aspect ratio}) |
| Original description | {description provided by user in the list} |

**Prompt**:
{subject description}, {style directive}, {color directive}, {composition directive}, {quality directive}

**Negative Prompt**:
{elements to exclude}

**Alt Text**:
> {Description for accessibility and image captions}
```

### 2.2 Prompt Components

| Component | Description | Example |
|-----------|-------------|---------|
| Subject description | Core content | `Abstract geometric shapes`, `Team collaboration scene` |
| Style directive | Visual style | `flat design`, `3D isometric`, `watercolor style` |
| Color directive | Color scheme | `color palette: navy blue (#1E3A5F), gold (#D4AF37)` |
| Composition directive | Layout ratio | `16:9 aspect ratio`, `centered composition` |
| Quality directive | Resolution quality | `high quality`, `4K resolution`, `sharp details` |
| Negative prompt | Exclude elements | `text, watermark, blurry, low quality` |

**PPT asset invariant**: The generated image must not carry final audited data, but it must still carry meaningful visual content. Avoid fake readable text, pseudo letters, random numbers that imply facts, UI gibberish, fake chart values, watermarks, logos, and tiny illegible captions. Do not generate a hollow frame. Use concrete objects, modules, process lanes, map paths, equipment silhouettes, matrix cells, status indicators, data traces, and relationship lines; exact Chinese labels and numbers are overlaid later in PPT/SVG.

**Goldwind template style anchor**: For `金风通用模板`, prepend every image prompt with: `native Goldwind PowerPoint style, mostly white and very light gray background, thin navy and teal linework, pale-gray panels, restrained teal accents, clean engineering information graphic, content-rich business visual, overlay-safe areas for editable PPT labels`. Add a negative prompt for `dark command-center dashboard, neon glow, cinematic black background, oversized blue gradient, dense sci-fi UI screens, hollow blank framework`.

**Clarification trigger**: If the image brief only says a generic style or format, ask the user one concise question before generation: `这张图需要重点呈现哪些对象、阶段、指标或业务场景？` Do not generate from an empty or generic brief.

### 2.3 Style Keywords Quick Reference

| Design Style | Recommended Image Style | Core Keywords |
|-------------|------------------------|---------------|
| General Versatile | Modern illustration, flat design | `modern`, `flat design`, `gradient`, `vibrant colors` |
| General Consulting | Clean professional, corporate | `professional`, `clean`, `corporate`, `minimalist` |
| Top Consulting | Premium minimal, abstract geometric | `premium`, `sophisticated`, `geometric`, `abstract`, `elegant` |
| Technology / SaaS | Futuristic, digital | `futuristic`, `digital`, `tech grid`, `circuit pattern`, `neon accents`, `dark background` |
| Education / Training | Friendly, instructional | `friendly`, `instructional`, `whiteboard style`, `pastel colors`, `simple shapes` |
| Marketing / Branding | Bold, energetic | `bold`, `energetic`, `dynamic composition`, `vivid colors`, `action-oriented` |
| Healthcare / Medical | Clean, reassuring | `clean`, `clinical`, `soft blue-green palette`, `organic curves`, `reassuring` |
| Finance / Banking | Conservative, trustworthy | `conservative`, `trustworthy`, `blue-gray palette`, `structured`, `precise` |
| Creative / Design | Artistic, experimental | `artistic`, `experimental`, `asymmetric`, `textured`, `hand-crafted feel` |

### 2.4 Color Integration Method

Extract colors from design spec, convert to prompt directives:

```
Primary: #1E3A5F (Deep Navy)  →  "deep navy blue (#1E3A5F)"
Secondary: #F8F9FA (Light Gray) →  "light gray (#F8F9FA)"
Accent: #D4AF37 (Gold)        →  "gold accent (#D4AF37)"

Full directive: "color palette: deep navy blue (#1E3A5F), light gray (#F8F9FA), gold accent (#D4AF37)"
```

### 2.5 Canvas Format & Aspect Ratio

| Canvas Format | Background Aspect Ratio | Recommended Resolution |
|--------------|------------------------|----------------------|
| PPT 16:9 | 16:9 | 1920x1080 or 2560x1440 |
| PPT 4:3 | 4:3 | 1600x1200 |
| Xiaohongshu (RED) | 3:4 | 1242x1660 |
| WeChat Moments | 1:1 | 1080x1080 |
| Story | 9:16 | 1080x1920 |

> Supported aspect ratios: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` (Gemini also supports `1:4`, `1:8`, `4:1`, `8:1`)

### 2.6 Multi-Image Coherence Strategy

When generating multiple images for a single deck, visual coherence is critical. Use a **Deck Style Anchor** — a shared prefix of 15-25 words prepended to every image prompt.

**Construction**: Combine style keywords (Section 2.3) + color directive (Section 2.4) + quality directive into one reusable prefix.

**Example**:
```
Deck Style Anchor:
"modern flat design illustration, color palette: deep navy (#1E3A5F), light gray (#F8F9FA), gold accent (#D4AF37), clean minimalist, high quality, 4K"

Image 1 prompt: [Deck Style Anchor], abstract technology network showing connected nodes...
Image 2 prompt: [Deck Style Anchor], team of professionals collaborating at a desk...
Image 3 prompt: [Deck Style Anchor], growth chart with upward trending line...
```

**Exception**: Background images may replace style keywords with `background`, `backdrop`, `negative space for text overlay` while keeping the same color directive. This ensures color consistency without compromising background functionality.

**Rule**: Define the Deck Style Anchor once in the prompt document header (Section 5), then reference it in every individual prompt.

---

## 3. Image Type Classification & Handling

### Type Determination Flow

1. Full-page / large-area backdrop → **Background** (3.1)
2. Real scenes / people / products → **Photography** (3.2)
3. Flat / illustration / cartoon style → **Illustration** (3.3)
4. Process / architecture / relationships → **Diagram / Architecture Visual** (3.4)
5. Partial decoration / texture → **Decorative Pattern** (3.5)
6. Dense tables / frameworks / risk maps → **Table-to-Infographic** (3.6)

### 3.1 Background

**Identifying characteristics**: Full-page background for covers or chapter pages; must support text overlay

| Key Point | Description |
|-----------|-------------|
| Emphasize background nature | Add `background`, `backdrop` |
| Reserve text area | `negative space in center for text overlay` |
| Avoid strong subjects | Use abstract, gradient, geometric elements |
| Low-contrast details | `subtle`, `soft`, `muted` |

**Template**: `Abstract {theme element} background, {style} style, {primary color} to {secondary color} gradient, subtle {decorative elements}, clean negative space in center for text overlay, {aspect ratio} aspect ratio, high resolution, professional presentation background`

**Negative prompt**: `text, letters, watermark, faces, busy patterns, high contrast details`

### 3.2 Photography

**Identifying characteristics**: Real scenes, people, products, architecture — photographic quality

| Key Point | Description |
|-----------|-------------|
| Emphasize realism | `photography`, `photorealistic`, `real photo` |
| Lighting effects | `natural lighting`, `soft shadows`, `studio lighting` |
| Background handling | `white background` / `blurred background` / `contextual setting` |
| People diversity | `diverse`, `professional attire` |

**Template**: `{subject description}, professional photography, {lighting type} lighting, {background type} background, color grading matching {color scheme}, high quality, sharp focus, 8K resolution`

**Negative prompt**: `watermark, text overlay, artificial, CGI, illustration, cartoon, distorted faces`

### 3.3 Illustration

**Identifying characteristics**: Flat design, vector style, cartoon, concept diagrams

| Key Point | Description |
|-----------|-------------|
| Specify style | `flat design`, `isometric`, `vector style`, `hand-drawn` |
| Simplify details | `simplified`, `clean lines`, `minimal details` |
| Unified palette | Strictly use design spec colors |
| Background choice | `white background` or `transparent background` |

**Template**: `{subject description}, {illustration style} illustration style, {detail level} with clean lines, color palette: {color list}, {background type} background, professional {purpose} illustration`

**Negative prompt**: `realistic, photography, 3D render, complex textures, watermark`

### 3.4 Diagram / Architecture Visual

**Identifying characteristics**: Flowcharts, architecture diagrams, concept relationship maps, process/lifecycle visuals, system architecture, technical mechanism diagrams, and data-flow visuals.

| Key Point | Description |
|-----------|-------------|
| Clear structure | `clear structure`, `organized layout`, `logical flow` |
| Connection representation | `arrows indicating flow`, `connecting lines` |
| Academic / professional feel | `suitable for academic publication`, `professional diagram` |
| Light background | `white background` or `light gray background` |
| Editable-label discipline | Generate a content-rich visual base; exact labels/numbers should be overlaid later in SVG/PPT |

**Template**: `{diagram type} visual showing {content description}, with {5-10 concrete modules/stages/objects}, connected by {connection method}, including status indicators / data traces / component hierarchy / scenario objects as appropriate, {style} style with {color scheme}, clean light background, professional technical diagram base, overlay-safe areas for editable labels`

**Negative prompt**: `cluttered, messy, overlapping elements, tiny unreadable text, incorrect labels, dark background, realistic photo unless requested`

### 3.5 Decorative Pattern

**Identifying characteristics**: Partial decoration, textures, borders, divider elements

| Key Point | Description |
|-----------|-------------|
| Repeatability | `seamless`, `tileable`, `repeatable` (if needed) |
| Understated support | `subtle`, `understated`, `supporting element` |
| Transparency-friendly | `transparent background` or `isolated element` |
| Small-size readability | Consider legibility at small dimensions |

**Template**: `{pattern type} decorative pattern, {style} style, {color scheme}, {background type} background, subtle and elegant, suitable for {purpose}`

**Negative prompt**: `busy, cluttered, high contrast, distracting, photorealistic`

### 3.6 Table-to-Infographic

**Identifying characteristics**: A slide begins as a dense table, comparison grid, risk matrix, milestone table, capability map, strategy framework, or layered control map, but comprehension improves if the table is visually structured.

| Key Point | Description |
|-----------|-------------|
| Preserve auditability | Exact table text, numbers, and labels stay editable in SVG/PPT |
| Generate structure | Ask for visual zones, bands, matrix cells, swimlanes, layer cards, or background panels |
| Avoid fake text | Request no fake readable text, pseudo letters, random fact numbers, or UI gibberish inside the generated image |
| Match template | Use Goldwind colors and restrained engineering style |
| Content fullness | Include concrete business categories, comparison bands, state indicators, timeline markers, risk levels, or scenario objects |

**Template**: `Professional presentation infographic visual for {table/framework purpose}, {layout type such as 3x3 matrix / swimlane / layered architecture / risk-control board}, containing {specific categories/stages/risk levels/status groups}, clean visual hierarchy, color palette: {color list}, subtle dividers, business icons, progress states, relationship lines, overlay-safe areas for editable text, no fake readable text, no pseudo letters, no random fact numbers, no UI gibberish`

**Negative prompt**: `fake readable text, pseudo letters, random fact numbers, UI gibberish, fake chart values, watermark, logo, cluttered table cells, dense tiny labels, low contrast, hollow blank framework`

---

## 4. Image Generation Workflow

### 4.1 Analysis Phase

1. Read the design spec; understand overall project style
2. Extract color scheme, canvas format, target audience
3. Analyze each image in the resource list individually
4. Determine each image's type (refer to Section 3)

### 4.2 Prompt Generation Phase

For each image with "Pending" or "Pending generation" status:

1. **Determine type** → Background / Photography / Illustration / Diagram / Architecture Visual / Table-to-Infographic / Decorative
2. **Understand purpose** → Which page? What function?
3. **Analyze original description** → Information from the user's "Generation description"
4. **Apply type-specific key points** → Reference the corresponding type's table
5. **Generate optimized prompt** → Use the 2.1 standard output format
6. **Save prompt document** → **Must** write to `project/images/image_prompts.md`

### 4.3 Image Generation Phase

> Prerequisite: Section 4.2 must be complete; `images/image_prompts.md` must exist

#### Method 1: Unified CLI Tool (Recommended)

```bash
python3 scripts/image_gen.py "your prompt" \
  --aspect_ratio 16:9 --image_size 2K \
  --output project/images --filename cover_bg
```

`image_gen.py` defaults to the `image2` backend, which uses `gpt-image-2` and reads the active provider from the user's Codex root files. Use `--backend image2` explicitly when a command must be self-documenting.

**Parameters**:

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `prompt` | - | Positive prompt (positional arg) | - |
| `--negative_prompt` | `-n` | Negative prompt | None |
| `--aspect_ratio` | - | Image aspect ratio | `16:9` |
| `--image_size` | - | Size (`1K`/`2K`/`4K`) | `2K` |
| `--output` | `-o` | Output directory | Current directory |
| `--filename` | `-f` | Output filename (no extension) | Auto-named |
| `--backend` | `-b` | Override backend (see `--list-backends` for options) | `image2` when `IMAGE_BACKEND` is unset |
| `--model` | `-m` | Model name | Backend default |
| `--list-backends` | - | Print support tiers and exit | `false` |

**Configuration sources**:
- Current process environment variables
- Project-root `.env` as fallback

Precedence:
- Current process environment wins
- `.env` fills missing values only

| Variable | Required | Description |
|----------|----------|-------------|
| `IMAGE_BACKEND` | Optional | Backend identifier; defaults to `image2` if unset. Run `image_gen.py --list-backends` for the current set |
| `{PROVIDER}_API_KEY` | Required | Provider-specific API key, e.g. `GEMINI_API_KEY`, `ZHIPU_API_KEY` |
| `{PROVIDER}_BASE_URL` | Optional | Provider-specific custom endpoint |
| `{PROVIDER}_MODEL` | Optional | Provider-specific model override |

For the default `image2` backend, the normal configuration is:
- `~/.codex/auth.json`: `OPENAI_API_KEY`
- `~/.codex/config.toml`: active `model_provider` and `[model_providers.<name>].base_url`
- optional overrides: `IMAGE2_MODEL`, `IMAGE2_CODEX_HOME`, `IMAGE2_BASE_URL`, `IMAGE2_API_KEY_ENV`, `IMAGE2_API_KEY`, `IMAGE2_TIMEOUT`, `IMAGE2_QUALITY`

> Use provider-specific names only (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`). See `.env.example` for the full set per backend.

> `IMAGE_API_KEY`, `IMAGE_MODEL`, and `IMAGE_BASE_URL` are intentionally unsupported.

> If `.env` or the current environment contains multiple provider configs, `IMAGE_BACKEND` explicitly selects the active one; otherwise `image2` is selected.

**Support tiers (recommended usage)**: Core / Extended / Experimental. Run `image_gen.py --list-backends` for the current assignments. Prefer `image2` for Goldwind PPT generation unless the user explicitly asks for another model/provider.

**Generation pacing (mandatory)**:
- Execute only one generation command at a time; wait for file confirmation before the next
- Recommend 2-5 second intervals between images to avoid concurrency failures
- If failure/no output occurs, halt the queue, check `IMAGE_BACKEND`, Codex provider config or provider-specific credentials, and the output directory, then resume

#### Method 2: Auto-generation

Directly call image generation API, download and save to `project/images/` directory. Use this only when the unified CLI cannot express a needed reference-image, edit, or mask workflow.

For reference images, localized edits, style transfer, or composition transfer, call the bundled low-level provider tool:

```bash
python3 scripts/api_image_generate.py \
  --prompt "Create a Goldwind-style technical architecture visual based on the reference. Preserve the module hierarchy and flow direction, but leave all labels empty for editable PPT overlay." \
  --image "project/images/reference_architecture.png" \
  --image-role "architecture structure reference" \
  --size 2048x1152 \
  --quality high \
  --out "project/images/architecture_base.png"
```

#### Method 3: Gemini Web Interface

1. Generate images in [Gemini](https://gemini.google.com/)
2. Select **Download full size** for high-resolution version
3. Remove watermark: `python3 scripts/gemini_watermark_remover.py <image_path>`
4. Place processed images in `project/images/` directory

#### Method 4: Manual Generation (Other AI Platforms)

Prompts are saved in `images/image_prompts.md`; inform the user of the file location. User generates on Midjourney, DALL-E, Stable Diffusion, etc. and places images in `project/images/` directory.

### 4.4 Verification Phase

- Confirm all images are saved to `images/` directory
- Check filenames match the resource list
- Update image resource list status to "Generated"

---

## 5. Prompt Document Template

Use the following structure when creating `project/images/image_prompts.md`:

```markdown
# Image Generation Prompts

> Project: {project_name}
> Generated: {date}
> Color scheme: Primary {#HEX} | Secondary {#HEX} | Accent {#HEX}

---

## Image List Overview

| # | Filename | Type | Dimensions | Status |
|---|----------|------|-----------|--------|
| 1 | cover_bg.png | Background | 1920x1080 | Pending |

---

## Detailed Prompts

### Image 1: cover_bg.png

| Attribute | Value |
|-----------|-------|
| Purpose | Cover background |
| Type | Background |
| Dimensions | 1920x1080 (16:9) |
| Original description | Modern tech abstract background, deep blue gradient |

**Prompt**:
Abstract futuristic background with flowing digital waves...

**Alt Text**:
> Modern tech abstract background with deep blue gradient, digital waves, and particle effects

---

## Usage Instructions

1. Generate with `python3 scripts/image_gen.py "<Prompt>" --backend image2 --aspect_ratio <ratio> --image_size 2K --output project/images --filename <name>`
2. For reference/edit jobs, use `python3 scripts/api_image_generate.py ...`
3. Verify filenames match the Image Resource List
4. Place final files in the `images/` directory
```

---

## 6. Negative Prompt Quick Reference

### By Image Type

| Type | Recommended Negative Prompt |
|------|---------------------------|
| Background | `text, letters, watermark, faces, busy patterns, high contrast details` |
| Photography | `watermark, text overlay, artificial, CGI, illustration, cartoon, distorted faces` |
| Illustration | `realistic, photography, 3D render, complex textures, watermark` |
| Diagram / Architecture visual | `cluttered, messy, overlapping elements, fake readable text, tiny illegible captions, incorrect factual labels, dark background, realistic photo unless requested, hollow blank framework` |
| Table-to-infographic | `fake readable text, pseudo letters, random fact numbers, watermark, cluttered table cells, dense tiny labels, low contrast, hollow blank framework` |
| Decorative pattern | `busy, cluttered, high contrast, distracting, photorealistic` |

### Universal Negative Prompts

- **Standard**: `fake readable text, watermark, signature, blurry, distorted, low quality`
- **Extended** (people scenarios): `fake readable text, watermark, signature, blurry, low quality, distorted, extra fingers, mutated hands, poorly drawn face, bad anatomy, extra limbs, disfigured, deformed`

---

## 7. Common Issues

### Default Inference When No "Generation Description" Provided

| Purpose | Default Inference |
|---------|------------------|
| Cover background | Abstract gradient background, reserve central text area |
| Chapter page background | Clean geometric pattern, monochrome focus |
| Team introduction page | Team collaboration scene illustration (flat style) |
| Data display page | Clean geometric pattern or solid color background |
| Product showcase | Product photography style, white or gradient background |

### When Images Are Unsatisfactory

Diagnose the problem category and apply a targeted prompt fix:

| Problem | Diagnosis | Prompt Adjustment |
|---------|-----------|-------------------|
| Wrong style | Image looks photorealistic when flat design was intended | Change style directive: replace `photography` with `flat design illustration` |
| Wrong colors | Colors don't match the design spec palette | Strengthen color directive: add explicit HEX codes, repeat color names |
| Wrong composition | Subject is off-center or layout doesn't fit the slide | Adjust composition directive: add `centered composition`, `rule of thirds`, or `wide negative space on left` |
| Wrong subject | Image depicts something different from what was described | Rewrite subject description with more specificity and concrete details |
| Low quality | Image is blurry, has artifacts, or lacks detail | Add `highly detailed, sharp focus, professional quality, 8K resolution` |

**Variant workflow**:
1. Keep the original prompt as "Variant A" in `image_prompts.md`
2. Create modified prompt as "Variant B" with targeted fixes from the table above
3. If needed, create "Variant C" with a different stylistic approach
4. Label all variants clearly so the user can compare results

---

## 8. Role Collaboration

### Handoff with Strategist

| Direction | Content |
|-----------|---------|
| Receives | Design Specification & Content Outline (with image resource list) |
| Trigger condition | User selected "C) AI generation" in "Image usage" |
| Key information | Color scheme, design style, canvas format |

### Handoff with Executor

| Direction | Content |
|-----------|---------|
| Delivers | All images placed in `project/images/` directory |
| Executor reference | `<image href="../images/xxx.png" .../>` |
| Path note | SVGs in `svg_output/`, images in `images/`; use relative path `../images/` |

---

## 9. Task Completion Checkpoint

### Must-complete Items

- [ ] Created prompt document `project/images/image_prompts.md`
- [ ] Each image has: type determination + optimized prompt + negative prompt + Alt Text
- [ ] Uses unified output format (2.1 standard format)
- [ ] Phase completion confirmation output

### Image Readiness (at least one must be satisfied)

- [ ] All images saved to `project/images/` directory
- [ ] Or: User clearly informed to self-generate using `image_prompts.md`

### Pipeline Flow

- [ ] User prompted to proceed to next step (switch to Executor role)

> **Critical check**: If `images/image_prompts.md` was not created, or the output format does not comply with 2.1 standard, the task is NOT complete.

### Completion Confirmation Output Format

```markdown
## Image_Generator Phase Complete

- [x] Created prompt document `project/images/image_prompts.md`
- [x] Generated optimized prompts for X images
- [x] All images saved to `images/` directory
- [x] Updated image resource list status

**Image Status Summary**:

| Filename | Type | Dimensions | Status |
|----------|------|-----------|--------|
| cover_bg.png | Background | 1920x1080 | Generated |

**Next step**: Switch to Executor role to begin SVG generation
```
