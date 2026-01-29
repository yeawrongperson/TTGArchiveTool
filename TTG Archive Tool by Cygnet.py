import asyncio
import os
import re
import json
import time
import traceback
import threading
from urllib.parse import urljoin, urlparse
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# ============================================================================
# ARCHIVER CORE
# ============================================================================

BASE_URL = "https://www.thetechgame.com/"

DELAY_SEC = 2.5
SLOW_MO_MS = 200
GOTO_TIMEOUT_MS = 120000
PAGE_LOAD_WAIT_MS = 3000
MAX_SEARCH_PAGES_PER_GROUP = 400

# Global variables for GUI communication
gui_log_callback = None
gui_progress_callback = None
gui_enable_continue_callback = None
should_stop = False
waiting_for_continue = False

def log(msg: str):
    """Log to both file and GUI"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    
    # Write to file
    if hasattr(log, 'file_path') and log.file_path:
        try:
            os.makedirs(os.path.dirname(log.file_path), exist_ok=True)
            with open(log.file_path, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except:
            pass
    
    # Send to GUI
    if gui_log_callback:
        gui_log_callback(formatted)
    
    # Also print to console
    print(formatted, flush=True)

def set_progress(current: int, total: int, status: str):
    """Update progress in GUI"""
    if gui_progress_callback:
        gui_progress_callback(current, total, status)

# Helper functions
def safe_filename(s: str, max_len: int = 120) -> str:
    s = re.sub(r"[^\w\-\.]+", "_", (s or "").strip())
    return s[:max_len].strip("_") or "page"

def is_same_site(url: str) -> bool:
    try:
        return urlparse(url).netloc == urlparse(BASE_URL).netloc
    except Exception:
        return False

def normalize_url(href: str, current_url: str) -> str:
    return urljoin(current_url, href)

def extract_all_links(html: str, current_url: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if not href or href.startswith("#"):
            continue
        url = normalize_url(href, current_url)
        if is_same_site(url):
            links.add(url)
    return links

def classify_content_url(url: str) -> str | None:
    if "/Forums/p=" in url or "/Archives/p=" in url:
        return "post"
    if "/Forums/t=" in url or "/Archives/t=" in url:
        return "topic"
    return None

def looks_like_search_page(url: str, root_search_url: str) -> bool:
    if not url.endswith(".html"):
        return False
    root_parts = root_search_url.split("/search/")
    if len(root_parts) < 2:
        return False
    base_path = root_parts[0] + "/search/"
    return (url.startswith(base_path) and 
            ("/search_id=" in url or "/search_author=" in url or "search_id=startedtopics" in url))

def extract_topic_pages(html: str, base_url: str) -> list[str]:
    """
    Extract all pagination pages from a topic.
    Instead of scraping links (which can be unreliable), we:
    1. Find the highest page number mentioned
    2. Generate sequential URLs for all pages
    """
    soup = BeautifulSoup(html, "html.parser")
    pages = [base_url]
    
    # Look for pagination indicators to find the total number of pages
    max_page = 1
    
    # Method 1: Look for page number links (e.g., "1 2 3 4 5 ... Last")
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        
        # Check if the link contains /start= pattern
        if "/start=" in href:
            # Extract the start value (e.g., /start=20.html -> 20)
            match = re.search(r'/start=(\d+)', href)
            if match:
                start_value = int(match.group(1))
                # TTG shows 10 posts per page, so start=20 means page 3
                page_num = (start_value // 10) + 1
                max_page = max(max_page, page_num)
        
        # Also check if the text is a number (page number link)
        if text.isdigit():
            page_num = int(text)
            max_page = max(max_page, page_num)
    
    # Method 2: Look for "Page X of Y" text
    page_text = soup.get_text()
    match = re.search(r'Page\s+\d+\s+of\s+(\d+)', page_text, re.IGNORECASE)
    if match:
        total_pages = int(match.group(1))
        max_page = max(max_page, total_pages)
    
    # Generate URLs for all pages sequentially
    # Remove any existing /start= parameter from base URL
    clean_url = re.sub(r'/start=\d+', '', base_url)
    
    # Page 1 is the base URL (no /start parameter)
    result = [clean_url]
    
    # Generate pages 2 through max_page
    for page_num in range(2, max_page + 1):
        start_value = (page_num - 1) * 10
        # Insert /start=X before .html
        page_url = clean_url.replace('.html', f'/start={start_value}.html')
        result.append(page_url)
    
    log(f"Detected {max_page} total pages")
    return result

async def looks_like_cloudflare(page) -> bool:
    try:
        content = (await page.content()).lower()
        title = (await page.title()).lower()
        url = page.url.lower()
    except Exception:
        return False
    if "forums" in url or "archives" in url:
        return False
    strong_indicators = [
        "verifying you are human",
        "verify you are human",
        "checking your browser before accessing",
        "just a moment",
        "cf-browser-verification",
    ]
    return any(indicator in content or indicator in title for indicator in strong_indicators)

async def wait_for_cloudflare_resolution(page, max_wait_seconds: int = 300):
    log("Waiting for Cloudflare challenge to resolve...")
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        if should_stop:
            return False
        await asyncio.sleep(3)
        if not await looks_like_cloudflare(page):
            log("Cloudflare challenge resolved!")
            await page.wait_for_timeout(2000)
            return True
    return False

async def handle_cloudflare_challenge(page):
    log("Cloudflare challenge detected - waiting for resolution...")
    resolved = await wait_for_cloudflare_resolution(page, max_wait_seconds=300)
    if not resolved:
        log("Cloudflare not resolved automatically - manual intervention may be needed")
    else:
        log("Continuing with archival...")

async def safe_goto(page, url: str, attempts: int = 3) -> bool:
    if should_stop:
        return False
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            log(f"Loading: {url}")
            
            # Check if page is still open
            if page.is_closed():
                log("Page was closed, cannot navigate")
                return False
            
            # Use domcontentloaded (faster) instead of networkidle (too slow)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=GOTO_TIMEOUT_MS)
            
            # Wait a bit for dynamic content to load
            await page.wait_for_timeout(3000)
            
            # Wait for images to load with a reasonable timeout
            try:
                await page.evaluate("""
                    () => {
                        const timeout = 10000; // 10 second max wait for images
                        const start = Date.now();
                        return Promise.all(
                            Array.from(document.images)
                                .filter(img => !img.complete)
                                .map(img => new Promise(resolve => {
                                    const check = () => {
                                        if (img.complete || Date.now() - start > timeout) {
                                            resolve();
                                        } else {
                                            setTimeout(check, 100);
                                        }
                                    };
                                    img.onload = img.onerror = resolve;
                                    check();
                                }))
                        );
                    }
                """)
                log("Images loaded")
            except Exception as e:
                # Don't worry if this fails - we'll still take the screenshot
                pass
            
            # Small final wait for any lazy-loaded content
            await page.wait_for_timeout(1000)
            
            if await looks_like_cloudflare(page):
                await handle_cloudflare_challenge(page)
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for browser/page closure errors
            if "closed" in error_msg.lower() or "target" in error_msg.lower():
                log(f"Browser or page was closed - cannot continue")
                return False
            
            last_error = e
            log(f"Navigation error (attempt {attempt}/{attempts}): {error_msg}")
            
            if attempt < attempts:
                await asyncio.sleep(5)  # Use asyncio.sleep instead of page.wait_for_timeout
    
    log(f"Failed to load after {attempts} attempts: {url}")
    return False

async def expand_click_to_view_content(page):
    locs = [
        page.locator("text=Click to View Content"),
        page.locator("a:has-text('Click to View Content')"),
    ]
    for _ in range(5):
        clicked = False
        for loc in locs:
            try:
                count = await loc.count()
                for i in range(count):
                    el = loc.nth(i)
                    if await el.is_visible():
                        await el.click(force=True, timeout=1500)
                        clicked = True
                        await page.wait_for_timeout(200)
            except:
                pass
        if not clicked:
            break

async def save_page(page, out_dir, group: str, kind: str, idx: int):
    if should_stop:
        return None
    try:
        title = await page.title()
    except:
        title = "untitled"
    
    slug = safe_filename(title)
    screen_dir = os.path.join(out_dir, "screenshots", group, kind)
    html_dir = os.path.join(out_dir, "html", group, kind)
    os.makedirs(screen_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    
    base = f"{idx:05d}__{slug}"
    png_path = os.path.join(screen_dir, base + ".png")
    html_path = os.path.join(html_dir, base + ".html")
    
    try:
        await page.screenshot(path=png_path, full_page=True)
    except Exception as e:
        log(f"Screenshot failed: {e}")
    
    try:
        html = await page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        log(f"HTML save failed: {e}")
    
    return {"url": page.url, "title": title, "png": png_path, "html": html_path}

async def collect_search_pages(page, root_search_url: str) -> list[str]:
    if should_stop:
        return []
    log(f"Collecting pagination pages...")
    to_visit = [root_search_url]
    visited = set()
    
    while to_visit and len(visited) < MAX_SEARCH_PAGES_PER_GROUP and not should_stop:
        cur = to_visit.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        
        ok = await safe_goto(page, cur)
        if not ok:
            continue
        
        html = await page.content()
        links = extract_all_links(html, page.url)
        
        for u in links:
            if looks_like_search_page(u, root_search_url) and u not in visited:
                to_visit.append(u)
        
        await asyncio.sleep(DELAY_SEC)
    
    log(f"Found {len(visited)} pagination pages")
    return sorted(visited)

async def collect_content_links(page, search_pages: list[str]) -> dict[str, list[str]]:
    if should_stop:
        return {"posts": [], "topics": []}
    posts, topics = set(), set()
    
    for i, sp in enumerate(search_pages, 1):
        if should_stop:
            break
        log(f"Scanning page {i}/{len(search_pages)}...")
        ok = await safe_goto(page, sp)
        if not ok:
            continue
        
        html = await page.content()
        links = extract_all_links(html, page.url)
        
        for u in links:
            k = classify_content_url(u)
            if k == "post":
                posts.add(u)
            elif k == "topic":
                topics.add(u)
        
        await asyncio.sleep(DELAY_SEC)
    
    log(f"Found {len(posts)} posts and {len(topics)} topics")
    return {"posts": sorted(posts), "topics": sorted(topics)}

async def archive_url_list(page, done: set, out_dir: str, group: str, kind: str, urls: list[str], posts_only: bool = False):
    if should_stop:
        return
    
    meta_dir = os.path.join(out_dir, "meta")
    os.makedirs(meta_dir, exist_ok=True)
    
    results_path = os.path.join(meta_dir, f"{group}__{kind}__results.json")
    results = []
    if os.path.exists(results_path):
        try:
            with open(results_path, "r", encoding="utf-8") as f:
                results = json.load(f)
        except:
            results = []
    
    idx = len([r for r in results if "error" not in r]) + 1
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        if should_stop:
            break
        if url in done:
            continue
        
        set_progress(i, total, f"Archiving {kind} {i}/{total}")
        
        # In posts_only mode, skip topic URLs
        if posts_only and kind == "topics":
            log(f"[{i}/{total}] Skipping topic (posts-only mode): {url}")
            done.add(url)
            continue
        
        log(f"[{i}/{total}] Archiving: {url}")
        
        ok = await safe_goto(page, url)
        if not ok:
            results.append({"url": url, "error": "failed to load"})
            continue
        
        await expand_click_to_view_content(page)
        rec = await save_page(page, out_dir, group, kind, idx)
        if rec:
            results.append(rec)
        
        done.add(url)
        
        # Save progress
        done_urls_path = os.path.join(meta_dir, "done_urls.json")
        with open(done_urls_path, "w", encoding="utf-8") as f:
            json.dump({"done": sorted(done)}, f, indent=2)
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        idx += 1
        await asyncio.sleep(DELAY_SEC)

# ============================================================================
# USER ARCHIVER
# ============================================================================

async def run_user_archiver(username: str, output_dir: str, include_profile: bool, 
                            topics_live: bool, topics_arch: bool, posts_live: bool, posts_arch: bool,
                            posts_only_mode: bool, allow_login: bool):
    global should_stop, waiting_for_continue
    should_stop = False
    waiting_for_continue = False
    
    log(f"Starting user archival for: {username}")
    log(f"Output directory: {output_dir}")
    if posts_only_mode:
        log("Posts-only mode: Will screenshot only user posts, not full topic pages")
    
    meta_dir = os.path.join(output_dir, "meta")
    os.makedirs(meta_dir, exist_ok=True)
    log.file_path = os.path.join(meta_dir, "runlog.txt")
    
    done_urls_path = os.path.join(meta_dir, "done_urls.json")
    done = set()
    if os.path.exists(done_urls_path):
        try:
            with open(done_urls_path, "r", encoding="utf-8") as f:
                done = set(json.load(f).get("done", []))
            log(f"Resuming - already archived {len(done)} URLs")
        except:
            pass
    
    profile_urls = [
        ("profile", f"https://www.thetechgame.com/{username}"),
        ("wall", f"https://www.thetechgame.com/{username}#wall"),
        ("friends", f"https://www.thetechgame.com/{username}#friends"),
        ("reputation", f"https://www.thetechgame.com/{username}#reputation"),
    ]
    
    search_urls = []
    if topics_live:
        search_urls.append(("topics_live", f"https://www.thetechgame.com/Forums/search/search_id=startedtopics/user={username}.html"))
    if topics_arch:
        search_urls.append(("topics_arch", f"https://www.thetechgame.com/Archives/search/search_id=startedtopics/user={username}.html"))
    if posts_live:
        search_urls.append(("posts_live", f"https://www.thetechgame.com/Forums/search/search_author={username}.html"))
    if posts_arch:
        search_urls.append(("posts_arch", f"https://www.thetechgame.com/Archives/search/search_author={username}.html"))
    
    try:
        async with async_playwright() as p:
            log("Launching browser...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=os.path.join(output_dir, "browser_profile"),
                headless=False,
                slow_mo=SLOW_MO_MS,
                viewport={"width": 1400, "height": 900},
                args=['--disable-blink-features=AutomationControlled'],
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Navigate to TTG first
            log("Opening TheTechGame...")
            await safe_goto(page, BASE_URL)
            
            # Now prompt for login if enabled
            if allow_login:
                log("\n=== LOGIN TIME ===")
                log("Page is loaded - log in if needed, then click 'Ready to Continue'")
                set_progress(0, 100, "Login if needed, then click 'Ready to Continue'")
                
                # Enable the continue button in GUI
                if gui_enable_continue_callback:
                    gui_enable_continue_callback()
                
                waiting_for_continue = True
                while waiting_for_continue and not should_stop:
                    await asyncio.sleep(0.5)
                log("User ready - continuing...")
            
            if should_stop:
                await context.close()
                return
            
            if include_profile:
                log("\n=== Archiving Profile ===")
                for name, url in profile_urls:
                    if should_stop:
                        break
                    await archive_url_list(page, done, output_dir, "extra", name, [url], posts_only_mode)
            
            for group_name, root_url in search_urls:
                if should_stop:
                    break
                log(f"\n=== {group_name} ===")
                search_pages = await collect_search_pages(page, root_url)
                content = await collect_content_links(page, search_pages)
                
                is_posts_group = "posts_" in group_name
                
                if content['posts']:
                    await archive_url_list(page, done, output_dir, group_name, "posts", 
                                          content["posts"], posts_only_mode and is_posts_group)
                
                if content['topics'] and not (posts_only_mode and is_posts_group):
                    await archive_url_list(page, done, output_dir, group_name, "topics", 
                                          content["topics"], posts_only_mode)
            
            await context.close()
            
            if should_stop:
                log("\n=== Stopped by User ===")
            else:
                log("\n=== Complete! ===")
                log(f"Archived: {len(done)} URLs")
            
    except Exception as e:
        log(f"\nERROR: {str(e)}")
        log(traceback.format_exc())
        raise

# ============================================================================
# CUSTOM URL ARCHIVER
# ============================================================================

async def run_custom_url_archiver(urls: list[str], output_dir: str, mode: str, allow_login: bool):
    global should_stop, waiting_for_continue
    should_stop = False
    waiting_for_continue = False
    
    log(f"Starting custom URL archival")
    log(f"Mode: {mode}")
    log(f"URLs to archive: {len(urls)}")
    
    meta_dir = os.path.join(output_dir, "meta")
    os.makedirs(meta_dir, exist_ok=True)
    log.file_path = os.path.join(meta_dir, "runlog_custom.txt")
    
    try:
        async with async_playwright() as p:
            log("Launching browser...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=os.path.join(output_dir, "browser_profile"),
                headless=False,
                slow_mo=SLOW_MO_MS,
                viewport={"width": 1400, "height": 900},
                args=['--disable-blink-features=AutomationControlled'],
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Navigate to TTG first
            log("Opening TheTechGame...")
            await safe_goto(page, BASE_URL)
            
            # Now prompt for login if enabled
            if allow_login:
                log("\n=== LOGIN TIME ===")
                log("Page is loaded - log in if needed, then click 'Ready to Continue'")
                set_progress(0, 100, "Login if needed, then click 'Ready to Continue'")
                
                # Enable the continue button in GUI
                if gui_enable_continue_callback:
                    gui_enable_continue_callback()
                
                waiting_for_continue = True
                while waiting_for_continue and not should_stop:
                    await asyncio.sleep(0.5)
                log("User ready - continuing...")
            
            if should_stop:
                await context.close()
                return
            
            total_saved = 0
            
            for url_idx, url in enumerate(urls, 1):
                if should_stop:
                    break
                
                # Check if page is still open
                if page.is_closed():
                    log("Browser was closed - stopping archival")
                    break
                
                log(f"\n=== URL {url_idx}/{len(urls)}: {url} ===")
                set_progress(url_idx, len(urls), f"Processing URL {url_idx}/{len(urls)}")
                
                if mode == "single_page":
                    # Screenshot the full first page
                    log("Mode: Single page (full)")
                    ok = await safe_goto(page, url)
                    if ok:
                        await expand_click_to_view_content(page)
                        await save_page(page, output_dir, "custom", "single_page", url_idx)
                        total_saved += 1
                
                elif mode == "all_pages":
                    # Get all pagination pages and screenshot each
                    log("Mode: All pages")
                    ok = await safe_goto(page, url)
                    if ok:
                        html = await page.content()
                        all_pages = extract_topic_pages(html, url)
                        log(f"Found {len(all_pages)} pages")
                        
                        for page_idx, page_url in enumerate(all_pages, 1):
                            if should_stop or page.is_closed():
                                break
                            log(f"  Page {page_idx}/{len(all_pages)}: {page_url}")
                            ok = await safe_goto(page, page_url)
                            if ok:
                                await expand_click_to_view_content(page)
                                await save_page(page, output_dir, "custom", f"url{url_idx}_pages", 
                                              (url_idx - 1) * 100 + page_idx)
                                total_saved += 1
                            await asyncio.sleep(DELAY_SEC)
                
                await asyncio.sleep(DELAY_SEC)
            
            if not page.is_closed():
                await context.close()
            
            if should_stop:
                log("\n=== Stopped by User ===")
            else:
                log("\n=== Complete! ===")
                log(f"Total pages saved: {total_saved}")
            
    except Exception as e:
        error_msg = str(e)
        if "closed" in error_msg.lower():
            log("\nBrowser was closed - archival stopped")
        else:
            log(f"\nERROR: {error_msg}")
            log(traceback.format_exc())
        raise

# ============================================================================
# GUI APPLICATION
# ============================================================================

class TTGArchiverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TTG Forum Archiver")
        self.root.geometry("900x800")  # Increased from 850x750
        self.root.resizable(True, True)
        
        self.archiver_thread = None
        self.is_running = False
        self.waiting_for_login = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: User Archiver
        self.user_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="Archive My Profile")
        self.create_user_tab()
        
        # Tab 2: Custom URL Archiver
        self.custom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_tab, text="Archive Custom URLs")
        self.create_custom_tab()
        
        # Shared: Progress and Log (at bottom, outside tabs)
        self.create_shared_widgets()
    
    def create_user_tab(self):
        main_frame = ttk.Frame(self.user_tab, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Archive Your TTG Profile", font=("Arial", 14, "bold"))
        title.pack(pady=(0, 5))
        subtitle = ttk.Label(main_frame, text="Save your posts, topics, and profile before Jan 31, 2026", font=("Arial", 9))
        subtitle.pack(pady=(0, 5))
        credit = ttk.Label(main_frame, text="Made by Cygnet", font=("Arial", 8, "italic"), foreground="#666666")
        credit.pack(pady=(0, 15))
        
        # Config
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(config_frame, text="TTG Username:").grid(row=0, column=0, sticky=W, pady=5)
        self.username_var = StringVar()
        ttk.Entry(config_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky=W, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Output Folder:").grid(row=1, column=0, sticky=W, pady=5)
        output_frame = ttk.Frame(config_frame)
        output_frame.grid(row=1, column=1, sticky=(W, E), padx=10, pady=5)
        self.output_var = StringVar(value=os.path.join(os.getcwd(), "archive_out"))
        ttk.Entry(output_frame, textvariable=self.output_var, width=35).pack(side=LEFT)
        ttk.Button(output_frame, text="Browse", command=self.browse_output, width=10).pack(side=LEFT, padx=(5, 0))
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="What to Archive", padding="5")
        options_frame.pack(fill=X, pady=(0, 10))
        
        self.profile_var = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Profile Pages", variable=self.profile_var).grid(row=0, column=0, sticky=W, padx=5, pady=2)
        
        ttk.Label(options_frame, text="Topics:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=W, padx=5, pady=(5,2))
        self.topics_live_var = BooleanVar(value=True)
        self.topics_arch_var = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Live Topics", variable=self.topics_live_var).grid(row=2, column=0, sticky=W, padx=20, pady=2)
        ttk.Checkbutton(options_frame, text="Archives", variable=self.topics_arch_var).grid(row=3, column=0, sticky=W, padx=20, pady=2)
        
        ttk.Label(options_frame, text="Posts:", font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=W, padx=5, pady=(5,2))
        self.posts_live_var = BooleanVar(value=True)
        self.posts_arch_var = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Live Posts", variable=self.posts_live_var).grid(row=2, column=1, sticky=W, padx=20, pady=2)
        ttk.Checkbutton(options_frame, text="Archives", variable=self.posts_arch_var).grid(row=3, column=1, sticky=W, padx=20, pady=2)
        
        ttk.Separator(options_frame, orient=HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        self.posts_only_var = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Posts-only mode (save space - screenshot only posts, not full topics)", 
                       variable=self.posts_only_var).grid(row=5, column=0, columnspan=2, sticky=W, padx=5, pady=2)
        
        self.allow_login_var = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Pause for login (recommended)", 
                       variable=self.allow_login_var).grid(row=6, column=0, columnspan=2, sticky=W, padx=5, pady=2)
        
        # Login info note
        login_note = ttk.Label(options_frame, 
                              text="💡 Wait for the page to load (~10 seconds), then click 'Ready to Continue'",
                              font=("Arial", 8),
                              foreground="#666666")
        login_note.grid(row=7, column=0, columnspan=2, sticky=W, pady=(2, 0), padx=20)
    
    def create_custom_tab(self):
        main_frame = ttk.Frame(self.custom_tab, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Archive Specific URLs", font=("Arial", 14, "bold"))
        title.pack(pady=(0, 5))
        subtitle = ttk.Label(main_frame, text="Save specific topics or posts from any user", font=("Arial", 9))
        subtitle.pack(pady=(0, 5))
        credit = ttk.Label(main_frame, text="Made by Cygnet", font=("Arial", 8, "italic"), foreground="#666666")
        credit.pack(pady=(0, 15))
        
        # URL Input
        url_frame = ttk.LabelFrame(main_frame, text="URLs to Archive", padding="10")
        url_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(url_frame, text="Paste URLs (one per line):").pack(anchor=W, pady=(0, 5))
        
        self.url_text = scrolledtext.ScrolledText(url_frame, wrap=WORD, height=8, width=70)
        self.url_text.pack(fill=BOTH, expand=True)
        self.url_text.insert(1.0, "https://www.thetechgame.com/Forums/t=7842769/...\nhttps://www.thetechgame.com/Archives/t=...\n")
        
        # Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="Archive Mode", padding="10")
        mode_frame.pack(fill=X, pady=(0, 10))
        
        self.archive_mode_var = StringVar(value="single_page")
        
        ttk.Radiobutton(mode_frame, text="Single Page - Screenshot the full first page (includes original post + some replies)", 
                       variable=self.archive_mode_var, value="single_page").pack(anchor=W, pady=2)
        
        ttk.Radiobutton(mode_frame, text="All Pages - Screenshot every page of the topic (complete thread archive)", 
                       variable=self.archive_mode_var, value="all_pages").pack(anchor=W, pady=2)
        
        # Output folder
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky=W, pady=5)
        folder_frame = ttk.Frame(output_frame)
        folder_frame.grid(row=0, column=1, sticky=(W, E), padx=10)
        self.custom_output_var = StringVar(value=os.path.join(os.getcwd(), "archive_custom"))
        ttk.Entry(folder_frame, textvariable=self.custom_output_var, width=40).pack(side=LEFT)
        ttk.Button(folder_frame, text="Browse", command=self.browse_custom_output, width=10).pack(side=LEFT, padx=(5, 0))
        
        self.custom_login_var = BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Pause for login (recommended)", 
                       variable=self.custom_login_var).grid(row=1, column=0, columnspan=2, sticky=W, pady=5)
        
        # Login info note
        login_note = ttk.Label(output_frame, 
                              text="⚠️ You don't need to login for URL archiving!\n"
                                   "Just wait a few seconds for the page to load, then click\n"
                                   "'Ready to Continue'. No login required for public topics.",
                              font=("Arial", 8),
                              foreground="#666666",
                              wraplength=450,
                              justify=LEFT)
        login_note.grid(row=2, column=0, columnspan=2, sticky=W, pady=(5, 0), padx=20)
    
    def create_shared_widgets(self):
        # Control buttons (below tabs)
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=X, padx=10, pady=(5, 5))
        
        self.start_btn = ttk.Button(button_frame, text="Start Archiving", command=self.start_archiving, width=20)
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.continue_btn = ttk.Button(button_frame, text="Ready to Continue", command=self.continue_after_login, 
                                      state=DISABLED, width=20)
        self.continue_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_archiving, state=DISABLED, width=20)
        self.stop_btn.pack(side=LEFT, padx=5)
        
        # Progress
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill=X, padx=10, pady=(0, 5))
        
        self.status_var = StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=X)
        
        # Log
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=WORD, height=10)
        self.log_text.pack(fill=BOTH, expand=True)
    
    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)
    
    def browse_custom_output(self):
        folder = filedialog.askdirectory(initialdir=self.custom_output_var.get())
        if folder:
            self.custom_output_var.set(folder)
    
    def log_message(self, msg):
        self.log_text.insert(END, msg + "\n")
        self.log_text.see(END)
        self.root.update_idletasks()
    
    def update_progress(self, current, total, status):
        if total > 0:
            self.progress['value'] = (current / total) * 100
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def start_archiving(self):
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # User tab
            self.start_user_archiving()
        else:  # Custom URL tab
            self.start_custom_archiving()
    
    def start_user_archiving(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your TTG username")
            return
        
        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        has_selection = (self.profile_var.get() or self.topics_live_var.get() or 
                        self.topics_arch_var.get() or self.posts_live_var.get() or 
                        self.posts_arch_var.get())
        
        if not has_selection:
            messagebox.showerror("Error", "Please select at least one option to archive")
            return
        
        self.start_archiving_common()
        
        self.archiver_thread = threading.Thread(
            target=self.run_user_archiver_thread,
            args=(username, output_dir, self.profile_var.get(), 
                  self.topics_live_var.get(), self.topics_arch_var.get(),
                  self.posts_live_var.get(), self.posts_arch_var.get(),
                  self.posts_only_var.get(), self.allow_login_var.get()),
            daemon=True
        )
        self.archiver_thread.start()
        # Removed the automatic button enabling - script will enable it when ready
    
    def start_custom_archiving(self):
        urls_text = self.url_text.get(1.0, END).strip()
        if not urls_text:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        
        urls = [u.strip() for u in urls_text.split("\n") if u.strip() and u.strip().startswith("http")]
        
        if not urls:
            messagebox.showerror("Error", "No valid URLs found")
            return
        
        output_dir = self.custom_output_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        self.start_archiving_common()
        
        self.archiver_thread = threading.Thread(
            target=self.run_custom_archiver_thread,
            args=(urls, output_dir, self.archive_mode_var.get(), self.custom_login_var.get()),
            daemon=True
        )
        self.archiver_thread.start()
        # Removed the automatic button enabling - script will enable it when ready
    
    def start_archiving_common(self):
        global gui_log_callback, gui_progress_callback, gui_enable_continue_callback, should_stop
        gui_log_callback = self.log_message
        gui_progress_callback = self.update_progress
        gui_enable_continue_callback = self.enable_continue_button_from_script
        should_stop = False
        self.waiting_for_login = False
        
        self.start_btn.config(state=DISABLED)
        self.continue_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.is_running = True
        self.log_text.delete(1.0, END)
        self.progress['value'] = 0
    
    def enable_continue_button_from_script(self):
        """Called by the archiver script when it's ready for user to continue"""
        self.root.after(0, lambda: self.continue_btn.config(state=NORMAL))
    
    def enable_continue_button(self):
        if self.is_running and not self.waiting_for_login:
            self.continue_btn.config(state=NORMAL)
            self.waiting_for_login = True
    
    def continue_after_login(self):
        global waiting_for_continue
        self.continue_btn.config(state=DISABLED)
        self.waiting_for_login = False
        waiting_for_continue = False
        log("User clicked continue - resuming...")
    
    def run_user_archiver_thread(self, username, output_dir, include_profile, 
                                 topics_live, topics_arch, posts_live, posts_arch,
                                 posts_only_mode, allow_login):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                run_user_archiver(username, output_dir, include_profile,
                                 topics_live, topics_arch, posts_live, posts_arch,
                                 posts_only_mode, allow_login)
            )
        except Exception as e:
            self.log_message(f"\nError: {str(e)}")
        finally:
            self.root.after(0, self.archiving_finished)
    
    def run_custom_archiver_thread(self, urls, output_dir, mode, allow_login):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                run_custom_url_archiver(urls, output_dir, mode, allow_login)
            )
        except Exception as e:
            self.log_message(f"\nError: {str(e)}")
        finally:
            self.root.after(0, self.archiving_finished)
    
    def stop_archiving(self):
        global should_stop
        should_stop = True
        self.log_message("\nStopping...")
        self.stop_btn.config(state=DISABLED)
    
    def archiving_finished(self):
        self.start_btn.config(state=NORMAL)
        self.continue_btn.config(state=DISABLED)
        self.stop_btn.config(state=DISABLED)
        self.is_running = False
        self.status_var.set("Finished")
        messagebox.showinfo("Complete", "Archival finished! Check the output folder.")

def main():
    root = Tk()
    app = TTGArchiverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
