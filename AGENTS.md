# Hallmark Christmas TRMNL Plugin - Agent Reference

## Project Summary

A complete TRMNL e-ink display plugin for the 2025 Hallmark "Countdown to Christmas" movie schedule. Built from the official Hallmark programming guide with 28 movies from October 17 - December 25, 2025.

## Quick Start Commands

### Local Testing
```bash
# Start TRMNL development server
docker run --rm -it -p 4567:4567 -v "$(pwd):/plugin" trmnl/trmnlp serve

# View layouts
open http://localhost:4567/full
open http://localhost:4567/half_horizontal
open http://localhost:4567/half_vertical
open http://localhost:4567/quadrant
```

### Image Conversion (when adding posters)
```bash
# Using ImageMagick
convert poster.jpg -resize 200x300 -colorspace Gray -ordered-dither o8x8 images/1bit/movie-title.png

# Using Python (run hallmark_build.py has helper functions)
python3 -c "from PIL import Image; img = Image.open('poster.jpg').resize((200,300)).convert('1'); img.save('images/1bit/output.png')"
```

### Python Script
```bash
# Run reference builder script (movies.json already exists)
python3 hallmark_build.py
```

## Project Structure

```
hallmark/
├── .trmnlp.yml                    # TRMNL plugin config (time_zone, watch dirs)
├── README.md                      # User-facing documentation
├── AGENTS.md                      # This file - agent reference
├── HALLMARK_PLUGIN_SPEC.md        # Original specification
├── ADD.md                         # Build notes from movies.json creation
├── Hallmark Christmas 2025.pdf    # Source schedule PDF
├── hallmark_build.py              # Reference script for PDF parsing
├── data/
│   └── movies.json                # Complete schedule data (28 movies)
├── images/
│   └── 1bit/                      # Movie posters (1-bit PNG, not yet added)
└── src/
    ├── settings.yml               # Plugin metadata
    ├── full.liquid                # 800×480 layout (6 movies, 2×3 grid)
    ├── half_horizontal.liquid     # 800×240 layout (4 movies, horizontal)
    ├── half_vertical.liquid       # 400×480 layout (6 movies, vertical)
    └── quadrant.liquid            # 400×240 layout (1-2 featured movies)
```

## Data Format

### movies.json Structure
```json
{
  "season": "2025 Countdown to Christmas",
  "start_date": "2025-10-17",
  "end_date": "2025-12-25",
  "movies": [
    {
      "title": "Movie Title",
      "date": "2025-10-18",           // YYYY-MM-DD format
      "time": "20:00",                 // 24-hour format
      "channel": "Hallmark Channel",
      "duration_minutes": 120,         // 120 for movies, 60 for series
      "description": "Plot description",
      "stars": "Actor Name, Actor Name",
      "premiere": true,                // Boolean for premiere badge
      "image": "images/1bit/movie-title.png"
    }
  ]
}
```

## How Templates Work

### Date Filtering Logic
All templates use this pattern:
```liquid
{% assign today = "now" | date: "%Y-%m-%d" %}
{% assign schedule_data = site.data.movies %}
{% assign upcoming_movies = schedule_data.movies | where_exp: "movie", "movie.date >= today" %}
```

### Time Conversion
Templates convert 24-hour to 12-hour display:
```liquid
{{ movie.time | replace: ":00", "" | replace: "20", "8 PM" | replace: "21", "9 PM" | replace: "18", "6 PM" }}
```

### Image Handling
```liquid
{% if movie.image %}
  <img src="{{ movie.image }}" alt="{{ movie.title }}">
{% else %}
  <div>🎬</div>
{% endif %}
```

## Layout Specifications

| Layout | Dimensions | Movies Shown | Key Features |
|--------|-----------|--------------|--------------|
| **Full** | 800×480 | 6 | 2×3 grid, posters (80×120), full info |
| **Half Horizontal** | 800×240 | 4 | Horizontal row, compact thumbnails (60×90) |
| **Half Vertical** | 400×480 | 6 | Vertical stack, small posters (50×75) |
| **Quadrant** | 400×240 | 1-2 | Featured movie, large poster (100×150), "Tonight" emphasis |

## Current Status

### ✅ Completed
- [x] Directory structure created
- [x] movies.json with 28 movies (Oct 17 - Dec 25, 2025)
- [x] All 4 Liquid templates (full, half_horizontal, half_vertical, quadrant)
- [x] Configuration files (.trmnlp.yml, settings.yml)
- [x] README.md documentation
- [x] hallmark_build.py reference script
- [x] Automatic date filtering (only shows upcoming movies)
- [x] Time zone support (America/New_York)
- [x] Premiere badge indicators
- [x] Channel information display
- [x] GitHub repo created: https://github.com/snucko/hallmark-christmas-trmnl
- [x] fetch_json integration for TRMNL platform
- [x] Hardcoded fallback data for local development
- [x] Both `_data/` and `data/` directories for compatibility
- [x] Local Docker testing working

### ⏳ Pending/Optional
- [ ] Add actual movie poster images to `images/1bit/`
- [ ] Convert posters to 1-bit PNG format
- [ ] Deploy to TRMNL platform
- [ ] Get actual poster images from Hallmark or TMDB

## Known Issues & Notes

1. **No Images Yet**: Movie posters not included - placeholders (🎬) used
2. **Image paths in JSON**: All movies have image paths defined, but files don't exist yet
3. **Static Data**: No live API - data is frozen for 2025 season
4. **Update Interval**: Set to 3600 seconds (1 hour) in settings.yml
5. **Date Comparison**: Templates compare dates as strings (YYYY-MM-DD format ensures correct sorting)
6. **Dual Data Approach**: Uses `fetch_json` from GitHub for TRMNL platform, hardcoded fallback for local dev
7. **Data Location**: JSON exists in both `_data/movies.json` (for Jekyll/local) and `data/movies.json` (for reference)

## Image Requirements

### Specifications
- **Format**: 1-bit PNG (black & white)
- **Size**: ~200×300 pixels (3:4.5 aspect ratio)
- **File size**: Keep under 50KB each
- **Naming**: lowercase, hyphens, e.g., `holiday-touchdown-a-bills-love-story.png`

### Where to Get Images
1. Hallmark Media Press site
2. TMDB (The Movie Database)
3. Google Images (search: "hallmark christmas 2025 [movie title] poster")
4. Manual screenshots from Hallmark website

## Testing Checklist

When ready to test:

- [ ] Start Docker TRMNL server
- [ ] Check full layout (800×480) - should show 6 movies
- [ ] Check half_horizontal (800×240) - should show 4 movies  
- [ ] Check half_vertical (400×480) - should show 6 movies
- [ ] Check quadrant (400×240) - should show 1-2 movies with "Tonight" if applicable
- [ ] Verify date filtering (only upcoming movies shown)
- [ ] Test premiere badges display
- [ ] Verify time conversion (24hr → 12hr display)
- [ ] Check channel information displays
- [ ] Test image fallbacks (🎬 emoji if no image)

## Deployment Steps

1. **Create Plugin on TRMNL**
   - Go to usetrmnl.com
   - Create new private plugin
   - Name: "Hallmark Christmas Movies"

2. **Upload Files**
   - Upload all `.liquid` files from `src/` to templates
   - Upload `settings.yml` to plugin root
   - Upload `movies.json` to data directory
   - Upload poster images (when ready) to images/1bit/

3. **Configure**
   - Set update interval: 3600 seconds
   - Set time zone: America/New_York
   - Enable desired layouts

4. **Test on Device**
   - Assign to TRMNL device
   - Verify display updates
   - Check date filtering works in production

## Maintenance Notes

### Updating for 2026
1. Get new Hallmark schedule PDF
2. Update `hallmark_build.py` to parse new PDF (or manually update movies.json)
3. Update `start_date` and `end_date` in movies.json
4. Get new movie posters for 2026 movies
5. Test and redeploy

### Adding New Movies Mid-Season
1. Edit `data/movies.json`
2. Add new movie object with all fields
3. Generate/add poster image to `images/1bit/`
4. Re-upload movies.json to TRMNL

## Key Technical Details

### Dependencies
- **TRMNL Platform**: Liquid templating engine
- **Docker**: For local testing (`trmnl/trmnlp` image)
- **Python 3** (optional): For hallmark_build.py script
- **ImageMagick or PIL** (optional): For image conversion

### No External APIs
- All data is static in movies.json
- No API keys needed
- No rate limits or external dependencies
- Updates only when movies.json is modified

### Time Zone Handling
- All times stored in 24-hour format (Eastern Time)
- Configured for America/New_York in .trmnlp.yml
- Templates display in 12-hour format for readability

### Browser Testing Without Docker
If Docker unavailable, templates can be tested by:
1. Converting to plain HTML
2. Loading movies.json via JavaScript fetch
3. Using Liquid.js for client-side rendering

## Troubleshooting

### Templates not showing movies
- Check date format in movies.json (must be YYYY-MM-DD)
- Verify movies have dates >= current date
- Check movies.json is in `data/` directory

### Images not displaying
- Verify image paths match files in `images/1bit/`
- Check file names are lowercase with hyphens
- Ensure images are 1-bit PNG format

### Docker server won't start
- Check port 4567 isn't already in use
- Verify volume mount path is correct
- Ensure Docker has permission to access directory

### Date filtering not working
- Verify system date/time is correct
- Check time_zone setting in .trmnlp.yml
- Ensure Liquid date filter is supported

## Movie List Summary

**Total Movies**: 28  
**Date Range**: October 17 - December 25, 2025  
**Channels**: Hallmark Channel  
**Content Types**: 
- Feature films (120 min)
- Series (60 min): Mistletoe Murders, Twelve Dates 'Til Christmas
- Competition shows (60 min): Finding Mr. Christmas, Baked With Love: Holiday

**Notable Movies**:
- First: Mistletoe Murders (Oct 17)
- Last: The Christmas Baby (Dec 21)
- Special: Holiday Touchdown: A Bills Love Story (Nov 22) - NFL themed
- Special: Oy to the World! (Dec 14) - Hanukkah/Christmas
- Star-studded: Three Wisest Men (Paul Campbell, Tyler Hynes, Andrew Walker)

## Commands Reference

```bash
# Navigate to project
cd /Users/unknown1/Downloads/hallmark

# View structure
tree -L 3

# Check movies.json
cat data/movies.json | head -20

# Run builder script
python3 hallmark_build.py

# Start dev server
docker run --rm -it -p 4567:4567 -v "$(pwd):/plugin" trmnl/trmnlp serve

# Convert image
convert input.jpg -resize 200x300 -colorspace Gray -ordered-dither o8x8 images/1bit/output.png

# Validate JSON
python3 -m json.tool data/movies.json > /dev/null && echo "Valid JSON"
```

## Version History

- **v1.0.0** (Current) - Initial plugin creation
  - 28 movies from 2025 schedule
  - 4 responsive layouts
  - Auto date filtering
  - Premiere badges
  - Ready for image integration

---

**Last Updated**: Created Oct 4, 2025  
**Plugin Status**: Built, ready for testing  
**Next Step**: Add movie poster images and test locally
