"""
Script to populate sample install and trial_started data for testing
"""
from database import SessionLocal, Video
import random

db = SessionLocal()

try:
    # Get all videos
    videos = db.query(Video).all()
    print(f"Found {len(videos)} videos")

    # Add random install and trial data
    for video in videos:
        # Generate installs based on views (roughly 1-5% conversion)
        if video.views:
            install_rate = random.uniform(0.01, 0.05)
            video.installs = int(video.views * install_rate)

            # Trial started is typically 20-40% of installs
            trial_rate = random.uniform(0.2, 0.4)
            video.trial_started = int(video.installs * trial_rate)
        else:
            video.installs = random.randint(0, 100)
            video.trial_started = random.randint(0, int(video.installs * 0.3))

    db.commit()
    print(f"✓ Successfully populated install and trial data for {len(videos)} videos")

    # Show some stats
    total_installs = sum(v.installs for v in videos)
    total_trials = sum(v.trial_started for v in videos)
    print(f"\nTotal installs: {total_installs:,}")
    print(f"Total trials started: {total_trials:,}")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
