import random
from flask import Flask, request, jsonify
from google.cloud import storage
import os
import json
import datetime

app = Flask(__name__)

# Set up Cloud Storage
storage_client = storage.Client()
bucket_name = 'storytellerbucket'
bucket = storage_client.bucket(bucket_name)

def generate_signed_url(blob_name, expiration_time=3600):
    """Generate a signed URL for a given blob."""
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(seconds=expiration_time),
        method='GET'
    )
    return url

def get_random_story(genre=None):
    blobs = bucket.list_blobs(prefix='stories/')
    stories = []

    for blob in blobs:
        if blob.name.endswith('story_data.json'):
            story_data = json.loads(blob.download_as_string())
            if genre is None or story_data['genre'] == genre:
                # Generate signed URLs for images and TTS files
                signed_image_urls = [generate_signed_url(image_url) for image_url in story_data['image_urls']]
                signed_tts_urls = {key: generate_signed_url(tts_url) for key, tts_url in story_data['tts_urls'].items()}

                stories.append({
                    'id': blob.name.split('/')[-3],
                    'title': story_data['title'],
                    'genre': story_data['genre'],
                    'tags': story_data['tags'],
                    'summary': story_data.get('summary', ''),
                    'image_urls': signed_image_urls,
                    'tts_urls': signed_tts_urls,
                    'content_en': story_data.get('content_en', ''),  # English story content
                    'content_tr': story_data.get('content_tr', '')   # Turkish story content
                })

    if not stories:
        return None

    return random.choice(stories)

@app.route('/')
def home():
    return "Story API is running."

@app.route('/random-story', methods=['GET'])
def fetch_random_story():
    genre = request.args.get('genre')
    if genre not in ['fantasy', 'sci-fi', None]:  # Assuming 'any' means None
        return jsonify({"error": "Invalid genre preference"}), 400

    story = get_random_story(genre)

    if story is None:
        return jsonify({"error": "No stories found for this genre"}), 404

    return jsonify(story), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
