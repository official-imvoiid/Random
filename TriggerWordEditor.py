#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


def get_folder():
    while True:
        raw = input("\nEnter folder path: ").strip().strip('"').strip("'")
        if not raw:
            print("  Error: path cannot be empty.")
            continue
        p = Path(raw)
        if p.is_file():
            p = p.parent
        if p.is_dir():
            return p
        print(f"  Error: folder not found — {raw}")


def get_txt_files(folder):
    files = sorted(folder.glob("*.txt"))
    if not files:
        print(f"  No .txt files found in: {folder}")
    else:
        print(f"  Found {len(files)} .txt file(s)")
    return files


def confirm(msg):
    return input(f"\n{msg} (y/n): ").strip().lower() in ("y", "yes")


def do_prepend(folder):
    files = get_txt_files(folder)
    if not files:
        return

    text = input("\nText to add at the START of every .txt: ").strip()
    if not text:
        print("  Cancelled — nothing entered.")
        return

    # Strip trailing comma/space from user input — we always add ", " ourselves
    text = text.rstrip(", ")

    if not confirm(f'Prepend  "{text}, "  to {len(files)} files?'):
        print("  Cancelled.")
        return

    ok = err = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8").lstrip(", ")
            f.write_text(text + ", " + content, encoding="utf-8")
            print(f"  OK  {f.name}")
            ok += 1
        except Exception as e:
            print(f"  ERR {f.name} — {e}")
            err += 1
    print(f"\n  Done: {ok} ok, {err} errors")


def do_remove(folder):
    files = get_txt_files(folder)
    if not files:
        return

    print("\nEnter word(s) to REMOVE, separated by commas.")
    print("  Example: anime, cartoon style, bad quality")
    raw = input("  Remove: ").strip()
    if not raw:
        print("  Cancelled — nothing entered.")
        return

    words = {w.strip().lower() for w in raw.split(",") if w.strip()}
    print(f"\n  Will remove: {', '.join(words)}")

    if not confirm(f"Remove from {len(files)} files?"):
        print("  Cancelled.")
        return

    ok = err = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            tags = [t.strip() for t in content.split(",")]
            filtered = [t for t in tags if t.lower() not in words and t]
            f.write_text(", ".join(filtered), encoding="utf-8")
            print(f"  OK  {f.name}")
            ok += 1
        except Exception as e:
            print(f"  ERR {f.name} — {e}")
            err += 1
    print(f"\n  Done: {ok} ok, {err} errors")


def do_replace(folder):
    files = get_txt_files(folder)
    if not files:
        return

    find = input("\n  Find:            ").strip()
    if not find:
        print("  Cancelled — nothing entered.")
        return
    repl = input("  Replace with:    ").strip()

    label = f'"{repl}"' if repl else "(delete)"
    if not confirm(f'Replace "{find}" → {label} in {len(files)} files?'):
        print("  Cancelled.")
        return

    ok = err = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            new = content.replace(find, repl)
            if not repl:
                new = re.sub(r",\s*,", ", ", new)
                new = new.strip(", ").strip()
            f.write_text(new, encoding="utf-8")
            print(f"  OK  {f.name}")
            ok += 1
        except Exception as e:
            print(f"  ERR {f.name} — {e}")
            err += 1
    print(f"\n  Done: {ok} ok, {err} errors")


def main():
    print("=" * 50)
    print("  TRIGGER WORD EDITOR")
    print("=" * 50)

    folder = get_folder()

    while True:
        print(f"\n  Folder : {folder}")
        print("  --------------------------------")
        print("  1. Prepend  (add word at start)")
        print("  2. Remove   (delete word(s))")
        print("  3. Replace  (find & replace)")
        print("  4. Change folder")
        print("  5. Exit")

        choice = input("\n  Choice: ").strip()

        if   choice == "1": do_prepend(folder)
        elif choice == "2": do_remove(folder)
        elif choice == "3": do_replace(folder)
        elif choice == "4": folder = get_folder()
        elif choice == "5": break
        else: print("  Invalid — enter 1 to 5")

    print("\n  Bye!")
    input("\nPress Enter to close...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
        sys.exit(0)
