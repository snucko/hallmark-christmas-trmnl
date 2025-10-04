# Hallmark Christmas Movies TRMNL Plugin - Complete Specification

## Project Overview
A TRMNL plugin to display the 2024/2025 Hallmark Christmas movie schedule with 1-bit (black & white) movie poster images.

## Key Differences from NFL Plugin
- **One-time data extraction**: Parse PDF once to create movies.json
- **No live API**: Data is static for the season
- **Weekly rotation**: Display changes based on current date, reading from pre-built JSON
- **Image support**: Include 1-bit movie posters

## Directory Structure
```
hallmark-christmas/
├── .trmnlp.yml              # TRMNL config
├── README.md                # Plugin documentation
├── Hallmark Christmas 2025.pdf  # Source data (copy from nfl dir)
├── hallmark_build.py        # One-time PDF parser to create JSON
├── data/
│   └── movies.json          # Generated movie schedule
├── images/
│   └── 1bit/                # 1-bit converted movie posters
│       ├── movie-title-1.png
│       ├── movie-title-2.png
│       └── ...
└── src/
    ├── settings.yml         # Plugin metadata
    ├── full.liquid          # Full screen layout (800×480)
    ├── half_horizontal.liquid  # Half horizontal (800×240)
    ├── half_vertical.liquid    # Half vertical (400×480)
    └── quadrant.liquid      # Quadrant layout (400×240)
```

## Data Format (movies.json)

```json
{
  "season": "2024-2025 Countdown to Christmas",
  "start_date": "2024-10-18",
  "end_date": "2024-12-25",
  "movies": [
    {
      "title": "Trivia at St. Nick's",
      "date": "2024-10-18",
      "time": "20:00",
      "channel": "Hallmark Channel",
      "duration_minutes": 120,
      "description": "A fun trivia night at a local pub",
      "stars": "Tammin Sursok, Brant Daugherty",
      "premiere": true,
      "image": "images/1bit/trivia-at-st-nicks.png"
    },
    {
      "title": "Holiday Touchdown: A Chiefs Love Story",
      "date": "2024-11-30",
      "time": "20:00",
      "channel": "Hallmark Channel",
      "duration_minutes": 120,
      "description": "Romance meets football",
      "stars": "Hunter King, Tyler Hynes",
      "premiere": true,
      "image": "images/1bit/holiday-touchdown.png"
    }
  ]
}
```

## hallmark_build.py - PDF Parser Script

### Purpose
One-time script to extract movie data from the PDF and create movies.json

### Key Functions Needed
1. **PDF Reading**: Use PyPDF2 or pdfplumber to extract text
2. **Data Parsing**: Extract movie titles, dates, times, channels, stars
3. **JSON Generation**: Create structured movies.json
4. **Image Preparation**: Instructions for converting posters to 1-bit

### Expected PDF Structure
- Movie listings by date
- Each entry has: Title, Date, Time, Channel, Stars/Description
- May span multiple pages
- Dates likely in format: "Friday, October 18" or similar

### Script Requirements
```python
#!/usr/bin/env python3
"""
One-time script to build movies.json from Hallmark PDF schedule.

Usage:
    python hallmark_build.py

Outputs:
    data/movies.json - Full season schedule
"""

import json
import re
from pathlib import Path
# import pdfplumber or PyPDF2

def parse_pdf(pdf_path):
    """Extract movie data from PDF"""
    # Read PDF
    # Parse text looking for patterns:
    #   - Movie titles (usually bold/larger)
    #   - Dates (Friday, October 18)
    #   - Times (8 PM ET/PT)
    #   - Channels (Hallmark Channel, Hallmark Mystery, etc.)
    #   - Stars/Description
    pass

def normalize_date(date_str, year=2024):
    """Convert 'Friday, October 18' to '2024-10-18'"""
    pass

def normalize_time(time_str):
    """Convert '8 PM ET/PT' to '20:00'"""
    pass

def generate_image_filename(title):
    """Convert 'Movie Title' to 'movie-title.png'"""
    pass

def build_movies_json():
    """Main function to create movies.json"""
    pass

if __name__ == "__main__":
    build_movies_json()
```

## Liquid Template Strategy

### Current Week/Day Detection
Each template needs to:
1. Get current date from `{{ "now" | date: "%Y-%m-%d" }}`
2. Filter movies to show upcoming/current week
3. Display appropriate number based on layout size

### Template Structure Pattern
```liquid
{% comment %}Get current date{% endcomment %}
{% assign today = "now" | date: "%Y-%m-%d" %}

{% comment %}Load movie data{% endcomment %}
{% assign schedule_data = site.data.movies %}

{% comment %}Filter to current week or upcoming{% endcomment %}
{% assign upcoming_movies = schedule_data.movies | where_exp: "movie", "movie.date >= today" %}

{% comment %}Display movies{% endcomment %}
<div class="plugin">
  <h1>Hallmark Christmas Movies</h1>
  {% for movie in upcoming_movies limit: 6 %}
    <div class="movie">
      {% if movie.image %}
        <img src="{{ movie.image }}" alt="{{ movie.title }}">
      {% endif %}
      <h2>{{ movie.title }}</h2>
      <p>{{ movie.date | date: "%a, %b %d" }} at {{ movie.time }}</p>
      <p>{{ movie.channel }}</p>
    </div>
  {% endfor %}
</div>
```

## Layout Specifications

### Full (800×480)
- Show 4-6 upcoming movies
- Display: Small poster image (100×150), title, date/time, channel, stars
- Grid layout: 2 columns × 3 rows

### Half Horizontal (800×240)  
- Show 3-4 movies
- Compact: Poster thumbnail (60×90), title, "Tonight 8PM" style time
- Single row, horizontal scroll

### Half Vertical (400×480)
- Show 5-6 movies
- Vertical list: Small poster, title, date/time
- Stack vertically

### Quadrant (400×240)
- Show 1-2 featured movies
- Large layout for "Tonight's Movie"
- Bigger poster (120×180), title, time only

## 1-bit Image Conversion

### Requirements
- Movie posters must be converted to 1-bit (black & white) for e-ink display
- Recommended size: ~200×300 pixels (3:4.5 ratio)
- Format: PNG with 1-bit color depth

### Conversion Process
Use ImageMagick or Python PIL:

```bash
# ImageMagick command
convert poster.jpg -resize 200x300 -colorspace Gray -ordered-dither o8x8 output-1bit.png
```

```python
# Python PIL approach
from PIL import Image

def convert_to_1bit(input_path, output_path):
    img = Image.open(input_path)
    img = img.resize((200, 300))
    img = img.convert('1')  # 1-bit
    img.save(output_path)
```

### Image Naming Convention
- Lowercase
- Replace spaces with hyphens
- Example: "Holiday Touchdown: A Chiefs Love Story" → "holiday-touchdown-a-chiefs-love-story.png"

## .trmnlp.yml Configuration

```yaml
# TRMNL Plugin Configuration
---
watch:
  - src
  - data
  - images

time_zone: America/New_York

custom_fields: {}

variables:
  trmnl:
    user:
      name: Christmas Movie Fan
    plugin_settings:
      instance_name: Hallmark Christmas
```

## settings.yml Configuration

```yaml
---
plugin_name: Hallmark Christmas Movies
description: Display the 2024-2025 Hallmark Christmas movie schedule
version: 1.0.0
author: Christmas Movie Fan

custom_fields: []

# No external data source needed - static JSON
data_sources: []

# Update display every hour to show current/upcoming
update_interval: 3600

layouts:
  - full
  - half_horizontal
  - half_vertical
  - quadrant
```

## Development Workflow

1. **Initial Setup** (one time):
   ```bash
   mkdir hallmark-christmas
   cd hallmark-christmas
   cp ../nfl/Hallmark\ Christmas\ 2025.pdf .
   mkdir -p data images/1bit src
   ```

2. **Parse PDF** (one time):
   ```bash
   python hallmark_build.py
   # Outputs: data/movies.json
   ```

3. **Prepare Images** (one time):
   - Download/acquire movie posters
   - Convert to 1-bit PNG
   - Save to images/1bit/
   - Update movies.json with correct image paths

4. **Create Templates**:
   - Build Liquid templates in src/
   - Templates read data/movies.json
   - Filter by current date
   - Display upcoming movies

5. **Test Locally**:
   ```bash
   docker run --rm -it -p 4567:4567 -v "$(pwd):/plugin" trmnl/trmnlp serve
   open http://localhost:4567/full
   ```

6. **Deploy to TRMNL**:
   - Create private plugin on usetrmnl.com
   - Upload template files from src/
   - Upload movies.json to data/
   - Upload images (if platform supports)

## Data Extraction Hints from PDF

### Expected PDF Patterns
- **Date headers**: "Friday, October 18", "Saturday, November 30"
- **Time format**: "8/7c" (8 PM Eastern/7 Central) or "8 PM ET/PT"
- **Channel indicators**: "Hallmark Channel", "Hallmark Movies & Mysteries"
- **Movie titles**: Often in bold or larger font
- **Premiere indicators**: "PREMIERE" badge or text
- **Stars**: "Starring: Name, Name"

### Parsing Strategy
1. Split PDF into sections by date
2. Within each date section, identify:
   - Time slots
   - Movie title (usually first bold text)
   - Channel (scan for "Hallmark Channel" etc.)
   - Stars (look for "Starring:" prefix)
3. Handle edge cases:
   - Multi-day airings
   - Encore presentations
   - Special time slots

## Important Notes

1. **Static Data**: Unlike NFL plugin, this doesn't fetch live data - it's pre-generated
2. **Date-based Display**: Templates filter movies based on current date
3. **Season Scope**: Only covers Oct 2024 - Dec 2024 (adjust dates in script)
4. **Image Optimization**: Keep 1-bit images small (<50KB each) for fast loading
5. **No External API**: Everything is self-contained in the plugin

## Testing Checklist

- [ ] PDF successfully parsed to JSON
- [ ] All movie dates in correct format (YYYY-MM-DD)
- [ ] All times in 24-hour format (HH:MM)
- [ ] Images converted to 1-bit PNG
- [ ] Image paths correct in JSON
- [ ] Full layout shows 4-6 movies
- [ ] Half horizontal shows 3-4 movies
- [ ] Half vertical shows 5-6 movies
- [ ] Quadrant shows 1-2 featured movies
- [ ] Current date filtering works
- [ ] Past movies don't show
- [ ] Display updates as weeks progress

## Future Enhancements

- Add countdown timer to next premiere
- Highlight "Tonight's Movie"
- Color-code by channel (if TRMNL supports)
- Add "Watched" checkbox functionality
- Include movie ratings/reviews

---

## File Locations Reference

**Source PDF**: `/Users/unknown1/Downloads/nfl/Hallmark Christmas 2025.pdf`

**New Project Directory**: Create at `/Users/unknown1/Downloads/hallmark-christmas/`

**No files from NFL plugin are reused** - build everything fresh for clean separation.
