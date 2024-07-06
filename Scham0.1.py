#Scham mit Image_Generating v0.2

import streamlit as st
from io import BytesIO

from pdf_utils import create_10x15_pdf_with_image

import os
import time

from openai import OpenAI
from datetime import datetime

from upload_pdf import upload_pdf_to_gcs


# Setze den API-Schlüssel

api_key = st.secrets["api"]["api_key"]
assert api_key.startswith('sk-'), 'Error loading the API key. The API key starts with "sk-"'
os.environ['OPENAI_API_KEY'] = api_key

#openai.api_key = api_key

client = OpenAI()

# Initialisierungen
questions = [
    """\n\n**1/8**\n\n**Hallo. Schön, dass du hier bist.**\n\nBist du bereit?\n\n**Dann schreib 'bereit' und drück auf 'Senden'.**""",

    "\n\n**2/8**\n\n**Erinnere dich an eine peinliche Situation.**\n\nDu kannst später ein Bild daraus kreieren. \n\n Entscheide dich für etwas, mit dem du hier und jetzt umgehen kannst.\n\nNimm dir Zeit.\n\n**Wenn du eine Erinnerung in deinem Kopf hast, schreib 'ok' und drück auf 'Senden'.**",

    "\n\n**3/8**\n\n**Ruf dir die Situation vor Augen.**\n\nWo ist sie passiert?\n\nWer war dabei?\n\nGibt es bestimmte Wörter oder Sätze, an die du dich erinnerst? Wie klang die Stimme von dir und deinem Gegenüber?\n\nGibt es Kleidungsstücke, Gegenstände, Farben, Gerüche, an die du dich erinnerst?\n\n**Wenn du dich genug erinnert hast, schreib 'ok' und drück auf 'Senden'.**",

    "\n\n**4/8**\n\n**Jetzt wandel es um: **\n\n**Stell dir vor, du wärst in der Situation ein Tier gewesen.** Was wäre das für ein Tier? Vielleicht eine kleine Maus oder ein tollpatschiges Schwein? Oder ein Gegenstand, wie ein stummer Stein oder ein verblühtes Gänseblümchen?\n\n**Schreib auf wer oder was du warst und drück auf 'Senden'.**",

    "\n\n**5/8**\n\n**Welches Tier oder anderes wären die anderen gewesen?**\n\nVielleicht ein fieses Stinktier, ein Herde lachender Kaninchen oder etwas anderes?\n\n**Schreib es auf und drück auf 'Senden'.**",

    "\n\n**6/8**\n\n**Raum oder Landschaft**\n\nWenn die Situation ein Raum oder eine Landschaft wäre, wie sähe das aus? Vielleicht ein enger Raum, in dem das Atmen schwer fällt. Oder eine Bühne mit grellem Scheinwerferlicht?\n\nSchreib es auf: **Wie sieht deine Landschaft aus?**\n\n**Drück anschließend auf 'Senden'.**",

    "**7/8**\n\n**Was gibt dir Kraft?**\n\nWas ist ein Lieblingsgegenstand, eine Farbe, eine Ort, der dir Kraft gibt.\n\n(Personen sind leider nicht erlaubt, aber du kannst sie in Form von kraftspendenden Tieren auch nennen.)",

    "**8/8**\n\n**Danke!**\n\nUnten erscheint gleich dein Bild. Vielleicht dauert es einen kleinen Moment."
]

bot_responses = list()
messages = list()

#system_prompt = 'Answer as concisely as possible.'
#messages.append({'role': 'system', 'content': system_prompt})

def chat_with_bot(user_input):
    messages.append({'role': 'user', 'content': user_input})

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.7,
    )

    current_response = completion.choices[0].message.content
    bot_responses.append(current_response)
    messages.append({'role': 'assistant', 'content': current_response})
    return current_response

# user-description ohne Eingaben
#description_prompt = "Eine Ente wackelt über die Straße"

def create_artistic_description(responses):
    description_prompt = (
        f"Erstelle (auf deutsch) eine künstlerische Beschreibung,und detailreiche Beschreibung, die als Prompt für DALL·E dient, um ein Bild zu generieren. Die Beschreibung sollte auf den folgenden Eingaben basieren und diese in eine zusammenhängende, bildhafte Szene integrieren:\n"
        f"3. Details (Kleidung, Gegenstände, Farben, Gerüche): {responses[3]}\n"
        f"4. Protagonist: {responses[4]}\n"
        f"5. andere Figuren: {responses[5]}\n"
        f"6. Raum oder Landschaft: {responses[6]}\n"
        f"7. besondere Aufmerksamkeit als Kraftgebendes Element bekommt: {responses[7]}\n"
        f"Spezielle Anweisungen: Keine Personen: Es sollen keine menschlichen Figuren im Bild vorkommen.Falls notwendig, können Personen durch Tiere ersetzt werden, um die Bildbeschreibung konsistent und vollständig zu machen. Stelle sicher, dass die Bildbeschreibung den Sicherheitsrichtlinien von DALL·E entspricht und keine geschützten oder unangemessenen Inhalte enthält. Bitte integriere all diese Elemente in eine zusammenhängende und künstlerische bildhafte Beschreibung, die DALL·E als Prompt für die Bilderstellung verwendet werden kann."

    )

    messages.append({'role': 'user', 'content': description_prompt})

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.7,
    )

    artistic_description = completion.choices[0].message.content
    return artistic_description

def create_image_url(description_prompt):
    response = client.images.generate(
        model='dall-e-3',
        prompt=description_prompt,
        style='vivid',
        size='1024x1024', # 1024x1792, 1792x1024 pixels
        quality='standard',
        n=1
    )
    image_url = response.data[0].url
    return image_url



if __name__ == '__main__':
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title('Chat Bot')
    with col2:
        st.image('ai.png', width=70)

    # Neues Eingabefeld für den Namen
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""

    if not st.session_state.user_name:
        st.write("Damit wir dir am Ende dein geschaffenes Bild übergeben können, brauchen wir deinen Namen. Bitte gib hier deinen Namen ein.")
        user_name = st.text_input("Dein Name:")
        if st.button("Name bestätigen"):
            if user_name:
                st.session_state.user_name = user_name
                print(f"Benutzername: {st.session_state.user_name}")  # Anzeige im Terminal
                st.success(f"Danke, {st.session_state.user_name}! Lass uns beginnen.")
                st.write(f"Eingegebener Name: {st.session_state.user_name}")  # Anzeige in der Streamlit-App
            else:
                st.warning("Bitte gib deinen Namen ein.")
    else:
        # Anzeige des gespeicherten Namens, wenn bereits eingegeben
        st.write(f"Eingegebener Name: {st.session_state.user_name}")
        print(f"Gespeicherter Benutzername: {st.session_state.user_name}")  # Anzeige im Terminal bei jedem Neustart

    # Nur den Chat-Bot anzeigen, wenn der Name eingegeben wurde
    if st.session_state.user_name:
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0

        if 'responses' not in st.session_state:
            st.session_state.responses = []

        with st.form(key='chat_form'):
            if st.session_state.current_question_index < len(questions):
                current_question = questions[st.session_state.current_question_index]
            else:
                current_question = "Danke für deine Antworten. Wie kann ich dir sonst noch helfen?"

            st.write(f'Chat Bot: {current_question}')
            user_input = st.text_input('Du:', '')

            submit_button = st.form_submit_button(label='Senden')

            if submit_button:
                if user_input.lower() in ['exit', 'quit']:
                    st.write('Chat Bot: Ich war froh, dir helfen zu können. Tschüss!')
                    time.sleep(2)
                    st.stop()

                if user_input.lower() == '':
                    st.warning('Bitte gib eine Nachricht ein.')
                else:
                    st.session_state.responses.append(user_input)

                    if 'history' not in st.session_state:
                        st.session_state['history'] = f'Du: {user_input}\n'
                    else:
                        st.session_state['history'] += f'Du: {user_input}\n'

                    st.text_area(label='Chat-Verlauf', value=st.session_state['history'], height=400)

                    if st.session_state.current_question_index < len(questions) - 1:
                        st.session_state.current_question_index += 1
                    elif st.session_state.current_question_index == len(questions) - 1:
                        artistic_description = create_artistic_description(st.session_state.responses)
                        st.write(f'Künstlerische Beschreibung: {artistic_description}')

                        # Erzeuge die Bild-URL und zeige sie an
                        image_url = create_image_url(artistic_description)
                        st.write(f'Bild-URL: {image_url}')
                        st.image(image_url)

                        # Erzeuge das PDF mit der generierten Bild-URL
                        pdf = create_10x15_pdf_with_image(image_url, st.session_state.user_name)

                        st.session_state.current_question_index += 1

    if 'pdf' in locals():
        # Konvertieren Sie das PDF in ein BytesIO-Objekt
        pdf_bytes = BytesIO(pdf.getvalue())

        # Generiere einen Timestamp für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Dateiname für GCS
        gcs_filename = f"10x15_pdf_mit_bild_{timestamp}.pdf"

        # Bucket-Name
        bucket_name = "vse-schamstaton24-07"

        try:
            # Upload zur Google Cloud Storage
            upload_pdf_to_gcs(bucket_name, pdf_bytes, f"MemePDFs/{gcs_filename}")
            st.success(f"PDF erfolgreich in Google Cloud Storage hochgeladen: {gcs_filename}")
        except Exception as e:
            st.error(f"Fehler beim Hochladen in Google Cloud Storage: {str(e)}")

        # Download-Button für den Benutzer
        st.download_button(
            label=f"10x15 PDF herunterladen ({timestamp})",
            data=pdf,
            file_name=gcs_filename,
            mime="application/pdf"
        )

