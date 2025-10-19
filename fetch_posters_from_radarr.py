#!/usr/bin/env python3
"""
Fetch movie posters from Radarr for Hallmark Christmas movies.
Radarr downloads posters from TMDB when movies are added.
"""

import requests
import re
import sys
from pathlib import Path

# Add parent directory to import path
sys.path.insert(0, str(Path(__file__).parent.parent / 'raddarr'))

try:
    from sync_radarr_tags_from_letterboxd import RADARR_API_KEY, RADARR_BASE_URL
except ImportError:
    print("❌ Could not import Radarr credentials from ../raddarr/")
    print("   Make sure sync_radarr_tags_from_letterboxd.py exists")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

HEADERS = {
    "X-Api-Key": RADARR_API_KEY,
    "Content-Type": "application/json"
}

# TMDB IDs to search for
HALLMARK_TMDB_IDS = [
    1535223, 1538155, 1547885, 1537560, 1537081, 1547913,
    1537084, 1547915, 1485002, 1547917, 1547918, 1547920,
    1546001, 1535221, 1547922, 1545999, 1516208, 1545997,
    1547925, 1547926, 1547927, 1547929, 1547882, 1547921
]

def title_to_filename(title):
    """Convert title to filename format."""
    filename = title.lower()
    filename = re.sub(r"[^\w\s-]", "", filename)
    filename = re.sub(r"[-\s]+", "-", filename)
    return filename.strip('-') + '.png'

def get_radarr_movies():
    """Get all movies from Radarr."""
    print("🎬 Fetching movies from Radarr...")
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/movie", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def download_image(url, output_path):
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
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

def main():
    """Fetch posters from Radarr."""
    
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'images' / '1bit'
    temp_dir = script_dir / 'temp_radarr'
    temp_dir.mkdir(exist_ok=True)
    
    print("🎄 Fetching Hallmark Posters from Radarr\n")
    
    # Get all movies from Radarr
    all_movies = get_radarr_movies()
    
    # Filter Hallmark movies
    hallmark_movies = [m for m in all_movies if m.get('tmdbId') in HALLMARK_TMDB_IDS]
    
    print(f"📽️  Found {len(hallmark_movies)} Hallmark movies in Radarr\n")
    
    success = 0
    skipped = 0
    failed = 0
    
    for movie in hallmark_movies:
        title = movie.get('title')
        filename = title_to_filename(title)
        output_path = output_dir / filename
        
        print(f"[{title}]")
        
        # Skip if exists
        if output_path.exists():
            print(f"  ✓ Already exists\n")
            skipped += 1
            continue
        
        # Get poster URL from Radarr
        images = movie.get('images', [])
        poster_url = None
        
        for image in images:
            if image.get('coverType') == 'poster':
                # Try remote URL first
                poster_url = image.get('remoteUrl')
                if not poster_url:
                    # Try local URL
                    poster_url = image.get('url')
                    if poster_url and not poster_url.startswith('http'):
                        poster_url = f"{RADARR_BASE_URL}{poster_url}"
                break
        
        if not poster_url:
            print(f"  ❌ No poster URL found in Radarr\n")
            failed += 1
            continue
        
        # Download poster
        print(f"  ⬇️  Downloading from Radarr...")
        temp_file = temp_dir / f"temp_{movie.get('tmdbId')}.jpg"
        
        if not download_image(poster_url, temp_file):
            failed += 1
            continue
        
        # Convert to 1-bit
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
    print(f"📊 Total: {len(hallmark_movies)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
