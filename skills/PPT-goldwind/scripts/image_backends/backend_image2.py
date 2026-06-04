#!/usr/bin/env python3
"""
GPT Image 2 backend using the Codex provider configuration.

This backend is the default PPT raster asset generator. It reads the active
provider from the user's Codex root files, matching the standalone api-image
skill behavior:

  ~/.codex/auth.json    -> OPENAI_API_KEY
  ~/.codex/config.toml  -> model_provider and provider base_url

Optional process or repo .env overrides:
  IMAGE2_MODEL
  IMAGE2_CODEX_HOME
  IMAGE2_BASE_URL
  IMAGE2_API_KEY_ENV
  IMAGE2_API_KEY
  IMAGE2_TIMEOUT
  IMAGE2_QUALITY
  IMAGE2_OUTPUT_FORMAT
  IMAGE2_BACKGROUND
  IMAGE2_MODERATION
  IMAGE2_DEFAULT_NEGATIVE_PROMPT
"""

from __future__ import annotations

import os
import time

from image_backends.backend_common import (
    MAX_RETRIES,
    is_rate_limit_error,
    normalize_image_size,
    resolve_output_path,
    retry_delay,
    save_image_bytes,
)
from provider_imagegen.config import load_provider_config, resolve_codex_home
from provider_imagegen.http_client import GENERATION_SUFFIX, extract_images, post_json


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_TIMEOUT = 1800
DEFAULT_NEGATIVE_PROMPT = (
    "fake readable text, pseudo letters, random fact numbers, UI gibberish, "
    "fake chart values, watermark, signature, logo, brand mark, cluttered tiny labels, "
    "dark command-center dashboard, neon glow, cinematic black background, oversized blue gradient, "
    "dense sci-fi UI screens, hollow blank framework, empty template with no business content"
)

VALID_ASPECT_RATIOS = [
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
]

ASPECT_RATIO_SIZE_MAP = {
    "512px": {
        "1:1": "1024x1024",
        "2:3": "768x1152",
        "3:2": "1152x768",
        "3:4": "864x1152",
        "4:3": "1152x864",
        "4:5": "896x1120",
        "5:4": "1120x896",
        "9:16": "720x1280",
        "16:9": "1280x720",
        "21:9": "1344x576",
    },
    "1K": {
        "1:1": "1536x1536",
        "2:3": "1024x1536",
        "3:2": "1536x1024",
        "3:4": "1152x1536",
        "4:3": "1536x1152",
        "4:5": "1216x1536",
        "5:4": "1536x1216",
        "9:16": "896x1600",
        "16:9": "1600x896",
        "21:9": "1792x768",
    },
    "2K": {
        "1:1": "2048x2048",
        "2:3": "1360x2048",
        "3:2": "2048x1360",
        "3:4": "1536x2048",
        "4:3": "2048x1536",
        "4:5": "1792x2240",
        "5:4": "2240x1792",
        "9:16": "1152x2048",
        "16:9": "2048x1152",
        "21:9": "2688x1152",
    },
    "4K": {
        "1:1": "2880x2880",
        "2:3": "2352x3520",
        "3:2": "3520x2352",
        "3:4": "2448x3264",
        "4:3": "3264x2448",
        "4:5": "2560x3200",
        "5:4": "3200x2560",
        "9:16": "2160x3840",
        "16:9": "3840x2160",
        "21:9": "3840x1648",
    },
}

IMAGE_SIZE_TO_QUALITY = {
    "512px": "low",
    "1K": "medium",
    "2K": "high",
    "4K": "high",
}


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _resolve_timeout() -> int | None:
    raw_timeout = _env("IMAGE2_TIMEOUT")
    if raw_timeout is None:
        return DEFAULT_TIMEOUT
    timeout = int(raw_timeout)
    if timeout < 0:
        raise ValueError("IMAGE2_TIMEOUT must be 0 or a positive integer.")
    return None if timeout == 0 else timeout


def _resolve_size(aspect_ratio: str, image_size: str) -> str:
    normalized = normalize_image_size(image_size)
    size = (ASPECT_RATIO_SIZE_MAP.get(normalized) or {}).get(aspect_ratio)
    if size:
        return size
    raise ValueError(
        f"Unsupported aspect ratio '{aspect_ratio}' or image size '{image_size}' "
        f"for image2. Supported ratios: {VALID_ASPECT_RATIOS}; sizes: {list(ASPECT_RATIO_SIZE_MAP)}"
    )


def _resolve_quality(image_size: str) -> str:
    override = _env("IMAGE2_QUALITY")
    if override:
        return override.lower()
    return IMAGE_SIZE_TO_QUALITY.get(normalize_image_size(image_size), "high")


def _default_negative_prompt() -> str:
    return _env("IMAGE2_DEFAULT_NEGATIVE_PROMPT") or DEFAULT_NEGATIVE_PROMPT


def _build_prompt(prompt: str, negative_prompt: str | None) -> str:
    avoid_parts = [part for part in (_default_negative_prompt(), negative_prompt) if part]
    if not avoid_parts:
        return prompt
    return f"{prompt}\n\nAvoid the following: {'; '.join(avoid_parts)}"


def _output_extension(output_format: str) -> str:
    if output_format == "jpeg":
        return ".jpg"
    return f".{output_format}"


def _generate_image(
    prompt: str,
    negative_prompt: str = None,
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
    output_dir: str = None,
    filename: str = None,
    model: str = DEFAULT_MODEL,
) -> str:
    final_prompt = _build_prompt(prompt, negative_prompt)
    size = _resolve_size(aspect_ratio, image_size)
    quality = _resolve_quality(image_size)
    output_format = (_env("IMAGE2_OUTPUT_FORMAT") or "png").lower()
    timeout = _resolve_timeout()

    codex_home = resolve_codex_home(_env("IMAGE2_CODEX_HOME"))
    provider = load_provider_config(
        codex_home,
        base_url_override=_env("IMAGE2_BASE_URL"),
        api_key_override=_env("IMAGE2_API_KEY"),
        api_key_env=_env("IMAGE2_API_KEY_ENV"),
    )

    payload = {
        "model": model,
        "prompt": final_prompt,
        "size": size,
        "quality": quality,
        "n": 1,
        "output_format": output_format,
        "background": _env("IMAGE2_BACKGROUND"),
        "moderation": _env("IMAGE2_MODERATION"),
    }
    payload = {key: value for key, value in payload.items() if value is not None}

    print("[GPT Image 2 - Codex provider]")
    print(f"  Model:        {model}")
    print(f"  Provider URL: {provider.base_url}")
    print(f"  Prompt:       {final_prompt[:120]}{'...' if len(final_prompt) > 120 else ''}")
    print(f"  Aspect Ratio: {aspect_ratio}")
    print(f"  Resolution:   {size}")
    print(f"  Quality:      {quality}")
    print()
    print("  [..] Generating...", end="", flush=True)
    start = time.time()

    response = post_json(
        f"{provider.base_url}{GENERATION_SUFFIX}",
        provider.api_key,
        payload,
        timeout,
    )
    image_bytes = extract_images(response, timeout)[0]

    elapsed = time.time() - start
    print(f"\n  [DONE] Image generated ({elapsed:.1f}s)")

    path = resolve_output_path(prompt, output_dir, filename, _output_extension(output_format))
    return save_image_bytes(image_bytes, path)


def generate(
    prompt: str,
    negative_prompt: str = None,
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
    output_dir: str = None,
    filename: str = None,
    model: str = None,
    max_retries: int = MAX_RETRIES,
) -> str:
    """Generate one image with GPT Image 2 and retry transient failures."""
    resolved_model = model or _env("IMAGE2_MODEL") or DEFAULT_MODEL
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return _generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                output_dir=output_dir,
                filename=filename,
                model=resolved_model,
            )
        except Exception as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            limited = is_rate_limit_error(exc)
            delay = retry_delay(attempt, rate_limited=limited)
            label = "Rate limit hit" if limited else f"Error: {exc}"
            print(f"\n  [WARN] {label}. Retrying in {delay}s...")
            time.sleep(delay)

    raise RuntimeError(f"Failed after {max_retries + 1} attempts. Last error: {last_error}")
