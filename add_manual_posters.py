#!/usr/bin/env python3
"""
Manual poster URL downloader - paste URLs for missing posters.
"""

import urllib.request
import ssl
from pathlib import Path
from PIL import Image

# Create SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Missing movie posters and their filenames
MISSING_POSTERS = {
    "mistletoe-murders.png": "https://",
    "finding-mr-christmas.png": "https://",
    "baked-with-love-holiday.png": "https://",
    "a-keller-christmas-vacation.png": "https://",
    "three-wisest-men.png": "https://",
    "tidings-for-the-season.png": "https://",
    "we-met-in-december.png": "https://",
    "the-more-the-merrier.png": "https://",
    "a-grand-ole-opry-christmas.png": "https://",
    "the-christmas-cup.png": "https://",
    "christmas-at-the-catnip-cafe.png": "https://",
    "twelve-dates-til-christmas.png": "https://",
    "shes-making-a-list.png": "https://",
    "single-on-the-25th.png": "https://",
    "a-suite-holiday-romance.png": "https://",
    "oy-to-the-world.png": "https://",
    "a-make-or-break-holiday.png": "https://",
}

def download_image(url, output_path):
    """Download image from URL."""
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
        print(f"  Error: {e}")
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
        print(f"  Conversion error: {e}")
        return False

def main():
    """Process manual poster URLs."""
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'images' / '1bit'
    temp_dir = script_dir / 'temp_manual'
    temp_dir.mkdir(exist_ok=True)
    
    print("Manual Poster Downloader")
    print("=" * 50)
    print("\nMissing posters:")
    for i, filename in enumerate(MISSING_POSTERS.keys(), 1):
        print(f"{i}. {filename}")
    
    print("\n" + "=" * 50)
    print("To add URLs, edit this script and replace https:// with actual URLs")
    print("Then run: python3 add_manual_posters.py")
    print("=" * 50)
    
    success = 0
    skipped = 0
    failed = 0
    
    for filename, url in MISSING_POSTERS.items():
        output_path = output_dir / filename
        
        # Skip if already exists
        if output_path.exists():
            skipped += 1
            continue
            
        # Skip if no URL provided
        if url == "https://":
            continue
        
        print(f"\nProcessing: {filename}")
        print(f"  Downloading from: {url}")
        
        temp_file = temp_dir / f"temp_{filename}.jpg"
        if download_image(url, temp_file):
            print(f"  Converting to 1-bit...")
            if convert_to_1bit(temp_file, output_path):
                print(f"  ✅ Saved!")
                success += 1
                temp_file.unlink()
            else:
                failed += 1
        else:
            failed += 1
    
    # Cleanup
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    print("\n" + "=" * 50)
    print(f"✅ Success: {success}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Pending: {17 - success - skipped}")
    print("=" * 50)

if __name__ == "__main__":
    main()
