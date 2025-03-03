import boto3
import os
import json
import pandas as pd
import time
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mint_criteria import process_popular_memes, clean_directory
from dotenv import load_dotenv
from ipfs_uploader import upload_to_ipfs

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
    
    # Create dirs if they don't exist
    if os.path.exists(METADATA_DIR):
        clean_directory(METADATA_DIR)
    else:
        os.makedirs(METADATA_DIR)
    
    
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
            
            # See if metadata is successfully processed & saved
            if save_metadata(metadata, metadata_path):
                print(f"Successfully processed meme and saved metadata: {base_filename}")
                
                # Upload to IPFS
                print(f"Uploading to IPFS: {base_filename}")
                ipfs_result = upload_to_ipfs(metadata)
                
                if ipfs_result["success"]:
                    print(f"Successfully uploaded to IPFS: {base_filename}")
                    
                    # Add IPFS data to metadata
                    metadata["ipfs_image_cid"] = ipfs_result["image_cid"]
                    metadata["ipfs_metadata_cid"] = ipfs_result["metadata_cid"]
                    metadata["ipfs_image_url"] = f"ipfs://{ipfs_result['image_cid']}"
                    
                    # Save updated metadata with IPFS info
                    save_metadata(metadata, metadata_path)
                else:
                    print(f"Failed to upload to IPFS: {base_filename}")
                
                
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