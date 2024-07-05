import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A6
import io
from PIL import Image
import requests
from reportlab.lib.utils import ImageReader

def create_10x15_pdf_with_image(image_url, user_name):
    buffer = io.BytesIO()

    # 10x15 cm Seitengröße
    # 10x15 cm Seitengröße
    page_width = 10 * cm
    page_height = 15 * cm

    c = canvas.Canvas(buffer, pagesize=(page_width, page_height), pdfVersion=(1, 5))

    # Metadaten hinzufügen
    c.setTitle("Generated Image PDF")
    c.setAuthor("Automated System")
    c.setSubject("Image PDF")

    # Berechnung der Bildgröße und Position
    margin = 0.5 * cm  # Schmaler Rand von 5mm
    max_width = page_width - 2 * margin
    max_height = page_height * 0.7  # Maximale Höhe des Bildes (70% der Seitenhöhe)

    # Bild von URL herunterladen
    response = requests.get(image_url)
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
    y = page_height - image_height - margin  # Oben mit Rand

    # Bild in PDF einfügen
    img_reader = ImageReader(img)
    c.drawImage(img_reader, x, y, width=image_width, height=image_height)

    # Namen hinzufügen
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
    c.setFont("Helvetica", 8)  # Schriftart und -größe
    name_text = f"created by: {user_name}"
    text_width = c.stringWidth(name_text, "Helvetica", 8)
    c.drawString(page_width - text_width - margin, margin, name_text)

    c.save()
    buffer.seek(0)
    return buffer

# st.title('A6 PDF Creator mit quadratischem Bild')
#
# # Eingabefeld für Bild-URL
# image_url = st.text_input("Geben Sie die URL eines Bildes ein:")
#
# if st.button('PDF erstellen und herunterladen') and image_url:
#     try:
#         pdf = create_a6_pdf_with_image(image_url)
#         st.download_button(
#             label="A6 PDF herunterladen",
#             data=pdf,
#             file_name="a6_pdf_mit_bild.pdf",
#             mime="application/pdf"
#         )
#     except Exception as e:
#         st.error(f"Fehler beim Erstellen des PDFs: {str(e)}")