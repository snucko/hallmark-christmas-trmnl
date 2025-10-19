#!/usr/bin/env python3
"""
Enhanced poster scraper - searches TMDB, Google, and Hallmark sources.
"""

import json
import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image
import ssl

TMDB_API_KEY = "4adf21ca8d1da5c81cb5463d8c731367"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# Create SSL context that doesn't verify certificates (for some image servers)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def download_image(url, output_path):
    """Download image from URL to output path."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
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

def search_google_images(title):
    """
    Search Google for movie poster image.
    Note: This uses a simple search - for production use Google Custom Search API.
    """
    try:
        # Clean title for search
        search_query = f"{title} hallmark movie 2025 poster"
        encoded_query = urllib.parse.quote(search_query)
        
        # Try searching for common poster hosting sites
        poster_sites = [
            f"https://www.hallmarkmoviesandmysteries.com/",
            f"https://www.hallmarkchannel.com/",
        ]
        
        print(f"  💡 Manual search needed: Google '{search_query}'")
        
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
    
    return None

def try_manual_url(title):
    """Provide instructions for manual poster URL entry."""
    print(f"  📝 To manually add poster:")
    print(f"     1. Find poster at: https://www.hallmarkchannel.com/hallmark-countdown-to-christmas")
    print(f"     2. Or Google: '{title} hallmark 2025 poster'")
    print(f"     3. Save URL and we'll download it")
    return None

def main():
    """Main script to scrape and convert movie posters."""
    
    # Load movies data
    script_dir = Path(__file__).parent
    movies_file = script_dir / 'data' / 'movies.json'
    
    with open(movies_file, 'r') as f:
        data = json.load(f)
    
    movies = data['movies']
    
    # Create output directory
    output_dir = script_dir / 'images' / '1bit'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temp directory for downloads
    temp_dir = script_dir / 'temp_posters'
    temp_dir.mkdir(exist_ok=True)
    
    # Only process missing movies
    missing_movies = []
    for movie in movies:
        expected_filename = movie['image'].split('/')[-1]
        output_path = output_dir / expected_filename
        if not output_path.exists():
            missing_movies.append(movie)
    
    if not missing_movies:
        print("✅ All posters already downloaded!")
        return
    
    print(f"📽️  Found {len(missing_movies)} missing posters\n")
    
    success_count = 0
    fail_count = 0
    
    for i, movie in enumerate(missing_movies, 1):
        title = movie['title']
        expected_filename = movie['image'].split('/')[-1]
        output_path = output_dir / expected_filename
        
        print(f"[{i}/{len(missing_movies)}] {title}")
        
        # Try TMDB first
        print(f"  🔍 Searching TMDB...")
        poster_url = search_tmdb(title)
        
        # Try alternate year
        if not poster_url:
            print(f"  🔍 Trying TMDB with 2024...")
            poster_url = search_tmdb(title, 2024)
        
        if poster_url:
            # Download poster
            temp_file = temp_dir / f"temp_{i}.jpg"
            print(f"  ⬇️  Downloading poster...")
            
            if download_image(poster_url, temp_file):
                # Convert to 1-bit
                print(f"  🔄 Converting to 1-bit PNG...")
                if convert_to_1bit(temp_file, output_path):
                    print(f"  ✅ Saved: {expected_filename}")
                    success_count += 1
                    temp_file.unlink()
                else:
                    fail_count += 1
            else:
                fail_count += 1
        else:
            print(f"  ❌ Not found on TMDB")
            try_manual_url(title)
            fail_count += 1
        
        print()
    
    # Cleanup temp directory
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    print("\n" + "="*50)
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"❌ Still missing: {fail_count}")
    print(f"📊 Total missing: {len(missing_movies)}")
    print("="*50)
    
    if fail_count > 0:
        print(f"\n💡 For missing posters, visit:")
        print(f"   https://www.hallmarkchannel.com/hallmark-countdown-to-christmas")
        print(f"   Or search Google Images for each title + 'hallmark 2025 poster'")

if __name__ == "__main__":
    main()
