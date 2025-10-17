# jvc_importer/constants.py
from pathlib import Path
from enum import Enum


# XML namespace used in MEDIAPRO.xml for parsing
MEDIA_PRO_NAMESPACE = {'mp': 'http://xmlns.sony.net/pro/metadata/mediaprofile'}

# Default folder structure on the SD card
PRIVATE_FOLDER = "PRIVATE"
JVC_FOLDER = "JVC"
BPAV_FOLDER = "BPAV"
MEDIAPRO_XML = "MEDIAPRO.xml"

# Default output folder if not specified by user
DEFAULT_OUTPUT_DIR = Path("output")

# FFmpeg encoding settings for universal compatibility
FFMPEG_VIDEO_CODEC = "libx264"   # H.264 video codec
FFMPEG_AUDIO_CODEC = "aac"       # AAC audio codec
FFMPEG_AUDIO_BITRATE = "256k"    # Audio bitrate

# Path to VHS-style font
VHS_FONT_PATH = Path(__file__).parent.parent / "font" / "VCR_OSD_MONO.ttf"
VHS_FONT_SIZE = 28

# Enum for scan type
class ScanType(Enum):
    PROGRESSIVE = "progressive"
    INTERLACED = "interlaced"

# Video encoding presets
class QualityPreset(Enum):
    HIGH = "high"       # visually lossless, CRF 16, slow preset
    MEDIUM = "medium"   # default, CRF 18, medium preset
    LOW = "low"         # smaller files, CRF 20, fast preset

# Map enum to actual FFmpeg settings
VIDEO_PRESETS = {
    QualityPreset.HIGH:   {"crf": 18, "preset": "slow"},
    QualityPreset.MEDIUM: {"crf": 20, "preset": "medium"},
    QualityPreset.LOW:    {"crf": 22, "preset": "fast"},
}

DEFAULT_VIDEO_PRESET = QualityPreset.HIGH
