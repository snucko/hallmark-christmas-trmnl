#!/usr/bin/env python3
"""
Download posters using TMDB movie IDs directly.
"""

import json
import urllib.request
from pathlib import Path
from PIL import Image

TMDB_API_KEY = "4adf21ca8d1da5c81cb5463d8c731367"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# TMDB IDs from Letterboxd/TMDB data
TMDB_MOVIES = [
    {"id": 1535223, "imdb_id": "tt36364046", "title": "A Royal Montana Christmas", "release_year": "2025"},
    {"id": 1538155, "imdb_id": "tt36503047", "title": "A Christmas Angel Match", "release_year": "2025"},
    {"id": 1547885, "imdb_id": "tt37133902", "title": "Christmas on Duty", "release_year": "2025"},
    {"id": 1537560, "imdb_id": "tt36491858", "title": "A Newport Christmas", "release_year": "2025"},
    {"id": 1537081, "imdb_id": "tt38183872", "title": "Christmas Above the Clouds", "release_year": "2025"},
    {"id": 1547913, "imdb_id": "tt38353730", "title": "A Keller Christmas Vacation", "release_year": "2025"},
    {"id": 1537084, "imdb_id": "tt38353919", "title": "Three Wisest Men", "release_year": "2025"},
    {"id": 1547915, "imdb_id": "tt38353925", "title": "Tidings For The Season", "release_year": "2025"},
    {"id": 1485002, "imdb_id": "tt36604797", "title": "Holiday Touchdown: A Bills Love Story", "release_year": "2025"},
    {"id": 1547917, "imdb_id": "tt37333639", "title": "Melt My Heart This Christmas", "release_year": "2025"},
    {"id": 1547918, "imdb_id": "tt38354934", "title": "We Met in December", "release_year": "2025"},
    {"id": 1547920, "imdb_id": "tt38354943", "title": "The Snow Must Go On", "release_year": "2025"},
    {"id": 1546001, "imdb_id": "tt38354960", "title": "The More the Merrier", "release_year": "2025"},
    {"id": 1535221, "imdb_id": "tt37891014", "title": "A Grand Ole Opry Christmas", "release_year": "2025"},
    {"id": 1547922, "imdb_id": "tt35180266", "title": "The Christmas Cup", "release_year": "2025"},
    {"id": 1545999, "imdb_id": "tt37985000", "title": "Christmas at the Catnip Cafe", "release_year": "2025"},
    {"id": 1516208, "imdb_id": "tt38354965", "title": "She's Making a List", "release_year": "2025"},
    {"id": 1545997, "imdb_id": "tt38347292", "title": "Single on the 25th", "release_year": "2025"},
    {"id": 1547925, "imdb_id": "tt38354975", "title": "A Suite Holiday Romance", "release_year": "2025"},
    {"id": 1547926, "imdb_id": "tt38354983", "title": "Oy to the World", "release_year": "2025"},
    {"id": 1547927, "imdb_id": "tt38354998", "title": "A Make or Break Holiday", "release_year": "2025"},
    {"id": 1547929, "imdb_id": "tt38355006", "title": "The Christmas Baby", "release_year": "2025"},
    {"id": 1547882, "imdb_id": "tt37263154", "title": "Merry Christmas, Ted Cooper!", "release_year": "2025"},
    {"id": 1547921, "imdb_id": "tt36836189", "title": "An Alpine Holiday", "release_year": "2025"},
]

def get_poster_by_tmdb_id(tmdb_id):
    """Get poster URL using TMDB movie ID."""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        poster_path = data.get('poster_path')
        if poster_path:
            return f"{TMDB_IMAGE_BASE}{poster_path}"
            
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    return None

def download_image(url, output_path):
    """Download image from URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Download error: {e}")
        return False

def convert_to_1bit(input_path, output_path, size=(200, 300)):
    """Convert image to 1-bit PNG."""
    try:
        img = Image.open(input_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        new_img = Image.new('RGB', size, 'white')
        paste_x = (size[0] - img.width) // 2
        paste_y = (size[1] - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        gray_img = new_img.convert('L')
        bw_img = gray_img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
        bw_img.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"  ⚠️  Conversion error: {e}")
        return False

def title_to_filename(title):
    """Convert title to filename format."""
    import re
    filename = title.lower()
    filename = re.sub(r"[^\w\s-]", "", filename)
    filename = re.sub(r"[-\s]+", "-", filename)
    return filename.strip('-') + '.png'

def main():
    """Download posters using TMDB IDs."""
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'images' / '1bit'
    temp_dir = script_dir / 'temp_tmdb'
    temp_dir.mkdir(exist_ok=True)
    
    print("📽️  Downloading posters using TMDB IDs\n")
    
    success = 0
    skipped = 0
    failed = 0
    
    for movie in TMDB_MOVIES:
        title = movie['title']
        tmdb_id = movie['id']
        filename = title_to_filename(title)
        output_path = output_dir / filename
        
        print(f"[{title}]")
        
        # Skip if exists
        if output_path.exists():
            print(f"  ✓ Already exists\n")
            skipped += 1
            continue
        
        # Get poster URL
        print(f"  🔍 Fetching from TMDB ID {tmdb_id}...")
        poster_url = get_poster_by_tmdb_id(tmdb_id)
        
        if not poster_url:
            print(f"  ❌ No poster found\n")
            failed += 1
            continue
        
        # Download
        temp_file = temp_dir / f"temp_{tmdb_id}.jpg"
        print(f"  ⬇️  Downloading...")
        
        if not download_image(poster_url, temp_file):
            failed += 1
            continue
        
        # Convert
        print(f"  🔄 Converting to 1-bit PNG...")
        if convert_to_1bit(temp_file, output_path):
            print(f"  ✅ Saved: {filename}\n")
            success += 1
            temp_file.unlink()
        else:
            failed += 1
    
    # Cleanup
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    print("=" * 50)
    print(f"✅ Successfully downloaded: {success}")
    print(f"⏭️  Skipped (already exist): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(TMDB_MOVIES)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
