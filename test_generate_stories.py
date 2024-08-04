import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the URL for the local Flask app
url = "http://127.0.0.1:5000/generate-story"

# Define the payload
payload = {
    "prompt": "Once upon a time in a magical land...",
    "title": "Magical Story",
    "tags": ["magic", "fantasy"],
    "genre": "fantasy"
}

# Set the headers
headers = {
    "Content-Type": "application/json"
}

def test_generate_story():
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("Story generated and stored successfully!")
        print("Response:", response.json())
    else:
        print("Failed to generate story.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    test_generate_story()
