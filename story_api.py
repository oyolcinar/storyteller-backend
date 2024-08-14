import random
from flask import Flask, request, jsonify
from google.cloud import storage
import os
import json

app = Flask(__name__)

# Set up Cloud Storage
storage_client = storage.Client()
bucket_name = 'storytellerbucket'
bucket = storage_client.bucket(bucket_name)

def get_random_story(genre=None):
    blobs = bucket.list_blobs(prefix='stories/')
    stories = []

    for blob in blobs:
        if blob.name.endswith('story_data.json'):
            story_data = json.loads(blob.download_as_string())
            if genre is None or story_data['genre'] == genre:
                stories.append({
                    'id': blob.name.split('/')[-3],
                    'title': story_data['title'],
                    'genre': story_data['genre'],
                    'tags': story_data['tags'],
                    'summary': story_data.get('summary', ''),
                    'image_urls': story_data['image_urls'],
                    'tts_urls': story_data['tts_urls'],
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
