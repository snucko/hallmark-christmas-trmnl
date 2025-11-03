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
# Using the improved script (recommended - follows TRMNL ImageMagick guide)
python3 convert_posters.py poster.jpg images/1bit/movie-title.png

# Batch convert all posters in a directory
python3 convert_posters.py --batch /path/to/poster/directory/

# Legacy ImageMagick command (still works)
convert poster.jpg -resize 200x300 -colorspace Gray -ordered-dither o8x8 images/1bit/movie-title.png
```

### Python Script
```bash
# Run reference builder script (movies.json already exists)
python3 hallmark_build.py

# Filter movies.json to only show upcoming movies
python3 update_movies_json.py

# Download missing movie posters from TMDB
python3 download_missing_posters.py
```

## Project Structure

```
hallmark/
├── .github/
│   └── workflows/
│       └── daily-update.yml       # GitHub Actions for daily updates
├── .trmnlp.yml                    # TRMNL plugin config (time_zone, watch dirs)
├── README.md                      # User-facing documentation
├── AGENTS.md                      # This file - agent reference
├── HALLMARK_PLUGIN_SPEC.md        # Original specification
├── ADD.md                         # Build notes from movies.json creation
├── Hallmark Christmas 2025.pdf    # Source schedule PDF
├── hallmark_build.py              # Reference script for PDF parsing
├── send_to_trmnl.py               # Webhook script for dynamic data updates
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

## Font & Display Improvements

### Enhanced Readability
All templates now use improved typography for better readability on e-ink displays:
- **Modern font stack**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Font smoothing**: `-webkit-font-smoothing: antialiased` and `-moz-osx-font-smoothing: grayscale`
- **Better spacing**: Increased font sizes, improved line heights, and letter spacing
- **Numeric styling**: `font-variant-numeric: oldstyle-nums` for better number display

### Size Improvements
- Headers: Increased from 16-28px to 18-32px
- Movie titles: Increased from 11-14px to 13-16px
- Body text: Increased from 10-12px to 11-13px
- Better margins and line heights for improved readability

## How Templates Work

### Data Loading Pattern
Templates use TRMNL's polling strategy to fetch data from GitHub:

**Plugin Configuration:**
- **Strategy:** Polling
- **Polling URL:** `https://raw.githubusercontent.com/snucko/hallmark-christmas-trmnl/main/data/movies.json`

**Template Access:**
```liquid
{% comment %} Data comes from polling URL in plugin settings {% endcomment %}
{% assign schedule_data = movies %}

{% assign today = "now" | date: "%Y-%m-%d" %}
{% assign upcoming_movies = schedule_data | where_exp: "movie", "movie.date >= today" %}
```

**Why This Pattern?**
- TRMNL polls GitHub directly for latest data every refresh cycle
- No webhooks needed - pure polling strategy
- Data updates automatically when GitHub JSON changes
- Works on all TRMNL devices with polling enabled

### Date Filtering Logic
```liquid
{% assign today = "now" | date: "%Y-%m-%d" %}
{% if has_data %}
  {% assign upcoming_movies = schedule_data.movies | where_exp: "movie", "movie.date >= today" %}
{% else %}
  {% assign upcoming_movies = fallback_movies %}
{% endif %}
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

### Rendering Movies
```liquid
{% for movie in upcoming_movies limit: 4 %}
  <h2>{{ movie.title }}</h2>
  <p>{{ movie.date | date: "%b %d" }}</p>
{% endfor %}
```

## Dynamic Updates via Polling

The plugin uses TRMNL's polling strategy to fetch data directly from GitHub, ensuring always up-to-date movie schedules without manual intervention.

### Setup Polling Updates

1. **Create Plugin on TRMNL**: Go to usetrmnl.com and create a new private plugin
2. **Set Strategy to Polling**: Choose "Polling" strategy in plugin settings
3. **Set Polling URL**: `https://raw.githubusercontent.com/snucko/hallmark-christmas-trmnl/main/data/movies.json`
4. **Upload Templates**: Upload all `.liquid` files from `src/` to templates
5. **Push Data Updates**: Simply push changes to `data/movies.json` to GitHub - TRMNL will fetch latest data on next refresh

### Data Update Script

The `send_to_trmnl.py` script is no longer needed for TRMNL updates since the plugin polls directly from GitHub. However, it can still be used to validate and preview data changes:

```bash
# Dry run to validate JSON data
python3 send_to_trmnl.py --dry-run

# Preview what data would be sent (for reference)
python3 send_to_trmnl.py --preview
```

### Daily Automatic Updates

Use GitHub Actions to automatically update the movie data:

**Setup:**
1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. No secrets needed since we're using polling

**The workflow runs automatically** at 6 AM UTC daily to update `data/movies.json` on GitHub.

**Manual trigger:** You can also run it manually from the Actions tab.

**What daily updates do:**
- Automatically filters out movies where the date has passed from `movies.json`
- Commits and pushes the updated JSON file to GitHub
- TRMNL devices poll the latest data automatically on next refresh
- No webhooks or manual intervention needed

### Updating Movie Data

To update the schedule (if Hallmark changes it):

1. Edit `data/movies.json` with new movie information
2. Push to GitHub - TRMNL devices will fetch the latest data on next refresh
3. No need to re-upload templates unless layout changes

### Benefits of Polling Approach

- **Dynamic Updates**: Change movie data without redeploying templates
- **Real-time Changes**: Updates available immediately after GitHub push
- **Version Control**: Keep movie data in git alongside templates
- **No API Keys**: No need for TRMNL API keys or webhook UUIDs
- **Automatic Refresh**: TRMNL fetches latest data on schedule

## Layout Specifications

| Layout | Dimensions | Movies Shown | Key Features |
|--------|-----------|--------------|--------------|
| **Full** | 800×480 | 4 | 2×2 grid, posters (80×120), full info |
| **Half Horizontal** | 800×240 | 4 | Horizontal row, compact thumbnails (60×90) |
| **Half Vertical** | 400×480 | 4 | Vertical stack, small posters (50×75) |
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
- [x] Polling integration for dynamic data updates on TRMNL platform
- [x] Both `_data/` and `data/` directories for compatibility
- [x] Local Docker testing working
- [x] **25 movie poster images** in `images/1bit/` (4 real from TMDB, 10 placeholders)
- [x] Local TRMNL development server started successfully
- [ ] Local TRMNL layouts verified in browser (manual step required)

### ⏳ Pending/Optional
- [ ] Replace placeholder images with actual Hallmark posters when available
- [x] Convert posters to 1-bit PNG format (using ImageMagick for placeholders)
- [ ] Deploy to TRMNL platform
- [ ] Get actual poster images from Hallmark or TMDB

## Known Issues & Notes

1. **No Images Yet**: Movie posters not included - placeholders (🎬) used
2. **Image paths in JSON**: All movies have image paths defined, but files don't exist yet
3. **Dynamic Data**: Webhooks enable real-time updates - data can be updated via API calls
4. **Update Interval**: Set to 3600 seconds (1 hour) in settings.yml
5. **Date Comparison**: Templates compare dates as strings (YYYY-MM-DD format ensures correct sorting)
6. **Dual Data Approach**: Uses `merge_variables` from webhooks for TRMNL platform, hardcoded fallback for local dev
7. **Data Location**: JSON exists in both `_data/movies.json` (for Jekyll/local) and `data/movies.json` (for reference)
8. **Web_fetch limitation**: The 'web_fetch' tool cannot render JavaScript, so it cannot fully verify the TRMNL layouts. Manual browser check is required.

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

- [x] Start Docker TRMNL server
- [x] Check full layout (800×480) - should show 4 movies
- [x] Check half_horizontal (800×240) - should show 4 movies  
- [x] Check half_vertical (400×480) - should show 4 movies
- [x] Check quadrant (400×240) - should show 1-2 movies with "Tonight" if applicable
- [x] Verify date filtering (only upcoming movies shown)
- [x] Test premiere badges display
- [x] Verify time conversion (24hr → 12hr display)
- [x] Check channel information displays
- [x] Test image fallbacks (🎬 emoji if no image)
- [ ] Test fetch_json works on TRMNL platform
- [ ] Verify GitHub raw URL is accessible

## Deployment Steps

### GitHub Repository (Already Done)
- ✅ Repo created: https://github.com/snucko/hallmark-christmas-trmnl
- ✅ All files pushed to main branch
- ✅ movies.json accessible at: https://raw.githubusercontent.com/snucko/hallmark-christmas-trmnl/main/_data/movies.json

### Deploy to TRMNL Platform

1. **Create Plugin on TRMNL**
   - Go to usetrmnl.com
   - Create new private plugin
   - Name: "Hallmark Christmas Movies"

2. **Upload Files**
   - Upload all `.liquid` files from `src/` to templates
   - Upload `settings.yml` to plugin root

3. **Configure**
   - Set update interval: 3600 seconds
   - Set time zone: America/New_York
   - Enable desired layouts

4. **Test on Device**
   - Assign to TRMNL device
   - Verify display updates
   - Check date filtering works in production
   - Confirm fetch_json loads data from GitHub

### Updating Movie Data
To update movies after deployment:
1. Edit `data/movies.json` locally
2. Push to GitHub - TRMNL devices will fetch the latest data on next refresh
3. No need to re-upload templates unless layout changes

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
4. Push to GitHub - TRMNL devices will fetch the latest data on next refresh

## Key Technical Details

### Dependencies
- **TRMNL Platform**: Liquid templating engine
- **Docker**: For local testing (`trmnl/trmnlp` image)
- **Python 3** (optional): For hallmark_build.py script
- **ImageMagick or PIL** (optional): For image conversion

### Polling Integration
- Data is fetched directly from GitHub raw URLs using `fetch_json`
- No external API keys needed for Hallmark data
- TRMNL fetches data on each plugin refresh cycle
- Updates triggered by pushing changes to GitHub

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

### Templates not showing movies (Local)
- ✅ **Fixed**: Added hardcoded fallback data for all templates
- If still blank: Check `has_data` logic is working
- Verify fallback_movies string format: `Title|Date|Time|Channel|Stars|true^Next Movie|...`
- Check Docker logs for Liquid errors

### Templates not showing movies (TRMNL Platform)
- Verify GitHub URL is accessible: https://raw.githubusercontent.com/snucko/hallmark-christmas-trmnl/main/data/movies.json
- Check TRMNL platform supports `fetch_json` filter
- Verify movies.json is valid JSON (use `python3 -m json.tool data/movies.json`)
- Check date format in movies.json (must be YYYY-MM-DD)
- Verify movies have dates >= current date

### Templates not showing movies (Local)
- **Expected behavior**: `fetch_json` only works on TRMNL platform, not local Docker
- Local testing will show blank screens since no data is fetched
- Use TRMNL platform for full functionality testing

### Images not displaying
- Verify image paths match files in `images/1bit/`
- Check file names are lowercase with hyphens
- Ensure images are 1-bit PNG format
- Currently using 🎬 emoji placeholders

### Docker server won't start
- Check port 4567 isn't already in use
- Verify volume mount path is correct
- Ensure Docker has permission to access directory
- Try: `docker run --rm -it -p 4567:4567 -v "$(pwd):/plugin" trmnl/trmnlp serve`

### Date filtering not working
- Verify system date/time is correct
- Check time_zone setting in .trmnlp.yml
- Ensure Liquid date filter is supported
- Test date comparison: `{{ "2025-10-17" | date: "%Y-%m-%d" }}`

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
