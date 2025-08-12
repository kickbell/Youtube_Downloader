<div align="right">
  <a href="README.md">한국어</a> | <b>English</b>
</div>

# YouTube Shorts Downloader (macOS)

A simple CLI tool to download YouTube videos (optimized for Shorts), extract screenshots at a fixed interval, and bundle them into a single PDF.

## ✅ Usage Guide 
<img width="925" height="564" alt="Image" src="https://github.com/user-attachments/assets/55252672-8e3a-455f-806b-d168f0e708a4" />
<img width="1011" height="623" alt="Image" src="https://github.com/user-attachments/assets/6fee779b-d312-44f5-bf8b-d9863f56dc74" />

## ✨ Features
- **Video download**: Save with audio using `yt-dlp` and choose the preferred format
- **Quality/codec selection**: Pick from available formats interactively
- **Screenshot extraction**: Grab frames every N seconds via `ffmpeg`
- **PDF generation**: Merge screenshots into a single PDF using `Pillow`
- **Estimated size**: Show rough PDF size based on the interval
- **Safe output location**: Results are organized under `Desktop/YouTube_Downloads/<video-title>/`
- **Optimized for YouTube Shorts**: Guidance for vertical (9:16) videos and recommended intervals

## 🧩 How it works
1) Enter URL → 2) Enter screenshot interval (sec) → 3) Review available formats → 4) Choose quality → 5) Download → 6) Extract screenshots → 7) Generate PDF

PDF size is estimated as: screenshots × 200KB, where screenshots ≈ \( \lfloor duration / interval \rfloor \).

## 🎯 Optimized for YouTube Shorts
- **Recommended interval (Shorts)**: 1–3 seconds
  - Example: 60s video with 2s interval → ~30 images → ~6MB (200KB × 30)
- **Recommended vertical resolutions**: `1080x1920`, `720x1280`
  - Lists may include both landscape (`1920x1080`) and portrait (`1080x1920`). Choose portrait for Shorts.
- **URL support**: `https://www.youtube.com/shorts/...` works as-is
- **Faster processing**: Short videos finish download/extract/merge quickly

## 🚀 Quickstart (macOS)

### 1) Install prerequisites
```bash
# Python packages
python3 -m pip install --upgrade pip
python3 -m pip install Pillow yt-dlp

# Frame extraction
brew install ffmpeg

# (optional) Add default pip bin path
echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# Verify
yt-dlp --version
ffmpeg -version
```

> On Apple Silicon (M1/M2), `yt-dlp` may be installed at `/opt/homebrew/bin/yt-dlp`. The script looks up common install paths automatically.

### 2) Run
```bash
python3 downloader.py
```

### 3) Flow
1. Paste the YouTube URL
2. Enter screenshot interval in seconds (e.g., `30`)
3. Choose a quality index from the list
4. Check results under `Desktop/YouTube_Downloads/<video-title>/`

## 📁 Output structure
Example with title `My Video`:

```
Desktop/
└── YouTube_Downloads/
    └── My Video/
        ├── My Video.mp4
        ├── screenshots/
        │   ├── screenshot_0001.png
        │   ├── screenshot_0002.png
        │   └── ...
        └── My Video_screenshots.pdf
```

## ⚙️ Details & options
- **Formats**: Only lists formats that include audio
- **Size**: Shows downloadable file size (if available) and estimated PDF size
- **Interval (sec)**:
  - Shorts (≤60s): `1–3s` recommended
  - Regular videos: `10–60s` recommended

## 💡 Example (console)
```
Enter YouTube URL: https://www.youtube.com/watch?v=EXAMPLE
How many seconds for the screenshot interval? 30

Available video formats:
--------------------------------------------------------------------------------
No.  Resolution  File (est.)     PDF (est.)           Codec
--------------------------------------------------------------------------------
1    1920x1080   120.45 MB       8.00 MB              avc1
2    1280x720    80.12 MB        8.00 MB              avc1
...
--------------------------------------------------------------------------------
Choose a format number (or 'q' to cancel): 2

Starting download to 'Desktop/YouTube_Downloads/My Video'...
Download complete!
Starting screenshot extraction (30s interval)...
Screenshots created.
Generating PDF '.../My Video_screenshots.pdf'...
PDF created!
```

## 🔍 Troubleshooting
- `python` not found: run with `python3 downloader.py`
- `No module named 'PIL'`: reinstall with `python3 -m pip install Pillow`
- `yt-dlp` not found:
  - `python3 -m pip install yt-dlp` and verify with `yt-dlp --version`
  - Add PATH: `echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc`
  - On Apple Silicon it may live at `/opt/homebrew/bin/yt-dlp`
- `ffmpeg` not found:
  - `brew install ffmpeg` then `ffmpeg -version`
  - Open a new terminal or `source ~/.zshrc`
- Permission/path conflicts: use a virtualenv
  - `python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install Pillow yt-dlp`

## 🛡️ Legal
- For personal/educational use only
- Follow platform Terms of Service and copyright law

## 🧱 Tech stack
- `yt-dlp`, `ffmpeg`, `Pillow (PIL)`, Python stdlib (`subprocess`, `json`, `os`, `shutil`)

## 🔧 Internals (short)
- `find_ytdlp_path()`: find `yt-dlp` in common locations
- `get_video_info(url)`: query formats/metadata via `yt-dlp -j`
- `display_formats(...)`: show selectable formats + estimated PDF size
- `download_video(...)`: download selected format and return path
- `take_screenshots_and_create_pdf(...)`: extract PNG via `ffmpeg`, merge PDF via `Pillow`

## 🗺️ Roadmap
- Auto selection by quality/size
- Screenshot resolution/quality control
- Simple drag-and-drop GUI

## 🙋 FAQ
- **Does it support Shorts?** Yes. It is optimized for Shorts; use portrait resolutions and 1–3s intervals.
- **Other sites?** It might work via `yt-dlp`, but only YouTube is documented here.
- **PDF too large?** Use longer intervals; resolution/quality controls may be added later.

---
Issues and suggestions are welcome. Thank you!


