"""
WLASL Dataset Downloader
Downloads the COMPLETE World Large-scale Sign Language dataset.
This script fetches metadata and downloads ALL videos for ALL signs.
Target: 21,000+ videos across 2,000+ signs.
Estimated size: 50-100GB
"""

import os
import json
import requests
import urllib.request
from pathlib import Path
from typing import List, Dict
import logging
from tqdm import tqdm
import time

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


def download_wlasl_metadata() -> Dict:
    """
    Download WLASL metadata from GitHub.
    Tries multiple URLs. Exits if all fail (no demo fallback for full dataset).
    
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
    
    # If all downloads fail, exit with error
    logger.error("\n❌ Could not download WLASL metadata from any source.")
    logger.error("Please check your internet connection and try again.")
    raise RuntimeError("Failed to download WLASL metadata")


def get_all_signs(metadata: Dict) -> List[Dict]:
    """
    Get all signs from the WLASL metadata.
    
    Args:
        metadata: WLASL metadata dictionary
        
    Returns:
        List of all sign dictionaries
    """
    all_signs = list(metadata)
    
    logger.info(f"Found {len(all_signs)} signs in WLASL dataset")
    
    # Count total videos
    total_videos = sum(len(sign.get("instances", [])) for sign in all_signs)
    logger.info(f"Total videos available: {total_videos}")
    
    return all_signs


def download_video(url: str, output_path: Path) -> bool:
    """
    Download a single video file with retry logic.
    
    Args:
        url: URL of the video to download
        output_path: Path where the video should be saved
        
    Returns:
        True if download successful, False otherwise
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if attempt == 0:
                logger.debug(f"Downloading {url} -> {output_path}")
            else:
                logger.debug(f"Retry {attempt}/{max_retries-1}: {url}")
            
            urllib.request.urlretrieve(url, output_path)
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # Convert to MB
            logger.debug(f"  ✓ Downloaded ({file_size:.2f} MB)")
            return True
            
        except Exception as e:
            logger.debug(f"  ✗ Attempt {attempt+1} failed: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial file
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            continue
    
    logger.warning(f"  ✗ Failed to download after {max_retries} attempts: {url}")
    return False


def download_all_videos(all_signs: List[Dict]) -> None:
    """
    Download ALL videos for ALL signs in WLASL dataset.
    Shows progress bar and handles failures gracefully.
    
    Args:
        all_signs: List of all sign dictionaries
    """
    # Count total videos to download
    total_videos = sum(len(sign.get("instances", [])) for sign in all_signs)
    logger.info(f"Starting download of {total_videos} videos across {len(all_signs)} signs")
    logger.info("Estimated download size: 50-100GB")
    logger.info("This may take several hours or days depending on your connection.\n")
    
    successful_downloads = 0
    failed_downloads = 0
    skipped_downloads = 0
    
    # Progress bar
    with tqdm(total=total_videos, desc="Downloading videos", unit="video") as pbar:
        for sign in all_signs:
            gloss = sign["gloss"]
            instances = sign.get("instances", [])
            
            if not instances:
                continue
            
            # Create subdirectory for each sign (sanitize name)
            sign_dir_name = gloss.replace(" ", "_").replace("/", "_").replace("\\", "_")
            sign_dir = DATA_RAW_PATH / sign_dir_name
            
            for instance in instances:
                video_id = instance["video_id"]
                video_url = f"{WLASL_VIDEO_BASE_URL}{video_id}.mp4"
                
                # Output path
                output_path = sign_dir / f"{video_id}.mp4"
                
                # Skip if already downloaded
                if output_path.exists():
                    skipped_downloads += 1
                    pbar.update(1)
                    continue
                
                # Try to download
                if download_video(video_url, output_path):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                
                pbar.update(1)
                
                # Update progress description occasionally
                if (successful_downloads + failed_downloads + skipped_downloads) % 100 == 0:
                    pbar.set_description(f"Downloaded {successful_downloads} | Failed {failed_downloads} | Skipped {skipped_downloads}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Download Complete!")
    logger.info(f"  Total videos processed: {total_videos}")
    logger.info(f"  Successfully downloaded: {successful_downloads}")
    logger.info(f"  Failed downloads: {failed_downloads}")
    logger.info(f"  Skipped (already exist): {skipped_downloads}")
    logger.info(f"  Output directory: {DATA_RAW_PATH}")
    logger.info(f"{'='*80}\n")


def save_metadata_locally(metadata: Dict) -> None:
    """
    Save WLASL metadata locally for reference.
    
    Args:
        metadata: Full WLASL metadata
    """
    metadata_path = DATA_RAW_PATH / "wlasl_metadata.json"
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Saved full WLASL metadata to {metadata_path}")
    
    # Also save summary stats
    total_signs = len(metadata)
    total_videos = sum(len(sign.get("instances", [])) for sign in metadata)
    
    stats = {
        "total_signs": total_signs,
        "total_videos": total_videos,
        "average_videos_per_sign": total_videos / total_signs if total_signs > 0 else 0,
        "download_date": "2026-04-26",
        "dataset_version": "WLASL_v0.3"
    }
    
    stats_path = DATA_RAW_PATH / "wlasl_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"Saved dataset statistics to {stats_path}")


def main():
    """
    Main function to orchestrate complete WLASL dataset download.
    """
    logger.info("="*80)
    logger.info("WLASL COMPLETE Dataset Download")
    logger.info("="*80)
    logger.info(f"Output directory: {DATA_RAW_PATH}")
    logger.info("Target: 21,000+ videos across 2,000+ signs")
    logger.info("Estimated size: 50-100GB\n")
    
    try:
        # Create output directory
        DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)
        
        # Download metadata
        metadata = download_wlasl_metadata()
        
        # Get all signs
        all_signs = get_all_signs(metadata)
        
        # Save metadata locally
        save_metadata_locally(metadata)
        
        # Download ALL videos
        download_all_videos(all_signs)
        
        logger.info("✅ WLASL complete dataset download complete!\n")
        logger.info("Next steps:")
        logger.info("1. Verify downloads:")
        logger.info("   python notebooks/exploration/video_info_reader.py data/raw/")
        logger.info("2. Extract MediaPipe landmarks:")
        logger.info("   python -m backend.services.landmark_extraction")
        logger.info("3. Process data for training:")
        logger.info("   python -m backend.services.data_processor")
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        logger.error("Please check the error above and try again.")
        raise


if __name__ == "__main__":
    main()
