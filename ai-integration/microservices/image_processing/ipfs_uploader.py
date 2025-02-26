import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath("../../../general-backend"))

from app import db, create_app
from app.models import Meme

load_dotenv()

# Pinata API configuration
PINATA_API_KEY = os.getenv('PINATA_API_KEY_ID')
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_KEY_ID')
PINATA_ENDPOINT = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_JSON_ENDPOINT = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
IPFS_CID_FILE = "ipfs_cids.json"


def pin_file_to_ipfs(file_path):
    # Upload a file to IPFS via Pinata and return the CID
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")
    
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(
            PINATA_ENDPOINT,
            files=files,
            headers=headers
        )
    
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        raise Exception(f"Failed to pin to IPFS: {response.text}")


def pin_json_to_ipfs(json_data):
    # Upload JSON data to IPFS via Pinata and return the CID
    headers = {
        "Content-Type": "application/json",
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    
    response = requests.post(
        PINATA_JSON_ENDPOINT,
        json=json_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        raise Exception(f"Failed to pin JSON to IPFS: {response.text}")


def save_to_database(metadata, image_cid, metadata_cid):
    """Save meme information to the database"""
    try:
        # Create a new Meme instance
        new_meme = Meme(
            picture=metadata.get("local_image_path", ""), 
            title=metadata.get("title", ""),
            up_vote=metadata.get("upvotes", 0),
            comments=metadata.get("comments", 0),
            created_at=datetime.now(),
            metadata_cid=metadata_cid,
            image_cid=image_cid
        )
        
        # Add to session and commit to database
        db.session.add(new_meme)
        db.session.commit()
        
        print(f"Successfully saved meme to database with ID: {new_meme.id}")
        return True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        db.session.rollback()
        return False


def save_ipfs_data(local_image_path, image_cid, metadata_cid, metadata):
    # Load existing CIDs
    if os.path.exists(IPFS_CID_FILE):
        with open(IPFS_CID_FILE, 'r') as f:
            cid_data = json.load(f)
    else:
        cid_data = {}
    
    # Store CIDs with additional metadata
    cid_data[local_image_path] = {
        "image_cid": image_cid,
        "metadata_cid": metadata_cid,
        "title": metadata.get("title", ""),
        "upvotes": metadata.get("upvotes", 0),
        "comments": metadata.get("comments", 0),
        "processed_at": datetime.now().isoformat()
    }
    
    # Save updated data to JSON file
    with open(IPFS_CID_FILE, 'w') as f:
        json.dump(cid_data, f, indent=2)
    
    return cid_data


def upload_to_ipfs(metadata):
    # Upload both image and metadata to IPFS
    try:
        local_image_path = metadata.get("local_image_path")
        
        # Upload image to IPFS
        image_cid = pin_file_to_ipfs(local_image_path)
        
        # Create enhanced metadata with IPFS link
        enhanced_metadata = metadata.copy()
        enhanced_metadata["ipfs_image_cid"] = image_cid
        enhanced_metadata["ipfs_image_url"] = f"ipfs://{image_cid}"
        enhanced_metadata["ipfs_pinned_at"] = datetime.now().isoformat()
        
        # Upload metadata to IPFS
        metadata_cid = pin_json_to_ipfs(enhanced_metadata)
        
        # Save CIDs with additional data to JSON file (keeping for backward compatibility)
        save_ipfs_data(local_image_path, image_cid, metadata_cid, metadata)
        
        # Initialize Flask app 
        app = create_app()
        with app.app_context():
            # Save to database
            db_save_result = save_to_database(metadata, image_cid, metadata_cid)
            if db_save_result:
                print(f"Successfully saved meme metadata to database")
            else:
                print(f"Failed to save meme metadata to database")
        
        return {
            "success": True,
            "image_cid": image_cid,
            "metadata_cid": metadata_cid
        }
    except Exception as e:
        print(f"Error uploading to IPFS: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }