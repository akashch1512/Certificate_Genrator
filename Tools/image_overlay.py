from PIL import Image, ImageDraw, ImageFont
import os


def generate_certificate(template_path, output_path, user, signs_dir=None):
    """
    Generate a certificate by overlaying user details and available signatures.

    :param template_path: Path to certificate template image
    :param output_path: Path where the generated certificate will be saved
    :param user: Dict with keys 'id', 'fname', 'lname', 'year'
    :param signs_dir: Directory containing signature images (optional)
    :return: path to saved certificate image
    """
    # Load template
    template = Image.open(template_path).convert("RGBA")
    canvas = Image.new("RGBA", template.size)
    canvas.paste(template, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Compose name (no year as requested)
    full_name = f"{user.get('fname', '')} {user.get('lname', '')}".strip()
    full_name = full_name.title()
    # Basic positioning heuristics: center name horizontally
    w, h = canvas.size

    # Choose font sizes relative to image width so text scales across devices
    def _load_font(preferred, size):
        for p in preferred:
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
        try:
            return ImageFont.truetype("arial.ttf", size=size)
        except Exception:
            return ImageFont.load_default()

    base_font_size = max(36, w // 18)  # ~5-6% of width
    small_font_size = max(18, w // 40)
    preferred_fonts = ["static/fonts/AlexBrush-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"]
    font = _load_font(preferred_fonts, base_font_size)
    small_font = _load_font(preferred_fonts, small_font_size)

    # Helper to get text size in a Pillow-version-safe way
    def _text_size(draw_obj, text, font_obj):
        try:
            # Pillow >= 8: textbbox is available
            bbox = draw_obj.textbbox((0, 0), text, font=font_obj)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            try:
                return font_obj.getsize(text)
            except Exception:
                # Last resort: approximate
                return (len(text) * 10, 20)

    # Name
    name_w, name_h = _text_size(draw, full_name, font)
    name_x = (w - name_w) // 2
    name_y = int(h * 0.40)  # 45% down the image
    draw.text((name_x, name_y), full_name, fill=(0, 0, 0), font=font)

    # (Year removed intentionally)

    # Signature overlay removed: signatures should be embedded in the template image itself.

    # Save result as PNG (preserve transparency flattened to white background)
    final = Image.new("RGB", canvas.size, (255, 255, 255))
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == 'RGBA' else None)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.save(output_path, format="PNG")

    return output_path


def convert_png_to_pdf(png_path, pdf_path):
    """Convert a PNG image to a single-page PDF using Pillow.

    :param png_path: input PNG file
    :param pdf_path: output PDF file
    :return: pdf_path
    """
    img = Image.open(png_path).convert('RGB')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    img.save(pdf_path, "PDF", resolution=100.0)
    return pdf_path
