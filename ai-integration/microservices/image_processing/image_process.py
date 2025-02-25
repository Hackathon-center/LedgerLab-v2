import boto3
import os
import json
import pandas as pd
import time
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mint_criteria import process_popular_memes, clean_directory
from text_removal import remove_text_from_meme
import requests
from PIL import Image
from io import BytesIO
import shutil
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize AWS clients
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

rekognition = session.client('rekognition')
textract = session.client('textract')

# Extract text function
def extract_text_from_image(image_path):
    """Extract text from image using AWS Textract"""
    try:
        with open(image_path, 'rb') as image:
            image_bytes = image.read()
            
        response = textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )
        
        extracted_text = []
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text.append(item['Text'])
                
        return ' '.join(extracted_text)
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}")
        return ""


# Analyze image content function
def analyze_image_content(image_path):
    """Analyze image content using AWS Rekognition"""
    try:
        with open(image_path, 'rb') as image:
            image_bytes = image.read()
            
        response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10,
            MinConfidence=70
        )
        
        return [label['Name'] for label in response['Labels']]
    except Exception as e:
        print(f"Error analyzing image content {image_path}: {e}")
        return []


# Create metadata function
def create_metadata(post_data, image_path, extracted_text, image_labels):
    """Create metadata dictionary for a meme"""
    return {
        'title': post_data.get('title', ''),
        'upvotes': post_data.get('upvotes', 0),
        'comments': post_data.get('comments', 0),
        'reddit_permalink': 'N/A',
        'image_url': post_data.get('image_url', ''),
        'local_image_path': image_path,
        'extracted_text': extracted_text,
        'image_labels': image_labels,
        'processed_at': datetime.now(timezone.utc).isoformat()
    }

def save_metadata(metadata, save_path):
    """Save metadata to JSON file"""
    try:
        with open(save_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving metadata to {save_path}: {e}")
        return False


# Process the memes
def process_memes_with_metadata(df):
    """Process popular memes and extract metadata"""
    METADATA_DIR = 'meme_metadata'
    TEXT_REMOVED_DIR = 'memes_no_text'
    
    # Create directory for metadata if it doesn't exist
    if os.path.exists(METADATA_DIR):
        clean_directory(METADATA_DIR)
    else:
        os.makedirs(METADATA_DIR)
        
    # Create directory for text-removed images
    if os.path.exists(TEXT_REMOVED_DIR):
        clean_directory(TEXT_REMOVED_DIR)
    else:
        os.makedirs(TEXT_REMOVED_DIR)
    
    # Get popular memes
    popular_memes = process_popular_memes(df)
    processed_memes = []
    
    print("Processing memes and extracting metadata...")
    for meme in popular_memes:
        image_path = meme['local_image_path']
        base_filename = os.path.basename(image_path).split('.')[0]
        metadata_path = os.path.join(METADATA_DIR, f"{base_filename}.json")
        
        # Process the image if it exists
        if os.path.exists(image_path):
            print(f"Processing meme: {meme['title']}")
            
            # Extract text and analyze image
            extracted_text = extract_text_from_image(image_path)
            image_labels = analyze_image_content(image_path)
            
            # Create and save metadata
            metadata = create_metadata(
                post_data=meme,
                image_path=image_path,
                extracted_text=extracted_text,
                image_labels=image_labels
            )
            
            # Continue if text is present
            if extracted_text:
                try:
                    # Call the remove_text_from_meme function
                    text_removed_path = remove_text_from_meme(image_path, metadata, output_dir=TEXT_REMOVED_DIR)
                    if text_removed_path:
                        # Update metadata with text-removed path
                        metadata['text_removed_path'] = text_removed_path
                        print(f"Successfully removed text from: {base_filename}")
                except Exception as e:
                    metadata['text_removed_path'] = None
            else:
                metadata['text_removed_path'] = None
            
            # See if metadata is successfully processed & saved
            if save_metadata(metadata, metadata_path):
                print(f"Successfully processed meme and saved metadata: {base_filename}")
                processed_memes.append(metadata)
            else:
                print(f"Failed to save metadata for: {base_filename}")
    
    return processed_memes


# Watchdog event handler
class CsvChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(CSV_FILE):
            print("CSV file has been modified. Reprocessing memes...")
            df = pd.read_csv(CSV_FILE)
            process_memes_with_metadata(df)


# CSV file path
CSV_FILE = "../scraper/memes_posts.csv"


if __name__ == "__main__":
    df = pd.read_csv(CSV_FILE)
        
    process_memes_with_metadata(df)
    
    # Watchdog observer
    event_handler = CsvChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(CSV_FILE), recursive=False)
    observer.start()
    
    try:
        print("Monitoring CSV file for changes. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()