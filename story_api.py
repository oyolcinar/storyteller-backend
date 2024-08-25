import random
from flask import Flask, request, jsonify
from google.cloud import storage
from google.cloud import secretmanager
from google.oauth2 import service_account
import json
import datetime

app = Flask(__name__)

# Set up Cloud Storage
storage_client = storage.Client()
bucket_name = 'storytellerbucket'
bucket = storage_client.bucket(bucket_name)

# Fetch the service account key from Secret Manager
def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/497374863203/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_data = response.payload.data.decode('UTF-8')
    return secret_data

# Load the service account JSON key
service_account_json = get_secret('storyteller_service_account')
signing_credentials = service_account.Credentials.from_service_account_info(json.loads(service_account_json))

def generate_signed_url(blob_name, expiration_time=3600):
    """Generate a signed URL for a given blob using signing credentials."""
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(seconds=expiration_time),
        method='GET',
        credentials=signing_credentials
    )
    return url


def get_blob_name_from_url(url):
    """Extract the blob name from a full URL."""
    # Assuming the URL format is consistent, split the URL to get the blob name.
    return '/'.join(url.split('/')[4:])  # Adjust based on your actual URL structure


def get_random_story(genre=None):
    blobs = bucket.list_blobs(prefix='stories/')
    stories = []

    for blob in blobs:
        if blob.name.endswith('story_data.json'):
            story_data = json.loads(blob.download_as_string())
            if genre is None or story_data['genre'] == genre:
                # Convert full URLs to blob names (relative paths) before generating signed URLs
                signed_image_urls = [generate_signed_url(get_blob_name_from_url(image_url)) for image_url in story_data['image_urls']]
                signed_tts_urls = {key: generate_signed_url(get_blob_name_from_url(tts_url)) for key, tts_url in story_data['tts_urls'].items()}

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
