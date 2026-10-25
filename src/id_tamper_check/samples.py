"""Synthetic, clearly fictional ID-card specimens for demos and tests.

Nothing here resembles a real issuer's document: every card is labeled
SPECIMEN, the issuer is fictional, and all personal data is made up.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CARD_SIZE = (856, 540)  # ISO/IEC 7810 ID-1 aspect ratio at 10 px/mm
INK = (28, 36, 52)
ACCENT = (22, 92, 140)


@dataclass(frozen=True)
class SpecimenFields:
    name: str = "JANE Q. SAMPLE"
    date_of_birth: str = "14 MAR 1991"
    document_number: str = "X 0482 1937"
    expiry: str = "31 DEC 2031"
    nationality: str = "UTOPIAN"
    hair: str = "short"


def render_specimen(fields: SpecimenFields | None = None) -> np.ndarray:
    """Draw a fictional ID card as an RGB ``uint8`` array."""
    fields = fields or SpecimenFields()
    width, height = CARD_SIZE
    card = Image.fromarray(_guilloche(width, height))
    draw = ImageDraw.Draw(card)

    draw.rounded_rectangle((0, 0, width - 1, 92), radius=0, fill=ACCENT)
    draw.text((32, 18), "REPUBLIC OF UTOPIA", font=_font(34), fill=(255, 255, 255))
    draw.text(
        (34, 60), "SPECIMEN IDENTITY CARD  ·  NOT A REAL DOCUMENT", font=_font(17), fill=(205, 225, 240)
    )

    _draw_portrait(draw, (40, 120, 260, 400), fields.hair)

    rows = [
        ("NAME", fields.name),
        ("DATE OF BIRTH", fields.date_of_birth),
        ("NATIONALITY", fields.nationality),
        ("DOCUMENT NO.", fields.document_number),
        ("EXPIRES", fields.expiry),
    ]
    for index, (label, value) in enumerate(rows):
        y = 124 + index * 56
        draw.text((300, y), label, font=_font(15), fill=ACCENT)
        draw.text((300, y + 18), value, font=_font(28), fill=INK)

    draw.text((40, 430), "IDUTO<<SAMPLE<<JANE<Q<<<<<<<<<<<<<<<<<", font=_font(24), fill=INK)
    draw.text((40, 466), "X04821937<9UTO9103145F3112319<<<<<<<<<", font=_font(24), fill=INK)
    _stamp_watermark(card)
    return np.asarray(card)


def specimen_pair(capture: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(reference, tampered)`` specimens.

    The tampered copy has an altered date of birth, document number and
    portrait. With ``capture=True`` it is also rotated, scaled, shifted and
    relit to look like a handheld phone photo, which needs ``align=True``.
    """
    reference_fields = SpecimenFields()
    tampered_fields = replace(
        reference_fields,
        date_of_birth="14 MAR 1981",
        document_number="X 0482 7731",
        hair="long",
    )
    reference = render_specimen(reference_fields)
    tampered = render_specimen(tampered_fields)
    if capture:
        tampered = simulate_capture(tampered)
    return reference, tampered


def simulate_capture(card: np.ndarray, angle: float = -7.0, seed: int = 0) -> np.ndarray:
    """Place ``card`` on a desk at an angle with uneven lighting and sensor noise."""
    height, width = card.shape[:2]
    canvas_size = (round(width * 1.35), round(height * 1.45))
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 0.92)
    matrix[:, 2] += ((canvas_size[0] - width) / 2, (canvas_size[1] - height) / 2)
    photo = cv2.warpAffine(card, matrix, canvas_size, flags=cv2.INTER_CUBIC, borderValue=(118, 96, 74))

    gradient = np.linspace(0.88, 1.05, canvas_size[0], dtype=np.float32)[None, :, None]
    noise = np.random.default_rng(seed).normal(0, 2.0, photo.shape).astype(np.float32)
    return np.clip(photo.astype(np.float32) * gradient + noise, 0, 255).astype(np.uint8)


def _guilloche(width: int, height: int) -> np.ndarray:
    """Pale interlaced sine waves, a nod to the fine-line security printing on real cards."""
    background = np.full((height, width, 3), (246, 243, 236), dtype=np.uint8)
    xs = np.arange(width, dtype=np.float32)
    for index in range(26):
        phase = index * 0.45
        amplitude = 12 + 6 * math.sin(index)
        ys = height / 2 + (index - 13) * 18 + amplitude * np.sin(xs / 38 + phase)
        points = np.stack([xs, ys], axis=1).astype(np.int32).reshape(-1, 1, 2)
        color = (205, 218, 226) if index % 2 else (226, 214, 200)
        cv2.polylines(background, [points], False, color, 1, cv2.LINE_AA)
    return background


def _draw_portrait(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], hair: str) -> None:
    left, top, right, bottom = box
    draw.rectangle(box, fill=(214, 224, 232), outline=ACCENT, width=3)
    center_x = (left + right) // 2
    if hair == "long":
        draw.rounded_rectangle(
            (center_x - 62, top + 34, center_x + 62, top + 210), radius=50, fill=(92, 62, 40)
        )
    draw.ellipse((center_x - 75, top + 175, center_x + 75, bottom + 60), fill=(60, 84, 120))
    draw.ellipse((center_x - 48, top + 52, center_x + 48, top + 172), fill=(226, 190, 160))
    draw.chord((center_x - 50, top + 40, center_x + 50, top + 120), 180, 360, fill=(70, 48, 32))
    draw.rectangle((left, bottom, right, bottom + 60), fill=(246, 243, 236))
    draw.rectangle(box, outline=ACCENT, width=3)


def _stamp_watermark(card: Image.Image) -> None:
    layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((420, 300), "SPECIMEN", font=_font(64), fill=(180, 40, 40, 70), anchor="mm")
    layer = layer.rotate(18, center=(420, 300))
    card.paste(Image.alpha_composite(card.convert("RGBA"), layer).convert("RGB"))


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)
