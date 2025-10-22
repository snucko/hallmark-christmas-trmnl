#!/usr/bin/env python3
"""
Script to send Hallmark Christmas movie data to TRMNL via webhook.

This enables dynamic updates to the plugin instead of relying on static GitHub data.

Usage:
    python3 send_to_trmnl.py --uuid YOUR_PLUGIN_UUID
    python3 send_to_trmnl.py --uuid YOUR_PLUGIN_UUID --check-screen YOUR_DEVICE_API_KEY
    python3 send_to_trmnl.py --uuid YOUR_PLUGIN_UUID --test-dynamic YOUR_DEVICE_API_KEY

Requirements:
    pip install requests

Notes:
- Get the UUID from your TRMNL plugin's webhook URL field
- Get the device API key from Devices > Edit in TRMNL dashboard
"""

import json
import argparse
import requests
import time
from pathlib import Path

def load_movies_data():
    """Load movies data from data/movies.json"""
    data_file = Path(__file__).parent / "data" / "movies.json"
    with open(data_file, 'r') as f:
        data = json.load(f)

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    # Create minimal version to fit 2kb free tier limit
    # Only include upcoming movies and minimal fields
    minimal_data = {
        "season": data["season"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "movies": []
    }

    for movie in data["movies"]:
        if movie["date"] >= today:  # Only upcoming movies
            minimal_movie = {
                "title": movie["title"],
                "date": movie["date"],
                "time": movie["time"],
                "channel": movie["channel"],
                "premiere": movie.get("premiere", False),
                "image": movie["image"]
            }
            minimal_data["movies"].append(minimal_movie)
            if len(minimal_data["movies"]) >= 4:  # Limit to 4 movies for free tier
                break

    return minimal_data

def send_to_trmnl(uuid, data):
    """Send data to TRMNL webhook"""
    url = f"https://usetrmnl.com/api/custom_plugins/{uuid}"
    payload = {
        "merge_variables": data
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"Sending data to {url}")
    print(f"Payload size: {len(json.dumps(payload))} characters")

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully sent data to TRMNL")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Failed to send data. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    return True

def check_current_screen(api_key):
    """Check current screen using private API"""
    url = "https://usetrmnl.com/api/current_screen"
    headers = {
        "access-token": api_key
    }

    print("Checking current screen...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ Current screen retrieved:")
        print(f"  Status: {data.get('status')}")
        print(f"  Image URL: {data.get('image_url')}")
        print(f"  Filename: {data.get('filename')}")
        print(f"  Refresh rate: {data.get('refresh_rate')}")
        return data
    else:
        print(f"❌ Failed to get current screen. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def download_screen_image(image_url, filename):
    """Download the screen image"""
    print(f"Downloading screen image to {filename}...")
    response = requests.get(image_url)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded {len(response.content)} bytes")
        return True
    else:
        print(f"❌ Failed to download image. Status: {response.status_code}")
        return False

def test_dynamic_updates(uuid, original_data, api_key):
    """Test dynamic updates: download before, send modified data, download after"""
    print("="*60)
    print("TESTING DYNAMIC UPDATES")
    print("="*60)

    # Step 1: Download current screen (before)
    print("Step 1: Downloading current screen (BEFORE)")
    before_screen = check_current_screen(api_key)
    if not before_screen:
        return 1

    before_filename = "screen_tests/before.png"
    if not download_screen_image(before_screen['image_url'], before_filename):
        return 1

    print()

    # Step 2: Modify data and send update
    print("Step 2: Modifying data and sending update")
    modified_data = original_data.copy()
    modified_data['season'] = f"{original_data['season']} - UPDATED {int(time.time())}"

    print(f"Modified season: {modified_data['season']}")

    success = send_to_trmnl(uuid, modified_data)
    if not success:
        return 1

    # Wait for TRMNL to process and refresh
    print("Waiting 30 seconds for TRMNL to process and refresh...")
    time.sleep(30)

    print()

    # Step 3: Download new screen (after)
    print("Step 3: Downloading updated screen (AFTER)")
    after_screen = check_current_screen(api_key)
    if not after_screen:
        return 1

    after_filename = "screen_tests/after.png"
    if not download_screen_image(after_screen['image_url'], after_filename):
        return 1

    print()

    # Step 4: Compare results
    print("Step 4: Comparing results")
    print("="*60)

    print("BEFORE:")
    print(f"  Filename: {before_screen['filename']}")
    print(f"  Image URL: {before_screen['image_url'][:100]}...")

    print("\nAFTER:")
    print(f"  Filename: {after_screen['filename']}")
    print(f"  Image URL: {after_screen['image_url'][:100]}...")

    # Check if they are different
    if before_screen['filename'] != after_screen['filename']:
        print("\n✅ SUCCESS: Screen updated! Filenames are different.")
        print("The plugin is dynamically updating based on webhook data!")
    else:
        print("\n⚠️  Note: Filenames are the same - may need to wait longer for refresh")

    print(f"\nImages saved to:")
    print(f"  Before: {before_filename}")
    print(f"  After:  {after_filename}")

    return 0

def main():
    parser = argparse.ArgumentParser(description="Send movie data to TRMNL webhook")
    parser.add_argument("--uuid", required=True, help="TRMNL plugin UUID from webhook URL")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without actually sending")
    parser.add_argument("--check-screen", help="Device API key to check current screen after sending data")
    parser.add_argument("--test-dynamic", help="Device API key to test dynamic updates: download before, send modified data, download after")

    args = parser.parse_args()

    # Load the data
    try:
        data = load_movies_data()
        print(f"Loaded {len(data.get('movies', []))} movies")
    except Exception as e:
        print(f"Error loading movies data: {e}")
        return 1

    if args.dry_run:
        print("DRY RUN - Would send:")
        print(json.dumps({"merge_variables": data}, indent=2))
        return 0

    # Test dynamic updates if requested
    if args.test_dynamic:
        return test_dynamic_updates(args.uuid, data, args.test_dynamic)

    # Send to TRMNL
    success = send_to_trmnl(args.uuid, data)

    # Check current screen if API key provided
    if success and args.check_screen:
        print("\n" + "="*50)
        check_current_screen(args.check_screen)

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
