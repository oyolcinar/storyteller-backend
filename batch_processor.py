from flask import request, jsonify
from app import generate_and_store_story_content, app  # Import the helper function

@app.route('/generate-stories-batch', methods=['POST'])
def generate_stories_batch():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of story requests"}), 400
    
    results = []
    for item in data:
        try:
            prompt = item.get('prompt')
            title = item.get('title')
            tags = item.get('tags', [])
            genre = item.get('genre')
            
            # Generate the story using the imported function
            response = generate_and_store_story_content(prompt, title, tags, genre)
            results.append({
                "status": "success",
                "data": response
            })
        except Exception as e:
            results.append({
                "status": "error",
                "message": str(e)
            })
    
    return jsonify(results), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ensure this runs on a different port if necessary
