#!/usr/bin/env python3
"""
Add Hallmark Christmas movies to Radarr using TMDB IDs.
"""

import requests
import json

RADARR_API_KEY = "e0c08c9df42e4ba3af5d81ce9f98da01"  # Will be replaced with actual key
RADARR_BASE_URL = "http://192.168.0.215:8310"
TAG_LABEL = "hallmark-christmas-2025"

HEADERS = {
    "X-Api-Key": RADARR_API_KEY,
    "Content-Type": "application/json"
}

# Movies to add to Radarr
HALLMARK_MOVIES = [
    {"tmdb_id": 1535223, "imdb_id": "tt36364046", "title": "A Royal Montana Christmas", "year": 2025},
    {"tmdb_id": 1538155, "imdb_id": "tt36503047", "title": "A Christmas Angel Match", "year": 2025},
    {"tmdb_id": 1547885, "imdb_id": "tt37133902", "title": "Christmas on Duty", "year": 2025},
    {"tmdb_id": 1537560, "imdb_id": "tt36491858", "title": "A Newport Christmas", "year": 2025},
    {"tmdb_id": 1537081, "imdb_id": "tt38183872", "title": "Christmas Above the Clouds", "year": 2025},
    {"tmdb_id": 1547913, "imdb_id": "tt38353730", "title": "A Keller Christmas Vacation", "year": 2025},
    {"tmdb_id": 1537084, "imdb_id": "tt38353919", "title": "Three Wisest Men", "year": 2025},
    {"tmdb_id": 1547915, "imdb_id": "tt38353925", "title": "Tidings For The Season", "year": 2025},
    {"tmdb_id": 1485002, "imdb_id": "tt36604797", "title": "Holiday Touchdown: A Bills Love Story", "year": 2025},
    {"tmdb_id": 1547917, "imdb_id": "tt37333639", "title": "Melt My Heart This Christmas", "year": 2025},
    {"tmdb_id": 1547918, "imdb_id": "tt38354934", "title": "We Met in December", "year": 2025},
    {"tmdb_id": 1547920, "imdb_id": "tt38354943", "title": "The Snow Must Go On", "year": 2025},
    {"tmdb_id": 1546001, "imdb_id": "tt38354960", "title": "The More the Merrier", "year": 2025},
    {"tmdb_id": 1535221, "imdb_id": "tt37891014", "title": "A Grand Ole Opry Christmas", "year": 2025},
    {"tmdb_id": 1547922, "imdb_id": "tt35180266", "title": "The Christmas Cup", "year": 2025},
    {"tmdb_id": 1545999, "imdb_id": "tt37985000", "title": "Christmas at the Catnip Cafe", "year": 2025},
    {"tmdb_id": 1516208, "imdb_id": "tt38354965", "title": "She's Making a List", "year": 2025},
    {"tmdb_id": 1545997, "imdb_id": "tt38347292", "title": "Single on the 25th", "year": 2025},
    {"tmdb_id": 1547925, "imdb_id": "tt38354975", "title": "A Suite Holiday Romance", "year": 2025},
    {"tmdb_id": 1547926, "imdb_id": "tt38354983", "title": "Oy to the World", "year": 2025},
    {"tmdb_id": 1547927, "imdb_id": "tt38354998", "title": "A Make or Break Holiday", "year": 2025},
    {"tmdb_id": 1547929, "imdb_id": "tt38355006", "title": "The Christmas Baby", "year": 2025},
    {"tmdb_id": 1547882, "imdb_id": "tt37263154", "title": "Merry Christmas, Ted Cooper!", "year": 2025},
    {"tmdb_id": 1547921, "imdb_id": "tt36836189", "title": "An Alpine Holiday", "year": 2025},
]

def get_root_folders():
    """Get available root folders from Radarr."""
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/rootfolder", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_quality_profiles():
    """Get available quality profiles from Radarr."""
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/qualityprofile", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_existing_tags():
    """Get existing tags from Radarr."""
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/tag", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def create_tag(label):
    """Create a new tag in Radarr."""
    print(f"🏷️  Creating tag '{label}'...")
    response = requests.post(f"{RADARR_BASE_URL}/api/v3/tag", headers=HEADERS, json={"label": label})
    response.raise_for_status()
    return response.json()["id"]

def get_tag_id(label):
    """Get or create a tag ID."""
    tags = get_existing_tags()
    for tag in tags:
        if tag["label"].lower() == label.lower():
            return tag["id"]
    return create_tag(label)

def get_existing_movies():
    """Get all movies already in Radarr."""
    print("🎬 Fetching existing Radarr movies...")
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/movie", headers=HEADERS)
    response.raise_for_status()
    return {movie["tmdbId"]: movie for movie in response.json()}

def lookup_movie(tmdb_id):
    """Lookup movie details from Radarr/TMDB."""
    response = requests.get(f"{RADARR_BASE_URL}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}", headers=HEADERS)
    if response.ok:
        return response.json()
    return None

def add_movie_to_radarr(movie_data, root_folder, quality_profile_id, tag_id):
    """Add a movie to Radarr."""
    movie = lookup_movie(movie_data["tmdb_id"])
    
    if not movie:
        print(f"  ❌ Could not lookup movie in Radarr")
        return False
    
    # Prepare movie payload
    payload = {
        "title": movie.get("title"),
        "year": movie.get("year"),
        "tmdbId": movie.get("tmdbId"),
        "imdbId": movie.get("imdbId"),
        "qualityProfileId": quality_profile_id,
        "rootFolderPath": root_folder,
        "monitored": True,
        "addOptions": {
            "searchForMovie": True
        },
        "tags": [tag_id]
    }
    
    response = requests.post(f"{RADARR_BASE_URL}/api/v3/movie", headers=HEADERS, json=payload)
    
    if response.ok:
        print(f"  ✅ Added to Radarr")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def main():
    """Add all Hallmark movies to Radarr."""
    
    print("🎄 Hallmark Christmas 2025 → Radarr\n")
    
    # Get Radarr configuration
    root_folders = get_root_folders()
    quality_profiles = get_quality_profiles()
    
    if not root_folders:
        print("❌ No root folders found in Radarr")
        return
    
    # Use first root folder and quality profile
    root_folder = root_folders[0]["path"]
    quality_profile_id = quality_profiles[0]["id"]
    
    print(f"📁 Root folder: {root_folder}")
    print(f"🎯 Quality profile: {quality_profiles[0]['name']}")
    
    # Get or create tag
    tag_id = get_tag_id(TAG_LABEL)
    print(f"🏷️  Tag: {TAG_LABEL} (ID: {tag_id})\n")
    
    # Get existing movies
    existing_movies = get_existing_movies()
    
    added = 0
    skipped = 0
    failed = 0
    
    for movie_data in HALLMARK_MOVIES:
        title = movie_data["title"]
        tmdb_id = movie_data["tmdb_id"]
        
        print(f"[{title}]")
        
        # Check if already in Radarr
        if tmdb_id in existing_movies:
            print(f"  ⏭️  Already in Radarr")
            skipped += 1
            continue
        
        # Add to Radarr
        print(f"  ➕ Adding to Radarr...")
        if add_movie_to_radarr(movie_data, root_folder, quality_profile_id, tag_id):
            added += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 50)
    print(f"✅ Added: {added}")
    print(f"⏭️  Skipped (already in Radarr): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(HALLMARK_MOVIES)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
