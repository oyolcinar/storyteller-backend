from flask import Flask, request, jsonify
from google.cloud import storage, texttospeech
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import uuid
import random

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Verify the environment variable is loaded correctly
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print("GOOGLE_APPLICATION_CREDENTIALS:", credentials_path)

# Set up Cloud Storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
storage_client = storage.Client()
bucket_name = 'storytellerbucket'
bucket = storage_client.bucket(bucket_name)

# Set up OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Google Text-to-Speech
tts_client = texttospeech.TextToSpeechClient()

def generate_story(prompt, system_message):
    unique_context = f"This is a story about {random.choice(['a brave knight', 'a curious child', 'an adventurous explorer'])}."
    full_prompt = f"{prompt} {unique_context}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=500
    )
    content = response.choices[0].message.content
    return add_ssml_anchors(content)

def translate_story(story):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": f"Translate the following story to Turkish. When you encounter names, translate them phonetically so they are pronounceable in Turkish. For example, 'Sir Alaric' should become 'Sör Alarik':\n\n{story}"}
        ],
        max_tokens=500
    )
    translated_content = response.choices[0].message.content
    return add_ssml_anchors(translated_content)

def add_ssml_anchors(text):
    paragraphs = text.split("\n\n")
    ssml = "<speak>"
    for i, paragraph in enumerate(paragraphs):
        ssml += f'<p>{paragraph}</p>'
        ssml += f'<mark name="page_{i+1}"/>'
    ssml += "</speak>"
    return ssml.replace(".", ".<break time='700ms'/>")

def synthesize_speech(ssml_text, language_code, name, gender):
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=name,
        ssml_gender=gender
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9  # Adjust speaking rate to slow down the speech
    )
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return response.audio_content

def upload_to_gcs(content, file_path):
    blob = bucket.blob(file_path)
    blob.upload_from_string(content, content_type='audio/mpeg')
    return blob.public_url

@app.route('/')
def home():
    return "Welcome to the Storyteller Backend"

@app.route('/generate-story', methods=['POST'])
def generate_and_store_story():
    data = request.json
    prompt = data.get('prompt')
    title = data.get('title')
    tags = data.get('tags', [])
    genre = data.get('genre')

    if not prompt or not title or not genre:
        return jsonify({"error": "Prompt, title, and genre are required"}), 400

    # Generate a unique ID for the story
    story_id = str(uuid.uuid4())

    # Generate English story content
    content_en = generate_story(prompt, "You are a storyteller.")
    
    # Translate English story content to Turkish
    content_tr = translate_story(content_en)

    # Define TTS voices with corrected gender for Turkish voices and more distinct old voices
    voices = [
        {"name": "en-US-Wavenet-D", "gender": texttospeech.SsmlVoiceGender.MALE, "age": "young_man"},
        {"name": "en-GB-Neural2-A", "gender": texttospeech.SsmlVoiceGender.FEMALE, "age": "young_woman"},
        {"name": "en-GB-Wavenet-D", "gender": texttospeech.SsmlVoiceGender.MALE, "age": "old_man"},
        {"name": "en-US-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE, "age": "old_woman"},
        {"name": "tr-TR-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE, "age": "young_man"},  # Corrected
        {"name": "tr-TR-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE, "age": "young_woman"},  # Corrected
        {"name": "tr-TR-Wavenet-E", "gender": texttospeech.SsmlVoiceGender.MALE, "age": "old_man"},
        {"name": "tr-TR-Wavenet-D", "gender": texttospeech.SsmlVoiceGender.FEMALE, "age": "old_woman"}  # Corrected
    ]

    # Generate TTS for English and Turkish stories with different voices
    tts_urls = {}
    for voice in voices:
        language_code = voice['name'][:5]  # Extract language code from name
        content = content_en if "en-" in voice['name'] else content_tr
        tts_audio = synthesize_speech(content, language_code, voice['name'], voice['gender'])
        directory = "en" if "en-" in voice['name'] else "tr"
        file_path = f'stories/{genre}/{story_id}/{directory}/{voice["age"]}.mp3'
        tts_urls[f'{voice["age"]}_{directory}'] = upload_to_gcs(tts_audio, file_path)

    # Store story content and TTS URLs in Cloud Storage
    story_data = {
        'title': title,
        'content_en': content_en,
        'content_tr': content_tr,
        'tags': tags,
        'genre': genre,
        'tts_urls': tts_urls
    }
    story_blob = bucket.blob(f'stories/{genre}/{story_id}/story_data.json')
    story_blob.upload_from_string(json.dumps(story_data), content_type='application/json')

    return jsonify({
        "story_id": story_id,
        "title": title,
        "content_en": content_en,
        "content_tr": content_tr,
        "tags": tags,
        "genre": genre,
        "tts_urls": tts_urls
    }), 201

if __name__ == '__main__':
    app.run(debug=True)
