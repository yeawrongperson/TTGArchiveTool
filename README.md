# TTG Forum Archiver

**Archive your TheTechGame forum history before January 31, 2026**

*Made by Cygnet*

---

## ⚠️ **ONLY 3 DAYS LEFT!**

TheTechGame is shutting down on **January 31, 2026**. This tool helps you preserve your forum memories before everything disappears forever.

---

## What Does This Do?

Automatically archives your TTG content:

- ✅ **All your posts** (live forums + archives)
- ✅ **All your topics** (threads you started)
- ✅ **Your profile** (wall, friends, reputation)
- ✅ **Specific URLs** (archive any thread from any user)
- ✅ **Full screenshots** (high-quality PNG images)
- ✅ **HTML source** (viewable in any browser)

---

## Quick Start

### 1. Install Python

**Download:** https://www.python.org/downloads/

⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation!

### 2. Install Dependencies

Open Command Prompt / Terminal:

```bash
pip install playwright beautifulsoup4
python -m playwright install chromium
```

### 3. Download This Tool

**Option A - Git Clone:**
```bash
git clone https://github.com/yourusername/ttg-archiver.git
cd ttg-archiver
```

**Option B - Direct Download:**
Download and extract the ZIP from the [Releases](https://github.com/yourusername/ttg-archiver/releases) page

### 4. Run the Archiver

```bash
python ttg_archive_gui_tabbed.py
```

---

## How to Use

### Tab 1: Archive Your Profile

1. Enter your TTG username
2. Select what to archive:
   - ☑ Profile Pages
   - ☑ Live Topics / Archived Topics
   - ☑ Live Posts / Archived Posts
3. Click "Start Archiving"
4. Wait ~10 seconds for browser to load
5. Click "Ready to Continue"
6. Let it run!

**Time required:**
- ~100 items: 10-20 minutes
- ~500 items: 45-90 minutes
- ~1000+ items: 1-3 hours

### Tab 2: Archive Specific URLs

Perfect for:
- Saving farewell posts from friends
- Important community announcements
- Memorable threads
- Content from other users

**How:**
1. Paste URLs (one per line)
2. Choose mode:
   - **Single Page** - First page only (fast)
   - **All Pages** - Complete thread (slower but complete)
3. Click "Start Archiving"

---

##  Features

###  Smart & Reliable

- **Sequential pagination** - Never skips pages
- **Image loading** - Waits for images before screenshotting
- **Resume anytime** - Stop and restart without losing progress
- **Cloudflare handling** - Automatically detects and helps with challenges

###  Flexible Options

- **Posts-only mode** - Save space (archives just your posts, not full topics)
- **Granular control** - Choose exactly what to archive
- **Custom URLs** - Archive content from anyone, not just yourself

###  Safe & Tested

- Progress saved continuously
- Browser profile persistence
- Detailed logging for troubleshooting
- No data loss on interruption

---

##  Output Structure

Everything saves to `archive_out/` folder:

```
archive_out/
├── screenshots/        # PNG images
│   ├── extra/         # Profile, wall, friends
│   ├── topics_live/   # Your topics (forums)
│   ├── topics_arch/   # Your topics (archives)
│   ├── posts_live/    # Your posts (forums)
│   └── posts_arch/    # Your posts (archives)
├── html/              # HTML source files
└── meta/              # Logs & progress tracking
    ├── done_urls.json # Resume progress
    └── runlog.txt     # Detailed log
```

---

##  Troubleshooting

### Images Not Loading

**Cause:** External images (Discord, Imgur) may be blocked or deleted

**Solution:** HTML files still contain image URLs - some may work when opened in browser

### Cloudflare Challenges

**Solution 1:** Wait 30-60 seconds (usually resolves automatically)

**Solution 2:** Run during off-peak hours (late night/early morning)

**Solution 3:** Complete the challenge manually in the browser

### Script Hangs

**Solution:** Click "Stop" button, then restart - progress is saved automatically

### Missing Pages

**Fixed!** Latest version detects all pages sequentially

Check log for: `Detected X total pages`

### Window Too Small

The GUI opens at 900x800 - resize if needed, or adjust in code:

```python
self.root.geometry("900x800")  # Change these numbers
```

---

##  Technical Details

**Built with:**
- Python 3.7+
- Playwright (browser automation)
- BeautifulSoup4 (HTML parsing)
- Tkinter (GUI)

**Architecture:**
- Async/await for performance
- Sequential URL generation for reliability
- Smart image loading detection
- Cloudflare challenge detection

**Open Source:** Feel free to modify, improve, or learn from the code!

---

##  Advanced Options

### Command Line Version

Prefer terminal? Use the command-line version:

```bash
python ttg_archive_universal.py
```

Edit `TTG_USERNAME` at the top of the file first.

### Custom Browser Profile

To use your existing Chrome profile (already logged in):

1. Find your Chrome profile path
2. Edit the script around line 450
3. Change `profile_path = "playwright_profile"` to your path

See `CHROME_PROFILE_GUIDE.md` for details.

---

##  Files Included

- `ttg_archive_gui_tabbed.py` - Main GUI application 
- `ttg_archive_universal.py` - Command-line version
- `README_GUI_UPDATED.md` - Comprehensive documentation
- `TROUBLESHOOTING.md` - Common issues & solutions
- `CHROME_PROFILE_GUIDE.md` - Browser profile setup

---

## Quick Tips

 **DO:**
- Archive during off-peak hours
- Test with a small archive first
- Keep the browser window open
- Use the Stop button (not browser close)
- Archive NOW - don't wait!

 **DON'T:**
- Close the browser window manually
- Run multiple instances simultaneously
- Wait until January 30th!

---

## Need Help?

1. **Check the logs:** `archive_out/meta/runlog.txt`
2. **Read full docs:** `README_GUI_UPDATED.md`
3. **Open an issue:** [GitHub Issues](https://github.com/yourusername/ttg-archiver/issues)

---

##  A Personal Note

Hey everyone,

I apologize for getting this tool out so late - with only 3 days left until TTG closes. Life got in the way, work piled up, and honestly, I kept putting it off because I wasn't ready to accept that this place is really ending.

TTG has been a huge part of my life for years. The tech discussions, the troubleshooting sessions, the friendships formed. This community shaped a lot of us, and while the forum may be closing, the memories don't have to disappear.

I built this tool because I wanted to make sure nobody loses their history without at least having a chance to save it. It's not perfect, and I wish I'd released it sooner, but I hope it helps some of you preserve your TTG memories.

Please share this with anyone who might want to archive their content. We're running out of time.

To everyone who's been part of this community: thank you. For the help, the laughs, the debates, the shared knowledge. 

**TheTechGame: 2009 - 2026**

*Thank you for the memories.*

— Cygnet

---

## License

Open Source - Feel free to use, modify, and share!

No warranty provided. Use at your own risk. The tool is provided as-is to help preserve forum content.

---


**Made by Cygnet**

---

* Remember: January 31, 2026 - Archive NOW!**

