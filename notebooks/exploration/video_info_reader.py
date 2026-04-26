"""
Video Information Reader
Extracts and displays metadata from video files.
Shows duration, frame count, resolution, FPS, and codec info.
"""

import cv2
import os
from pathlib import Path
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoInfoReader:
    """
    Utility class to read and extract information from video files.
    """
    
    def __init__(self, video_path: str):
        """
        Initialize VideoInfoReader with a video file path.
        
        Args:
            video_path: Path to the video file
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If file is not a valid video
        """
        self.video_path = Path(video_path)
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
    
    def get_video_info(self) -> Dict:
        """
        Extract comprehensive information from the video.
        
        Returns:
            Dictionary containing video metadata
        """
        # Get frame properties
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate duration
        duration_seconds = frame_count / fps if fps > 0 else 0
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        
        # Get file size
        file_size_mb = self.video_path.stat().st_size / (1024 * 1024)
        
        # Get codec info (fourcc)
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        codec = self._fourcc_to_string(fourcc)
        
        info = {
            "filename": self.video_path.name,
            "file_path": str(self.video_path),
            "file_size_mb": round(file_size_mb, 2),
            "resolution": {
                "width": width,
                "height": height,
                "display": f"{width}x{height}"
            },
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "duration": {
                "seconds": round(duration_seconds, 2),
                "formatted": f"{minutes}m {seconds}s"
            },
            "codec": codec
        }
        
        return info
    
    @staticmethod
    def _fourcc_to_string(fourcc: int) -> str:
        """
        Convert fourcc integer to human-readable codec string.
        
        Args:
            fourcc: Four-character code as integer
            
        Returns:
            Codec name or "Unknown"
        """
        try:
            bytes_code = bytes([(fourcc >> 8 * i) & 0xFF for i in range(4)])
            return ''.join(chr(b) for b in bytes_code).rstrip('\x00')
        except:
            return "Unknown"
    
    def get_sample_frame(self, frame_number: int = 0) -> Tuple:
        """
        Extract and return a sample frame from the video.
        
        Args:
            frame_number: Index of frame to extract (0-based)
            
        Returns:
            Tuple of (success: bool, frame: numpy.ndarray or None)
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        return (ret, frame)
    
    def release(self) -> None:
        """Release the video capture object."""
        self.cap.release()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


def print_video_info(video_path: str) -> None:
    """
    Print formatted video information.
    
    Args:
        video_path: Path to the video file
    """
    try:
        with VideoInfoReader(video_path) as reader:
            info = reader.get_video_info()
            
            print("\n" + "="*70)
            print(f"VIDEO INFORMATION: {info['filename']}")
            print("="*70)
            print(f"File Path:        {info['file_path']}")
            print(f"File Size:        {info['file_size_mb']} MB")
            print(f"\nResolution:       {info['resolution']['display']}")
            print(f"Frame Count:      {info['frame_count']} frames")
            print(f"FPS:              {info['fps']} frames/second")
            print(f"Duration:         {info['duration']['formatted']} ({info['duration']['seconds']}s)")
            print(f"Codec:            {info['codec']}")
            print("="*70 + "\n")
            
            # Additional analysis
            bitrate_mbps = (info['file_size_mb'] * 8) / info['duration']['seconds'] if info['duration']['seconds'] > 0 else 0
            print(f"Calculated Bitrate: {bitrate_mbps:.2f} Mbps")
            print()
    
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
    except ValueError as e:
        logger.error(f"❌ {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


def scan_directory_videos(directory: str) -> None:
    """
    Scan a directory for video files and print their information.
    
    Args:
        directory: Path to directory containing videos
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
    video_dir = Path(directory)
    
    if not video_dir.exists():
        logger.error(f"❌ Directory not found: {directory}")
        return
    
    video_files = [f for f in video_dir.rglob('*') if f.suffix.lower() in video_extensions]
    
    if not video_files:
        logger.warning(f"⚠️  No video files found in {directory}")
        return
    
    logger.info(f"Found {len(video_files)} video file(s) in {directory}")
    print()
    
    for video_file in sorted(video_files):
        print_video_info(str(video_file))


def main():
    """
    Main function - example usage.
    Can be called directly or used as a module.
    """
    import sys
    
    if len(sys.argv) < 2:
        # Example: scan data/raw directory
        data_raw_path = Path(__file__).parent.parent.parent / "data" / "raw"
        
        if data_raw_path.exists():
            logger.info("No video path provided. Scanning data/raw directory...")
            scan_directory_videos(str(data_raw_path))
        else:
            logger.warning(f"data/raw directory not found: {data_raw_path}")
            logger.info("Usage: python video_info_reader.py <video_path_or_directory>")
    else:
        # User provided path
        path = sys.argv[1]
        path_obj = Path(path)
        
        if path_obj.is_file():
            print_video_info(path)
        elif path_obj.is_dir():
            scan_directory_videos(path)
        else:
            logger.error(f"❌ Path not found: {path}")


if __name__ == "__main__":
    main()
