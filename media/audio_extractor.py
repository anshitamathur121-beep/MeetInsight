# media/audio_extractor.py

import os
import subprocess
import logging

import imageio_ffmpeg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_audio_file(input_path: str, work_dir: str) -> str:
    """
    Normalize uploaded media to mono MP3 for transcription.
    Handles MP4 (extract), MP3 (passthrough), WAV/M4A (convert).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    _, ext = os.path.splitext(input_path.lower())
    if ext == ".mp3":
        return input_path
    if ext == ".mp4":
        return extract_audio(input_path, os.path.join(work_dir, "extracted_audio.mp3"))

    output_path = os.path.join(work_dir, "converted_audio.mp3")
    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "22050",
        "-ac", "1",
        "-b:a", "64k",
        output_path,
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        raise RuntimeError(f"FFmpeg failed to convert audio: {e.stderr}") from e


def extract_audio(video_path: str, output_audio_path: str = None) -> str:
    """
    Extracts audio from a video file and saves it as a lightweight mono MP3.

    Args:
        video_path (str): Path to the input video file.
        output_audio_path (str, optional): Target path for the output audio.

    Returns:
        str: Path to the extracted audio file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video file not found: {video_path}")

    if not output_audio_path:
        base, _ = os.path.splitext(video_path)
        output_audio_path = f"{base}_extracted.mp3"

    logger.info(f"Extracting audio from {video_path} to {output_audio_path}")

    # Run ffmpeg command to extract audio to MP3 mono 22050Hz 64kbps (optimal for speech + upload size)
    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y",
        "-i", video_path,
        "-vn",                      # Disable video
        "-acodec", "libmp3lame",    # Use MP3 codec
        "-ar", "22050",             # 22.05 kHz sample rate
        "-ac", "1",                 # Mono audio
        "-b:a", "64k",              # 64kbps bitrate
        output_audio_path
    ]

    try:
        # Run subprocess silently
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        logger.info("Audio extraction completed successfully.")
        return output_audio_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg extraction failed: {e.stderr}")
        raise RuntimeError(f"FFmpeg failed to extract audio: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during audio extraction: {e}")
        raise e
