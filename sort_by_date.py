#!/usr/bin/env python3
"""Copy files from a folder into per-date subfolders (YYYY-MM-DD).

Images use the EXIF capture date when available (needs Pillow, optional).
Everything else (or images without EXIF) uses the file creation date,
falling back to modification time where the filesystem has no birth time.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow optional
    Image = None

EXIF_IFD = 0x8769
EXIF_DATE_TAGS = (36867, 36868, 306)  # DateTimeOriginal, Digitized, DateTime
IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".webp", ".heic", ".heif"}


def exif_date(path: Path):
    if Image is None or path.suffix.lower() not in IMAGE_EXTS:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            candidates = [exif.get_ifd(EXIF_IFD).get(t) for t in EXIF_DATE_TAGS[:2]]
            candidates.append(exif.get(EXIF_DATE_TAGS[2]))
    except Exception:
        return None
    for value in candidates:
        if not value:
            continue
        try:
            dt = datetime.strptime(str(value).strip()[:19], "%Y:%m:%d %H:%M:%S")
        except ValueError:
            continue
        if dt.year > 1900:  # skip "0000:00:00" junk
            return dt
    return None


def fs_date(path: Path) -> datetime:
    st = path.stat()
    ts = getattr(st, "st_birthtime", None)  # Python 3.12+ on Linux, if fs supports
    if not ts:
        ts = st.st_mtime
    return datetime.fromtimestamp(ts)


def file_date(path: Path) -> datetime:
    return exif_date(path) or fs_date(path)


def unique_target(dest: Path, src: Path):
    """Return a free path, or None if identical file already there."""
    if not dest.exists():
        return dest
    if dest.stat().st_size == src.stat().st_size:
        return None  # same name + size: treat as already copied
    n = 1
    while True:
        cand = dest.with_name(f"{dest.stem}_{n}{dest.suffix}")
        if not cand.exists():
            return cand
        n += 1


def iter_files(root: Path, recursive: bool, skip: Path):
    if recursive:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if (Path(dirpath) / d).resolve() != skip]
            for f in filenames:
                yield Path(dirpath) / f
    else:
        for p in sorted(root.iterdir()):
            if p.is_file():
                yield p


def main():
    ap = argparse.ArgumentParser(description="Sort files into per-date folders.")
    ap.add_argument("folder", help="source folder")
    ap.add_argument("-o", "--output", help="output folder (default: <folder>_sorted next to source)")
    ap.add_argument("-r", "--recursive", action="store_true", help="include subfolders")
    ap.add_argument("-n", "--dry-run", action="store_true", help="show actions, copy nothing")
    ap.add_argument("--format", default="%Y-%m-%d", help="date folder format (default: %%Y-%%m-%%d)")
    args = ap.parse_args()

    src = Path(args.folder).expanduser().resolve()
    if not src.is_dir():
        sys.exit(f"Not a directory: {src}")
    out = Path(args.output).expanduser().resolve() if args.output else src.with_name(src.name + "_sorted")

    if Image is None:
        print("Note: Pillow not installed, image EXIF dates unavailable (pip install pillow).",
              file=sys.stderr)

    copied = skipped = 0
    for f in iter_files(src, args.recursive, out):
        dest_dir = out / file_date(f).strftime(args.format)
        target = unique_target(dest_dir / f.name, f)
        if target is None:
            skipped += 1
            continue
        print(f"{f} -> {target}")
        if not args.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
        copied += 1

    print(f"Done. {'Would copy' if args.dry_run else 'Copied'}: {copied}, skipped duplicates: {skipped}. Output: {out}")


if __name__ == "__main__":
    main()
