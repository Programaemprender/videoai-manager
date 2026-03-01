#!/usr/bin/env python3
"""
VideoAI Manager - Main entry point
Analyzes videos in a folder and organizes them automatically
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from src.core.video_analyzer import DynamicVideoAnalyzer
from src.core.facial_recognition import RecurrentFaceDetector

def main():
    parser = argparse.ArgumentParser(
        description='VideoAI Manager - AI-powered video organization'
    )
    parser.add_argument(
        '--folder',
        type=str,
        default=os.getenv('VIDEO_INPUT_FOLDER', './videos'),
        help='Folder containing videos to analyze'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview analysis without making changes'
    )
    parser.add_argument(
        '--disable-facial',
        action='store_true',
        help='Disable facial recognition'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output folder for organized videos'
    )
    
    args = parser.parse_args()
    
    # Validate input folder
    if not os.path.exists(args.folder):
        print(f"❌ Error: Folder not found: {args.folder}")
        sys.exit(1)
    
    # Find video files
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v'}
    video_files = [
        f for f in Path(args.folder).rglob('*')
        if f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        print(f"❌ No video files found in {args.folder}")
        sys.exit(1)
    
    print(f"📹 Found {len(video_files)} videos")
    print(f"{'🔍 DRY RUN MODE - No changes will be made' if args.dry_run else '✅ Processing videos...'}")
    print("-" * 60)
    
    # Initialize analyzer
    analyzer = DynamicVideoAnalyzer()
    
    # Initialize facial recognition (if enabled)
    facial_detector = None
    if not args.disable_facial:
        min_videos = int(os.getenv('MIN_VIDEOS_FOR_NOTIFICATION', 2))
        min_appearances = int(os.getenv('MIN_APPEARANCES_FOR_NOTIFICATION', 3))
        facial_detector = RecurrentFaceDetector(
            min_videos=min_videos,
            min_appearances=min_appearances
        )
    
    # Process each video
    results = []
    for idx, video_path in enumerate(video_files, 1):
        print(f"\n[{idx}/{len(video_files)}] Processing: {video_path.name}")
        
        try:
            # Analyze video
            result = analyzer.process_video_optimized(str(video_path))
            
            if result:
                results.append(result)
                print(f"  ✅ Categorized as: {result['new_name']}")
                
                # Facial recognition
                if facial_detector:
                    faces = facial_detector.process_video(str(video_path))
                    if faces:
                        print(f"  👤 Detected {len(faces)} unique face(s)")
            else:
                print(f"  ⚠️ Analysis failed")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Check for pending face identifications
    if facial_detector:
        pending = facial_detector.get_faces_pending_identification()
        if pending:
            print(f"\n⚠️ {len(pending)} recurring face(s) need identification")
            print("   Run: python identify_faces.py --pending")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Processed {len(results)}/{len(video_files)} videos successfully")
    
    if args.dry_run:
        print("\n💡 This was a dry run. To process for real, remove --dry-run flag")
    
    print("\n🎉 Done! Check output folder for organized videos.")

if __name__ == "__main__":
    main()
