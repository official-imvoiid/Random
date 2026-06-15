#!/usr/bin/env python3
"""
Gallery Downloader — Browse, Preview & Selectively Download
Powered by gallery-dl | Supports any gallery-dl compatible site
"""

import os
import sys
import json
import subprocess
import re
import shutil
import urllib.parse
import webbrowser
import requests

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup

# ==================== CONFIGURATION ====================
# Paste cookies from browser DevTools (F12 → Application → Cookies)
# Required only for sites that need authentication
COOKIES = {
    # "cookie_name": "cookie_value",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

STATE_FILE  = "download_progress.json"
COOKIE_FILE = "cookies.txt"   # Written automatically from COOKIES dict

# Gallery link pattern — adjust regex to match target site's URL structure
# Default matches common /g/ID/HASH/ style gallery URLs
GALLERY_URL_PATTERN = re.compile(r"/g/\d+/[a-f0-9]+/")
# ======================================================


# ──────────────────────────────────────────────────────
# gallery-dl helpers
# ──────────────────────────────────────────────────────

def find_gallery_dl():
    probe = subprocess.run(
        [sys.executable, "-m", "gallery_dl", "--version"],
        capture_output=True
    )
    if probe.returncode == 0:
        return [sys.executable, "-m", "gallery_dl"]
    for name in ("gallery-dl", "gallery_dl"):
        exe = shutil.which(name)
        if exe:
            return [exe]
    return None


def write_cookie_file():
    active = {k: v for k, v in COOKIES.items() if v}
    if not active:
        return None
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for name, value in active.items():
            f.write(f".example.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
    return COOKIE_FILE


def run_gallery_dl(base_cmd, output_dir, url, cookie_file=None):
    cmd = list(base_cmd)
    cmd += ["-d", output_dir]
    if cookie_file and os.path.exists(cookie_file):
        cmd += ["--cookies", cookie_file]
    cmd.append(url)
    print(f"    $ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            return True, "Download complete."
        else:
            return False, f"gallery-dl exited with code {result.returncode}"
    except FileNotFoundError:
        return False, "gallery-dl executable not found."
    except Exception as exc:
        return False, str(exc)


# ──────────────────────────────────────────────────────
# Qt dialogs
# ──────────────────────────────────────────────────────

class DecisionDialog(QDialog):
    def __init__(self, title_text, gallery_url, idx, total, page_num):
        super().__init__()
        self.choice      = None
        self.gallery_url = gallery_url
        self._build_ui(title_text, idx, total, page_num)

    def _build_ui(self, title_text, idx, total, page_num):
        self.setWindowTitle(f"Page {page_num}  |  Entry {idx}/{total}")
        self.setFixedSize(540, 230)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout()
        layout.setSpacing(8)

        progress = QLabel(f"Page {page_num}  ·  Entry {idx} of {total}")
        progress.setAlignment(Qt.AlignCenter)
        progress.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(progress)

        heading = QLabel("Reviewing Entry:")
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("font-weight: bold; font-size: 13px; color: #111;")
        layout.addWidget(heading)

        title_lbl = QLabel(title_text)
        title_lbl.setWordWrap(True)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 11px; color: #444; margin: 2px 12px;")
        layout.addWidget(title_lbl)

        btn_preview = QPushButton("🔍  Preview in Browser")
        btn_preview.setStyleSheet(
            "background-color: #FF9800; color: white; font-weight: bold; "
            "min-height: 28px; border-radius: 4px;"
        )
        btn_preview.clicked.connect(self._on_preview)
        layout.addWidget(btn_preview)

        row = QHBoxLayout()

        btn_yes = QPushButton("✅  Download")
        btn_yes.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; "
            "min-height: 34px; border-radius: 4px;"
        )
        btn_yes.clicked.connect(self._on_yes)

        btn_no = QPushButton("⏭  Skip")
        btn_no.setStyleSheet(
            "background-color: #f44336; color: white; font-weight: bold; "
            "min-height: 34px; border-radius: 4px;"
        )
        btn_no.clicked.connect(self._on_no)

        btn_quit = QPushButton("💾  Quit & Save")
        btn_quit.setStyleSheet(
            "background-color: #9E9E9E; color: white; font-weight: bold; "
            "min-height: 34px; border-radius: 4px;"
        )
        btn_quit.clicked.connect(self._on_quit)

        row.addWidget(btn_yes)
        row.addWidget(btn_no)
        row.addWidget(btn_quit)
        layout.addLayout(row)
        self.setLayout(layout)

    def _on_preview(self):
        if self.gallery_url:
            webbrowser.open(self.gallery_url)

    def _on_yes(self):
        self.choice = "y"
        self.accept()

    def _on_no(self):
        self.choice = "n"
        self.accept()

    def _on_quit(self):
        self.choice = "q"
        self.reject()

    def closeEvent(self, event):
        if self.choice is None:
            self.choice = "n"
        super().closeEvent(event)


def show_alert(title, message):
    dlg = QDialog()
    dlg.setWindowTitle(title)
    dlg.setFixedSize(480, 170)
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowStaysOnTopHint)
    layout = QVBoxLayout()
    lbl = QLabel(message)
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet("font-size: 12px; color: #333; margin: 10px;")
    layout.addWidget(lbl)
    btn = QPushButton("OK")
    btn.setStyleSheet("min-height: 30px; font-weight: bold;")
    btn.clicked.connect(dlg.accept)
    layout.addWidget(btn)
    dlg.setLayout(layout)
    dlg.exec_()


# ──────────────────────────────────────────────────────
# Scraping helpers
# ──────────────────────────────────────────────────────

def get_search_term(url):
    params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    return params.get("f_search", ["results"])[0]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)


def fetch_page_galleries(page_url):
    try:
        resp = requests.get(page_url, headers=HEADERS, cookies=COOKIES, timeout=20)
        if resp.status_code != 200:
            return [], f"HTTP {resp.status_code}"

        text_lower = resp.text.lower()
        if "cloudflare" in text_lower or "just a moment" in text_lower:
            return [], "Cloudflare is blocking the request."

        soup  = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=GALLERY_URL_PATTERN)

        seen = {}
        for link in links:
            href = link["href"]
            if not href.startswith("http"):
                href = urllib.parse.urljoin(page_url, href)
            title = link.get_text(strip=True) or "Unknown Title"
            if href not in seen or len(title) > len(seen[href]):
                seen[href] = title

        return [{"url": u, "title": t} for u, t in seen.items()], None

    except requests.exceptions.Timeout:
        return [], "Request timed out (20s)."
    except Exception as exc:
        return [], str(exc)


# ──────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)

    print("[*] Locating gallery-dl...")
    gdl_cmd = find_gallery_dl()
    if not gdl_cmd:
        show_alert(
            "gallery-dl Not Found",
            "gallery-dl is not installed.\n\n"
            "Fix:  pip install gallery-dl\n\n"
            "Then restart the script."
        )
        print("[!] Install:  pip install gallery-dl")
        sys.exit(1)
    print(f"[+] gallery-dl ready: {' '.join(gdl_cmd)}")

    cookie_file = write_cookie_file()
    if cookie_file:
        print(f"[+] Cookie file written → {cookie_file}")
    else:
        print("[!] No cookies configured — auth-required content will fail.")

    search_url = input("\nEnter search/listing URL: ").strip()
    if not search_url:
        print("[!] URL cannot be empty.")
        sys.exit(1)

    folder_name = re.sub(r'[\\/*?:"<>|]', "_", get_search_term(search_url))
    output_dir  = os.path.join(".", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Output: {output_dir}")

    state        = load_state()
    parsed_base  = urllib.parse.urlparse(search_url)
    base_params  = urllib.parse.parse_qs(parsed_base.query)

    current_page     = 0
    total_downloaded = 0
    total_skipped    = 0
    quit_requested   = False

    print("[*] Scanning pages until no results remain...\n")

    while not quit_requested:
        base_params["page"] = [str(current_page)]
        page_url = urllib.parse.urlunparse((
            parsed_base.scheme, parsed_base.netloc, parsed_base.path,
            parsed_base.params,
            urllib.parse.urlencode(base_params, doseq=True),
            parsed_base.fragment
        ))

        print(f"══ PAGE {current_page} ══  {page_url}")
        galleries, error = fetch_page_galleries(page_url)

        if error:
            show_alert("Fetch Error", f"Page {current_page} failed:\n{error}")
            print(f"[!] {error}")
            break

        if not galleries:
            if current_page == 0:
                show_alert(
                    "No Results",
                    "Page 0 returned 0 entries.\n\n"
                    "The site may be blocking you, or cookies are required."
                )
            print(f"[+] Page {current_page} empty — all pages scanned. Done!")
            break

        pending       = [g for g in galleries if g["url"] not in state]
        skipped_count = len(galleries) - len(pending)
        print(f"    {len(galleries)} found  |  {skipped_count} already processed  |  {len(pending)} to review")

        for idx, item in enumerate(pending, start=1):
            url, title = item["url"], item["title"]

            dialog = DecisionDialog(title, url, idx, len(pending), current_page)
            dialog.exec_()
            choice = dialog.choice

            if choice == "q":
                print("[*] Quit & Save — stopping.")
                quit_requested = True
                break

            elif choice == "n":
                print(f"  [SKIP]  {title}")
                state[url] = "skipped"
                total_skipped += 1
                save_state(state)

            elif choice == "y":
                print(f"  [DL]    {title}")
                success, msg = run_gallery_dl(gdl_cmd, output_dir, url, cookie_file)
                state[url]   = "downloaded" if success else "failed"
                if success:
                    total_downloaded += 1
                print(f"  [{'OK' if success else 'ERR'}]   {msg}")
                save_state(state)

        if not quit_requested:
            current_page += 1

    print(f"\n{'='*48}")
    print(f"  Session complete.")
    print(f"  Pages scanned : {current_page}")
    print(f"  Downloaded    : {total_downloaded}")
    print(f"  Skipped       : {total_skipped}")
    print(f"  Progress file : {STATE_FILE}")
    print(f"{'='*48}\n")


if __name__ == "__main__":
    main()
