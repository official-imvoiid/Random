#!/usr/bin/env python3
"""
Gallery-DL Quick Tool v1.0
Cross-platform: Windows, Linux, macOS
Supports 300+ sites: Pixiv, DeviantArt, Twitter/X, ArtStation, Danbooru, etc.
"""

import os
import sys
import subprocess
import platform
import getpass
from shutil import which

# ── Colours ──────────────────────────────────────────────────────────────────
IS_WIN = platform.system() == "Windows"
if IS_WIN:
    os.system("color")   # enable ANSI on Windows 10+

R  = "\033[0;31m"
G  = "\033[0;32m"
Y  = "\033[1;33m"
C  = "\033[0;36m"
RS = "\033[0m"

# ── Helpers ───────────────────────────────────────────────────────────────────
def clr():
    os.system("cls" if IS_WIN else "clear")

def pause():
    input("  Press Enter to continue...")

def ask(prompt, hidden=False):
    try:
        return (getpass.getpass(prompt) if hidden else input(prompt)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        main_menu()
        return ""

def run(cmd):
    """Run command and keep terminal fully interactive."""
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        print(f"\n{R}  [!] Not found: {cmd[0]}{RS}")
        print("      Install gallery-dl first (option 1 in the menu).\n")

def find_pip():
    return which("pip3") or which("pip") or "pip"

def find_gdl():
    return which("gallery-dl")

def section(title):
    print(f"\n{Y}  ─────────────────────────────────────────────────────")
    print(f"   {title}")
    print(f"  ─────────────────────────────────────────────────────{RS}\n")

# ── Main menu ─────────────────────────────────────────────────────────────────
def main_menu():
    clr()
    print(f"""{C}
  =========================================================
   _____       _ _                        _____  _ 
  / ____|     | | |                      |  __ \| |
 | |  __  __ _| | | ___ _ __ _   _ ______| |  | | |
 | | |_ |/ _` | | |/ _ \ '__| | | |______| |  | | |
 | |__| | (_| | | |  __/ |  | |_| |      | |__| | |
  \_____|\__,_|_|_|\___|_|   \__, |      |_____/|_|
                              __/ |                
                             |___/                 
  ========================================================={RS}
   Gallery-DL Quick Tool
{Y}  ─────────────────────────────────────────────────────{RS}
   Pixiv · DeviantArt · Twitter/X · ArtStation
   Danbooru · Gelbooru · Instagram · Nijie · Weibo
   Reddit · Tumblr · Pinterest · and 300+ more sites
{Y}  ========================================================={RS}

   [1]  Install / Upgrade gallery-dl
   [2]  Remove gallery-dl
   [3]  Quick Download  (step-by-step setup)
   [4]  Check installed version
   [0]  Exit
{Y}  ========================================================={RS}""")

    ch = ask("  >> Choose: ")
    {
        "1": install_menu,
        "2": remove_menu,
        "3": quick_tool,
        "4": check_version,
        "0": bye,
    }.get(ch, main_menu)()

# ── Install / Upgrade ─────────────────────────────────────────────────────────
def install_menu():
    clr()
    print(f"""
  =========================================================
   INSTALL / UPGRADE gallery-dl
  =========================================================
   [1]  Install / Upgrade  (standard pip)
   [2]  Install for current user only  (--user, no admin)
   [3]  Install a specific version
   [4]  Install latest dev build from GitHub
   [B]  Back
  =========================================================""")

    ch = ask("  >> Choose: ").lower()
    pip = find_pip()

    if   ch == "1": run([pip, "install", "--upgrade", "gallery-dl"])
    elif ch == "2": run([pip, "install", "--upgrade", "--user", "gallery-dl"])
    elif ch == "3":
        ver = ask("  Version number (e.g. 1.27.0): ")
        run([pip, "install", f"gallery-dl=={ver}"])
    elif ch == "4":
        run([pip, "install", "--upgrade",
             "git+https://github.com/mikf/gallery-dl.git"])
    elif ch == "b":
        main_menu(); return

    print(f"\n{G}  [OK] Done!{RS}\n")
    pause(); main_menu()

# ── Remove ─────────────────────────────────────────────────────────────────────
def remove_menu():
    clr()
    print(f"""
  =========================================================
   REMOVE gallery-dl
  =========================================================
  {R} WARNING: This will uninstall gallery-dl.{RS}
   [Y] Confirm   [N] Go back
  =========================================================""")
    if ask("  >> (Y/N): ").lower() == "y":
        run([find_pip(), "uninstall", "gallery-dl", "-y"])
        print(f"\n{G}  [OK] Removed.{RS}\n")
        pause()
    main_menu()

# ── Version ────────────────────────────────────────────────────────────────────
def check_version():
    clr()
    print("\n  =========================================================")
    print("   VERSION INFO")
    print("  =========================================================\n")
    if find_gdl():
        run(["gallery-dl", "--version"])
    else:
        print(f"  {R}[!] gallery-dl is not installed.{RS}")
    print()
    pause(); main_menu()

# ── Quick Download ─────────────────────────────────────────────────────────────
def quick_tool():
    clr()
    print("""
  =========================================================
   QUICK DOWNLOAD – Step-by-step setup
   Just press Enter to skip any option.
  =========================================================""")

    args = []
    url_provided = False

    # Output folder
    print()
    out = ask("  [OUTPUT] Save folder (blank = current directory): ")
    if out: args += ["--destination", out]

    # ── 1/4 Initial settings ──────────────────────────────────────────────
    section("1 / 4   INITIAL SETTINGS")

    if ask("  Verbose / trace output? (y/N): ").lower() == "y":
        args.append("--verbose")

    s = ask("  Sleep between downloads in seconds (blank=skip): ")
    if s: args += ["--sleep", s]

    sr = ask("  Sleep between HTTP requests in seconds (blank=skip): ")
    if sr: args += ["--sleep-request", sr]

    if ask("  Abort on 4xx HTTP errors? (y/N): ").lower() == "y":
        code = ask("    Specific error code to abort on (e.g. 404 | blank=all): ")
        args += (["--abort", code] if code else ["--abort-on-error"])

    ret = ask("  Retries on failure (default=4 | blank=skip): ")
    if ret: args += ["--retries", ret]

    # ── 2/4 Metadata ──────────────────────────────────────────────────────
    section("2 / 4   METADATA OPTIONS")

    if ask("  Save source URL in metadata? (y/N): ").lower() == "y":
        args.append("--url-metadata")

    if ask("  Write .json metadata files alongside downloads? (y/N): ").lower() == "y":
        args.append("--write-metadata")

    if ask("  Write .tags files? (y/N): ").lower() == "y":
        args.append("--write-tags")

    # ── 3/4 Download options ──────────────────────────────────────────────
    section("3 / 4   DOWNLOAD OPTIONS")

    inf = ask("  Input file containing URLs (blank = enter URL below): ")
    if inf:
        args += ["--input-file", inf]
        url_provided = True

    rng = ask("  Item range  (e.g. 1-100 or 5,10,20 | blank=all): ")
    if rng: args += ["--range", rng]

    rate = ask("  Speed limit  (e.g. 1M = 1 MB/s | blank=unlimited): ")
    if rate: args += ["--rate", rate]

    fmt = ask("  Filename format  (e.g. {id}.{extension} | blank=default): ")
    if fmt: args += ["--filename", fmt]

    if ask("  Skip already downloaded files? (Y/n): ").lower() != "n":
        args.append("--skip")

    # ── 4/4 Authentication ────────────────────────────────────────────────
    section("4 / 4   AUTHENTICATION")
    print("""   [1]  cookies.txt file
   [2]  Browser cookies  (Chrome / Firefox / Edge / Brave / Opera …)
   [3]  Username + Password
   [4]  OAuth token  (edit config.json)
   [5]  None
""")
    auth = ask("  >> Choose auth method: ")

    if auth == "1":
        cf = ask("  Path to cookies.txt: ")
        if cf: args += ["--cookies", cf]

    elif auth == "2":
        print("  Supported: chrome, firefox, edge, safari, opera, brave, chromium, vivaldi")
        br   = ask("  Browser name: ")
        prof = ask("  Profile (blank=default): ")
        if br:
            args += ["--cookies-from-browser", f"{br}:{prof}" if prof else br]

    elif auth == "3":
        u = ask("  Username / Email: ")
        p = ask("  Password: ", hidden=True)
        if u: args += ["--username", u, "--password", p]

    elif auth == "4":
        cfg = (r"%APPDATA%\gallery-dl\config.json" if IS_WIN
               else "~/.config/gallery-dl/config.json")
        print(f"\n  {Y}[i] Edit config file to add OAuth tokens:{RS}")
        print(f"      {cfg}\n")
        pause()

    # ── URL ───────────────────────────────────────────────────────────────
    if not url_provided:
        print()
        url = ask("  URL to download: ")
        if url: args.append(url)

    # ── Confirm & run ─────────────────────────────────────────────────────
    cmd_str = "gallery-dl " + " ".join(
        f'"{a}"' if " " in a else a for a in args
    )
    print(f"""
{Y}  =========================================================
   FINAL COMMAND:

   {cmd_str}
  ========================================================={RS}""")

    if ask("  Run now? (Y/n): ").lower() == "n":
        quick_tool(); return

    print(f"\n{G}  Starting download …{RS}\n")
    print("  ─────────────────────────────────────────────────────\n")
    run(["gallery-dl"] + args)

    print(f"""
  =========================================================
{G}   Done!{RS}
  =========================================================""")

    if ask("\n  Download another URL? (y/N): ").lower() == "y":
        quick_tool()
    else:
        main_menu()

# ── Exit ───────────────────────────────────────────────────────────────────────
def bye():
    clr()
    print(f"\n  {G}Goodbye! Happy downloading.{RS}\n")
    sys.exit(0)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Interrupted.{RS}\n")
        sys.exit(0)
