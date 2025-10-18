# jvc_importer/parser.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from .constants import MEDIA_PRO_NAMESPACE, PRIVATE_FOLDER, JVC_FOLDER, BPAV_FOLDER, MEDIAPRO_XML, ScanType


@dataclass
class Clip:
    """
    Represents a single video clip from a JVC GY-HM100 SD card.
    """
    clip_uri: str
    video_file: str
    duration: int
    fps: float
    scan_type: ScanType
    aspect_ratio: str
    channels: int
    video_type: str
    audio_type: str
    creation_time: datetime


def extract_creation_date(meta_xml_path: Path) -> datetime | None:
    import xml.etree.ElementTree as ET
    
    if not meta_xml_path.exists():
        return None

    tree = ET.parse(meta_xml_path)
    root = tree.getroot()
    ns = {"nrt": "urn:schemas-professionalDisc:nonRealTimeMeta:ver.1.30"}

    creation_date_elem = root.find("nrt:CreationDate", ns)
    if creation_date_elem is not None:
        value = creation_date_elem.attrib.get("value")
        if value:
            # Example: 2025-10-17T10:38:39-05:00
            iso_naive = value[:-6]
            return datetime.fromisoformat(iso_naive)
    return None


def parse_mediapro_xml(sdcard_path: str) -> list[Clip]:
    """
    Parses MEDIAPRO.xml on the SD card and returns a list of Clip objects.

    Args:
        sdcard_path: Path to the root of the SD card.

    Returns:
        List of Clip instances containing metadata for each recorded video.
    """
    xml_path = Path(sdcard_path) / PRIVATE_FOLDER / JVC_FOLDER / BPAV_FOLDER / MEDIAPRO_XML
    if not xml_path.exists():
        raise FileNotFoundError(f"MEDIAPRO.xml not found at {xml_path}")

    bpav_root = Path(sdcard_path) / PRIVATE_FOLDER / JVC_FOLDER / BPAV_FOLDER
    tree = ET.parse(xml_path)
    root = tree.getroot()

    clips = []

    for material in root.findall('.//mp:Material', MEDIA_PRO_NAMESPACE):
        component = material.find('mp:Component', MEDIA_PRO_NAMESPACE)

        # Parse fps and scan type
        fps_str = material.get('fps')  # e.g., "23.98p"
        fps_value = float(fps_str[:-1])
        scan_type_char = fps_str[-1]
        scan_type = ScanType.PROGRESSIVE if scan_type_char == "p" else ScanType.INTERLACED

        video_full_path = bpav_root / component.get('uri').lstrip("./")

        # Grab the first RelevantInfo XML file for creation date
        creation_time = None
        for info in material.findall("mp:RelevantInfo", MEDIA_PRO_NAMESPACE):
            if info.attrib.get("type") == "XML":
                meta_xml_path = bpav_root / info.attrib.get("uri").lstrip("./")
                creation_time = extract_creation_date(meta_xml_path)
                break  # only one XML matters

        clip = Clip(
            clip_uri=material.get('uri'),
            video_file=str(video_full_path),
            duration=int(material.get('dur')),
            fps=fps_value,
            scan_type=scan_type,
            aspect_ratio=material.get('aspectRatio'),
            channels=int(material.get('ch')),
            video_type=component.get('videoType'),
            audio_type=component.get('audioType'),
            creation_time=creation_time
        )
        clips.append(clip)
    
    return clips
