import streamlit as st
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_sample_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 750, "Dies ist ein Test-PDF für den E-Mail-Versand via Mailgun.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def send_email(to_email, subject, content, attachment):
    return requests.post(
        f"https://api.mailgun.net/v3/{st.secrets['mailgun']['domain']}/messages",
        auth=("api", st.secrets['mailgun']['api_key']),
        files=[("attachment", ("test.pdf", attachment.getvalue()))],
        data={"from": f"Mailgun Sandbox <postmaster@{st.secrets['mailgun']['domain']}>",
              "to": to_email,
              "subject": subject,
              "text": content})

st.title("Test: PDF per E-Mail senden mit Mailgun")

# Erstelle ein Beispiel-PDF
pdf = create_sample_pdf()

# E-Mail-Adresse Eingabefeld
email = st.text_input("Empfänger E-Mail-Adresse", "christopher.schleif@gmx.de")

# Button zum Senden der E-Mail
if st.button("PDF per E-Mail senden"):
    try:
        response = send_email(email, "Test: Ihr generiertes PDF", "Hier ist Ihr Test-PDF-Dokument.", pdf)
        if response.status_code == 200:
            st.success("E-Mail wurde erfolgreich gesendet!")
        else:
            st.error(f"Fehler beim Senden der E-Mail: {response.text}")
    except Exception as e:
        st.error(f"Fehler beim Senden der E-Mail: {str(e)}")

# Button zum Herunterladen des PDFs (optional, zum Testen)
st.download_button(
    label="Test-PDF herunterladen",
    data=pdf,
    file_name="test.pdf",
    mime="application/pdf"
)