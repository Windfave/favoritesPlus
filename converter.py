import requests
import json
import re
import uuid
from bs4 import BeautifulSoup
from tqdm import tqdm  # For the progress bar

INPUT_FILE = "urls.txt"  # Input file with URLs
OUTPUT_FILE = "gifs.json"  # Output JSON file


def is_valid_gif(url):
    """Check if the given URL is a valid and accessible GIF."""
    try:
        response = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"})
        content_type = response.headers.get("Content-Type", "")

        # Check if it's an image and response is successful
        if response.status_code == 200 and "image" in content_type:
            return True
    except requests.RequestException:
        pass
    return False


def get_tenor_gif_url(view_url):
    """Extract the direct GIF URL from a Tenor view page using scraping."""
    embed_url = re.sub(r'/view/[^/?]+-(\d+)', r'/embed/\1', view_url)

    try:
        response = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        return None  # Skip on failure

    soup = BeautifulSoup(response.text, "html.parser")

    script_tag = soup.find("script", id="gif-json")
    if script_tag:
        try:
            gif_data = json.loads(script_tag.string)
            return gif_data['media_formats']['gif']['url']
        except json.JSONDecodeError:
            pass

    img_tag = soup.select_one("div.Gif img")
    if img_tag:
        return img_tag.get("src")

    return None  # No GIF found


def process_gifs():
    """Reads URLs, processes them, and saves to JSON with a progress bar."""
    gif_entries = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        urls = file.read().splitlines()

    total_gifs = len(urls)  # Count total GIFs
    processed_gifs = 0

    with tqdm(total=total_gifs, desc="Processing GIFs", unit="gif") as pbar:
        for url in urls:
            original_url = url.strip()

            # Convert Tenor view URLs to direct GIF links
            if "tenor.com/view/" in original_url:
                direct_url = get_tenor_gif_url(original_url)
                if not direct_url:
                    pbar.set_postfix({"Skipped": processed_gifs})
                    pbar.update(1)
                    continue
            else:
                direct_url = original_url  # Assume non-Tenor URLs are direct links

            # Validate GIF URL
            if not is_valid_gif(direct_url):
                pbar.set_postfix({"Skipped": processed_gifs})
                pbar.update(1)
                continue

            # Generate JSON entry
            gif_entry = {
                "id": str(uuid.uuid4()),
                "gif": direct_url,
                "thumbnail": direct_url,
                "tags": []  # Tags can be added later
            }
            gif_entries.append(gif_entry)

            processed_gifs += 1
            pbar.set_postfix({"Processed": processed_gifs})
            pbar.update(1)

    # Save to JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        json.dump(gif_entries, outfile, indent=2)

    print(f"\n✅ Saved {processed_gifs} valid GIFs to {OUTPUT_FILE}.")


# Run the script
process_gifs()
