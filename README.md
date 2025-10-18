# JVC GY-HM100 Video Importer

A Python script to import video clips from a JVC GY-HM100 camera SD card, parse metadata, and encode videos to widely compatible H.264 + AAC MP4 files with optional vhs-like dynamic timestamp.

## Features

- Automatically parses the camera’s `MEDIAPRO.xml` to detect clips and retrieve metadata (duration, FPS, audio channels, progressive/interlaced).
- Supports hybrid CLI behavior:
  - Run from SD card root with no parameters.
  - Pass `--source` to specify SD card path manually.
- Encodes video to H.264 + AAC MP4 with configurable quality presets.
- Automatic creation of output folder if it doesn’t exist.
- Progress bar showing encoding progress for each clip.
- Handles multiple clips in a single run.
- Oprional dynamic real VHS-like timestamp

## Installation

```bash
git clone <repo-url>
cd gy-hm100-video-importer
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Usage

### Run from SD card root (auto-detect)

`gy-import`

### Specify SD card path

`gy-import --source /Volumes/Untitled`

### Specify output folder

`gy-import --output ./imported_clips`

### Set video quality preset (high, medium, low)

`gy-import --quality high`

### Include real dyncamic VHS-like timestamp

`gy-import --include-timestamp`

## Quality Presets

| Preset             | CRF | FFmpeg Preset | Description                                       |
| ------------------ | --- | ------------- | ------------------------------------------------- |
| **high** (default) | 18  | slow          | Visually lossless, best quality, larger file size |
| **medium**         | 20  | medium        | Good balance of quality and file size             |
| **low**            | 22  | fast          | Smaller files, faster encoding, lower quality     |

## Output

- Converted files are saved in the output folder (`imported` by default).
- Output filenames are generated as `ORIGINALNAME_converted.mp4`.
- Clip metadata is printed in the console:

## Notes

- Progressive vs interlaced clips are automatically detected and converted if needed
- Works on macOS, Windows, and iOS devices
- Optional dynamic timestamp like on old tape recorders
