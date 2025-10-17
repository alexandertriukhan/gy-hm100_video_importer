# jvc_importer/cli.py
import argparse
from pathlib import Path
from .constants import QualityPreset, DEFAULT_VIDEO_PRESET


def parse_args():
    """
    Parses command-line arguments for the JVC video importer.

    Hybrid behavior:
    - If --source is not provided, the current working directory is assumed to be
      the SD card root.
    - Optional flags:
        --output/-o : output folder (default: "output")
        --timecode  : add timecode overlay
        --compress  : compress video (visually lossless)
    """
    
    parser = argparse.ArgumentParser(
        description="Import and convert JVC GY-HM100 clips from SD card."
    )
    parser.add_argument(
        "--source", "-s",
        type=str,
        default=None,
        help="Path to SD card root. Defaults to current working directory if not specified."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="imported",
        help="Output folder for converted clips."
    )
    parser.add_argument(
        "--quality", "-q",
        type=str,
        choices=[preset.value for preset in QualityPreset],
        default=DEFAULT_VIDEO_PRESET.value,
        help="Video encoding quality preset (high, medium, low). Default: high"
    )
    parser.add_argument(
        "--include-timestamp",
        action="store_true",
        default=False,
        help="Include VHS-style timestamp in bottom-right corner"
    )

    args = parser.parse_args()

    # Hybrid behavior: use cwd if source not provided
    if args.source is None:
        args.source = Path.cwd()

    return args
