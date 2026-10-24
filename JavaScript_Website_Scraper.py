import os
import re
import time
import random
from urllib.parse import urlparse, unquote

import requests
from selenium import webdriver

MAX_SCROLLS = 60            # how many screens to scroll at most
IDLE_SCROLLS = 4            # stop after this many scrolls at the bottom with nothing new
SLOW_LINE_PATIENCE = 2.0    # extra wait per fruitless scroll (slow connections)
MIN_IMAGE_BYTES = 5 * 1024  # delete images smaller than 5 KB (icons, tracking pixels)

# Collects every image and video URL the page shows or has loaded
MEDIA_JS = r"""
const images = new Set(), videos = new Set();
const add = (set, address) => {
  if (!address || /^(data|blob|javascript|about):/i.test(address)) return;
  try { set.add(new URL(address, document.baseURI).href); } catch (e) {}
};
const largest = (srcset) => {
  let best = null, size = -1;
  for (const part of (srcset || '').split(',')) {
    const [address, descriptor] = part.trim().split(/\s+/);
    const value = parseFloat(descriptor) || 0;
    if (address && value > size) { best = address; size = value; }
  }
  return best;
};
for (const img of document.images) {
  add(images, img.currentSrc || img.src);
  add(images, largest(img.srcset));
  for (const attr of ['data-src', 'data-lazy-src', 'data-original']) add(images, img.getAttribute(attr));
}
for (const source of document.querySelectorAll('picture source[srcset]')) add(images, largest(source.srcset));
for (const video of document.querySelectorAll('video')) {
  add(videos, video.currentSrc || video.src);
  add(images, video.poster);
}
for (const source of document.querySelectorAll('video source[src]')) add(videos, source.src);
for (const entry of performance.getEntriesByType('resource')) {
  if (/\.(mp4|webm|mov|m4v)(\?|$)/i.test(entry.name) || entry.initiatorType === 'video') add(videos, entry.name);
  else if (entry.initiatorType === 'img' || entry.initiatorType === 'image' ||
           /\.(jpe?g|png|gif|webp|avif|bmp)(\?|$)/i.test(entry.name)) add(images, entry.name);
}
return [[...images], [...videos]];
"""

PAGE_STATE_JS = """
return [document.documentElement.scrollHeight,
        window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 5];
"""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("=" * 60)
    print("  JAVASCRIPT PAGE SCRAPER")
    print("  Pages built by scripts or that load more while you scroll")
    print("=" * 60)
    print("  Type q at any prompt to quit.\n")


def security_check_page(driver):
    """True if the page looks like an 'are you human?' check."""
    try:
        title = driver.title.lower()
        source = driver.page_source.lower()
    except Exception:
        return False
    return ("just a moment" in title or "attention required" in title
            or "checking your browser" in source or "verify you are human" in source)


def wait_for_human(driver, timeout=300):
    if not security_check_page(driver):
        return True
    print("Security check detected. Solve it in the Firefox window (waiting up to 5 minutes)...")
    end = time.time() + timeout
    while time.time() < end:
        time.sleep(2)
        if not security_check_page(driver):
            return True
    return False


def get_page(url):
    """Open the page in Firefox, scroll through it, return (images, videos, user_agent, cookies)."""
    print("Opening Firefox...")
    driver = webdriver.Firefox()
    images, videos = {}, {}
    try:
        driver.get(url)
        time.sleep(3)

        if not wait_for_human(driver):
            print("Security check was not solved in time.")
            return [], [], "", []

        driver.execute_script("performance.setResourceTimingBufferSize(20000);")

        print("Scrolling to load content...")
        idle = 0
        last_height = 0
        scroll = 0
        for scroll in range(1, MAX_SCROLLS + 1):
            found_images, found_videos = driver.execute_script(MEDIA_JS)
            images.update(dict.fromkeys(found_images))
            videos.update(dict.fromkeys(found_videos))
            print(f"  scroll {scroll}: {len(images)} images, {len(videos)} videos found")

            driver.execute_script("window.scrollBy({top: window.innerHeight * 0.9, behavior: 'smooth'});")
            time.sleep(random.uniform(0.8, 1.4) + SLOW_LINE_PATIENCE * idle)

            height, at_bottom = driver.execute_script(PAGE_STATE_JS)
            idle = idle + 1 if (at_bottom and height == last_height) else 0
            last_height = height
            if idle >= IDLE_SCROLLS:
                break

        # let the last images finish loading
        deadline = time.time() + 10
        while time.time() < deadline:
            if driver.execute_script("return Array.from(document.images).every((img) => img.complete);"):
                break
            time.sleep(0.5)

        found_images, found_videos = driver.execute_script(MEDIA_JS)
        images.update(dict.fromkeys(found_images))
        videos.update(dict.fromkeys(found_videos))
        print(f"Done scrolling ({scroll} steps): {len(images)} images, {len(videos)} videos.")

        user_agent = driver.execute_script("return navigator.userAgent;")
        return list(images), list(videos), user_agent, driver.get_cookies()

    except Exception as e:
        print(f"Loading the page in Firefox failed: {e}")
        return [], [], "", []
    finally:
        driver.quit()


def download_all(urls, folder, kind, session):
    if not urls:
        return 0
    os.makedirs(folder, exist_ok=True)
    saved = 0
    for i, link in enumerate(urls, 1):
        name = os.path.basename(unquote(urlparse(link).path)) or f"{kind}_{i}"
        name = re.sub(r'[<>:"/\\|?*]', "_", name)[:100]
        if "." not in name:
            name += ".jpg" if kind == "image" else ".mp4"
        path = os.path.join(folder, f"{i:04d}_{name}")
        try:
            r = session.get(link, stream=True, timeout=30)
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(65536):
                    f.write(chunk)
            if kind == "image" and os.path.getsize(path) < MIN_IMAGE_BYTES:
                os.remove(path)
                continue
            saved += 1
            print(f"  [{i}/{len(urls)}] saved {os.path.basename(path)}")
        except Exception as e:
            print(f"  [{i}/{len(urls)}] failed: {e}")
    return saved


def run_task():
    """One full scrape. Returns False if the user chose to quit."""
    url = input("Page URL: ").strip()
    if url.lower() in ("q", "quit", "exit"):
        return False
    if not url:
        print("No URL entered.")
        return True
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    default_folder = "downloads_" + urlparse(url).netloc.replace(":", "_")
    folder = input(f"Save folder (Enter = {default_folder}): ").strip()
    if folder.lower() in ("q", "quit", "exit"):
        return False
    folder = folder or default_folder
    print()

    images, videos, user_agent, cookies = get_page(url)
    if not images and not videos:
        print("\nNothing found.")
        return True

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent or "Mozilla/5.0", "Referer": url})
    for c in cookies:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"))

    print()
    n_img = download_all(images, os.path.join(folder, "images"), "image", session)
    n_vid = download_all(videos, os.path.join(folder, "videos"), "video", session)
    print(f"\nFinished: {n_img} images and {n_vid} videos saved in '{os.path.abspath(folder)}'.")
    return True


def main():
    while True:
        clear_screen()
        banner()
        try:
            keep_going = run_task()
        except KeyboardInterrupt:
            print("\n\nTask cancelled.")
            keep_going = True
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            keep_going = True

        if not keep_going:
            break

        # Results stay on screen until you decide what to do next
        try:
            answer = input("\nPress Enter to scrape another page, or type q to quit: ").strip().lower()
        except KeyboardInterrupt:
            break
        if answer in ("q", "quit", "exit"):
            break

    print("\nBye!")


if __name__ == "__main__":
    main()
