import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any
import os
import requests
from PIL import Image
import shutil
from io import BytesIO

class MemeMonitor:
    def __init__(self, 
                min_upvotes: int = 10000,    
                min_comments: int = 100,     
                engagement_ratio: float = 0.1,
                time_window_hours: int = 168):  
        self.min_upvotes = min_upvotes
        self.min_comments = min_comments
        self.engagement_ratio = engagement_ratio
        self.time_window_hours = time_window_hours
        self.analyzed_memes = set()
        
    def is_popular(self, post: Dict[str, Any]) -> bool:
        """Determine if a meme is popular enough for analysis"""
        # Skip if already analyzed
        post_id = post['permalink']
        if post_id in self.analyzed_memes:
            return False
            
        # Basic criteria check
        if post['ups'] < self.min_upvotes or post['num_comments'] < self.min_comments:
            return False
            
        # Time window check
        post_time = pd.to_datetime(post['created_utc'])
        current_time = datetime.now(timezone.utc)
        hours_diff = (current_time - post_time).total_seconds() / 3600
        if hours_diff > self.time_window_hours:
            return False
            
        return True

    def prepare_meme_data(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare meme data for AWS analysis"""
        metadata = {
            'title': post['title'],
            'image_url': post['url'],
            'created_at': str(post['created_utc']),
            'upvotes': post['ups'],
            'comments': post['num_comments'],
            'reddit_permalink': post['permalink']
        }
        self.analyzed_memes.add(post['permalink'])
        return metadata

def download_and_save_image(url, save_path, max_width=500, max_height=500):
    """Download and resize image from URL"""
    if not url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        print(f"Skipping {url}: Not a supported image format")
        return False

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # Calculate aspect ratio
        aspect_ratio = img.width / img.height
        
        # Determine new size while maintaining aspect ratio
        if img.width > img.height:
            new_width = min(img.width, max_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(img.height, max_height)
            new_width = int(new_height * aspect_ratio)
        
        # Resize image
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save the resized image
        img_resized.save(save_path)
        
        return True
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False

def process_popular_memes(df: pd.DataFrame):
    """Find popular memes and save their images"""
    POPULAR_MEMES_DIR = 'popular_meme_images'
    
    # Empty the directory if it exists
    if os.path.exists(POPULAR_MEMES_DIR):
        shutil.rmtree(POPULAR_MEMES_DIR)
        
    # Create directory for popular meme images
    os.makedirs(POPULAR_MEMES_DIR)
    
    # Find popular memes
    monitor = MemeMonitor()
    popular_memes = []
    
    print("Processing popular memes...")
    for idx, row in df.iterrows():
        post_dict = row.to_dict()
        if monitor.is_popular(post_dict):
            meme_data = monitor.prepare_meme_data(post_dict)
            popular_memes.append(meme_data)
            
            # Download and save the image
            url = meme_data['image_url']
            # Create a filename using upvotes and comments for easy identification
            filename = f"upvotes_{meme_data['upvotes']}_comments_{meme_data['comments']}.jpg"
            save_path = os.path.join(POPULAR_MEMES_DIR, filename)
            
            if not os.path.exists(save_path):
                success = download_and_save_image(url, save_path)
                if success:
                    print(f"Successfully downloaded popular meme: {url}")
                    print(f"Upvotes: {meme_data['upvotes']}, Comments: {meme_data['comments']}")
                else:
                    print(f"Failed to download popular meme: {url}")
            else:
                print(f"Popular meme image already exists: {save_path}")
    
    print(f"Found and processed {len(popular_memes)} popular memes")
    return popular_memes