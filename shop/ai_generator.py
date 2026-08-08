"""
AI Wallpaper Generation Service — powered by Cloudflare Workers AI.
Ultra-optimized for minimal neuron usage to serve many users within
the 10,000 neuron/day free tier.

Strategy:
  - Generate at 512×512 with 1 diffusion step = ~261 neurons/image
  - Supports ~38 generations/day on free tier
  - Upscale client-side via CSS if user requests larger sizes
  - Multi-provider fallback: Cloudflare → Pollinations → retry queue
"""
import base64
import os
import time

import requests
from django.conf import settings

# ── Cloudflare Workers AI Config ──────────────────────────────────────
CF_ACCOUNT_ID = os.environ.get('CF_ACCOUNT_ID', '')
CF_API_TOKEN = os.environ.get('CF_API_TOKEN', '')
CF_MODEL = '@cf/black-forest-labs/flux-1-schnell'
CF_API_URL = (
    f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}'
)

# Ultra-minimal settings: 512×512, 1 step = ~261 neurons per image
# This allows ~38 images/day on the 10,000 neuron free tier
CF_GEN_WIDTH = 512
CF_GEN_HEIGHT = 512
CF_GEN_STEPS = 1

# Default negative prompt applied to ALL generations
DEFAULT_NEGATIVE_PROMPT = (
    'blurry, low quality, pixelated, distorted, deformed, '
    'watermark, signature, text, logo, border, frame, '
    'extra limbs, disfigured, ugly, duplicate, cropped'
)


# ── Category Definitions ──────────────────────────────────────────────
# Each category has style keywords injected into the prompt so the AI
# knows exactly what aesthetic to produce.

AI_CATEGORIES = {
    'painting': {
        'label': 'AI Painting',
        'icon': '🎨',
        'description': 'Hand-painted artistic wall art — oils, watercolours, abstracts',
        'style_hint': (
            'a fine-art wall painting, visible brushstrokes, oil-on-canvas texture, '
            'gallery quality, museum lighting, expressive artistic composition'
        ),
        'suggestions': [
            'Abstract gold leaf and navy geometric composition',
            'Serene mountain landscape in soft watercolour tones',
            'Bold floral bouquet in warm earthy palette',
        ],
        'negative_hint': 'photograph, photorealistic, 3d render, digital art',
    },
    'mural': {
        'label': 'AI Wall Mural',
        'icon': '🏛️',
        'description': 'Large-scale murals — heritage, European, tropical, temple art',
        'style_hint': (
            'a grand wall mural, floor-to-ceiling scale, immersive panoramic scene, '
            'rich detailing, dramatic depth and perspective, seamless wall coverage'
        ),
        'suggestions': [
            'Tropical jungle with exotic birds and lush greenery',
            'European classical architecture with ornate columns',
            'Majestic peacock mural in royal Indian heritage style',
        ],
        'negative_hint': 'small scale, framed art, miniature, flat pattern',
    },
    'wallpaper': {
        'label': 'AI Wallpaper Roll',
        'icon': '🪞',
        'description': 'Repeat-pattern wallpaper rolls — damask, floral, geometric',
        'style_hint': (
            'a seamless repeating wallpaper pattern, tessellated design, '
            'elegant surface print, consistent lighting, roll-format, '
            'no central focal point — even pattern distribution'
        ),
        'suggestions': [
            'Luxury gold damask pattern on deep maroon',
            'Delicate cherry blossom on cream background',
            'Modern geometric hexagonal pattern in sage green',
        ],
        'negative_hint': 'single focal point, photograph, portrait, landscape scene',
    },
    'wall-art': {
        'label': 'AI Wall Art',
        'icon': '🖼️',
        'description': 'Contemporary framed art — minimal, typography, mixed media',
        'style_hint': (
            'modern wall art piece, clean composition, contemporary aesthetic, '
            'framed artwork appearance, balanced negative space, trendy colour palette'
        ),
        'suggestions': [
            'Minimalist line-art face in monochrome',
            'Boho sun and arches in terracotta tones',
            'Retro typography poster with bold colours',
        ],
        'negative_hint': 'photorealistic, busy background, cluttered composition',
    },
    'texture': {
        'label': 'AI Texture',
        'icon': '✨',
        'description': 'Textured surfaces — metallic, stone, concrete, fabric',
        'style_hint': (
            'a textured wall surface, tactile material finish, '
            'metallic / stone / concrete / linen texture, '
            'macro detail, even lighting across surface'
        ),
        'suggestions': [
            'Brushed gold metallic with subtle patina',
            'Exposed brick wall in warm terracotta',
            'Linen weave texture in soft beige',
        ],
        'negative_hint': 'illustration, cartoon, painting, abstract art',
    },
    'kids-nursery': {
        'label': 'AI Kids & Nursery',
        'icon': '🧸',
        'description': "Playful designs for children's rooms and nurseries",
        'style_hint': (
            'a whimsical nursery wallpaper design, soft pastel colours, '
            'child-friendly illustration style, cute and gentle, '
            'playful patterns suitable for a kids bedroom or nursery'
        ),
        'suggestions': [
            'Cute safari animals — giraffe, elephant, lion in pastels',
            'Dreamy hot air balloons among fluffy clouds',
            'Woodland forest with friendly foxes and trees',
        ],
        'negative_hint': 'scary, dark, horror, photorealistic, realistic texture',
    },
    '3d-mural': {
        'label': 'AI 3D Mural',
        'icon': '🌀',
        'description': 'Three-dimensional sculpted murals with depth illusion',
        'style_hint': (
            'a 3D sculpted wall mural, optical-depth illusion, raised relief panels, '
            'shadow-casting geometric forms, trompe-l\'oeil, photorealistic depth'
        ),
        'suggestions': [
            '3D lotus relief panels in warm stone tones',
            'Geometric wave pattern with dramatic shadow depth',
            'Abstract flowing organic forms in white plaster',
        ],
        'negative_hint': 'flat surface, 2d illustration, cartoon style',
    },
    'ceiling': {
        'label': 'AI Ceiling Art',
        'icon': '🌌',
        'description': 'Ceiling murals and painted ceiling designs',
        'style_hint': (
            'a ceiling mural artwork, viewed from below looking up, '
            'sistine-chapel-style grandeur, symmetrical radial composition, '
            'ornate ceiling fresco, dramatic upward perspective'
        ),
        'suggestions': [
            'Celestial sky with clouds and golden angels',
            'Art-deco geometric ceiling in gold and black',
            'Starry night cosmos with constellations',
        ],
        'negative_hint': 'floor view, ground level, side view, wall perspective',
    },
}


def classify_prompt(user_prompt, category_key):
    """
    Build the final generation prompt by combining the user's text with
    category-specific style hints.
    """
    cat = AI_CATEGORIES.get(category_key)
    if not cat:
        style = 'premium wall decor, elegant, high-quality interior design'
    else:
        style = cat['style_hint']

    return (
        f'{user_prompt.strip()}. '
        f'Styled as {style}. '
        f'High resolution, professional interior design photography, '
        f'suitable for a premium wallpaper & decor store.'
    )


def build_negative_prompt(user_negative, category_key):
    """
    Combine the default negative prompt, category-specific negative hints,
    and any user-supplied negative prompt into a single string.
    """
    cat = AI_CATEGORIES.get(category_key, {})
    parts = [DEFAULT_NEGATIVE_PROMPT]

    cat_negative = cat.get('negative_hint')
    if cat_negative:
        parts.append(cat_negative)

    user_neg = (user_negative or '').strip()
    if user_neg:
        parts.append(user_neg)

    return ', '.join(parts)


def _generate_via_cloudflare(full_prompt, final_negative):
    """
    Generate via Cloudflare Workers AI with ultra-minimal neuron settings.
    Returns (base64_string, None) on success, (None, error_msg) on failure.
    """
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return None, 'Cloudflare credentials not configured.'

    headers = {
        'Authorization': f'Bearer {CF_API_TOKEN}',
        'Content-Type': 'application/json',
    }

    payload = {
        'prompt': full_prompt,
        'width': CF_GEN_WIDTH,
        'height': CF_GEN_HEIGHT,
        'num_steps': CF_GEN_STEPS,   # 1 step = minimal neurons
    }

    if final_negative:
        payload['negative_prompt'] = final_negative

    try:
        resp = requests.post(CF_API_URL, headers=headers, json=payload, timeout=90)
    except requests.exceptions.Timeout:
        return None, None  # fallback to next provider
    except requests.exceptions.ConnectionError:
        return None, None

    if resp.status_code == 429:
        # Rate limit / daily limit exhausted — return None so fallback kicks in
        return None, None

    if resp.status_code != 200:
        try:
            err_data = resp.json()
            cf_errors = err_data.get('errors', [])
            if cf_errors:
                msg = cf_errors[0].get('message', '')
                if 'authentication' in msg.lower():
                    return None, None  # auth issue — try fallback
        except (ValueError, KeyError):
            pass
        return None, None  # any error — try fallback

    # Cloudflare returns binary image (image/png)
    content_type = resp.headers.get('Content-Type', '')

    if 'image' in content_type:
        b64 = base64.b64encode(resp.content).decode('ascii')
        return b64, None

    # JSON response with base64
    try:
        data = resp.json()
        if data.get('success') and data.get('result'):
            result = data['result']
            if isinstance(result, dict) and result.get('image'):
                img_b64 = result['image']
                if img_b64.startswith('data:image'):
                    img_b64 = img_b64.split(',', 1)[-1]
                return img_b64, None
    except (ValueError, KeyError):
        pass

    return None, None


def _generate_via_pollinations(full_prompt, final_negative):
    """
    Fallback: Pollinations.ai free image generation.
    Returns (base64_string, None) on success, (None, None) on failure.
    """
    from urllib.parse import quote

    # Combine prompt with negatives
    prompt_text = full_prompt
    if final_negative:
        prompt_text = f'{full_prompt}. Avoid: {final_negative}'

    url = (
        f'https://image.pollinations.ai/prompt/{quote(prompt_text[:500])}'
        f'?width=512&height=512&nologo=true&seed={int(time.time()) % 100000}'
    )

    try:
        resp = requests.get(url, timeout=90)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return None, None

    if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
        b64 = base64.b64encode(resp.content).decode('ascii')
        return b64, None

    return None, None


def generate_image(user_prompt, category_key, size='1024x1024', negative_prompt=''):
    """
    Main entry point. Generate an image with minimal neuron usage.
    Always generates at 512×512 internally (saves neurons), the display
    size is handled by CSS on the frontend.

    Fallback chain: Cloudflare (minimal neurons) → Pollinations (free)

    Returns (b64_string, error_message).
    """
    final_prompt = classify_prompt(user_prompt, category_key)
    final_negative = build_negative_prompt(negative_prompt, category_key)

    # ── Provider 1: Cloudflare Workers AI (ultra-minimal neurons) ──
    b64, _ = _generate_via_cloudflare(final_prompt, final_negative)
    if b64:
        return b64, None

    # ── Provider 2: Pollinations.ai (free fallback) ──
    b64, _ = _generate_via_pollinations(final_prompt, final_negative)
    if b64:
        return b64, None

    # ── All providers failed ──
    return None, (
        'Image generation is temporarily busy. Our AI providers have reached '
        'their daily limit. Please try again in a few hours — '
        'the limit resets daily. Thank you for your patience!'
    )
