from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import os
import re
from bs4 import BeautifulSoup
import uuid

app = Flask(__name__)

DATABASE_FILE = "gifs.json"


def load_gifs():
    """Load GIFs from file, removing corrupt entries."""
    if not os.path.exists(DATABASE_FILE):
        return []  

    try:
        with open(DATABASE_FILE, "r") as f:
            gifs = json.load(f)
            valid_gifs = [gif for gif in gifs if "id" in gif]  

            # Remove corrupt GIFs automatically
            if len(valid_gifs) != len(gifs):
                save_gifs(valid_gifs)
                print("🧹 Removed corrupt GIFs")

            return valid_gifs
    except (json.JSONDecodeError, IOError):
        print("⚠️ Error reading gifs.json, resetting database...")
        return []


def save_gifs(gifs):
    """Save GIFs to file."""
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(gifs, f, indent=2)
        print("✅ GIF database updated successfully.")
    except IOError as e:
        print(f"❌ Error saving gifs.json: {e}")


def get_gifs_from_file():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                gifs = json.load(f)
                print(f"Loaded {len(gifs)} GIFs from file")  # Debugging
                return gifs
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {DATABASE_FILE}: {e}")
            return []  # Prevent crash
    return []


def get_tenor_gif_url(view_url):
    """Extract the direct GIF URL from a Tenor view page using scraping."""
    embed_url = re.sub(r'/view/[^/?]+-(\d+)', r'/embed/\1', view_url)
    
    try:
        response = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error fetching Tenor page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="gif-json")

    if script_tag:
        try:
            gif_data = json.loads(script_tag.string)
            return gif_data['media_formats']['gif']['url']
        except json.JSONDecodeError:
            print("❌ Error decoding JSON from Tenor page.")

    img_tag = soup.select_one("div.Gif img")
    if img_tag:
        return img_tag.get("src")

    return None  


@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')




@app.route("/gifs", methods=["GET"])
def get_gifs():
    gifs = load_gifs()
    
    # Reverse order to show newest first
    gifs.reverse()

    # Pagination parameters
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    start = (page - 1) * limit
    end = start + limit

    paginated_gifs = gifs[start:end]

    return jsonify({
        "gifs": paginated_gifs,
        "total": len(gifs),
        "page": page,
        "limit": limit
    })



@app.route('/gifs', methods=['POST'])
def add_gif():
    data = request.get_json()
    url = data.get('url')
    tags = data.get('tags', [])

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    gif_url = get_tenor_gif_url(url) if "tenor.com/view" in url else url
    if gif_url:
        gifs = get_gifs_from_file()
        gif_entry = {
            "id": str(uuid.uuid4()),  
            "gif": gif_url,
            "thumbnail": gif_url,
            "tags": tags if tags else ["tagless"]  # Ensure at least one tag
        }


        gifs.append(gif_entry)
        save_gifs(gifs)
        return jsonify(gif_entry)

    return jsonify({"error": "GIF not found"}), 404


@app.route('/gifs/delete', methods=['POST'])
def delete_gif():
    data = request.get_json()
    gif_id = data.get("id")

    if not gif_id:
        return jsonify({"error": "Invalid GIF ID"}), 400  

    gifs = get_gifs_from_file()
    new_gifs = [gif for gif in gifs if gif["id"] != gif_id]  

    if len(new_gifs) == len(gifs):  
        return jsonify({"error": "GIF not found"}), 404  

    save_gifs(new_gifs)
    return jsonify({"message": "GIF deleted"})


@app.route('/gifs/update-tags', methods=['POST'])
def update_tags():
    data = request.get_json()
    gif_id = data.get("id")
    new_tags = data.get("tags")

    # Convert empty array to None
    if not new_tags:  
        new_tags = None  

    gifs = load_gifs()  # Load fresh data from file
    for gif in gifs:
        if gif["id"] == gif_id:
            gif["tags"] = new_tags if new_tags else ["tagless"]  # Prevent empty tags
            save_gifs(gifs)
            return jsonify({"message": "Tags updated"})

    return jsonify({"error": "GIF not found"}), 404


@app.route('/gifs/search', methods=['GET'])
def search_gifs():
    tag = request.args.get("tag", "").strip().lower()
    gifs = load_gifs()
    
    filtered_gifs = [gif for gif in gifs if tag in (t.lower() for t in gif.get("tags", []))]
    
    return jsonify({"gifs": filtered_gifs})


@app.route('/tags', methods=['GET'])
def get_tags():
    gifs = get_gifs_from_file()

    # Ensure every gif has a valid tags list before processing
    unique_tags = list(set(
        tag for gif in gifs for tag in (gif.get("tags") or [])  # Convert None to []
    ))

    print(f"Total unique tags found: {len(unique_tags)}")  # Debugging
    return jsonify(unique_tags)


if __name__ == '__main__':
    app.run(port=5000, debug=False)
