#!/usr/bin/env python3
"""
YT-DLP Quick Tool v1.0
Cross-platform: Windows, Linux, macOS
Supports: YouTube, Twitch, Crunchyroll, Bilibili, RapidCloud, and 1000+ sites
"""

import os
import sys
import subprocess
import platform
import getpass
from shutil import which

# ── Colours ───────────────────────────────────────────────────────────────────
IS_WIN = platform.system() == "Windows"
if IS_WIN:
    os.system("color")

R  = "\033[0;31m"
G  = "\033[0;32m"
Y  = "\033[1;33m"
C  = "\033[0;36m"
M  = "\033[0;35m"
RS = "\033[0m"

# ── Helpers ───────────────────────────────────────────────────────────────────
def clr():
    os.system("cls" if IS_WIN else "clear")

def pause():
    input("  Press Enter to continue...")

def ask(prompt, hidden=False):
    try:
        ans = getpass.getpass(prompt) if hidden else input(prompt)
        return ans.strip()
    except (EOFError, KeyboardInterrupt):
        print()
        main_menu()
        return ""

def section(title):
    print(f"\n{Y}  ─────────────────────────────────────────────────────────")
    print(f"   {title}")
    print(f"  ─────────────────────────────────────────────────────────{RS}\n")

def run(cmd):
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        print(f"\n{R}  [!] Command not found: {cmd[0]}")
        print(f"      Make sure yt-dlp is installed (option 1 in menu).{RS}\n")

def find_pip():
    return which("pip3") or which("pip") or "pip"

def find_ytdlp():
    return which("yt-dlp")

def find_ffmpeg():
    return which("ffmpeg")

def check_tools():
    ok = True
    if not find_ytdlp():
        print(f"  {Y}[!] yt-dlp not found — select option [1] to install it.{RS}")
        ok = False
    if not find_ffmpeg():
        print(f"  {Y}[!] FFmpeg not found — some features will be limited.")
        print(f"      Install: https://ffmpeg.org/download.html{RS}")
        ok = False
    return ok

# ═════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ═════════════════════════════════════════════════════════════════════════════
def main_menu():
    clr()
    ffmpeg_status = f"{G} found{RS}" if find_ffmpeg() else f"{R} missing{RS}"
    ytdlp_status  = f"{G} found{RS}" if find_ytdlp()  else f"{R} missing{RS}"

    print(f"""{C}
  ╔═══════════════════════════════════════════════════════╗
  ║  ██╗   ██╗████████╗      ██████╗ ██╗     ██████╗      ║
  ║  ╚██╗ ██╔╝╚══██╔══╝      ██╔══██╗██║     ██╔══██╗     ║
  ║   ╚████╔╝    ██║   █████╗██║  ██║██║     ██████╔╝     ║
  ║    ╚██╔╝     ██║   ╚════╝██║  ██║██║     ██╔═══╝      ║
  ║     ██║      ██║         ██████╔╝███████╗██║          ║
  ║     ╚═╝      ╚═╝         ╚═════╝ ╚══════╝╚═╝          ║
  ╚═══════════════════════════════════════════════════════╝{RS}
   Quick Tool  —  YouTube, Twitch, Crunchyroll & 1000+ sites
{Y}  ─────────────────────────────────────────────────────────{RS}
   yt-dlp  : {ytdlp_status}     FFmpeg : {ffmpeg_status}
{Y}  ─────────────────────────────────────────────────────────{RS}

   [1]  Install | Upgrade yt-dlp
   [2]  Remove yt-dlp
   [3]  Download Video | with format picker
   [4]  Download Audio Only
   [5]  Download Video Only | no audio
   [6]  Download Playlist | Channel
   [7]  Advanced / Custom | spoofing, referer, user-agent
   [8]  Check versions
   [0]  Exit
{Y}  ═════════════════════════════════════════════════════════{RS}""")

    ch = ask("  >> Choose: ")
    {
        "1": install_menu,
        "2": remove_menu,
        "3": download_video,
        "4": download_audio,
        "5": download_video_only,
        "6": download_playlist,
        "7": advanced_menu,
        "8": check_versions,
        "0": bye,
    }.get(ch, main_menu)()

# ═════════════════════════════════════════════════════════════════════════════
#  [1] INSTALL / UPGRADE
# ═════════════════════════════════════════════════════════════════════════════
def install_menu():
    clr()
    print(f"""
  ═════════════════════════════════════════════════════════
   INSTALL / UPGRADE  yt-dlp
  ═════════════════════════════════════════════════════════
   [1]  Install | Upgrade via pip  (recommended)
   [2]  Install | Upgrade via pip --user  (no admin)
   [3]  Install specific version
   [4]  Install latest nightly from GitHub
   [5]  Also install | upgrade FFmpeg  (via pip imageio-ffmpeg)
   [B]  Back
  ═════════════════════════════════════════════════════════""")

    ch  = ask("  >> Choose: ").lower()
    pip = find_pip()

    if   ch == "1": run([pip, "install", "--upgrade", "yt-dlp"])
    elif ch == "2": run([pip, "install", "--upgrade", "--user", "yt-dlp"])
    elif ch == "3":
        ver = ask("  Version (e.g. 2024.11.04): ")
        run([pip, "install", f"yt-dlp=={ver}"])
    elif ch == "4":
        run([pip, "install", "--upgrade",
             "git+https://github.com/yt-dlp/yt-dlp.git@master"])
    elif ch == "5":
        print(f"\n{Y}  Installing FFmpeg wrapper via pip…{RS}\n")
        run([pip, "install", "--upgrade", "imageio[ffmpeg]"])
        print(f"\n{Y}  For native FFmpeg (better), download from:{RS}")
        print("  https://ffmpeg.org/download.html\n")
        pause(); install_menu(); return
    elif ch == "b":
        main_menu(); return

    print(f"\n{G}  [OK] Done!{RS}\n")
    pause(); main_menu()

# ═════════════════════════════════════════════════════════════════════════════
#  [2] REMOVE
# ═════════════════════════════════════════════════════════════════════════════
def remove_menu():
    clr()
    print(f"""
  ═════════════════════════════════════════════════════════
   REMOVE yt-dlp
  ═════════════════════════════════════════════════════════
  {R} WARNING: This will uninstall yt-dlp.{RS}
   [Y] Confirm   [N] Back
  ═════════════════════════════════════════════════════════""")
    if ask("  >> (Y/N): ").lower() == "y":
        run([find_pip(), "uninstall", "yt-dlp", "-y"])
        print(f"\n{G}  [OK] Removed.{RS}\n")
        pause()
    main_menu()

# ═════════════════════════════════════════════════════════════════════════════
#  [8] VERSION CHECK
# ═════════════════════════════════════════════════════════════════════════════
def check_versions():
    clr()
    print("\n  ═════════════════════════════════════════════════════════")
    print("   VERSION INFO")
    print("  ═════════════════════════════════════════════════════════\n")
    print(f"  {Y}yt-dlp:{RS}")
    if find_ytdlp():
        run(["yt-dlp", "--version"])
    else:
        print(f"  {R}  Not installed.{RS}")
    print(f"\n  {Y}FFmpeg:{RS}")
    if find_ffmpeg():
        run(["ffmpeg", "-version"])
    else:
        print(f"  {R}  Not found. Download: https://ffmpeg.org/download.html{RS}")
    print()
    pause(); main_menu()

# ═════════════════════════════════════════════════════════════════════════════
#  Shared auth builder
# ═════════════════════════════════════════════════════════════════════════════
def build_auth(args):
    section("AUTHENTICATION")
    print("""   [1]  cookies.txt file
   [2]  Browser cookies  (Chrome / Firefox / Edge / Brave / Opera …)
   [3]  Username + Password  (sites that support it)
   [4]  Netrc file  (~/.netrc)
   [5]  No authentication
""")
    auth = ask("  >> Choose auth method: ")

    if auth == "1":
        cf = ask("  Path to cookies.txt: ")
        if cf: args += ["--cookies", cf]

    elif auth == "2":
        print("  Supported: chrome, firefox, edge, chromium, opera, brave, safari, vivaldi")
        br   = ask("  Browser name: ")
        prof = ask("  Profile name (blank = default): ")
        if br:
            args += ["--cookies-from-browser",
                     f"{br}:{prof}" if prof else br]

    elif auth == "3":
        u = ask("  Username / Email: ")
        p = ask("  Password: ", hidden=True)
        if u: args += ["--username", u, "--password", p]

    elif auth == "4":
        args.append("--netrc")

    return args

# ═════════════════════════════════════════════════════════════════════════════
#  Shared output builder
# ═════════════════════════════════════════════════════════════════════════════
def build_output(args):
    out = ask("  Save folder  (blank = current directory): ")
    if out:
        args += ["--paths", out]

    print("""
  Output filename template:
   [1]  %(title)s.%(ext)s                  ← default
   [2]  %(uploader)s - %(title)s.%(ext)s
   [3]  %(upload_date)s - %(title)s.%(ext)s
   [4]  %(id)s.%(ext)s
   [5]  Custom
""")
    tmpl_ch = ask("  >> Template choice (blank=default): ")
    templates = {
        "1": "%(title)s.%(ext)s",
        "2": "%(uploader)s - %(title)s.%(ext)s",
        "3": "%(upload_date)s - %(title)s.%(ext)s",
        "4": "%(id)s.%(ext)s",
    }
    if tmpl_ch in templates:
        args += ["--output", templates[tmpl_ch]]
    elif tmpl_ch == "5":
        cust = ask("  Custom template: ")
        if cust: args += ["--output", cust]

    return args

# ═════════════════════════════════════════════════════════════════════════════
#  Shared misc options
# ═════════════════════════════════════════════════════════════════════════════
def build_misc(args):
    section("EXTRA OPTIONS")

    if ask("  Write subtitle files? (y/N): ").lower() == "y":
        args.append("--write-subs")
        lang = ask("  Subtitle languages  (e.g. en,ja  | blank=all): ")
        if lang: args += ["--sub-langs", lang]
        if ask("  Embed subtitles into file? (y/N): ").lower() == "y":
            args.append("--embed-subs")

    if ask("  Embed thumbnail? (y/N): ").lower() == "y":
        args.append("--embed-thumbnail")

    if ask("  Write metadata tags? (y/N): ").lower() == "y":
        args.append("--add-metadata")

    if ask("  Write info .json file? (y/N): ").lower() == "y":
        args.append("--write-info-json")

    limit = ask("  Download speed limit (e.g. 2M = 2 MB/s | blank=off): ")
    if limit: args += ["--limit-rate", limit]

    retries = ask("  Retries on error (default=10 | blank=skip): ")
    if retries: args += ["--retries", retries]

    if ask("  Skip already downloaded files? (Y/n): ").lower() != "n":
        args.append("--no-overwrites")

    if ask("  Verbose output? (y/N): ").lower() == "y":
        args.append("--verbose")

    return args

# ═════════════════════════════════════════════════════════════════════════════
#  [3] DOWNLOAD VIDEO
# ═════════════════════════════════════════════════════════════════════════════
def download_video():
    clr()
    print("""
  ═════════════════════════════════════════════════════════
   DOWNLOAD VIDEO  —  Format Picker
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    # ── Format ───────────────────────────────────────────────────────────
    section("1 / 4   VIDEO FORMAT")
    print(f"""   {Y}Recommended presets:{RS}
   [1]  Best H.264/AVC + best audio → mp4   {G}(max compat, hardware decode){RS}
   [2]  Best H.265/HEVC + best audio → mp4  (smaller file)
   [3]  Best VP9 + best audio → webm         (open codec)
   [4]  Best AV1 + best audio → mkv          (best compression)
   [5]  Best overall any codec → mkv         (highest quality)
   [6]  1080p H.264 → mp4                    {G}(most common choice){RS}
   [7]   720p H.264 → mp4
   [8]   480p H.264 → mp4
   [9]  Custom format string
   [L]  List all available formats for URL first
""")
    fmt_ch = ask("  >> Choose format: ").lower()

    FORMAT_MAP = {
        "1": ("bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]"
              "/bestvideo[vcodec^=avc1]+bestaudio/best[ext=mp4]/best", "mp4"),
        "2": ("bestvideo[vcodec^=hvc1]+bestaudio[ext=m4a]"
              "/bestvideo[vcodec^=hevc]+bestaudio/best", "mp4"),
        "3": ("bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best", "webm"),
        "4": ("bestvideo[vcodec^=av01]+bestaudio/best", "mkv"),
        "5": ("bestvideo+bestaudio/best", "mkv"),
        "6": ("bestvideo[height<=1080][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]"
              "/bestvideo[height<=1080][vcodec^=avc1]+bestaudio"
              "/best[height<=1080][ext=mp4]/best[height<=1080]", "mp4"),
        "7": ("bestvideo[height<=720][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]"
              "/best[height<=720][ext=mp4]/best[height<=720]", "mp4"),
        "8": ("bestvideo[height<=480][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]"
              "/best[height<=480][ext=mp4]/best[height<=480]", "mp4"),
    }

    if fmt_ch == "l":
        url_tmp = ask("  URL to list formats for: ")
        if url_tmp:
            run(["yt-dlp", "-F", url_tmp])
        pause()
        download_video(); return

    elif fmt_ch == "9":
        fmt_str = ask("  Format string: ")
        merge   = ask("  Merge output format (mp4/mkv/webm | blank=mkv): ") or "mkv"
        args += ["-f", fmt_str, "--merge-output-format", merge]

    elif fmt_ch in FORMAT_MAP:
        fmt_str, merge = FORMAT_MAP[fmt_ch]
        args += ["-f", fmt_str, "--merge-output-format", merge]
    else:
        # default fallback
        args += ["-f",
                 "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                 "--merge-output-format", "mp4"]

    # FFmpeg codec remux options for clean output
    if find_ffmpeg():
        args += ["--ffmpeg-location", which("ffmpeg"),
                 "--postprocessor-args", "ffmpeg:-c copy"]

    # ── Output ───────────────────────────────────────────────────────────
    section("2 / 4   OUTPUT")
    args = build_output(args)

    # ── Auth ─────────────────────────────────────────────────────────────
    args = build_auth(args)

    # ── Misc ─────────────────────────────────────────────────────────────
    args = build_misc(args)

    # ── URL ──────────────────────────────────────────────────────────────
    section("4 / 4   URL")
    url = ask("  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, download_video)

# ═════════════════════════════════════════════════════════════════════════════
#  [4] AUDIO ONLY
# ═════════════════════════════════════════════════════════════════════════════
def download_audio():
    clr()
    print("""
  ═════════════════════════════════════════════════════════
   DOWNLOAD AUDIO ONLY
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("1 / 3   AUDIO FORMAT")
    print("""   [1]  Best quality → mp3       (universal)
   [2]  Best quality → m4a/aac  (Apple compat)
   [3]  Best quality → opus     (smallest, best quality)
   [4]  Best quality → flac     (lossless)
   [5]  Best quality → wav      (uncompressed)
   [6]  Keep original codec     (fastest, no re-encode)
""")
    fmt_ch = ask("  >> Choose format: ")

    AUDIO_MAP = {
        "1": ("mp3",  "320"),
        "2": ("m4a",  "0"),
        "3": ("opus", "0"),
        "4": ("flac", "0"),
        "5": ("wav",  "0"),
    }

    if fmt_ch in AUDIO_MAP:
        aext, qual = AUDIO_MAP[fmt_ch]
        args += ["-x", "--audio-format", aext]
        if fmt_ch == "1":
            args += ["--audio-quality", qual]   # 320k for mp3
        if find_ffmpeg():
            args += ["--ffmpeg-location", which("ffmpeg")]
    else:
        # Keep original
        args += ["-f", "bestaudio/best"]

    if ask("  Embed thumbnail into audio file? (y/N): ").lower() == "y":
        args.append("--embed-thumbnail")
    if ask("  Write metadata tags? (y/N): ").lower() == "y":
        args.append("--add-metadata")

    section("2 / 3   OUTPUT")
    args = build_output(args)
    args = build_auth(args)

    limit = ask("  Speed limit (e.g. 2M | blank=off): ")
    if limit: args += ["--limit-rate", limit]
    if ask("  Skip already downloaded? (Y/n): ").lower() != "n":
        args.append("--no-overwrites")

    section("3 / 3   URL")
    url = ask("  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, download_audio)

# ═════════════════════════════════════════════════════════════════════════════
#  [5] VIDEO ONLY
# ═════════════════════════════════════════════════════════════════════════════
def download_video_only():
    clr()
    print("""
  ═════════════════════════════════════════════════════════
   DOWNLOAD VIDEO ONLY  (no audio stream)
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("1 / 3   FORMAT")
    print("""   [1]  Best video only → mp4  (H.264/AVC)
   [2]  Best video only → mp4  (any codec)
   [3]  1080p video only → mp4
   [4]   720p video only → mp4
   [5]  Best video only → mkv
   [6]  Custom format string
""")
    fmt_ch = ask("  >> Choose: ")

    FMT = {
        "1": "bestvideo[ext=mp4][vcodec^=avc1]/bestvideo[ext=mp4]",
        "2": "bestvideo[ext=mp4]/bestvideo",
        "3": "bestvideo[height<=1080][ext=mp4][vcodec^=avc1]/bestvideo[height<=1080]",
        "4": "bestvideo[height<=720][ext=mp4][vcodec^=avc1]/bestvideo[height<=720]",
        "5": "bestvideo",
    }
    if fmt_ch in FMT:
        args += ["-f", FMT[fmt_ch], "--merge-output-format", "mp4"]
    elif fmt_ch == "6":
        f = ask("  Format string: ")
        m = ask("  Container (mp4/mkv/webm): ") or "mp4"
        args += ["-f", f, "--merge-output-format", m]
    else:
        args += ["-f", "bestvideo[ext=mp4]/bestvideo", "--merge-output-format", "mp4"]

    if find_ffmpeg():
        args += ["--ffmpeg-location", which("ffmpeg"),
                 "--postprocessor-args", "ffmpeg:-c copy -an"]

    section("2 / 3   OUTPUT")
    args = build_output(args)
    args = build_auth(args)

    section("3 / 3   URL")
    url = ask("  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, download_video_only)

# ═════════════════════════════════════════════════════════════════════════════
#  [6] PLAYLIST / CHANNEL
# ═════════════════════════════════════════════════════════════════════════════
def download_playlist():
    clr()
    print("""
  ═════════════════════════════════════════════════════════
   DOWNLOAD PLAYLIST / CHANNEL
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("1 / 4   FORMAT")
    print("""   [1]  Best H.264 → mp4       (recommended)
   [2]  Best overall → mkv
   [3]  Audio only → mp3
   [4]  Audio only → m4a
   [5]  Custom format string
""")
    fmt_ch = ask("  >> Choose: ")

    if fmt_ch == "1":
        args += ["-f",
                 "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                 "--merge-output-format", "mp4"]
    elif fmt_ch == "2":
        args += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv"]
    elif fmt_ch == "3":
        args += ["-x", "--audio-format", "mp3", "--audio-quality", "320"]
    elif fmt_ch == "4":
        args += ["-x", "--audio-format", "m4a"]
    elif fmt_ch == "5":
        f = ask("  Format string: ")
        m = ask("  Container (mp4/mkv/webm): ") or "mkv"
        if f: args += ["-f", f, "--merge-output-format", m]

    if find_ffmpeg():
        args += ["--ffmpeg-location", which("ffmpeg")]

    section("2 / 4   PLAYLIST RANGE")
    pi = ask("  Start index  (blank=1): ")
    pe = ask("  End index    (blank=all): ")
    if pi: args += ["--playlist-start", pi]
    if pe: args += ["--playlist-end",   pe]

    items = ask("  Specific items  (e.g. 1,3,5-7 | blank=skip): ")
    if items: args += ["--playlist-items", items]

    rev = ask("  Download in reverse order? (y/N): ")
    if rev.lower() == "y": args.append("--playlist-reverse")

    section("3 / 4   OUTPUT")
    print(f"  {Y}Tip: use %(playlist_index)s in template for numbered files{RS}")
    args = build_output(args)
    args = build_auth(args)
    args = build_misc(args)

    section("4 / 4   URL")
    url = ask("  Playlist / Channel URL: ")
    if url: args.append(url)

    _confirm_and_run(args, download_playlist)

# ═════════════════════════════════════════════════════════════════════════════
#  [7] ADVANCED / CUSTOM  (spoofing, referer, proxies, fixup …)
# ═════════════════════════════════════════════════════════════════════════════
def advanced_menu():
    clr()
    print(f"""
  ═════════════════════════════════════════════════════════
   ADVANCED / CUSTOM DOWNLOAD
  ═════════════════════════════════════════════════════════
   For restricted sites, CDN streams, geo-blocked content,
   RapidCloud, Zoro, 9anime, Crunchyroll DRM-free, etc.
  ═════════════════════════════════════════════════════════

   [1]  RapidCloud / StreamTape preset        {Y}(anime / streaming){RS}
   [2]  Geo-blocked content  (via proxy/VPN)
   [3]  Fully custom  (build every flag yourself)
   [B]  Back
  ═════════════════════════════════════════════════════════""")

    ch = ask("  >> Choose: ").lower()
    if   ch == "1": advanced_rapidcloud()
    elif ch == "2": advanced_geo()
    elif ch == "3": advanced_custom()
    elif ch == "b": main_menu()
    else: advanced_menu()

# ── RapidCloud / streaming sites preset ──────────────────────────────────────
def advanced_rapidcloud():
    clr()
    print(f"""
  ═════════════════════════════════════════════════════════
   RAPIDCLOUD / STREAMING SITE PRESET
  ─────────────────────────────────────────────────────────
   Pre-fills: referer, modern user-agent, native downloader,
   --fixup never, best quality up to 1080p
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("1 / 4   REFERER & USER-AGENT")
    default_ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/139.0.0.0 Safari/537.36")
    default_ref = "https://rapid-cloud.co/"

    ref = ask(f"  Referer URL\n  [{default_ref}]\n  >> (blank=use default): ")
    ua  = ask(f"\n  User-Agent\n  [Chrome 139 Windows]\n  >> (blank=use default): ")

    args += ["--referer",    ref or default_ref]
    args += ["--user-agent", ua  or default_ua]
    args += ["--downloader", "native"]
    args += ["--fixup",      "never"]

    section("2 / 4   FORMAT")
    print("""   [1]  Best ≤ 1080p  (any codec)  ← default
   [2]  Best ≤  720p
   [3]  Best ≤  480p
   [4]  Best H.264 ≤ 1080p → mp4
   [5]  Custom format string
""")
    fmt_ch = ask("  >> Choose (blank=1): ") or "1"
    FMT = {
        "1": ("best[height<=1080]/best",                            "mp4"),
        "2": ("best[height<=720]/best",                             "mp4"),
        "3": ("best[height<=480]/best",                             "mp4"),
        "4": ("bestvideo[height<=1080][vcodec^=avc1]+bestaudio"
              "/best[height<=1080][ext=mp4]/best[height<=1080]",    "mp4"),
    }
    if fmt_ch in FMT:
        f, m = FMT[fmt_ch]
        args += ["-f", f, "--merge-output-format", m]
    elif fmt_ch == "5":
        f = ask("  Format string: ")
        m = ask("  Container: ") or "mp4"
        args += ["-f", f, "--merge-output-format", m]
    else:
        args += ["-f", "best[height<=1080]/best", "--merge-output-format", "mp4"]

    # Extra headers
    if ask("\n  Add extra HTTP headers? (y/N): ").lower() == "y":
        while True:
            hdr = ask("  Header  (e.g. Origin: https://example.com | blank=done): ")
            if not hdr: break
            args += ["--add-header", hdr]

    section("3 / 4   OUTPUT")
    args = build_output(args)
    args = build_auth(args)

    if ask("  Verbose output? (y/N): ").lower() == "y":
        args.append("--verbose")

    section("4 / 4   URL")
    url = ask("  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, advanced_rapidcloud)

# ── Geo-blocked preset ────────────────────────────────────────────────────────
def advanced_geo():
    clr()
    print("""
  ═════════════════════════════════════════════════════════
   GEO-BLOCKED CONTENT
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("PROXY / GEO OPTIONS")
    print("""   [1]  HTTP/HTTPS proxy
   [2]  SOCKS5 proxy
   [3]  Geo-bypass  (yt-dlp built-in)
   [4]  Geo-bypass for specific country code
""")
    geo_ch = ask("  >> Choose: ")

    if geo_ch == "1":
        prx = ask("  Proxy URL  (e.g. http://user:pass@host:port): ")
        if prx: args += ["--proxy", prx]
    elif geo_ch == "2":
        prx = ask("  SOCKS5 URL  (e.g. socks5://127.0.0.1:1080): ")
        if prx: args += ["--proxy", prx]
    elif geo_ch == "3":
        args.append("--geo-bypass")
    elif geo_ch == "4":
        cc = ask("  Country code  (e.g. US, JP, GB): ").upper()
        if cc: args += ["--geo-bypass-country", cc]

    args += ["-f",
             "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
             "--merge-output-format", "mp4"]

    if find_ffmpeg():
        args += ["--ffmpeg-location", which("ffmpeg")]

    args = build_output(args)
    args = build_auth(args)

    url = ask("\n  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, advanced_geo)

# ── Fully custom ──────────────────────────────────────────────────────────────
def advanced_custom():
    clr()
    print(f"""
  ═════════════════════════════════════════════════════════
   FULLY CUSTOM  —  set every flag yourself
  ═════════════════════════════════════════════════════════
  {Y}  Tip: run  yt-dlp --help  to see all flags.{RS}
  ═════════════════════════════════════════════════════════""")

    args = ["yt-dlp"]

    section("CUSTOM FLAGS")
    print("  Enter flags one at a time (e.g.  --referer https://example.com )")
    print("  For flags with values enter both parts on the same line separated by space.")
    print("  Type 'done' when finished.\n")

    while True:
        flag = ask("  Flag: ")
        if not flag or flag.lower() == "done": break
        parts = flag.split(" ", 1)
        args += parts

    url = ask("\n  URL to download: ")
    if url: args.append(url)

    _confirm_and_run(args, advanced_custom)

# ═════════════════════════════════════════════════════════════════════════════
#  Confirm & run  (shared)
# ═════════════════════════════════════════════════════════════════════════════
def _confirm_and_run(args, retry_fn):
    cmd_str = " ".join(f'"{a}"' if (" " in a and not a.startswith("-")) else a
                       for a in args)
    print(f"""
{Y}  ═════════════════════════════════════════════════════════
   FINAL COMMAND:

   {cmd_str}
  ════════════════════════════════════════════════════════={RS}""")

    ch = ask("  [R]un  [E]dit  [C]ancel: ").lower()
    if ch == "r":
        print(f"\n{G}  Starting download …{RS}\n")
        print("  ─────────────────────────────────────────────────────\n")
        run(args)
        print(f"""
  ═════════════════════════════════════════════════════════
{G}   Done!{RS}
  ═════════════════════════════════════════════════════════""")
        if ask("\n  Download another? (y/N): ").lower() == "y":
            retry_fn()
        else:
            main_menu()
    elif ch == "e":
        retry_fn()
    else:
        main_menu()

# ═════════════════════════════════════════════════════════════════════════════
#  Exit
# ═════════════════════════════════════════════════════════════════════════════
def bye():
    clr()
    print(f"\n  {G}Goodbye! Happy downloading.{RS}\n")
    sys.exit(0)

# ═════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Interrupted. Bye!{RS}\n")
        sys.exit(0)
