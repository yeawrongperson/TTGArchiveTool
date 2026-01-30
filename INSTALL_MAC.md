# 🍎 TTG Forum Archiver - macOS Installation Guide

**Made by Cygnet**

Complete guide for installing and running the TTG Forum Archiver on your Mac.

---

## ⚠️ Quick Note

This tool works on macOS! The installation is slightly different from Windows, but it's straightforward. Follow these steps and you'll be archiving in 5 minutes.

---

## 📋 Requirements

- **macOS 10.13 or newer** (High Sierra or later)
- **20 minutes to 3 hours** (depending on how much content you have)
- **2-5GB free disk space** (for a typical archive)
- **Internet connection**

---

## 🚀 Installation Steps

### Step 1: Install Python

**Check if you already have Python:**

Open **Terminal** (Applications → Utilities → Terminal) and type:

```bash
python3 --version
```

If you see something like `Python 3.9.6` or higher, **skip to Step 2**.

**If you need to install Python:**

1. Go to https://www.python.org/downloads/
2. Download the latest Python 3 for macOS
3. Open the downloaded `.pkg` file
4. Follow the installer (click Continue/Install)
5. **Important:** The installer will handle PATH setup automatically

**Verify installation:**

```bash
python3 --version
```

You should see: `Python 3.x.x`

---

### Step 2: Install Dependencies

Open Terminal and run these commands **one at a time**:

```bash
pip3 install playwright beautifulsoup4
```

Wait for it to finish, then run:

```bash
python3 -m playwright install chromium
```

This downloads the browser (takes 1-2 minutes, ~200MB download).

**Troubleshooting:**

If you get "command not found: pip3", try:
```bash
python3 -m pip install playwright beautifulsoup4
```

---

### Step 3: Download the Archiver

**Option A - Download ZIP (Easiest):**

1. Download the ZIP from GitHub
2. Go to Downloads folder
3. Double-click the ZIP to extract it
4. You'll get a folder with all the files

**Option B - Using Git:**

```bash
cd ~/Downloads
git clone https://github.com/yourusername/ttg-archiver.git
cd ttg-archiver
```

---

### Step 4: Run the Archiver

In Terminal, navigate to where you extracted the files:

```bash
cd ~/Downloads/ttg-archiver
```

(Adjust the path if you put it somewhere else)

Then run:

```bash
python3 ttg_archive_gui_tabbed.py
```

**The GUI window will open!** 🎉

---

## 🎮 Using the Tool

The GUI works the same on Mac as on Windows:

### Tab 1: Archive Your Profile

1. Enter your TTG username
2. Select what to archive
3. Click "Start Archiving"
4. Wait for browser to open (~10 seconds)
5. Click "Ready to Continue"
6. ☕ Let it run!

### Tab 2: Archive Specific URLs

1. Paste URLs (one per line)
2. Choose Single Page or All Pages
3. Click "Start Archiving"

---

## 📁 Where Files Are Saved

By default, files save to:

```
/Users/YourName/archive_out/
```

Or wherever you chose in the "Output Folder" field.

**To find them:**
1. Open **Finder**
2. Press **Cmd+Shift+G** (Go to Folder)
3. Type the path shown in the GUI
4. Press Enter

---

## 🔧 macOS-Specific Notes

### Chromium Permission Dialog

First time you run, macOS might ask:
> "Do you want the application 'chromium' to accept incoming network connections?"

Click **Allow**. This is normal for Playwright.

### Gatekeeper Warning

If you get "cannot be opened because the developer cannot be verified":

1. Go to **System Preferences → Security & Privacy**
2. Click **"Open Anyway"** at the bottom
3. Or run: `xattr -d com.apple.quarantine ttg_archive_gui_tabbed.py`

### Terminal Permissions

macOS might ask Terminal to access folders. Click **OK** to allow.

### Keyboard Shortcuts

- **Cmd+Q** to quit (not Ctrl+Q)
- **Cmd+W** to close window
- Use **Cmd** instead of **Ctrl** in browser

---

## 🆘 Troubleshooting

### "No module named 'tkinter'"

**Solution 1 - If installed from python.org:**

Reinstall Python from python.org (includes tkinter by default)

**Solution 2 - If installed via Homebrew:**

```bash
brew install python-tk@3.11
```

(Replace 3.11 with your Python version)

### "command not found: python3"

Use the full path:

```bash
/usr/local/bin/python3 ttg_archive_gui_tabbed.py
```

Or:

```bash
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 ttg_archive_gui_tabbed.py
```

### "Permission denied"

Make the script executable:

```bash
chmod +x ttg_archive_gui_tabbed.py
```

### Browser doesn't open

Check if chromium was installed:

```bash
python3 -m playwright install chromium --force
```

### GUI looks blurry on Retina display

This is a Tkinter/Python limitation. The screenshots will still be high quality!

To improve GUI appearance:
```bash
defaults write -g AppleFontSmoothing -int 0
```

(Then restart the app)

---

## 💡 Mac Tips

### Run from Anywhere

Create an alias in your `~/.zshrc` or `~/.bash_profile`:

```bash
alias ttg-archive="cd ~/Downloads/ttg-archiver && python3 ttg_archive_gui_tabbed.py"
```

Then just type `ttg-archive` in Terminal!

### Desktop Shortcut

1. Open **Automator** (Applications → Automator)
2. New Document → Application
3. Add "Run Shell Script" action
4. Paste:
   ```bash
   cd ~/Downloads/ttg-archiver
   /usr/local/bin/python3 ttg_archive_gui_tabbed.py
   ```
5. Save to Desktop as "TTG Archiver"
6. Double-click to run!

### Faster Terminal Navigation

Drag the folder from Finder into Terminal to auto-type the path:

```bash
cd [drag folder here]
python3 ttg_archive_gui_tabbed.py
```

---

## ⚡ Performance Tips

### For Apple Silicon (M1/M2/M3):

Everything works! Playwright runs natively on ARM.

### For Intel Macs:

No special configuration needed.

### To reduce CPU usage:

The script is intentionally slow (10-15 sec per page) to ensure quality. This is normal!

---

## 🔍 Checking Logs

**Open in Terminal:**

```bash
cat ~/archive_out/meta/runlog.txt
```

**Open in Finder:**

1. Go to your output folder
2. Navigate to `meta/`
3. Double-click `runlog.txt`

---

## 📱 Quick Reference Commands

```bash
# Navigate to archiver folder
cd ~/Downloads/ttg-archiver

# Run the archiver
python3 ttg_archive_gui_tabbed.py

# Check Python version
python3 --version

# Check if dependencies installed
pip3 list | grep playwright

# Reinstall chromium browser
python3 -m playwright install chromium --force

# View logs
cat ~/archive_out/meta/runlog.txt

# Open output folder in Finder
open ~/archive_out
```

---

## 🎓 Advanced: Virtual Environment (Optional)

If you want to keep dependencies isolated:

```bash
# Create virtual environment
python3 -m venv ttg-env

# Activate it
source ttg-env/bin/activate

# Install dependencies
pip install playwright beautifulsoup4
python -m playwright install chromium

# Run archiver
python ttg_archive_gui_tabbed.py

# When done, deactivate
deactivate
```

---

## ✅ Verification Checklist

Before archiving, make sure:

- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Playwright installed (`pip3 list | grep playwright`)
- [ ] Chromium installed (`python3 -m playwright install chromium`)
- [ ] GUI opens without errors
- [ ] You have enough disk space
- [ ] You're connected to the internet

---

## 🆘 Still Having Issues?

**Check these:**

1. **Python version too old?**
   - Minimum: Python 3.7
   - Recommended: Python 3.9+

2. **macOS too old?**
   - Minimum: macOS 10.13 (High Sierra)
   - Recommended: macOS 11+

3. **Permissions issues?**
   - Grant Terminal full disk access in System Preferences

4. **Network issues?**
   - Disable VPN temporarily
   - Check firewall settings

**Still stuck?**

1. Check the logs: `~/archive_out/meta/runlog.txt`
2. Report on GitHub: https://github.com/yourusername/ttg-archiver/issues
3. Include:
   - macOS version
   - Python version
   - Error message
   - What you tried

---

## 📊 What to Expect

**Time estimates:**

- ~100 posts: 10-20 minutes ☕
- ~500 posts: 45-90 minutes 🍕
- ~1000+ posts: 1-3 hours 🎬

**File sizes:**

- Screenshots: ~1-5MB each
- HTML files: ~50-500KB each
- Total for 1000 pages: ~2-3GB

**Resource usage:**

- CPU: Light (script is intentionally slow)
- RAM: ~500MB
- Network: Continuous (downloading pages)

---

## 🍎 macOS vs Windows Differences

| Feature | macOS | Windows |
|---------|-------|---------|
| Command | `python3` | `python` |
| Package manager | `pip3` | `pip` |
| Terminal | Terminal.app | Command Prompt |
| Paths | `/Users/you/` | `C:\Users\You\` |
| Shortcuts | Cmd+C/V | Ctrl+C/V |
| Window style | Native Mac | Native Windows |

Everything else works identically!

---

## 💾 Backup Your Archive

Once archiving is complete:

**Option 1 - External Drive:**
```bash
cp -r ~/archive_out /Volumes/YourDrive/TTG_Backup
```

**Option 2 - iCloud:**
```bash
cp -r ~/archive_out ~/Library/Mobile\ Documents/com~apple~CloudDocs/TTG_Backup
```

**Option 3 - ZIP it:**
```bash
cd ~
zip -r ttg_archive.zip archive_out
```

---

## 🎯 Quick Start (TL;DR)

```bash
# Install dependencies
pip3 install playwright beautifulsoup4
python3 -m playwright install chromium

# Download and extract the archiver
cd ~/Downloads/ttg-archiver

# Run it
python3 ttg_archive_gui_tabbed.py
```

That's it! 🎉

---

## 📞 Need Help?

- **Documentation:** README_GUI_UPDATED.md
- **Issues:** https://github.com/yourusername/ttg-archiver/issues
- **Logs:** `~/archive_out/meta/runlog.txt`

---

**Made by Cygnet** 🦢

*Thank you for preserving your TTG memories!*

**TheTechGame: 2006 - 2026**

---

*Last updated: January 29, 2026*  
*Tested on: macOS 12 (Monterey), macOS 13 (Ventura), macOS 14 (Sonoma)*
