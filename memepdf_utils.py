from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A6
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests
import io
import os


def create_placeholder_image(width, height):
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    return img


def create_10x15_meme_pdf(user_name="PlaceholderName", meme_text="", image_url=None):
    buffer = io.BytesIO()
    page_width = 10 * cm
    page_height = 15 * cm
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height), pdfVersion=(1, 5))

    margin = 0.5 * cm
    max_width = page_width - 2 * margin
    max_height = page_height * 0.7

    if image_url:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode == 'CMYK':
                img = img.convert('RGB')

            img_ratio = img.width / img.height

            if max_width / max_height > img_ratio:
                image_height = max_height
                image_width = image_height * img_ratio
            else:
                image_width = max_width
                image_height = image_width / img_ratio

            x = (page_width - image_width) / 2
            y = page_height - image_height - margin

            img_reader = ImageReader(img)
            c.drawImage(img_reader, x, y, width=image_width, height=image_height)
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            img = create_placeholder_image(int(max_width), int(max_height))
            c.drawImage(ImageReader(img), margin, y, width=max_width, height=max_height)

    # Memetext hinzufügen (mehrzeilig)
    c.setFillColorRGB(0, 0, 0)  # Schwarz

    # Überprüfen und registrieren der Schriftart
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('LiberationSans', font_path))
        font_name = 'LiberationSans'
    else:
        font_name = 'Helvetica'  # Fallback auf eine Standardschriftart

    c.setFont(font_name, 14)

    # Text in Zeilen aufteilen
    words = meme_text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if c.stringWidth(test_line, font_name, 14) <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    # Maximale Anzahl von Zeilen begrenzen
    max_lines = 5
    if len(lines) > max_lines:
        lines = lines[:max_lines - 1] + ['...']

    # Text zentriert zeichnen
    line_height = 20  # Zeilenhöhe
    text_height = len(lines) * line_height
    start_y = y - 1 * cm - line_height  # Startposition für den Text

    for i, line in enumerate(lines):
        text_width = c.stringWidth(line, font_name, 14)
        x = (page_width - text_width) / 2
        c.drawString(x, start_y - i * line_height, line)

    # Namen hinzufügen
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
    c.setFont(font_name, 8)
    name_text = f"created by: {user_name}"
    text_width = c.stringWidth(name_text, font_name, 8)
    c.drawString(page_width - text_width - margin, margin, name_text)

    c.save()
    buffer.seek(0)
    return buffer