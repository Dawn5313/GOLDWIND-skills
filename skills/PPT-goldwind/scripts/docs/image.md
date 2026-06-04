# Image Tools

Image tools cover prompt-based generation, image inspection, and Gemini watermark removal.

## `image_gen.py`

Unified image generation entry point. By default it uses `image2`, the bundled GPT Image 2 backend that reads the active provider from the user's Codex root config.

```bash
python3 scripts/image_gen.py "A modern futuristic workspace"
python3 scripts/image_gen.py "Abstract tech background" --aspect_ratio 16:9 --image_size 2K
python3 scripts/image_gen.py "Concept car" -o projects/demo/images
python3 scripts/image_gen.py "Beautiful landscape" -n "low quality, blurry, watermark"
python3 scripts/image_gen.py --list-backends
```

Backends are grouped into Core / Extended / Experimental tiers. Run `python3 scripts/image_gen.py --list-backends` for the current list.

Backend selection:

```bash
python3 scripts/image_gen.py "A Goldwind technical architecture visual" --backend image2
python3 scripts/image_gen.py "A cat" --backend openai
python3 scripts/image_gen.py "A cinematic portrait" --backend minimax
python3 scripts/image_gen.py "A product launch hero image" --backend qwen
python3 scripts/image_gen.py "科技感背景图" --backend zhipu
python3 scripts/image_gen.py "A product KV in cinematic style" --backend volcengine
```

Configuration sources:

1. Current process environment variables
2. Repo-root `.env` as a fallback

If no backend is selected, `image_gen.py` defaults to `image2`.

Default `image2` configuration:

```text
~/.codex/auth.json: OPENAI_API_KEY
~/.codex/config.toml: active model_provider and provider base_url
```

Optional `.env` overrides:

```env
IMAGE_BACKEND=image2
IMAGE2_MODEL=gpt-image-2
# IMAGE2_BASE_URL=https://provider.example/v1
# IMAGE2_API_KEY_ENV=API_IMAGE_API_KEY
# IMAGE2_TIMEOUT=1800
# IMAGE2_QUALITY=high
```

Example `.env` for Gemini:

```env
IMAGE_BACKEND=gemini
GEMINI_API_KEY=your-api-key
GEMINI_BASE_URL=https://your-proxy-url.com/v1beta
GEMINI_MODEL=gemini-3.1-flash-image-preview
```

Example process environment:

```bash
export IMAGE_BACKEND=gemini
export GEMINI_API_KEY=your-api-key
export GEMINI_MODEL=gemini-3.1-flash-image-preview
```

Current process environment wins over `.env`.

Use provider-specific keys only (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`). See `.env.example` for the full list per backend.

`IMAGE_API_KEY`, `IMAGE_MODEL`, and `IMAGE_BASE_URL` are intentionally unsupported.

If you keep multiple providers in one `.env` or environment, `IMAGE_BACKEND` explicitly selects the active provider. If unset, `image2` is selected.

Recommendation:
- Default to the Core tier for routine PPT work
- Prefer `image2` / `gpt-image-2` for Goldwind PPT raster assets
- Use Extended only when you need a specific model style
- Treat Experimental backends as opt-in

Example `.env` for MiniMax image backend:

```env
IMAGE_BACKEND=minimax
MINIMAX_API_KEY=your-api-key
# Optional: override base URL (defaults to https://api.minimaxi.com, domestic China endpoint)
# Use https://api.minimax.io for overseas access
# MINIMAX_BASE_URL=https://api.minimax.io
# MINIMAX_MODEL=image-01
```

## `analyze_images.py`

Analyze images in a project directory before writing the design spec or composing slide layouts.

```bash
python3 scripts/analyze_images.py <project_path>/images
```

Use this instead of opening image files directly when following the project workflow.

## `api_image_generate.py`

Low-level GPT Image 2 provider tool copied from `api-image`. Use it when the PPT workflow needs reference images, image edits, masks, or composition/style transfer.

```bash
python3 scripts/api_image_generate.py \
  --prompt "Generate a content-rich Goldwind-style architecture visual; preserve the reference flow direction, show module hierarchy and status indicators, and keep final Chinese labels editable in PPT." \
  --image project/images/reference.png \
  --image-role "architecture structure reference" \
  --size 2048x1152 \
  --quality high \
  --out project/images/architecture_base.png
```

## `gemini_watermark_remover.py`

Remove Gemini watermark assets after manual download.

```bash
python3 scripts/gemini_watermark_remover.py <image_path>
python3 scripts/gemini_watermark_remover.py <image_path> -o output_path.png
python3 scripts/gemini_watermark_remover.py <image_path> -q
```

Notes:
- Requires `scripts/assets/bg_48.png` and `scripts/assets/bg_96.png`
- Best used after downloading “full size” Gemini images

Dependencies:

```bash
pip install Pillow numpy
```
