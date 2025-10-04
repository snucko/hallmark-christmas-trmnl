#!/usr/bin/env python3
"""
Hallmark Christmas Movies Schedule Parser

One-time script to build movies.json from Hallmark PDF schedule.
NOTE: movies.json has already been created from the official 2025 schedule.
This script is provided as reference for future updates.

Usage:
    python hallmark_build.py

Outputs:
    data/movies.json - Full season schedule in structured format
"""

import json
import re
from pathlib import Path
from datetime import datetime

def normalize_date(date_str, year=2025):
    """
    Convert various date formats to YYYY-MM-DD
    
    Examples:
        'Friday, October 18' -> '2025-10-18'
        'October 18' -> '2025-10-18'
        'Oct 18' -> '2025-10-18'
    """
    try:
        # Try full format with day name
        date_obj = datetime.strptime(f"{date_str}, {year}", "%A, %B %d, %Y")
    except ValueError:
        try:
            # Try without day name
            date_obj = datetime.strptime(f"{date_str}, {year}", "%B %d, %Y")
        except ValueError:
            try:
                # Try abbreviated month
                date_obj = datetime.strptime(f"{date_str}, {year}", "%b %d, %Y")
            except ValueError:
                return None
    
    return date_obj.strftime("%Y-%m-%d")


def normalize_time(time_str):
    """
    Convert various time formats to 24-hour HH:MM
    
    Examples:
        '8 PM ET/PT' -> '20:00'
        '8/7c' -> '20:00'
        '6 PM' -> '18:00'
        '9/8c' -> '21:00'
    """
    # Extract first number (Eastern time)
    match = re.search(r'(\d+)', time_str)
    if not match:
        return "20:00"  # Default to 8 PM
    
    hour = int(match.group(1))
    
    # Convert to 24-hour format
    if 'PM' in time_str.upper() or hour <= 12:
        if hour < 12:
            hour += 12
        elif 'AM' in time_str.upper():
            hour = hour if hour != 12 else 0
    
    return f"{hour:02d}:00"


def generate_image_filename(title):
    """
    Convert movie title to image filename
    
    Examples:
        'Holiday Touchdown: A Chiefs Love Story' -> 'holiday-touchdown-a-chiefs-love-story.png'
        'Trivia at St. Nick\'s' -> 'trivia-at-st-nicks.png'
    """
    # Convert to lowercase
    filename = title.lower()
    
    # Remove apostrophes
    filename = filename.replace("'", "")
    
    # Replace special characters and spaces with hyphens
    filename = re.sub(r'[^a-z0-9]+', '-', filename)
    
    # Remove leading/trailing hyphens
    filename = filename.strip('-')
    
    return f"images/1bit/{filename}.png"


def parse_pdf(pdf_path):
    """
    Extract movie data from PDF
    
    NOTE: This is a reference implementation. The actual movies.json
    was created from the official Hallmark website and programming guide.
    
    To implement PDF parsing, use a library like:
    - pdfplumber: for text extraction with layout awareness
    - PyPDF2: for basic text extraction
    
    Example:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Parse text looking for patterns:
                # - Date headers: "Friday, October 18"
                # - Time slots: "8/7c", "8 PM ET/PT"
                # - Movie titles (usually bold/larger)
                # - Channels: "Hallmark Channel"
                # - Stars: "Starring: Name, Name"
    """
    print("PDF parsing not implemented - movies.json already exists")
    print("This function is provided as reference for future updates")
    
    return []


def build_movies_json(output_path="data/movies.json"):
    """
    Main function to create movies.json
    
    Since movies.json already exists from the official schedule,
    this function demonstrates the expected structure.
    """
    
    # Check if movies.json already exists
    if Path(output_path).exists():
        print(f"✓ {output_path} already exists")
        with open(output_path, 'r') as f:
            data = json.load(f)
            print(f"✓ Contains {len(data['movies'])} movies")
            print(f"✓ Season: {data['season']}")
            print(f"✓ Date range: {data['start_date']} to {data['end_date']}")
        return
    
    # Example structure for building from scratch
    schedule = {
        "season": "2025 Countdown to Christmas",
        "start_date": "2025-10-17",
        "end_date": "2025-12-25",
        "movies": []
    }
    
    # In a real implementation, parse PDF here
    movies_data = parse_pdf("Hallmark Christmas 2025.pdf")
    
    # Process each movie
    for movie in movies_data:
        schedule["movies"].append({
            "title": movie.get("title"),
            "date": normalize_date(movie.get("date")),
            "time": normalize_time(movie.get("time")),
            "channel": movie.get("channel", "Hallmark Channel"),
            "duration_minutes": movie.get("duration", 120),
            "description": movie.get("description", ""),
            "stars": movie.get("stars", ""),
            "premiere": movie.get("premiere", True),
            "image": generate_image_filename(movie.get("title"))
        })
    
    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"✓ Created {output_path}")


if __name__ == "__main__":
    print("Hallmark Christmas Movies Schedule Builder")
    print("=" * 50)
    
    # Example usage of utility functions
    print("\nExample conversions:")
    print(f"Date: 'Friday, October 18' -> {normalize_date('Friday, October 18')}")
    print(f"Time: '8/7c' -> {normalize_time('8/7c')}")
    print(f"Time: '8 PM ET/PT' -> {normalize_time('8 PM ET/PT')}")
    print(f"Image: 'Holiday Touchdown' -> {generate_image_filename('Holiday Touchdown: A Chiefs Love Story')}")
    
    print("\n" + "=" * 50)
    build_movies_json()
    
    print("\n✓ All done! Movies data is ready.")
    print("\nNext steps:")
    print("1. Convert movie posters to 1-bit PNG format")
    print("2. Save images to images/1bit/ directory")
    print("3. Test templates with: docker run --rm -it -p 4567:4567 -v \"$(pwd):/plugin\" trmnl/trmnlp serve")
