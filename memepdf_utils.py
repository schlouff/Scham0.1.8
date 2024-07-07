import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A6
import io
from PIL import Image
import requests
from reportlab.lib.utils import ImageReader


def create_placeholder_image(width, height):
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    return img


def create_10x15_meme_pdf(user_name="PlaceholderName", meme_text="", image_url=None):
    buffer = io.BytesIO()

    # 10x15 cm Seitengröße
    page_width = 10 * cm
    page_height = 15 * cm

    c = canvas.Canvas(buffer, pagesize=(page_width, page_height), pdfVersion=(1, 5))

    # Metadaten hinzufügen
    c.setTitle("Generated Meme PDF")
    c.setAuthor("Automated System")
    c.setSubject("Meme PDF")

    # Berechnung der Bildgröße und Position
    margin = 0.5 * cm  # Schmaler Rand von 5mm
    max_width = page_width - 2 * margin
    max_height = page_height * 0.7  # Maximale Höhe des Bildes (70% der Seitenhöhe)

    # Bildposition berechnen
    x = margin
    y = page_height - max_height - margin

    if image_url:
        try:
            # Bild von URL herunterladen
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            # Bild in RGB-Modus konvertieren (falls es im CMYK-Modus ist)
            if img.mode == 'CMYK':
                img = img.convert('RGB')

            # Bild skalieren
            img.thumbnail((int(max_width), int(max_height)))
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            img = create_placeholder_image(int(max_width), int(max_height))
    else:
        img = create_placeholder_image(int(max_width), int(max_height))

    # Bild in PDF einfügen
    img_reader = ImageReader(img)
    c.drawImage(img_reader, x, y, width=img.width, height=img.height)

    # Memetext hinzufügen
    c.setFillColorRGB(0, 0, 0)  # Schwarz
    c.setFont("Helvetica", 14)
    text_width = c.stringWidth(meme_text, "Helvetica", 14)
    c.drawString((page_width - text_width) / 2, y - 1 * cm, meme_text)

    # Namen hinzufügen
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
    c.setFont("Helvetica", 8)  # Schriftart und -größe
    name_text = f"created by: {user_name}"
    text_width = c.stringWidth(name_text, "Helvetica", 8)
    c.drawString(page_width - text_width - margin, margin, name_text)

    c.save()
    buffer.seek(0)
    return buffer