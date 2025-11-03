#!/usr/bin/env python3
"""
Script to filter movies.json to only include upcoming movies (date >= today).

This ensures the GitHub-hosted data only contains relevant movies for the TRMNL plugin.
"""

import json
from pathlib import Path
from datetime import datetime

def update_movies_json():
    """Filter movies.json to only include upcoming movies"""
    data_file = Path(__file__).parent / "data" / "movies.json"

    # Load existing data
    with open(data_file, 'r') as f:
        data = json.load(f)

    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Filtering movies for dates >= {today}")

    # Filter movies
    original_count = len(data["movies"])
    upcoming_movies = [movie for movie in data["movies"] if movie["date"] >= today]
    data["movies"] = upcoming_movies

    print(f"Filtered {original_count} movies down to {len(upcoming_movies)} upcoming movies")

    # Save back to file
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Updated {data_file}")

if __name__ == "__main__":
    update_movies_json()
