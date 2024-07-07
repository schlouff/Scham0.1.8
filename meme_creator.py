import streamlit as st
from memepdf_utils import create_10x15_meme_pdf
from upload_pdf import upload_pdf_to_gcs
from datetime import datetime
from io import BytesIO


def create_meme(user_name, meme_text, image_url):
    try:
        # PDF erstellen
        pdf = create_10x15_meme_pdf(user_name=user_name, meme_text=meme_text, image_url=image_url)

        # Generiere einen Timestamp für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Dateiname für GCS
        gcs_filename = f"meme_pdf_{timestamp}.pdf"

        # Bucket-Name
        bucket_name = "vse-schamstaton24-07"

        try:
            # Upload zur Google Cloud Storage
            upload_pdf_to_gcs(bucket_name, pdf, f"MemePDFs/{gcs_filename}")
            st.success(f"PDF erfolgreich in Google Cloud Storage hochgeladen: {gcs_filename}")
        except Exception as e:
            st.error(f"Fehler beim Hochladen in Google Cloud Storage: {str(e)}")

        # Download-Button für den Benutzer
        st.download_button(
            label=f"Meme PDF herunterladen ({timestamp})",
            data=pdf,
            file_name=gcs_filename,
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Fehler beim Erstellen des PDFs: {str(e)}")


def meme_creator_ui(image_url, user_name):
    st.subheader("Erstelle dein Meme")

    # Anzeige des Benutzernamens
    st.write(f"Meme erstellt von: {user_name}")

    # Eingabefeld für den Memetext
    st.subheader("Schreibe hier deinen Wenn-du-Satz auf")
    meme_text = st.text_input("Wenn-du-Satz", "")

    if st.button('Memetext hinzufügen'):
        if meme_text:
            create_meme(user_name, meme_text, image_url)
        else:
            st.warning("Bitte gib einen Wenn-du-Satz ein.")