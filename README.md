# sort_by_date

Copy files from a folder into per-date subfolders (`YYYY-MM-DD`).

- Images (jpg, jpeg, tiff, png, webp, heic*): date from EXIF metadata
  (`DateTimeOriginal` > `DateTimeDigitized` > `DateTime`).
- Other files, or images without EXIF: file creation date; if filesystem/Python
  has no birth time, modification time is used.
- Originals are never touched (copy only, timestamps preserved).

\*HEIC needs `pillow-heif` registered; without it these fall back to file date.

## Install

Requires Python 3. Pillow is optional, needed for EXIF dates:

```bash
pip install --user pillow      # or: sudo apt install python3-pil
```

Make it runnable from any directory:

```bash
chmod +x /home/florjan/Documents/SW/Python/linux_tools/sort_images/sort_by_date.py
mkdir -p ~/.local/bin
ln -s /home/florjan/Documents/SW/Python/linux_tools/sort_images/sort_by_date.py ~/.local/bin/sort_by_date
```

Ensure `~/.local/bin` is in `PATH`.

## Usage

```bash
sort_by_date FOLDER [-o OUTPUT] [-r] [-n] [--format FMT]
```

| Option | Meaning |
|--------|---------|
| `FOLDER` | source folder |
| `-o, --output` | output folder. Default: `<FOLDER>_sorted` next to source |
| `-r, --recursive` | include subfolders |
| `-n, --dry-run` | print what would be copied, copy nothing |
| `--format` | date folder name format, strftime. Default `%Y-%m-%d` |

Examples:

```bash
sort_by_date ~/Pictures/phone
sort_by_date ~/Pictures/phone -o ~/Pictures/by_date -r
sort_by_date . -n
sort_by_date ~/Pictures/phone --format "%Y/%m"
```

Result:

```
phone_sorted/
├── 2024-07-14/
│   ├── IMG_0001.jpg
│   └── notes.txt
└── 2024-07-15/
    └── IMG_0002.jpg
```

## Duplicates

If target name exists: same size is treated as already copied and skipped;
different size gets a suffix (`name_1.jpg`). Re-running is safe.
