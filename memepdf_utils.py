import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A6
import io
from PIL import Image
import requests
from reportlab.lib.utils import ImageReader

def create_10x15_meme_pdf(user_name="PlaceholderName", meme_text=""):
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

    # Feste Bild-URL als Platzhalter
    image_url = "https://help.blackbit.com/hubfs/hilfe.blackbit.de/wordpress%20bild%20aus%20url%20hinzufuegen%201.png"

    try:
        # Bild von URL herunterladen
        response = requests.get(image_url)
        response.raise_for_status()  # Wirft eine Ausnahme für HTTP-Fehler

        img = Image.open(io.BytesIO(response.content))

        # Bild in RGB-Modus konvertieren (falls es im CMYK-Modus ist)
        if img.mode == 'CMYK':
            img = img.convert('RGB')

        # Seitenverhältnis des Bildes berechnen
        img_ratio = img.width / img.height

        # Bildgröße unter Beibehaltung des Seitenverhältnisses berechnen
        if max_width / max_height > img_ratio:
            # Höhe ist der begrenzende Faktor
            image_height = max_height
            image_width = image_height * img_ratio
        else:
            # Breite ist der begrenzende Faktor
            image_width = max_width
            image_height = image_width / img_ratio

        # Bildposition berechnen
        x = (page_width - image_width) / 2  # Zentriert horizontal
        y = page_height - max_height - margin  # Oben mit Rand

        # Bild in PDF einfügen
        img_reader = ImageReader(img)
        c.drawImage(img_reader, x, y, width=image_width, height=image_height)

    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Herunterladen des Bildes: {e}")
        # Hier könnten Sie ein Platzhalterbild oder eine Fehlermeldung einfügen
    except Exception as e:
        print(f"Fehler beim Verarbeiten des Bildes: {e}")
        # Hier könnten Sie ein Platzhalterbild oder eine Fehlermeldung einfügen

    # Memetext hinzufügen
    c.setFillColorRGB(0, 0, 0)  # Schwarz
    c.setFont("Helvetica", 14)
    text_width = c.stringWidth(meme_text, "Helvetica", 14)
    c.drawString((page_width - text_width) / 2, y - 1*cm, meme_text)

    # Namen hinzufügen
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
    c.setFont("Helvetica", 8)  # Schriftart und -größe
    name_text = f"created by: {user_name}"
    text_width = c.stringWidth(name_text, "Helvetica", 8)
    c.drawString(page_width - text_width - margin, margin, name_text)

    c.save()
    buffer.seek(0)
    return buffer