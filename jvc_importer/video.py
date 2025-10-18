# jvc_importer/video.py
from pathlib import Path
from datetime import datetime
from .parser import Clip
from .constants import (
    FFMPEG_VIDEO_CODEC, FFMPEG_AUDIO_CODEC, FFMPEG_AUDIO_BITRATE, ScanType, VHS_FONT_PATH, VHS_FONT_SIZE
)
import subprocess
from tqdm import tqdm
import re


def build_vhs_datestamp_filter(creation_time: datetime) -> str:
    """
    Returns a pair of FFmpeg drawtext filters for a dynamic VHS-like timestamp.
    Bottom-right aligned, date on top, time below.
    Timestamp increments according to video time.
    """
    start_ts = int(creation_time.timestamp())

    # Date on top
    drawtext_date = (
        f"drawtext=fontfile='{VHS_FONT_PATH}':"
        f"text='%{{pts\\:localtime\\:{start_ts}\\:%d %m %Y}}':"
        f"x=w-tw-10:"          # right-aligned
        f"y=h-th-10-{VHS_FONT_SIZE}:"  # slightly above bottom to leave room for time
        f"fontsize={VHS_FONT_SIZE}:"
        f"fontcolor=white"
    )

    # Time below date
    drawtext_time = (
        f"drawtext=fontfile='{VHS_FONT_PATH}':"
        f"text='%{{pts\\:localtime\\:{start_ts}\\:%H\\\\\:%M\\\\\:%S}}':"
        f"x=w-tw-10:"          # same right-alignment
        f"y=h-th-10:"          # bottom of video
        f"fontsize={VHS_FONT_SIZE}:"
        f"fontcolor=white"
    )

    # Combine both filters
    drawtext_filter = f"{drawtext_date},{drawtext_time}"
    return drawtext_filter


def build_ffmpeg_command(
    input_path: Path,
    output_path: Path,
    clip: Clip,
    preset: dict,
    include_timestamp: bool
) -> list[str]:
    """
    Builds an FFmpeg command to encode a clip with optional deinterlacing and audio normalization.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(input_path),
    ]

    vf_filters = []

    # Deinterlace if needed
    if clip.scan_type == ScanType.INTERLACED:
        vf_filters.append("yadif")

    # Add VHS timestamp if requested
    if include_timestamp and clip.creation_time:
        vf_filters.append(build_vhs_datestamp_filter(clip.creation_time))

    # Only add -vf if we have at least one filter
    if vf_filters:
        cmd += ["-vf", ",".join(vf_filters)]

    # Encoding parameters
    cmd += [
        "-c:v", FFMPEG_VIDEO_CODEC,
        "-preset", preset['preset'],
        "-crf", str(preset['crf']),
        "-c:a", FFMPEG_AUDIO_CODEC,
        "-b:a", FFMPEG_AUDIO_BITRATE,
        # "-force_key_frames", "expr:gte(t,n_forced*0)",  # keyframe at start
        # TODO: this didn with lag in the begining of the video 
        # need futher investigation
        # "-movflags", "+faststart",
        "-progress", "pipe:1",
        str(output_path)
    ]

    return cmd


def run_ffmpeg_with_progress(cmd: list[str], total_frames: int, description: str = "Encoding") -> None:
    """
    Runs FFmpeg command and shows TQDM progress bar based on frames.
    """
    print(f"\n{description} {Path(cmd[-1]).name} ...")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1) as proc:
        with tqdm(total=total_frames, unit="frame", ncols=100, desc=description) as pbar:
            last_frame = 0
            for line in proc.stdout:
                line = line.strip()
                match = re.match(r"frame=(\d+)", line)
                if match:
                    current_frame = int(match.group(1))
                    delta = current_frame - last_frame
                    if delta > 0:
                        pbar.update(delta)
                        last_frame = current_frame
        proc.wait()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd)


def encode_clip(clip: Clip, output_dir: Path, preset: dict, include_timestamp: bool):
    """
    Converts a single Clip to H.264 + AAC MP4 with optional audio normalization.
    """
    input_path = Path(clip.video_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Video file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / Path(clip.video_file).name.replace(".MP4", "_converted.mp4")

    cmd = build_ffmpeg_command(input_path, output_path, clip, preset, include_timestamp)
    run_ffmpeg_with_progress(cmd, total_frames=clip.duration, description="Encoding")

    print(f"✅ Finished {output_path.name}\n")
    return output_path


def encode_clips(clips: list[Clip], output_dir: Path, video_preset: dict, include_timestamp: bool):
    """
    Encode multiple clips in batch with progress bars for each clip.
    """
    converted_files = []
    for clip in clips:
        try:
            output_file = encode_clip(clip, output_dir, video_preset, include_timestamp)
            converted_files.append(output_file)
        except Exception as e:
            print(f"❌ Failed to encode {clip.video_file}: {e}")
    return converted_files
