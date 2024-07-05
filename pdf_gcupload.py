import streamlit as st
from google.cloud import storage
import os


def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Lädt eine Datei in den Google Cloud Storage Bucket hoch."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    return f"gs://{bucket_name}/{destination_blob_name}"


# Streamlit UI
st.title("PDF Uploader für Google Cloud Storage")

# Fester Dateipfad
file_path = "test_pdf.pdf"
file_name = os.path.basename(file_path)

# GCS Bucket Name
bucket_name = "vse-schamstation24-07-2"

if st.button("Datei hochladen"):
    try:
        # Datei zu GCS hochladen
        destination_blob_name = f"uploads/{file_name}"
        gcs_uri = upload_to_gcs(bucket_name, file_path, destination_blob_name)

        st.success(f"Datei erfolgreich hochgeladen! GCS URI: {gcs_uri}")
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {str(e)}")

# Anzeigen des Dateiinhalts (optional)
if os.path.exists(file_path):
    with open(file_path, "rb") as file:
        st.text("Inhalt der Datei test_pdf.pdf:")
        st.text(file.read().decode('utf-8', errors='ignore'))
else:
    st.warning(f"Die Datei {file_path} wurde nicht gefunden.")

st.write("Umgebungsinformationen:")
st.write(f"KUBERNETES_SERVICE_HOST: {os.environ.get('KUBERNETES_SERVICE_HOST', 'Nicht gesetzt')}")
st.write(f"KUBERNETES_SERVICE_PORT: {os.environ.get('KUBERNETES_SERVICE_PORT', 'Nicht gesetzt')}")
st.write(f"GKE_METADATA_SERVER: {os.environ.get('GKE_METADATA_SERVER', 'Nicht gesetzt')}")
st.write(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'Nicht gesetzt')}")
st.write(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Nicht gesetzt')}")

try:
    response = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/', headers={'Metadata-Flavor': 'Google'}, timeout=2)
    if response.status_code == 200:
        st.write("Läuft in einer Google Cloud Umgebung (möglicherweise GKE)")
        st.write(f"Default Service Account: {response.text}")
    else:
        st.write("Kein Zugriff auf den Google Metadata-Server")
except requests.exceptions.RequestException:
    st.write("Nicht in einer Google Cloud Umgebung")

credentials, project = default()
st.write(f"Verwendetes Service-Account: {credentials.service_account_email}")
st.write(f"Projekt: {project}")

# Versuchen Sie, eine Liste der Buckets zu erhalten
storage_client = storage.Client(credentials=credentials, project=project)
try:
    buckets = list(storage_client.list_buckets())
    st.write(f"Anzahl der verfügbaren Buckets: {len(buckets)}")
    st.write("Buckets:")
    for bucket in buckets:
        st.write(f"- {bucket.name}")
except Exception as e:
    st.error(f"Fehler beim Abrufen der Buckets: {str(e)}")