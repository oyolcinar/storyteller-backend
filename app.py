from flask import Flask, request, jsonify
from google.cloud import storage, texttospeech
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import uuid
import random
import requests

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

# List of generic fantasy protagonists
protagonists = [
    'a brave knight', 'a curious child', 'an adventurous explorer', 'a wise old wizard',
    'a clever rogue', 'a noble prince', 'a fierce warrior', 'a kind healer',
    'a magical fairy', 'a fearless ranger', 'a clever inventor', 'a powerful sorcerer',
    'a loyal squire', 'a daring pirate', 'a mysterious stranger', 'a legendary hero',
    'a valiant paladin', 'a gifted bard', 'a resourceful hunter', 'a watchful guardian'
]

sci_fi_protagonists = [
    'a brave star pilot', 'a curious space cadet', 'an adventurous astronaut', 'a wise alien sage',
    'a clever robot engineer', 'a noble space prince', 'a fierce galactic warrior', 'a kind star healer',
    'a magical space fairy', 'a fearless explorer', 'a clever AI inventor', 'a powerful cosmic sorcerer',
    'a loyal android companion', 'a daring space pirate', 'a mysterious alien visitor', 'a legendary star hero',
    'a valiant space guardian', 'a gifted cosmic musician', 'a resourceful starship captain', 'a watchful cosmic protector'
]


fantasy_land_names = [
    "Aeloria", "Valoria", "Nymaria", "Thaloria", "Zephyria",
    "Lunaris", "Drakoria", "Mystara", "Sylphia", "Eryndor",
    "Thalindor", "Aurelia", "Celandor", "Valkyra", "Frostveil",
    "Eldrath", "Shadowmere", "Arvandor", "Brighthaven", "Cyranor",
    "Mythralis", "Evernight", "Ravenwood", "Starfall", "Windrider",
    "Silverleaf", "Stormwatch", "Briarwood", "Darkspire", "Moonveil",
    "Sunhaven", "Highpeak", "Ironhold", "Goldhaven", "Feywild",
    "Emberfall", "Shadowfen", "Whisperwind", "Crystalholm", "Ravenshire",
    "Brightmoon", "Glimmerdeep", "Mistveil", "Twilightmere", "Windscar",
    "Frostfang", "Darkwater", "Ashenvale", "Sunspire", "Winterhold",
    "Stormkeep", "Duskwood", "Brightspire", "Dragonfell", "Hallowmere",
    "Stonehaven", "Whispering Hollow", "Grimshade", "Brightvale", "Hollowpeak",
    "Moonshadow", "Stormveil", "Starfire", "Wildwood", "Frostmourne",
    "Glimmerwood", "Ashfall", "Thornwild", "Wyrmwood", "Silvermere",
    "Dawnhaven", "Nightfall", "Brightwood", "Frostholm", "Ironwood"
]

sci_fi_location_names = [
    "Nova Prime", "Starlight Station", "Lunar Falls", "Nebula Bay", "Galaxia",
    "Orion's Edge", "Astroport", "Quantum Fields", "Stellar Harbor", "Cosmic Cove",
    "Eclipse Ridge", "Meteor Valley", "Celestial Gardens", "Solaris", "Comet's Cradle",
    "Pulsar City", "Nebulon", "Photon Plains", "Cosmos Reach", "Starbeam Junction",
    "Andromeda Outpost", "Galactic Glade", "Astral Heights", "Sirius Ridge", "Vortex Plaza",
    "Meteor Shores", "Skyward Station", "Nebula Heights", "Supernova Plains", "Starlight Springs",
    "Cosmos Haven", "Asteroid Fields", "Quantum Cove", "Nebula Nexus", "Starglow Gardens",
    "Lunar Horizon", "Eclipse Bay", "Celestial Heights", "Nova City", "Astroglow Plains",
    "Galactic Ridge", "Solaris Bay", "Astroland", "Pulsar Peaks", "Comet's Gate",
    "Quantum Quay", "Nebulon Vista", "Starlight Grove", "Meteor Crater", "Astral Bay",
    "Cosmic Junction", "Orion's Landing", "Celestia", "Starlight Plains", "Solarwind Shores",
    "Nebula Heights", "Meteor Harbor", "Skybeam Ridge", "Astro Heights", "Supernova Shores",
    "Galaxia Gardens", "Starglow City", "Cosmos Cradle", "Eclipse Cove", "Lunar Shores",
    "Quantum Peaks", "Nebula Quay", "Starfall Ridge", "Photon Bay", "Stellar Springs",
    "Orion's Harbor", "Cosmic Heights", "Asteroid Shores", "Galactic Nexus", "Pulsar Haven"
]




def generate_story(prompt, system_message, protagonist):
    unique_context = f"This is a story about {protagonist}."
    full_prompt = f"{prompt} {unique_context}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=2500,
        temperature=0.7,
        stop=None
    )
    content = response.choices[0].message.content
    return add_ssml_anchors(content)

def summarize_story(story):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a summarizer."},
            {"role": "user", "content": f"Summarize the following story in a concise manner:\n\n{story}"}
        ],
        max_tokens=100
    )
    summary = response.choices[0].message.content
    return summary

def translate_story(story):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": f"Translate the following story to Turkish. When you encounter names, translate them phonetically so they are pronounceable in Turkish. For example, 'Sir Alaric' should become 'Sör Alarik':\n\n{story}"}
        ],
        max_tokens=2500
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

def chunk_text_to_ssml(text, max_size=5000):
    """Splits text into SSML-valid chunks of specified byte size."""
    current_chunk = []
    current_size = len('<speak>') + len('</speak>')  # Account for <speak> and </speak> tags
    
    for paragraph in text.split('<p>'):
        paragraph = paragraph.strip()
        paragraph_ssml = f"<p>{paragraph}</p>"
        paragraph_bytes = len(paragraph_ssml.encode('utf-8'))
        
        if current_size + paragraph_bytes > max_size:
            yield f"<speak>{''.join(current_chunk)}</speak>"
            current_chunk = []
            current_size = len('<speak>') + len('</speak>')
        
        current_chunk.append(paragraph_ssml)
        current_size += paragraph_bytes
    
    if current_chunk:
        yield f"<speak>{''.join(current_chunk)}</speak>"


def synthesize_speech(ssml_text, language_code, name, gender):
    chunks = chunk_text_to_ssml(ssml_text, max_size=5000)
    audio_contents = []
    
    for chunk in chunks:
        synthesis_input = texttospeech.SynthesisInput(ssml=chunk)
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
        audio_contents.append(response.audio_content)
    
    return b"".join(audio_contents)  # Concatenate all audio parts into a single byte stream


def upload_to_gcs(content, file_path):
    blob = bucket.blob(file_path)
    blob.upload_from_string(content, content_type='audio/mpeg' if file_path.endswith('.mp3') else 'image/png')
    return blob.public_url

def extract_key_points(story, num_points=3):
    sentences = story.split('. ')
    if len(sentences) < num_points:
        return sentences
    step = len(sentences) // num_points
    return [sentences[i*step] for i in range(num_points)]

def generate_image(prompt, char_profile):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"{prompt} Character profile: {char_profile}. The image should not contain any text, writing, or captions.",
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

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

    # Pick a random protagonist from the list
    protagonist = random.choice(protagonists)
    char_profile = f"Main character: {protagonist}"

    # Generate a unique ID for the story
    story_id = str(uuid.uuid4())

    # Generate English story content
    content_en = generate_story(prompt, "You are a storyteller.", protagonist)
    
    # Translate English story content to Turkish
    content_tr = translate_story(content_en)

    # Summarize the story
    summary = summarize_story(content_en)

    # Extract key points
    key_points = extract_key_points(summary)

    # Generate images for each key point
    image_urls = []
    for point in key_points:
        image_url = generate_image(point, char_profile)
        image_urls.append(image_url)

    # Store images in Cloud Storage
    image_paths = []
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        file_path = f'stories/{genre}/{story_id}/images/image_{i+1}.png'
        blob = bucket.blob(file_path)
        blob.upload_from_string(response.content, content_type='image/png')
        image_paths.append(blob.public_url)

    # Add anchors to the story text
    content_en_with_anchors = insert_image_tags(content_en, image_paths)
    content_tr_with_anchors = insert_image_tags(content_tr, image_paths)

    # Define TTS voices with corrected gender for Turkish voices and more distinct old voices
    voices = [
        {"name": "en-US-Wavenet-D", "gender": texttospeech.SsmlVoiceGender.MALE, "age": "young_man"},
        {"name": "en-GB-Wavenet-A", "gender": texttospeech.SsmlVoiceGender.FEMALE, "age": "young_woman"},
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
        content = content_en_with_anchors if "en-" in voice['name'] else content_tr_with_anchors
        tts_audio = synthesize_speech(content, language_code, voice['name'], voice['gender'])
        directory = "en" if "en-" in voice['name'] else "tr"
        file_path = f'stories/{genre}/{story_id}/{directory}/{voice["age"]}.mp3'
        tts_urls[f'{voice["age"]}_{directory}'] = upload_to_gcs(tts_audio, file_path)

    # Store story content and TTS URLs in Cloud Storage
    story_data = {
        'title': title,
        'content_en': content_en_with_anchors,
        'content_tr': content_tr_with_anchors,
        'tags': tags,
        'genre': genre,
        'tts_urls': tts_urls,
        'image_urls': image_paths
    }
    story_blob = bucket.blob(f'stories/{genre}/{story_id}/story_data.json')
    story_blob.upload_from_string(json.dumps(story_data), content_type='application/json')

    return jsonify({
        "story_id": story_id,
        "title": title,
        "content_en": content_en_with_anchors,
        "content_tr": content_tr_with_anchors,
        "tags": tags,
        "genre": genre,
        "tts_urls": tts_urls,
        "image_urls": image_paths
    }), 201

def insert_image_tags(content, image_paths):
    paragraphs = content.split('</p>')
    for i, image_url in enumerate(image_paths):
        if i < len(paragraphs):
            paragraphs[i] += f' <img src="{image_url}" alt="story_image_{i+1}" />'
    return '</p>'.join(paragraphs)

if __name__ == '__main__':
    app.run(debug=True)
