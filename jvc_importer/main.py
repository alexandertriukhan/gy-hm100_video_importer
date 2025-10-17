# jvc_importer/main.py
from pathlib import Path
from .cli import parse_args
from .parser import parse_mediapro_xml
from .video import encode_clips
from .constants import DEFAULT_OUTPUT_DIR, QualityPreset, VIDEO_PRESETS


def main():
    """
    Main entry point for the JVC video importer.

    Workflow:
    1. Parse command-line arguments (supports hybrid behavior: --source optional)
    2. Parse MEDIAPRO.xml to get all clips
    3. Display clip metadata
    4. Encode all clips to H.264 + AAC MP4
    """
    args = parse_args()
    sdcard_path: Path = Path(args.source or Path.cwd())

    # Use either the user-specified output folder or the default
    output_path: Path = Path(args.output or DEFAULT_OUTPUT_DIR)

    print(f"🔹 SD card path: {sdcard_path}")
    print(f"🔹 Output folder: {output_path}")

    # Parse clips from MEDIAPRO.xml
    try:
        clips = parse_mediapro_xml(sdcard_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    print(f"Found {len(clips)} clips on SD card.\n")

    # Display clip metadata
    for clip in clips:
        print(f"- {clip.video_file} ({clip.duration} frames, {clip.fps}, {clip.channels}ch, {clip.scan_type.value})")

    quality_enum = QualityPreset(args.quality)
    preset_settings = VIDEO_PRESETS[quality_enum]
    include_timestamp: bool = args.include_timestamp
    # Encode all clips
    print("\nStarting conversion to H.264 + AAC MP4...\n")
    converted_files = encode_clips(clips, output_path, preset_settings, include_timestamp)

    print(f"\n✅ Conversion complete! {len(converted_files)} files saved to {output_path}\n")
    for f in converted_files:
        print(f"- {f.name}")
