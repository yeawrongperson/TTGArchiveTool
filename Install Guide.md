# TTG Forum Archiver - Complete Your Archive Before Jan 31st!

**Made by Cygnet**

TheTechGame is shutting down on January 31, 2026. This tool helps you archive all your posts, topics, profile, and even specific URLs from other users before it's gone forever.

## Features

✅ **Two Archiving Modes:**
- **Tab 1:** Archive your entire profile (posts, topics, wall, friends, etc.)
- **Tab 2:** Archive specific URLs from any user

✅ **Smart Image Loading** - Waits for images to load before taking screenshots

✅ **Sequential Pagination** - Never misses pages, archives everything in order

✅ **Cloudflare Handling** - Automatically detects and helps you solve challenges

✅ **Resume Capability** - Stop and restart anytime, picks up where you left off

✅ **Posts-Only Mode** - Save space by archiving just your posts, not full topic pages

✅ **Granular Control** - Choose exactly what to archive (live topics, archived posts, etc.)

## Quick Start

### 1. Install Dependencies

**Install Python** (if you don't have it):
- Download from: https://www.python.org/downloads/
- ⚠️ **Important:** Check "Add Python to PATH" during installation

**Install required packages:**
```bash
pip install playwright beautifulsoup4
python -m playwright install chromium
```

### 2. Run the Archiver

```bash
python ttg_archive_gui_tabbed.py
```

## Tab 1: Archive Your Profile

Perfect for archiving YOUR content.

### Configuration:

1. **TTG Username:** Enter your exact username (case-sensitive)
2. **Output Folder:** Where files will be saved (default: `archive_out`)
3. **What to Archive:**
   - ☑ Profile Pages (profile, wall, friends, reputation)
   - ☑ Live Topics / Archives (topics you started)
   - ☑ Live Posts / Archives (all your posts)
4. **Options:**
   - **Posts-only mode** - Screenshots only your posts, not full topic pages (saves space!)
   - **Pause for login** - Recommended, but optional

### How Long It Takes:

- ~100 posts/topics: 10-20 minutes
- ~500 posts/topics: 45-90 minutes
- ~1000+ posts/topics: 1-3 hours

Each page takes ~10-15 seconds to ensure images load properly.

## Tab 2: Archive Custom URLs

Perfect for archiving specific topics, important threads, or content from other users.

### How to Use:

1. **Paste URLs** (one per line):
   ```
   https://www.thetechgame.com/Forums/t=7843018/...
   https://www.thetechgame.com/Archives/t=...
   ```

2. **Choose Archive Mode:**
   - **Single Page** - Just the first page (fast)
   - **All Pages** - Every page of the topic (complete archive)

3. **Output Folder:** Where to save (default: `archive_custom`)

4. **Login Option:**
   - ⚠️ **You don't need to login for URL archiving!**
   - Even if "Pause for login" is checked, just wait a few seconds for the page to load
   - Click "Ready to Continue" when the button becomes active
   - No login required for public topics

### Examples:

**Archive important announcements:**
```
https://www.thetechgame.com/Forums/t=7842769/updated-sunsetting-thetechgamecom.html
```

**Archive a friend's farewell post:**
```
https://www.thetechgame.com/Forums/t=7843018/the-final-countdown-lets-say-goodbye-together-shouterday.html
```

**Archive multiple discussions:**
- Paste 10-20 URLs
- Select "All Pages"
- Click Start
- All archived automatically!

## The Login Flow (Important!)

### When "Pause for login" is Checked:

1. Click "Start Archiving"
2. Browser opens
3. **Wait 5-15 seconds** for page to load
4. Log message appears: "=== LOGIN TIME ==="
5. **"Ready to Continue" button becomes active**
6. Login if needed (or skip if already logged in)
7. Click "Ready to Continue"
8. Archival begins

### Important Notes:

✅ **You DON'T need to login every time** - Browser profile remembers your session

✅ **URL archiving doesn't need login** - Public topics are accessible without login

✅ **Just wait for the button** - Don't click continue until it's enabled

✅ **Cloudflare is automatic** - If challenged, wait or solve it, then continue

## Output Structure

Everything gets saved to your chosen output folder:

```
archive_out/  (or archive_custom/)
├── screenshots/           # Full-page PNG screenshots
│   ├── extra/            # Profile, wall, friends, reputation
│   ├── topics_live/      # Your topics from live forums
│   ├── topics_arch/      # Your topics from archives
│   ├── posts_live/       # Your posts from live forums
│   ├── posts_arch/       # Your posts from archives
│   └── custom/           # Custom URL archives
│
├── html/                 # Complete HTML files (same structure)
│
└── meta/                 # Progress tracking & logs
    ├── done_urls.json    # Tracks archived URLs (for resuming)
    ├── runlog.txt        # Detailed execution log
    └── *_results.json    # Results for each section
```

## Features Explained

###  Smart Image Loading

The script waits for images to load before taking screenshots:
- Initial page load: ~3 seconds
- Image loading: up to 10 seconds
- Total per page: ~10-15 seconds

You'll see "Images loaded" in the log when ready.

###  Sequential Pagination

For topics with multiple pages, the script:
- Detects total page count automatically
- Generates sequential URLs (page 1, 2, 3, 4, 5...)
- Never skips pages or jumps to "Last Page"
- Logs: "Detected X total pages"

###  Posts-Only Mode

When enabled:
- Archives your individual posts/replies
- Skips the full topic pages those posts are in
- Saves tons of disk space and time
- Perfect for users with 1000+ posts

Without it:
- Archives both your posts AND the topics they're in
- More complete but uses more space

###  Pause for Login

Why it's recommended:
- Lets you login once at the start
- Handles Cloudflare challenges
- Browser profile remembers your session

You can uncheck it if:
- Already logged in from previous run
- Archiving public URLs only
- Want it to run unattended

###  Resume Anytime

Progress is saved automatically:
- `done_urls.json` tracks everything archived
- Stop with the "Stop" button or close the GUI
- Restart later - it skips what's already done
- No duplicate downloads

## Troubleshooting

### Images Not Loading

**Problem:** Some screenshots show broken image placeholders

**Causes:**
- Images hosted on external services (Discord, Imgur)
- Images already deleted/expired
- Slow image servers

**Solutions:**
- The HTML files are still saved with image URLs
- Images might load if you open the HTML in browser
- Some image loss is unavoidable for old content

### Missing Pages

**Problem:** Topic shows 6 pages but only archived 4

**Fixed!** The script now:
- Detects total pages correctly
- Generates sequential URLs
- Archives every page in order

Check the log for: "Detected X total pages"

### Cloudflare Loops

**Problem:** Stuck on Cloudflare verification

**Solutions:**
1. **Wait it out** - Often resolves in 30-60 seconds
2. **Run during off-peak hours** - Late night/early morning
3. **Use existing browser profile** - Already logged in = less challenges
4. **Just be patient** - The script waits up to 5 minutes automatically

### "Ready to Continue" Never Enables

**Problem:** Button stays grayed out

**Solution:**
- Wait for page to fully load (~5-15 seconds)
- Look for "=== LOGIN TIME ===" in the log
- Button only enables AFTER that message appears
- If still stuck after 30 seconds, restart the script

### Script Hangs/Freezes

**Problem:** Progress stops, no activity

**Solutions:**
1. Check if browser window is still open
2. Look at the log for last activity
3. Click "Stop" button
4. Restart - progress is saved!

### Browser Closes Unexpectedly

**Don't close the browser manually!** Use the Stop button instead.

If browser crashes:
- Script will detect it
- Logs: "Browser was closed - stopping archival"
- Restart and it will resume

## Tips for Best Results

### 1. Archive During Off-Peak Hours
- Late night or early morning
- Fewer users = faster loading
- Less Cloudflare challenges

### 2. Start with a Test
- Archive just your profile first
- Check screenshot quality
- Verify everything looks good
- Then do the full archive

### 3. Use Stop Button, Not Browser Close
- Saves progress properly
- Cleaner shutdown
- Easier to resume

### 4. Check Your Disk Space
- Screenshots can be large (1-5MB each)
- 1000 pages = ~2-3GB
- Make sure you have enough space

### 5. Organize Your Archives
- Use different output folders for different archives
- Example: `archive_personal`, `archive_important_topics`
- Keeps things organized

### 6. Archive Multiple Times
- Run once now to get most content
- Run again closer to Jan 31st for recent posts
- Script skips duplicates automatically

## Advanced: Command Line Version

If you prefer command line over GUI, use:
- `ttg_archive_universal.py` - For your profile
- Edit the `TTG_USERNAME` variable at the top
- Run: `python ttg_archive_universal.py`

## Common Questions

### Q: Do I need to keep the browser window open?

**A:** Yes! Don't close it. The script controls it. Use the Stop button if you need to quit.

### Q: Can I archive someone else's profile?

**A:** Not directly in Tab 1, but you can:
- Use Tab 2 (Custom URLs)
- Paste their topic/post URLs
- Archive specific content

### Q: Will this work after January 31st?

**A:** NO! The site will be gone. Archive NOW, don't wait!

### Q: How do I view the archived content later?

**A:** 
- **Screenshots:** Open in any image viewer
- **HTML files:** Open in any web browser (Chrome, Firefox, etc.)
- Images in HTML may not load if hosted externally

### Q: Can I stop and resume?

**A:** Yes! The script saves progress. Just restart with the same output folder.

### Q: Does this archive private messages?

**A:** No, only public forum content (posts, topics, profile).

### Q: Can I run this on multiple computers?

**A:** Yes, but use different output folders or you'll mix archives.

## Need Help?

### Check the Logs

All activity is logged in detail:

**Main log:**
```
archive_out/meta/runlog.txt
```

**Custom URL log:**
```
archive_custom/meta/runlog_custom.txt
```

**Crash log (if script crashes):**
```
archive_out/meta/crash_log.txt
```

### Common Log Messages

✅ **"Images loaded"** - Good! Page is ready

✅ **"Detected X total pages"** - Pagination working

✅ **"Archived: X URLs"** - Success count

⚠️ **"Image wait timed out"** - Some images didn't load (OK)

⚠️ **"Cloudflare challenge detected"** - Waiting for resolution

❌ **"Failed to load"** - Page couldn't be accessed


## Final Checklist Before January 31st

- [ ] Install Python and dependencies
- [ ] Test with a small archive first
- [ ] Archive your profile (Tab 1)
- [ ] Archive important topics (Tab 2)
- [ ] Check screenshot quality
- [ ] Verify HTML files open properly
- [ ] Back up the archive folder somewhere safe
- [ ] Consider archiving again closer to shutdown date

## Credits

**Made by Cygnet**

Created to help the TTG community preserve their forum history.

Special thanks to:
- The TTG community for years of memories
- Everyone working to preserve forum content before the shutdown

## Remember

**TheTechGame shuts down January 31, 2026.**

Don't wait until the last day! Archive your memories now while the site is still up and running. Once it's gone, it's gone forever.

---

*This tool is provided as-is to help preserve forum content. Archive responsibly and respect the work of content creators.*

**Made by Cygnet**
