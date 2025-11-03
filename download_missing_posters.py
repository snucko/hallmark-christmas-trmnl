#!/usr/bin/env python3
"""
Simple script to download missing Hallmark Christmas movie posters.
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

TMDB_API_KEY = "4adf21ca8d1da5c81cb5463d8c731367"  # Working TMDB key
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def download_image(url, output_path):
    """Download image from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Error downloading: {e}")
        return False

def search_tmdb(title, year=2025):
    """Search TMDB for a movie poster."""
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'year': year,
        'include_adult': False
    }

    url = f"{TMDB_SEARCH_URL}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        if data['results']:
            result = data['results'][0]
            poster_path = result.get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE}{poster_path}"

    except Exception as e:
        print(f"  ⚠️  TMDB error: {e}")

    return None

def convert_with_imagemagick(input_path, output_path):
    """Convert image using ImageMagick."""
    import subprocess
    cmd = [
        'magick', str(input_path),
        '-resize', '200x300>',
        '-dither', 'FloydSteinberg',
        '-remap', 'pattern:gray50',
        '-depth', '1',
        '-strip',
        'png:' + str(output_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  ImageMagick error: {e.stderr}")
        return False

def main():
    """Download and convert missing posters."""
    script_dir = Path(__file__).parent
    movies_file = script_dir / 'data' / 'movies.json'

    with open(movies_file, 'r') as f:
        data = json.load(f)

    movies = data['movies']

    # Create directories
    output_dir = script_dir / 'images' / '1bit'
    temp_dir = script_dir / 'temp_posters'
    temp_dir.mkdir(exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find missing movies
    missing_movies = []
    for movie in movies:
        expected_filename = movie['image'].split('/')[-1]
        output_path = output_dir / expected_filename
        if not output_path.exists():
            missing_movies.append(movie)

    if not missing_movies:
        print("✅ All posters already exist!")
        return

    print(f"📽️  Downloading {len(missing_movies)} missing posters...\n")

    success_count = 0

    for i, movie in enumerate(missing_movies, 1):
        title = movie['title']
        expected_filename = movie['image'].split('/')[-1]
        output_path = output_dir / expected_filename

        print(f"[{i}/{len(missing_movies)}] {title}")

        # Try TMDB with different search terms
        poster_url = search_tmdb(title)
        if not poster_url:
            poster_url = search_tmdb(title, 2024)  # Try previous year

        # Try alternative search terms for some movies
        if not poster_url:
            alt_titles = {
                "Tidings For the Season": ["Tidings for the Season"],
                "The More the Merrier": ["The More The Merrier"],
                "A Grand Ole Opry Christmas": ["Grand Ole Opry Christmas"],
                "The Christmas Cup": ["Christmas Cup"],
                "Christmas at the Catnip Café": ["Christmas at the Catnip Cafe", "Catnip Cafe"],
                "Twelve Dates 'Til Christmas (S1)": ["Twelve Dates Till Christmas", "Twelve Dates til Christmas"],
                "Single on the 25th": ["Single On The 25th"],
                "A Suite Holiday Romance": ["Suite Holiday Romance"],
                "Oy to the World!": ["Oy To The World"],
                "A Make Or Break Holiday": ["Make or Break Holiday", "Make Or Break Holiday"]
            }

            for alt_title in alt_titles.get(title, []):
                poster_url = search_tmdb(alt_title)
                if poster_url:
                    break

        if poster_url:
            temp_file = temp_dir / f"temp_{i}.jpg"
            print(f"  ⬇️  Downloading...")

            if download_image(poster_url, temp_file):
                print(f"  🔄 Converting...")
                if convert_with_imagemagick(temp_file, output_path):
                    print(f"  ✅ Saved: {expected_filename}")
                    success_count += 1
                    temp_file.unlink()
                else:
                    print(f"  ❌ Conversion failed")
            else:
                print(f"  ❌ Download failed")
        else:
            print(f"  ❌ Not found on TMDB")

        print()

    # Cleanup
    if temp_dir.exists() and not list(temp_dir.iterdir()):
        temp_dir.rmdir()

    print(f"📊 Results: {success_count}/{len(missing_movies)} posters downloaded and converted")

if __name__ == "__main__":
    main()
