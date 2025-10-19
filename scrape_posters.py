#!/usr/bin/env python3
"""
Scrape movie posters for Hallmark Christmas movies from TMDB.
Converts them to 1-bit PNG format for e-ink displays.
"""

import json
import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

TMDB_API_KEY = "4adf21ca8d1da5c81cb5463d8c731367"  # Get free key from https://www.themoviedb.org/settings/api
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def slugify(title):
    """Convert movie title to filename-safe slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def search_tmdb(title, year=2025):
    """Search TMDB for a movie and return the poster path."""
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'year': year,
        'include_adult': False
    }
    
    url = f"{TMDB_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        if data['results']:
            result = data['results'][0]
            poster_path = result.get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE}{poster_path}"
            
    except Exception as e:
        print(f"  ⚠️  Error searching TMDB: {e}")
    
    return None

def download_image(url, output_path):
    """Download image from URL to output path."""
    try:
        with urllib.request.urlopen(url) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Error downloading: {e}")
        return False

def convert_to_1bit(input_path, output_path, size=(200, 300)):
    """Convert image to 1-bit PNG for e-ink display."""
    try:
        img = Image.open(input_path)
        
        # Resize while maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create new image with exact dimensions (add padding if needed)
        new_img = Image.new('RGB', size, 'white')
        paste_x = (size[0] - img.width) // 2
        paste_y = (size[1] - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        # Convert to grayscale then 1-bit with dithering
        gray_img = new_img.convert('L')
        bw_img = gray_img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
        
        bw_img.save(output_path, 'PNG')
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error converting to 1-bit: {e}")
        return False

def main():
    """Main script to scrape and convert movie posters."""
    
    # Check for API key
    if TMDB_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ Please set your TMDB API key in the script.")
        print("   Get a free API key from: https://www.themoviedb.org/settings/api")
        return
    
    # Load movies data
    script_dir = Path(__file__).parent
    movies_file = script_dir / 'data' / 'movies.json'
    
    with open(movies_file, 'r') as f:
        data = json.load(f)
    
    movies = data['movies']
    print(f"📽️  Found {len(movies)} movies to process\n")
    
    # Create output directory
    output_dir = script_dir / 'images' / '1bit'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temp directory for downloads
    temp_dir = script_dir / 'temp_posters'
    temp_dir.mkdir(exist_ok=True)
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, movie in enumerate(movies, 1):
        title = movie['title']
        expected_filename = movie['image'].split('/')[-1]
        output_path = output_dir / expected_filename
        
        print(f"[{i}/{len(movies)}] {title}")
        
        # Skip if already exists
        if output_path.exists():
            print(f"  ✓ Already exists: {expected_filename}")
            skip_count += 1
            continue
        
        # Search TMDB for poster
        print(f"  🔍 Searching TMDB...")
        poster_url = search_tmdb(title)
        
        if not poster_url:
            print(f"  ❌ No poster found on TMDB")
            fail_count += 1
            continue
        
        # Download poster
        temp_file = temp_dir / f"temp_{i}.jpg"
        print(f"  ⬇️  Downloading poster...")
        
        if not download_image(poster_url, temp_file):
            fail_count += 1
            continue
        
        # Convert to 1-bit
        print(f"  🔄 Converting to 1-bit PNG...")
        if convert_to_1bit(temp_file, output_path):
            print(f"  ✅ Saved: {expected_filename}")
            success_count += 1
            temp_file.unlink()  # Delete temp file
        else:
            fail_count += 1
        
        print()
    
    # Cleanup temp directory
    if temp_dir.exists():
        temp_dir.rmdir()
    
    print("\n" + "="*50)
    print(f"✅ Successfully processed: {success_count}")
    print(f"⏭️  Skipped (already exist): {skip_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(movies)}")
    print("="*50)

if __name__ == "__main__":
    main()
