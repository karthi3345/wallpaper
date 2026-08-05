"""
AI Wallpaper Generation Service — powered by Mistral AI.
Uses Mistral's image_generation tool (Flux via Black Forest Labs) to
generate high-quality images from text prompts with category-based
style enhancement.

Mistral handles image generation internally via its tool system —
we send a chat completion with the image_generation tool enabled,
and the response includes the generated image URL.
"""
import base64
import os

import requests

# ── Mistral AI Config ─────────────────────────────────────────────────
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', '')
MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'
MISTRAL_MODEL = os.environ.get('MISTRAL_MODEL', 'mistral-medium-latest')

# Default negative prompt applied to ALL generations (can be extended by user)
DEFAULT_NEGATIVE_PROMPT = (
    'blurry, low quality, pixelated, distorted, deformed, '
    'watermark, signature, text, logo, border, frame, '
    'extra limbs, disfigured, ugly, duplicate, cropped'
)


# ── Category Definitions ──────────────────────────────────────────────
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


def _extract_image_url(data):
    """
    Extract the generated image URL from Mistral's multi-completion response.
    The response structure is:
      choices[0].messages[] — array of messages including tool calls and results.
    The image URL appears in either:
      1. A tool result message's content (JSON with "url" key)
      2. An assistant message's content array with type "image_url"
    """
    for choice in data.get('choices', []):
        messages = choice.get('messages', [])
        for msg in messages:
            # Check tool result messages for image URL
            content = msg.get('content', '')
            if isinstance(content, str) and content:
                try:
                    import json
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and parsed.get('url'):
                        return parsed['url']
                except (ValueError, TypeError):
                    pass

            # Check assistant messages with content array (image_url type)
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'image_url':
                            img_url = block.get('image_url', '')
                            if isinstance(img_url, dict):
                                return img_url.get('url', '')
                            return img_url

        # Fallback: check choice.message (single-message format)
        single_msg = choice.get('message', {})
        single_content = single_msg.get('content', '')
        if isinstance(single_content, list):
            for block in single_content:
                if isinstance(block, dict) and block.get('type') == 'image_url':
                    img_url = block.get('image_url', '')
                    if isinstance(img_url, dict):
                        return img_url.get('url', '')
                    return img_url

    return None


def generate_image(user_prompt, category_key, size='1024x1024', negative_prompt=''):
    """
    Generate an image via Mistral AI's image_generation tool.
    Returns (b64_string, error_message).
    On success b64_string is a base64-encoded image; on failure it is None.
    """
    if not MISTRAL_API_KEY:
        return None, (
            'Mistral AI API key not configured. '
            'Set MISTRAL_API_KEY environment variable.'
        )

    final_prompt = classify_prompt(user_prompt, category_key)
    final_negative = build_negative_prompt(negative_prompt, category_key)

    # Build the prompt for Mistral — include negative prompt in the text
    # since the image_generation tool doesn't have a separate negative field
    full_instruction = f'Generate an image: {final_prompt}'
    if final_negative:
        full_instruction += f'\nAvoid: {final_negative}'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
    }

    payload = {
        'model': MISTRAL_MODEL,
        'tools': [{'type': 'image_generation'}],
        'messages': [
            {
                'role': 'user',
                'content': full_instruction,
            }
        ],
    }

    try:
        resp = requests.post(
            MISTRAL_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout:
        return None, 'The image generation timed out. Please try again.'
    except requests.exceptions.ConnectionError:
        return None, 'Could not connect to Mistral AI. Please try again.'

    if resp.status_code != 200:
        try:
            err_data = resp.json()
            err_msg = err_data.get('message', '') or err_data.get('detail', '')
            if err_msg:
                return None, f'Mistral AI error: {err_msg}'
        except (ValueError, KeyError):
            pass
        return None, f'Mistral AI error (HTTP {resp.status_code}). Please try again.'

    try:
        data = resp.json()
    except (ValueError, KeyError):
        return None, 'Unexpected response from Mistral AI. Please try again.'

    # Extract image URL from the response
    image_url = _extract_image_url(data)
    if not image_url:
        return None, 'No image was generated. Please try again with a different description.'

    # Download the image and convert to base64
    try:
        img_resp = requests.get(image_url, timeout=30)
        if img_resp.status_code == 200:
            b64 = base64.b64encode(img_resp.content).decode('ascii')
            return b64, None
    except requests.exceptions.RequestException:
        pass

    return None, 'Failed to download generated image. Please try again.'
