#!/usr/bin/env python3

import os
import shutil
from PIL import Image, PngImagePlugin
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog

THREADS = os.cpu_count() or 4
SEP = "=" * 50


def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(title="Select folder with images to compress")
    root.destroy()
    return folder


def extract_png_text_chunks(img):
    return dict(getattr(img, 'text', {}))


def compress_one(img_file: Path, dest_stem: Path, quality: int, max_width: int):
    try:
        original_size = img_file.stat().st_size

        with Image.open(img_file) as img:
            is_png      = img_file.suffix.lower() == '.png'
            text_chunks = extract_png_text_chunks(img) if is_png else {}
            has_meta    = bool(text_chunks)

            if img.width > max_width:
                new_h = int(img.height * max_width / img.width)
                img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)

            if has_meta:
                if img.mode == 'P':
                    img = img.convert('RGBA')
                pnginfo = PngImagePlugin.PngInfo()
                for k, v in text_chunks.items():
                    pnginfo.add_text(k, v)
                out = dest_stem.with_suffix('.png')
                img.save(str(out), 'PNG', pnginfo=pnginfo, compress_level=9, optimize=True)
                fmt = 'PNG'
            else:
                if img.mode in ('RGBA', 'LA'):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                elif img.mode == 'P':
                    img = img.convert('RGBA')
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                out = dest_stem.with_suffix('.jpg')
                img.save(str(out), 'JPEG', quality=quality, optimize=True)
                fmt = 'JPEG'

        compressed_size = out.stat().st_size
        return original_size, compressed_size, fmt, None

    except Exception as e:
        return 0, 0, '?', str(e)


def compress_folder(input_folder, quality=85, max_width=1920):
    input_path = Path(input_folder)
    if not input_path.exists():
        print(f"Error: '{input_folder}' does not exist!")
        return

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir  = Path(__file__).parent.resolve()
    output_path = script_dir / f"ImageCompressed_{timestamp}"
    output_path.mkdir(exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    all_files     = [f for f in input_path.rglob('*') if f.is_file()]
    image_files   = [f for f in all_files if f.suffix.lower() in image_extensions]
    sidecar_files = [f for f in all_files if f.suffix.lower() not in image_extensions]

    if not all_files:
        print(f"No files found in '{input_folder}'")
        return

    print(SEP)
    print(" IMAGE COMPRESSOR")
    print(SEP)
    print(f"Input   : {input_path}")
    print(f"Output  : {output_path.name}")
    print(f"Images  : {len(image_files)}")
    print(f"Quality : {quality}   Max width: {max_width}px")
    print(SEP)

    dest_map = {}
    for img_file in image_files:
        rel       = img_file.relative_to(input_path)
        dest_stem = output_path / rel.parent / rel.stem
        dest_stem.parent.mkdir(parents=True, exist_ok=True)
        dest_map[img_file] = dest_stem

    total_before  = 0
    total_after   = 0
    success_count = 0

    # Index map so we can show [n/total] in order results arrive
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        future_to_file = {
            pool.submit(compress_one, f, dest_map[f], quality, max_width): f
            for f in image_files
        }
        done = 0
        for future in as_completed(future_to_file):
            img_file = future_to_file[future]
            done += 1
            orig, comp, fmt, err = future.result()

            if err:
                print(f"[{done}/{len(image_files)}]  {img_file.name}  -- {err}")
            else:
                total_before  += orig
                total_after   += comp
                success_count += 1
                pct = (1 - comp / orig) * 100 if orig else 0
                print(
                    f"[{done}/{len(image_files)}]  {img_file.name}  "
                    f"[{fmt}]  -{pct:.1f}%  "
                    f"({orig/1024/1024:.2f} MB -> {comp/1024/1024:.2f} MB)"
                )

    if sidecar_files:
        for f in sidecar_files:
            rel  = f.relative_to(input_path)
            dest = output_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(f, dest)
            except Exception:
                pass

    print()
    print("DONE")
    print(f"Compressed : {success_count}/{len(image_files)}")
    if total_before:
        saved = total_before - total_after
        print(f"Before     : {total_before / 1024**3:.3f} GB")
        print(f"After      : {total_after  / 1024**3:.3f} GB")
        print(f"Saved      : {saved        / 1024**3:.3f} GB  ({saved/total_before*100:.1f}%)")
    print(f"Output -> {output_path}")


if __name__ == "__main__":
    print()
    print("IMAGE COMPRESSOR")
    print("Opening folder picker...")
    print()

    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
    else:
        QUALITY   = 85
        MAX_WIDTH = 1920

        compress_folder(folder, quality=QUALITY, max_width=MAX_WIDTH)

    print()
    input("Press Enter to exit...")
