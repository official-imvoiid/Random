from PIL import Image
import io
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import traceback
import json
import sys
import cloudscraper
from tqdm import tqdm
import logging

class Scraper:
    def __init__(self):
        self.base_download_dir = os.path.join(os.getcwd(), "Scraper")
        os.makedirs(self.base_download_dir, exist_ok=True)

        self.scraper = None
        self.driver = None
        self.is_dynamic_site = False
        
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    def setup_cloudflare_scraper(self):
        try:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=10,
            )
            return self.scraper
        except Exception as e:
            print(f"Cloudflare scraper setup failed: {e}")
            return None

    def setup_selenium_webdriver(self, headless=True):
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            })

            service = Service(ChromeDriverManager().install())
            service.log_path = os.devnull
            
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """
            })

            return driver
        except Exception as e:
            print(f"WebDriver setup failed: {e}")
            traceback.print_exc()
            return None

    def scroll_page(self, driver, scrolls=5, wait_time=2):
        try:
            print("Scrolling to load dynamic content...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            for i in range(scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(wait_time)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                
                if new_height == last_height:
                    break
                last_height = new_height
                
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            print(f"Scrolling complete. Performed {i+1} scroll cycles.")
        except Exception as e:
            print(f"Scrolling error: {e}")
            traceback.print_exc()

    def wait_for_images_to_load(self, driver, timeout=30):
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script(
                    """
                    return Array.from(document.images).every(img => img.complete);
                    """
                )
            )
            print("All images loaded.")
        except TimeoutException:
            print("Timeout waiting for images, continuing anyway...")

    def dynamic_site_scrape(self, url, wait_time=20, scroll_count=5):
        self.driver = self.setup_selenium_webdriver(headless=True)

        if not self.driver:
            print("ERROR: Failed to initialize WebDriver")
            return None, []

        try:
            print(f"Loading dynamic site: {url}")
            self.driver.get(url)
            
            time.sleep(5)
            
            cloudflare_selectors = [
                "#challenge-form",
                ".ray-id",
                "#cf-hcaptcha-container",
                "div[class*='challenge']"
            ]
            
            for selector in cloudflare_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print("Cloudflare challenge detected, waiting...")
                    time.sleep(10)
                except:
                    pass
            
            print(f"Waiting {wait_time} seconds for dynamic content to load...")
            time.sleep(wait_time)
            
            self.scroll_page(self.driver, scrolls=scroll_count, wait_time=2)
            
            self.wait_for_images_to_load(self.driver, timeout=15)
            
            time.sleep(5)
            
            page_source = self.driver.page_source
            
            try:
                logs = self.driver.get_log('performance')
                media_urls = self.extract_media_from_logs(logs)
                if media_urls:
                    print(f"Captured {len(media_urls)} media URLs from network logs")
            except Exception as e:
                print(f"Could not extract media from logs: {e}")
                media_urls = []
            
            return page_source, media_urls

        except Exception as e:
            print(f"Dynamic site scraping failed: {e}")
            traceback.print_exc()
            return None, []
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def extract_media_from_logs(self, logs):
        media_urls = set()
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.mov']
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if log['method'] == 'Network.responseReceived':
                    url = log['params']['response']['url']
                    if any(ext in url.lower() for ext in media_extensions):
                        media_urls.add(url)
            except:
                pass
        
        return list(media_urls)

    def extract_content(self, page_source, url, additional_media_urls=None):
        try:
            soup = BeautifulSoup(page_source, 'html.parser')

            cloudflare_indicators = [
                soup.find(string=re.compile(r'Cloudflare|Security Check|Checking your browser')),
                soup.find('div', {'id': 'cf-wrapper'}),
                soup.find('span', {'class': 'ray-id'})
            ]

            if any(indicator is not None for indicator in cloudflare_indicators):
                print("Warning: Cloudflare challenge may still be active.")

            text_elements = soup.find_all(['p', 'div', 'span', 'article', 'section', 'h1', 'h2', 'h3'],
                           string=lambda text: text and len(text.strip()) > 10)
            text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements])

            def is_valid_link(href):
                return href and (href.startswith('http') or href.startswith('/')) \
                       and not any(x in href.lower() for x in ['javascript:', '#', 'mailto:', 'tel:'])

            links = [urllib.parse.urljoin(url, a.get('href'))
                     for a in soup.find_all('a', href=True)
                     if is_valid_link(a.get('href'))]

            images = set()
            
            for img in soup.find_all('img'):
                for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                    img_src = img.get(attr)
                    if img_src:
                        full_url = urllib.parse.urljoin(url, img_src)
                        if not any(x in full_url.lower() for x in ['pixel', 'placeholder', 'transparent', 'icon', 'logo', 'avatar']):
                            images.add(full_url)
            
            for picture in soup.find_all('picture'):
                for source in picture.find_all('source'):
                    srcset = source.get('srcset', '')
                    for src in srcset.split(','):
                        img_url = src.strip().split(' ')[0]
                        if img_url:
                            images.add(urllib.parse.urljoin(url, img_url))
            
            for elem in soup.find_all(style=re.compile(r'background-image')):
                style = elem.get('style', '')
                urls = re.findall(r'url\([\'"]?(.*?)[\'"]?\)', style)
                for img_url in urls:
                    images.add(urllib.parse.urljoin(url, img_url))
            
            for elem in soup.find_all(attrs={'data-background': True}):
                images.add(urllib.parse.urljoin(url, elem['data-background']))
            
            if additional_media_urls:
                images.update(additional_media_urls)

            videos = set()
            for video in soup.find_all('video'):
                video_src = video.get('src')
                if video_src:
                    videos.add(urllib.parse.urljoin(url, video_src))
                for source in video.find_all('source'):
                    src = source.get('src')
                    if src:
                        videos.add(urllib.parse.urljoin(url, src))

            domain = urllib.parse.urlparse(url).netloc

            print(f"\nFound {len(images)} unique images and {len(videos)} videos")
            
            image_count = self.download_images(list(images), domain)
            video_count = self.download_videos(list(videos), domain)

            return {
                'text_content': text_content[:500] + '...' if len(text_content) > 500 else text_content,
                'links': list(set(links)),
                'images': list(images),
                'videos': list(videos),
                'images_downloaded': image_count,
                'videos_downloaded': video_count
            }

        except Exception as e:
            print(f"Content extraction failed: {e}")
            traceback.print_exc()
            return None

    def download_images(self, images, domain):
        domain_dir = os.path.join(self.base_download_dir, domain, "images")
        os.makedirs(domain_dir, exist_ok=True)

        if not self.scraper:
            self.setup_cloudflare_scraper()

        downloaded_count = 0
        downloaded_hashes = set()
        unique_images = list(set(images))
        
        progress_bar = tqdm(total=len(unique_images), desc="Downloading images", unit="img")

        for idx, img_url in enumerate(unique_images, 1):
            try:
                response = None
                if self.scraper:
                    try:
                        response = self.scraper.get(img_url, timeout=15)
                    except Exception as e:
                        print(f"\nCloudscraper error for {img_url}: {e}")
                
                if not response or response.status_code != 200:
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        response = requests.get(img_url, timeout=15, headers=headers)
                    except Exception as e:
                        print(f"\nRequests error for {img_url}: {e}")
                        progress_bar.update(1)
                        continue

                if response and response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if not content_type.startswith('image/'):
                        progress_bar.update(1)
                        continue

                    try:
                        img_data = response.content
                        img = Image.open(io.BytesIO(img_data))

                        if img.width < 215 or img.height < 215:
                            progress_bar.update(1)
                            continue

                        img_hash = hash(img_data)
                        if img_hash in downloaded_hashes:
                            progress_bar.update(1)
                            continue
                        downloaded_hashes.add(img_hash)

                        filename = re.sub(r'[^\w\-_\. ]', '_',
                                          os.path.basename(urllib.parse.urlparse(img_url).path))
                        if not filename or len(filename) < 3:
                            filename = f"image_{idx}.png"
                        if not filename.lower().endswith('.png'):
                            filename = f"{os.path.splitext(filename)[0]}.png"

                        filepath = os.path.join(domain_dir, f"{idx}_{filename}")

                        img.save(filepath, format='PNG')

                        downloaded_count += 1
                        progress_bar.write(f"Downloaded: {filename}")

                    except Exception as e:
                        print(f"\nImage processing error: {e}")

                progress_bar.update(1)

            except Exception as e:
                print(f"\nUnexpected error downloading image: {e}")
                progress_bar.update(1)
                continue

        progress_bar.close()
        return downloaded_count

    def download_videos(self, videos, domain):
        if not videos:
            return 0
            
        domain_dir = os.path.join(self.base_download_dir, domain, "videos")
        os.makedirs(domain_dir, exist_ok=True)

        downloaded_count = 0
        progress_bar = tqdm(total=len(videos), desc="Downloading videos", unit="video")

        for idx, video_url in enumerate(videos, 1):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(video_url, timeout=30, headers=headers, stream=True)
                
                if response.status_code == 200:
                    filename = re.sub(r'[^\w\-_\. ]', '_',
                                      os.path.basename(urllib.parse.urlparse(video_url).path))
                    if not filename or len(filename) < 3:
                        filename = f"video_{idx}.mp4"
                    
                    filepath = os.path.join(domain_dir, f"{idx}_{filename}")
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    downloaded_count += 1
                    progress_bar.write(f"Downloaded video: {filename}")

                progress_bar.update(1)

            except Exception as e:
                print(f"\nVideo download error: {e}")
                progress_bar.update(1)
                continue

        progress_bar.close()
        return downloaded_count

    def display_warning(self):
        print("\n" + "="*80)
        print(" SCRAPER - IMPORTANT NOTICE ".center(80))
        print("="*80)
        print("""
This tool scrapes both STATIC and DYNAMIC websites. Please note:

1. LEGAL: Check Terms of Service and robots.txt. Many sites prohibit scraping.
2. COPYRIGHT: News facts are not copyrighted, but photos, videos, and specific 
   expressions often ARE. Verify licensing before use.
3. RATE LIMITING: Use delays to avoid overwhelming servers.
4. DYNAMIC SITES: This scraper waits for JavaScript content to load.
5. ETHICAL USE: Only use scraped content according to copyright laws.
        """)
        print("="*80 + "\n")

    def main(self):
        print("Enhanced Web Scraper (Static + Dynamic Sites)")
        self.display_warning()

        while True:
            url = input("Enter the website URL to scrape: ").strip()
            if url.startswith(('http://', 'https://')):
                break
            print("Invalid URL. Please include http:// or https://")

        print("\nSite Type:")
        print("1. Static site (news, blogs - faster)")
        print("2. Dynamic site (JavaScript-heavy - slower)")
        choice = input("Select (1 or 2) [default: 2]: ").strip() or "2"

        try:
            page_source = None
            media_urls = []

            if choice == "1":
                self.setup_cloudflare_scraper()
                if self.scraper:
                    try:
                        print("Attempting static scraping...")
                        response = self.scraper.get(url)
                        if response.status_code == 200:
                            page_source = response.text
                            print("Static scraping successful.")
                        else:
                            print(f"Static scraping returned status code: {response.status_code}")
                    except Exception as e:
                        print(f"Static scraping failed: {e}")
                        traceback.print_exc()

            if not page_source or choice == "2":
                wait_time = int(input("\nWait time for page load (seconds) [default: 20]: ").strip() or "20")
                scroll_count = int(input("Number of scroll cycles [default: 5]: ").strip() or "5")
                
                result = self.dynamic_site_scrape(url, wait_time=wait_time, scroll_count=scroll_count)
                if result:
                    page_source, media_urls = result

            if not page_source:
                print("\n" + "="*60)
                print("SCRAPING FAILED".center(60))
                print("="*60)
                print("Failed to retrieve page content.")
                print("The site may have strong anti-bot protection.")
                print("="*60)
                input("\nPress Enter to exit...")
                return

            print("\nExtracting content...")
            result = self.extract_content(page_source, url, media_urls)

            print("\n" + "="*60)
            print("SCRAPING RESULTS".center(60))
            print("="*60)
            
            if result:
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"Unique Links Found: {len(result.get('links', []))}")
                    print(f"Images Found: {len(result.get('images', []))}")
                    print(f"Images Downloaded: {result.get('images_downloaded', 0)}")
                    print(f"Videos Found: {len(result.get('videos', []))}")
                    print(f"Videos Downloaded: {result.get('videos_downloaded', 0)}")
                    print(f"\nContent saved to: {self.base_download_dir}")
            else:
                print("Content extraction failed.")
            
            print("="*60)
            input("\nPress Enter to exit...")

        except KeyboardInterrupt:
            print("\n\nScraping interrupted by user.")
            input("\nPress Enter to exit...")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            traceback.print_exc()
            input("\nPress Enter to exit...")


if __name__ == "__main__":
    scraper = Scraper()
    scraper.main()