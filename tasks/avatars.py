"""Bounded image decoding; never store the untrusted original bytes or name."""
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _

MAX_AVATAR_BYTES = 2 * 1024 * 1024


def normalize_avatar(upload):
    if upload.size > MAX_AVATAR_BYTES:
        raise ValidationError(_('Choose an image no larger than 2 MB.'))
    if Path(upload.name).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise ValidationError(_('Choose a valid JPG, PNG or WebP image.'))
    data = upload.read(MAX_AVATAR_BYTES + 1)
    if len(data) > MAX_AVATAR_BYTES:
        raise ValidationError(_('Choose an image no larger than 2 MB.'))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'} or max(image.size) > 4096:
                    raise ValueError('Unsupported format or dimensions')
                image.verify()
            with Image.open(BytesIO(data)) as image:
                image.load()  # Fully decode, including truncated-file checks.
                image = ImageOps.exif_transpose(image)
                image.thumbnail((512, 512))
                # Fresh pixel buffer strips EXIF, text, animation and trailing payloads.
                pixels = Image.new('RGBA', image.size)
                pixels.paste(image.convert('RGBA'))
                output = BytesIO()
                pixels.save(output, format='PNG')
        return ContentFile(output.getvalue(), name='avatar.png')
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
        raise ValidationError(_('Choose a valid JPG, PNG or WebP image (up to 4096 pixels per side).')) from error
