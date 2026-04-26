"""
WLASL Dataset Downloader
Downloads a sample of the World Large-scale Sign Language dataset.
This script fetches metadata and downloads video samples for the top 10 signs.
Can also create synthetic demo data for local testing.
"""

import os
import json
import requests
import urllib.request
from pathlib import Path
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WLASL dataset URLs (try multiple mirrors)
WLASL_URLS = [
    "https://raw.githubusercontent.com/dxli94/WLASL/main/WLASL_v0.3.json",
    "https://raw.githubusercontent.com/dxli94/WLASL/master/WLASL_v0.3.json",
    "https://wlasl.github.io/WLASL_v0.3.json",
]
WLASL_VIDEO_BASE_URL = "https://github.com/dxli94/WLASL/raw/main/videos/"

# Output directory
DATA_RAW_PATH = Path(__file__).parent.parent.parent / "data" / "raw"

# Demo data for testing (when WLASL unavailable)
DEMO_SIGNS = [
    "HELLO", "THANK_YOU", "GOOD_MORNING", "GOOD_NIGHT", "I_LOVE_YOU",
    "HOW_ARE_YOU", "NICE_TO_MEET_YOU", "MY_NAME_IS", "HELP", "PLEASE"
]


def download_wlasl_metadata() -> Dict:
    """
    Download WLASL metadata from GitHub.
    Tries multiple URLs. Falls back to demo data if all fail.
    
    Returns:
        Dictionary containing the WLASL dataset metadata
    """
    # Try multiple URLs
    for url in WLASL_URLS:
        try:
            logger.info(f"Attempting to download metadata from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            metadata = response.json()
            logger.info(f"✓ Successfully downloaded metadata for {len(metadata)} signs")
            return metadata
        except Exception as e:
            logger.warning(f"  ✗ Failed: {type(e).__name__}")
            continue
    
    # If all downloads fail, create demo metadata
    logger.warning("\n⚠️  Could not download WLASL metadata from GitHub.")
    logger.info("Creating demo dataset for local testing...\n")
    return create_demo_metadata()


def create_demo_metadata() -> List[Dict]:
    """
    Create synthetic demo WLASL metadata for testing.
    Simulates the WLASL dataset structure.
    
    Returns:
        List of sign dictionaries with demo instances
    """
    demo_data = []
    
    for sign_id, gloss in enumerate(DEMO_SIGNS, 1):
        # Create 2 fake video instances per sign for demo
        instances = [
            {"video_id": f"{sign_id:05d}_{idx:02d}"} 
            for idx in range(2)
        ]
        
        demo_data.append({
            "sign_id": sign_id,
            "gloss": gloss,
            "instances": instances
        })
    
    logger.info(f"Created demo metadata for {len(demo_data)} signs")
    return demo_data


def get_top_signs(metadata: Dict, num_signs: int = 10) -> List[Dict]:
    """
    Extract top N signs by number of videos available.
    
    Args:
        metadata: WLASL metadata dictionary
        num_signs: Number of top signs to select
        
    Returns:
        List of sign dictionaries sorted by video count (descending)
    """
    # Sort by number of videos per sign
    sorted_signs = sorted(metadata, key=lambda x: len(x.get("instances", [])), reverse=True)
    top_signs = sorted_signs[:num_signs]
    
    logger.info(f"Selected top {num_signs} signs:")
    for i, sign in enumerate(top_signs, 1):
        video_count = len(sign.get("instances", []))
        logger.info(f"  {i}. {sign['gloss']} - {video_count} videos")
    
    return top_signs


def download_video(url: str, output_path: Path) -> bool:
    """
    Download a single video file.
    
    Args:
        url: URL of the video to download
        output_path: Path where the video should be saved
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading {url} -> {output_path}")
        urllib.request.urlretrieve(url, output_path)
        
        file_size = output_path.stat().st_size / (1024 * 1024)  # Convert to MB
        logger.info(f"  ✓ Downloaded ({file_size:.2f} MB)")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Failed to download: {e}")
        if output_path.exists():
            output_path.unlink()  # Remove partial file
        return False


def download_sample_videos(top_signs: List[Dict], videos_per_sign: int = 2) -> None:
    """
    Download sample videos for each of the top signs.
    Falls back to creating demo video placeholders if download fails.
    
    Args:
        top_signs: List of sign dictionaries
        videos_per_sign: Number of videos to download per sign
    """
    total_videos = 0
    successful_downloads = 0
    failed_downloads = 0
    
    for sign in top_signs:
        gloss = sign["gloss"]
        instances = sign.get("instances", [])[:videos_per_sign]
        
        logger.info(f"\nProcessing videos for '{gloss}' ({len(instances)} videos)...")
        
        for idx, instance in enumerate(instances, 1):
            video_id = instance["video_id"]
            video_url = f"{WLASL_VIDEO_BASE_URL}{video_id}.mp4"
            
            # Create subdirectory for each sign
            sign_dir = DATA_RAW_PATH / gloss.replace(" ", "_")
            output_path = sign_dir / f"{video_id}.mp4"
            
            # Skip if already downloaded
            if output_path.exists():
                logger.info(f"  Skipping {video_id}.mp4 (already exists)")
                continue
            
            total_videos += 1
            
            # Try to download actual video
            if download_video(video_url, output_path):
                successful_downloads += 1
            else:
                failed_downloads += 1
                # Create demo placeholder file
                create_demo_video_placeholder(output_path)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Download Summary:")
    logger.info(f"  Total videos processed: {total_videos}")
    logger.info(f"  Successfully downloaded: {successful_downloads}")
    logger.info(f"  Demo placeholders created: {failed_downloads}")
    logger.info(f"  Output directory: {DATA_RAW_PATH}")
    logger.info(f"{'='*60}\n")


def create_demo_video_placeholder(output_path: Path) -> None:
    """
    Create a placeholder file for demo videos when real downloads fail.
    
    Args:
        output_path: Path where the placeholder should be created
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a small placeholder file with metadata
        demo_content = f"""
DEMO VIDEO PLACEHOLDER
======================
This is a placeholder file created for local testing.

Sign: {output_path.parent.name}
Video ID: {output_path.stem}
Created: 2026-04-24

In production, this would contain actual WLASL sign language video.
Download instructions are in data/README.md

To use real WLASL videos:
1. Clone: https://github.com/dxli94/WLASL
2. Copy videos to data/raw/{output_path.parent.name}/
3. Re-run the landmark extraction pipeline
""".encode()
        
        with open(output_path, 'wb') as f:
            f.write(demo_content)
        
        logger.info(f"  ✓ Created demo placeholder ({len(demo_content) / 1024:.1f} KB)")
        
    except Exception as e:
        logger.error(f"  ✗ Failed to create placeholder: {e}")


def save_metadata_locally(metadata: Dict, top_signs: List[Dict]) -> None:
    """
    Save WLASL metadata locally for reference.
    
    Args:
        metadata: Full WLASL metadata
        top_signs: Top signs that were downloaded
    """
    metadata_path = DATA_RAW_PATH / "wlasl_metadata.json"
    top_signs_path = DATA_RAW_PATH / "wlasl_top_10_signs.json"
    
    # Save top 10 signs info
    top_signs_info = []
    for sign in top_signs:
        top_signs_info.append({
            "gloss": sign["gloss"],
            "sign_id": sign["sign_id"],
            "instance_count": len(sign.get("instances", [])),
            "instances_sample": sign.get("instances", [])[:2]
        })
    
    with open(top_signs_path, 'w') as f:
        json.dump(top_signs_info, f, indent=2)
    
    logger.info(f"Saved top signs metadata to {top_signs_path}")


def main():
    """
    Main function to orchestrate WLASL dataset download.
    """
    logger.info("="*70)
    logger.info("WLASL Sample Dataset Setup")
    logger.info("="*70)
    logger.info(f"Output directory: {DATA_RAW_PATH}\n")
    
    try:
        # Create output directory
        DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)
        
        # Download metadata (with fallback to demo)
        metadata = download_wlasl_metadata()
        
        # Get top 10 signs
        top_signs = get_top_signs(metadata, num_signs=10)
        
        # Save metadata locally
        save_metadata_locally(metadata, top_signs)
        
        # Download sample videos (with demo fallback)
        download_sample_videos(top_signs, videos_per_sign=2)
        
        logger.info("✅ WLASL sample dataset setup complete!\n")
        logger.info("Next steps:")
        logger.info("1. Inspect downloaded files:")
        logger.info("   python notebooks/exploration/video_info_reader.py data/raw/\n")
        logger.info("2. Extract MediaPipe landmarks (coming next)")
        logger.info("3. Process data for training")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        logger.error("Please check the error above and try again.")
        raise


if __name__ == "__main__":
    main()
