import streamlit as st
from memepdf_utils import create_10x15_meme_pdf
from upload_pdf import upload_pdf_to_gcs
from datetime import datetime
from io import BytesIO

def main():
    st.title('Meme Creator')

    # Eingabefeld für den Memetext
    st.subheader("Schreibe hier deinen Wenn-du-Satz auf")
    meme_text = st.text_input("Wenn-du-Satz", "")

    if st.button('Memetext hinzufügen'):
        if meme_text:
            # PDF erstellen
            pdf = create_10x15_meme_pdf(meme_text=meme_text)

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
        else:
            st.warning("Bitte gib einen Wenn-du-Satz ein.")

if __name__ == '__main__':
    main()