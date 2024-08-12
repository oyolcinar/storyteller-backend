import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the URL for the local Flask app
url = "http://127.0.0.1:5000/generate-story"
batch_url = "http://127.0.0.1:5001/generate-stories-batch"

# Updated Prompt Templates
fantasy_prompt_templates = [
    "Once upon a time in a magical land...",
    "In the heart of an enchanted forest...",
    "Long ago in a kingdom far away...",
    "In a world where dragons and magic ruled...",
    "In a realm where fairies and wizards coexisted...",
    "In a mystical land filled with hidden secrets...",
    "In a forgotten kingdom surrounded by enchanted mountains...",
    "In a village where everyone had a magical gift...",
    "Where the stars spoke to those who could listen...",
    "In a world where mythical creatures guarded ancient treasures...",
    "In a castle perched high on a cloud...",
    "In a forest where the trees whispered ancient spells...",
    "In a land where the rivers sparkled with magic...",
    "In a realm where the moon never set...",
    "In a land where every child could speak to animals...",
    "In a kingdom protected by a powerful, invisible force...",
    "In a place where wishes came true under the moonlight...",
    "In a world where time itself was a treasure...",
    "In a magical library where every book was alive...",
    "In a land where the seasons changed with a single word..."
]

sci_fi_prompt_templates = [
    "In a distant galaxy, far from Earth...",
    "In the year 3000, humanity discovered...",
    "On a far-off planet, where aliens and robots exist...",
    "In the vastness of space, where adventure awaits...",
    "In a futuristic city among the stars...",
    "In a world where spaceships soar between planets...",
    "On a starship exploring the uncharted regions of space...",
    "In a galaxy where alien creatures and humans coexist...",
    "On a space station orbiting a distant planet...",
    "In a universe where every star hides a mystery...",
    "In a future where children dream of exploring the stars...",
    "In a city built on a distant moon...",
    "In a world where space travel is as common as driving a car...",
    "On a mission to a planet filled with strange and wonderful creatures...",
    "In a future where kids invent their own spaceships...",
    "In a world where stars can be harvested for energy...",
    "On a journey to the edge of the universe...",
    "In a galaxy where kids are the best explorers...",
    "On a mission to find a lost colony among the stars...",
    "In a future where everyone lives on floating islands in space..."
]


# Title Templates
fantasy_title_templates = [
    "Magical Fantasy Story",
    "The Enchanted Kingdom",
    "Tales of the Mystic Lands",
    "The Legend of the Dragon's Heart",
    "The Wizard's Quest",
    "The Fairy's Secret",
    "The Enchanted Forest Adventure",
    "The Kingdom of Dreams",
    "The Dragon's Treasure",
    "The Secret of the Crystal Cave",
    "The Moonlit Castle",
    "The Whispering Woods",
    "The Shimmering River",
    "The Endless Night",
    "The Animal Whisperer",
    "The Guardian of the Kingdom",
    "The Midnight Wish",
    "The Timeless Journey",
    "The Living Library",
    "The Changing Seasons"
]


sci_fi_title_templates = [
    "Epic Sci-Fi Adventure",
    "The Galactic Quest",
    "Tales of the Starship",
    "The Lost Planet",
    "The Alien Encounter",
    "The Space Explorer's Journey",
    "The Quest for the Stars",
    "The Cosmic Voyage",
    "The Mystery of the Galaxy",
    "The Starship Chronicles",
    "The Lunar City",
    "The Space Traveler",
    "The Adventures of Starship Alpha",
    "The Journey to the Stars",
    "The Cosmic Explorer",
    "The Planet of Wonders",
    "The Starry Odyssey",
    "The Galactic Adventure",
    "The Space Explorer's Tale",
    "The Floating Islands of Space"
]


# Tags Pool
fantasy_tags_pool = ["magic", "fantasy", "adventure", "dragons", "wizards", "enchanted", "kingdom", "fairy", "legend", "quest"]
sci_fi_tags_pool = ["sci-fi", "adventure", "space", "aliens", "robots", "futuristic", "galaxy", "technology", "exploration", "future"]


# Define the payload
payload = {
    "prompt": "Once upon a time in a magical land...",
    "title": "Magical Story",
    "tags": ["magic", "fantasy"],
    "genre": "fantasy"
}

def generate_random_payload(genre):
    if genre == "fantasy":
        prompt = random.choice(fantasy_prompt_templates)
        title = random.choice(fantasy_title_templates)
        tags = random.sample(fantasy_tags_pool, 3)
    elif genre == "sci-fi":
        prompt = random.choice(sci_fi_prompt_templates)
        title = random.choice(sci_fi_title_templates)
        tags = random.sample(sci_fi_tags_pool, 3)
    
    payload = {
        "prompt": prompt,
        "title": title,
        "tags": tags,
        "genre": genre
    }
    
    return payload

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# def test_generate_story():
#     for genre in ["fantasy", "sci-fi"]:
#         payload = generate_random_payload(genre)
#         response = requests.post(url, json=payload, headers=headers)

#         if response.status_code == 201:
#             print(f"{genre.capitalize()} story generated and stored successfully!")
#             print("Response:", response.json())
#         else:
#             print(f"Failed to generate {genre} story.")
#             print("Status Code:", response.status_code)
#             print("Response:", response.text)

# if __name__ == "__main__":
#     test_generate_story()

def test_generate_stories_batch():
    batch_payload = []

    for genre in ["fantasy", "sci-fi"]:
        for _ in range(10):  # Generate X stories for each genre
            payload = generate_random_payload(genre)
            batch_payload.append(payload)

    response = requests.post(batch_url, json=batch_payload, headers=headers)

    if response.status_code == 201:
        print("Batch stories generated and stored successfully!")
        print("Response:", response.json())
    else:
        print("Failed to generate batch stories.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    test_generate_stories_batch()