import streamlit as st
import pyttsx3
import speech_recognition as sr
import requests
import webbrowser
from googleapiclient.discovery import build
import pytube
from pytube import YouTube
import os
from gtts import gTTS
import urllib.parse
import re
import googletrans
import IPython.display as ipd
import streamlit.components.v1 as components

YOUTUBE_API_KEY = "AIzaSyDCC5zPAxFUMsDlR2YyRjq0zH_LvMfKxu8"


def medical_google_search(query, site="medlineplus.gov", num_results=3):
    api_key = "AIzaSyA-WZ9vzyRjKpnJVH_uuWXg0LLM7K3ocfE"
    search_engine_id = "04ff519ffa85f48c6"

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&siteSearch={site}&num={num_results}"
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        results = data['items']
        formatted_snippets = []
        for result in results:
            snippet = result.get('snippet', 'No snippet available')
            snippet_without_dates = re.sub(
                r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',
                '', snippet, flags=re.IGNORECASE)
            snippet_without_dates = re.sub(r'\b\d{4}\b', '', snippet_without_dates)
            sentences = re.split(r'[.;]', snippet_without_dates)
            bullet_points = "\n".join([f"- {sentence.strip()}" for sentence in sentences if sentence.strip()])
            formatted_snippets.append(bullet_points.strip())
        return "\n\n".join(formatted_snippets)
    else:
        return "Sorry, I couldn't find an answer to your question."


def google_search(query, num_results=2):
    api_key = "AIzaSyA-WZ9vzyRjKpnJVH_uuWXg0LLM7K3ocfE"
    search_engine_id = "04ff519ffa85f48c6"

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&num={num_results}"
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        results = data['items']
        formatted_snippets = []
        for result in results:
            snippet = result.get('snippet', 'No snippet available')
            snippet_without_dates = re.sub(
                r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',
                '', snippet, flags=re.IGNORECASE)
            snippet_without_dates = re.sub(r'\b\d{4}\b', '', snippet_without_dates)
            sentences = re.split(r'[.;]', snippet_without_dates)
            bullet_points = "\n".join([f"- {sentence.strip()}" for sentence in sentences if sentence.strip()])
            formatted_snippets.append(bullet_points.strip())
        return "\n\n".join(formatted_snippets)
    else:
        return "Sorry, I couldn't find an answer to your question."


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()


# def speak_text_dynamic_language_jupyter(text, language):
#     try:
#         tts = gTTS(text=text, lang=language)
#         tts.save("output.mp3")
#         return ipd.Audio("output.mp3", autoplay=True)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

def speak_text_dynamic_language_streamlit(text, language):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save("output.mp3")
        st.audio("output.mp3", format='audio/mp3', start_time=0, autoplay=True)
        os.remove("output.mp3")  # Clean up the temporary audio file after playing
    except Exception as e:
        st.error(f"An error occurred: {e}")


def listen(min_energy_threshold=3500):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        current_threshold = max(recognizer.energy_threshold, min_energy_threshold)
        recognizer.energy_threshold = current_threshold
        st.write(f"Listening... (threshold: {current_threshold})")

        while True:
            try:
                audio = recognizer.listen(source, timeout=7)
                st.write("Analyzing...")
                query = recognizer.recognize_google(audio)
                st.write(f"You asked: {query}")
                return query
            except sr.WaitTimeoutError:
                st.write("No speech detected within the timeout. Still listening...")
            except sr.UnknownValueError:
                st.write("Sorry, I couldn't understand what you said. Trying again...")
                continue
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")
                return ""




def download_and_play_music(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url)
    video_id = response.text.split('watch?v=')[1].split('"')[0]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    download_folder = "C:\\Users\\KIIT\\Desktop\\Minor Project\\Minor"
    audio_file_name = "music.mp4"
    audio_file_path = os.path.join(download_folder, audio_file_name)
    encoded_file_path = urllib.parse.quote(audio_file_path)

    audio_stream.download(output_path=download_folder, filename=audio_file_name)
    downloaded_file = os.path.join(download_folder, audio_file_name)
    os.rename(downloaded_file, audio_file_path)

    if os.path.exists(audio_file_path):
        return audio_file_path
    else:
        return None


def open_mail(url):
    webbrowser.open_new_tab(url)
    speak(f"Opening gmail.")


def translate_text(text, source_lang, dest_lang):
    translator = googletrans.Translator()
    translated_text = translator.translate(text, src=source_lang, dest=dest_lang)
    return translated_text.text


def get_language_code(language_name):
    for code, name in googletrans.LANGUAGES.items():
        if name.lower() == language_name.lower():
            return code


def main(audio_file_path=None):
    st.title("NEXA-THE VOICE BOT")
    st.write("Hi! I am Nexa")
    st.write("How can I assist you?")

    # Toggle Listening State
    if 'listening' not in st.session_state:
        st.session_state.listening = False

    def start_listening():
        st.session_state.listening = True

    st.button("Start Listening", on_click=start_listening)

    if st.session_state.listening:
        user_input = listen()  # Your listen function needs to return the transcribed text
        process_command(user_input)

def process_command(user_input):
    if user_input.lower() == "exit":
        st.write("Goodbye!")
        speak("Goodbye!")
        st.session_state.listening = False  # Ensure we stop listening
    elif "open" in user_input.lower():
        video_query = user_input.lower().replace("open", "").strip()
        st.write(f"Searching for {video_query} on YouTube...")
        speak(f"Searching for {video_query} on YouTube...")
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(
                        q=video_query,
                        part="snippet",
                        type="video",
                        maxResults=1
        ).execute()
        video_url = f"https://www.youtube.com/watch?v={search_response['items'][0]['id']['videoId']}"
        st.write(f"Playing {search_response['items'][0]['snippet']['title']}...")
        speak(f"Playing {search_response['items'][0]['snippet']['title']}...")
        webbrowser.open(video_url)

    elif "gmail" in user_input.lower():
        open_mail("https://mail.google.com/")

    elif "play" in user_input.lower():
        music_query = user_input.lower().replace("play", "").strip()
        st.write(f"Playing music: {music_query}...")
        speak(f"Playing music: {music_query}...")

        audio_file_path = download_and_play_music(music_query)
        if audio_file_path:
            st.audio(audio_file_path, format='audio/mp3', start_time=0)
        else:
            st.write("Error: Failed to download or locate the music file.")

    # elif "translate" in user_input.lower():
    #     speak("Sure, what is your source language?")
    #     st.write("Sure, what is your source language?")
    #     source_lang = st.text_input("Source language:")
    #     st.write("Got it. Now, what is your destination language?")
    #     dest_lang = st.text_input("Destination language:")
    #     st.write("Okay, please say the text you want to translate.")
    #     text_to_translate = listen()
    #     translated_text = translate_text(text_to_translate, source_lang, dest_lang)
    #     code = get_language_code(dest_lang)
    #     st.write(f"Here is the translated text: {translated_text}")
    #     speak("Here is the translated text")
    #     audio = speak_text_dynamic_language_jupyter(translated_text, code)
    #     st.write(audio)
    elif "translate" in user_input.lower():
        speak("Sure, what is your source language?")
        source_lang = listen().lower()  # Listening for the source language
        speak("Got it. Now, what is your destination language?")
        dest_lang = listen().lower()  # Listening for the destination language
        speak("Okay, please say the text you want to translate.")
        text_to_translate = listen()  # Listening for the text to translate
        translated_text = translate_text(text_to_translate, source_lang, dest_lang)
        code = get_language_code(dest_lang)
        speak(f"Here is the translated text: {translated_text}")
        # Assuming `speak_text_in_language` is a function that can speak in the specified language
        speak_text_dynamic_language_streamlit(translated_text, code)


    elif "medical issue" in user_input.lower():
        txt="You can share your medical issue with me"
        speak(txt)
        st.write("You can share your medical issue with me")
        issue = listen().lower()
        answer = medical_google_search(issue)
        st.write("Answer:", answer)
        speak(answer)

    else:
        answer = google_search(user_input)
        st.write("Answer:", answer)
        speak(answer)


    st.session_state.listening = False


if __name__ == "__main__":
    main()
