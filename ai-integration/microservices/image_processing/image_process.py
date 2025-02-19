import boto3
import os
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mint_criteria import process_popular_memes


# Initialize AWS clients
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

rekognition = session.client('rekognition')
textract = session.client('textract')
comprehend = session.client('comprehend')

# CSV file path
CSV_FILE = "../scraper/memes_posts.csv"
df = pd.read_csv(CSV_FILE)

# Process popular memes
popular_memes = process_popular_memes(df)

# Watchdog event handler
class CsvChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(CSV_FILE):
            print("CSV file has been modified. Reprocessing popular memes...")
            df = pd.read_csv(CSV_FILE)
            process_popular_memes(df)


if __name__ == "__main__":
    # Initial processing
    df = pd.read_csv(CSV_FILE)
    process_popular_memes(df)
    
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