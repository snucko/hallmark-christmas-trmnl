# Hallmark Christmas Movies TRMNL Plugin

A TRMNL e-ink display plugin that shows the 2025 Hallmark "Countdown to Christmas" movie schedule with support for 1-bit movie poster images.

## Overview

This plugin displays the complete Hallmark Christmas 2025 movie schedule from October 17 through December 25, 2025. It automatically filters to show only upcoming movies based on the current date.

## Features

- **Automatic date filtering**: Only shows upcoming movies
- **Four display layouts**: Full, Half Horizontal, Half Vertical, and Quadrant
- **Movie posters**: Support for 1-bit converted movie poster images
- **Static data**: No external API required - all data stored in `data/movies.json`
- **Premiere indicators**: Highlights new movie premieres
- **Channel information**: Shows which Hallmark channel each movie airs on

## Directory Structure

```
hallmark/
├── .trmnlp.yml              # TRMNL configuration
├── README.md                # This file
├── Hallmark Christmas 2025.pdf  # Source schedule PDF
├── hallmark_build.py        # PDF parser script (reference)
├── data/
│   └── movies.json          # Complete movie schedule
├── images/
│   └── 1bit/                # 1-bit converted movie posters
│       ├── movie-title-1.png
│       └── ...
└── src/
    ├── settings.yml         # Plugin metadata
    ├── full.liquid          # Full screen layout (800×480)
    ├── half_horizontal.liquid  # Half horizontal (800×240)
    ├── half_vertical.liquid    # Half vertical (400×480)
    └── quadrant.liquid      # Quadrant layout (400×240)
```

## Layout Specifications

### Full (800×480)
- Shows 6 upcoming movies
- Grid layout: 2 columns × 3 rows
- Displays: Poster (80×120), title, date/time, channel, stars, premiere badge

### Half Horizontal (800×240)
- Shows 4 upcoming movies
- Single row horizontal layout
- Compact: Thumbnail (60×90), title, time, premiere badge

### Half Vertical (400×480)
- Shows 6 upcoming movies
- Vertical stack layout
- Displays: Small poster (50×75), title, date/time, premiere badge

### Quadrant (400×240)
- Shows 1-2 featured movies
- "Tonight's Movie" emphasis when available
- Large poster (100×150), title, time, channel, "Next Up" preview

## Data Format

The `data/movies.json` file contains:

```json
{
  "season": "2025 Countdown to Christmas",
  "start_date": "2025-10-17",
  "end_date": "2025-12-25",
  "movies": [
    {
      "title": "Movie Title",
      "date": "2025-10-18",
      "time": "20:00",
      "channel": "Hallmark Channel",
      "duration_minutes": 120,
      "description": "Movie description",
      "stars": "Actor Name, Actor Name",
      "premiere": true,
      "image": "images/1bit/movie-title.png"
    }
  ]
}
```

## Image Preparation

Movie posters should be converted to 1-bit (black & white) PNG format for optimal e-ink display:

### Using ImageMagick:
```bash
convert poster.jpg -resize 200x300 -colorspace Gray -ordered-dither o8x8 images/1bit/movie-title.png
```

### Using Python PIL:
```python
from PIL import Image

def convert_to_1bit(input_path, output_path):
    img = Image.open(input_path)
    img = img.resize((200, 300))
    img = img.convert('1')
    img.save(output_path)
```

### Image Naming Convention:
- Lowercase
- Replace spaces with hyphens
- Example: "Holiday Touchdown: A Bills Love Story" → `holiday-touchdown-a-bills-love-story.png`

## Local Development

1. **Test locally using Docker:**
   ```bash
   docker run --rm -it -p 4567:4567 -v "$(pwd):/plugin" trmnl/trmnlp serve
   ```

2. **View layouts:**
   - Full: http://localhost:4567/full
   - Half Horizontal: http://localhost:4567/half_horizontal
   - Half Vertical: http://localhost:4567/half_vertical
   - Quadrant: http://localhost:4567/quadrant

## Deployment to TRMNL

1. Create a private plugin on [usetrmnl.com](https://usetrmnl.com)
2. Upload template files from `src/` directory
3. Upload `movies.json` to the data directory
4. Upload movie poster images (if platform supports)
5. Configure update interval (default: 3600 seconds / 1 hour)

## Movie Schedule Coverage

**Season**: 2025 Countdown to Christmas  
**Dates**: October 17, 2025 - December 25, 2025  
**Total Movies**: 28 movies and series  
**Channels**: Hallmark Channel

### Included Content:
- Feature Films (2-hour movies)
- Series (Mistletoe Murders, Twelve Dates 'Til Christmas)
- Competition Shows (Finding Mr. Christmas, Baked With Love: Holiday)

## How It Works

1. Templates read the current date using Liquid: `{{ "now" | date: "%Y-%m-%d" }}`
2. Movies are filtered to show only upcoming dates: `movie.date >= today`
3. Display updates hourly to show current schedule
4. Past movies automatically removed from display

## Customization

- **Update frequency**: Modify `update_interval` in `src/settings.yml`
- **Number of movies shown**: Adjust `limit` values in template files
- **Styling**: Customize CSS in each `.liquid` template file
- **Time zone**: Change `time_zone` in `.trmnlp.yml`

## Credits

- **Source**: Hallmark Channel 2025 Programming Guide
- **Plugin Author**: Christmas Movie Fan
- **Version**: 1.0.0

## Notes

- This plugin uses static data - no external API calls
- Movies.json was generated from the official Hallmark 2025 schedule PDF
- Images are placeholders until actual poster images are added
- All times are in 24-hour format (converted to 12-hour in templates)
- Dates in YYYY-MM-DD format for proper sorting

## Future Enhancements

- [ ] Add countdown timer to next premiere
- [ ] Highlight "Tonight's Movie" with special styling
- [ ] Include movie ratings/reviews
- [ ] Add "Watched" tracking functionality
- [ ] Color-code by channel (if TRMNL supports)
