import cv2
import numpy as np
import boto3
import os
from io import BytesIO
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize AWS clients
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

textract = session.client('textract')

def create_text_mask(image_path, img_shape):
    """
    - Uses AWS Textract to detect text areas in the image
    - Creates a binary mask where text is present
    - Dilates the mask to ensure complete text coverage
    """
    
    with open(image_path, 'rb') as image:
        image_bytes = image.read()
    
    # Get text detection with bounding boxes
    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    
    # Create a blank mask
    height, width = img_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # Fill in mask where text is detected
    for item in response['Blocks']:
        if item['BlockType'] in ['LINE', 'WORD']:
            # Get bounding box coordinates
            bbox = item['Geometry']['BoundingBox']
            
            # Convert relative coordinates to absolute pixel coordinates
            left = int(bbox['Left'] * width)
            top = int(bbox['Top'] * height)
            box_width = int(bbox['Width'] * width)
            box_height = int(bbox['Height'] * height)
            
            # Add padding around text 
            padding = 3
            left = max(0, left - padding)
            top = max(0, top - padding)
            box_width = min(width - left, box_width + 2 * padding)
            box_height = min(height - top, box_height + 2 * padding)
            
            # Fill the mask 
            mask[top:top+box_height, left:left+box_width] = 255
    
    # Dilate the mask 
    kernel = np.ones((5, 5), np.uint8)  
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    return mask


def extract_text_with_preprocessing(image_path):
    # Extract text from image using AWS Textract 
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "", None
        
        # Create a list that stores multiple versions of the image
        preprocessed_images = []
        
        # V1: Original
        preprocessed_images.append(("original", img))
        
        # V2: Increase contrast
        contrast_img = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
        preprocessed_images.append(("contrast", contrast_img))
        
        # V3: Inverted image 
        inverted_img = cv2.bitwise_not(img)
        preprocessed_images.append(("inverted", inverted_img))
        
        # V4: Grayscale 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        preprocessed_images.append(("threshold", thresh))
        
        # Create a combined mask for all detected text
        height, width = img.shape[:2]
        combined_mask = np.zeros((height, width), dtype=np.uint8)
        all_text = []
        
        # Process each version with Textract
        for version_name, version_img in preprocessed_images:
            success, encoded_img = cv2.imencode('.jpg', version_img)
            if not success:
                continue
                
            image_bytes = encoded_img.tobytes()
            
            response = textract.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            # Extract text and update mask
            version_text = []
            for item in response['Blocks']:
                if item['BlockType'] in ['LINE', 'WORD']:
                    if 'Text' in item:
                        version_text.append(item['Text'])
                    
                    # Add to mask
                    bbox = item['Geometry']['BoundingBox']
                    left = int(bbox['Left'] * width)
                    top = int(bbox['Top'] * height)
                    box_width = int(bbox['Width'] * width)
                    box_height = int(bbox['Height'] * height)
                    
                    # Add padding
                    padding = 5
                    left = max(0, left - padding)
                    top = max(0, top - padding)
                    box_width = min(width - left, box_width + 2 * padding)
                    box_height = min(height - top, box_height + 2 * padding)
                    
                    combined_mask[top:top+box_height, left:left+box_width] = 255
            
            if version_text:
                all_text.append(f"[{version_name}] " + " ".join(version_text))
                print(f"Found text in {version_name} version: {' '.join(version_text)}")
        
        # Dilate the mask
        kernel = np.ones((7, 7), np.uint8)
        combined_mask = cv2.dilate(combined_mask, kernel, iterations=2)
        
        return " | ".join(all_text), combined_mask
    
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}")
        return "", None
    

def remove_text_from_meme(image_path, metadata, output_dir="memes_no_text"):
    # Remove detected text from an image and save it to a specified directory
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Process the image 
    extracted_text, text_mask = extract_text_with_preprocessing(image_path)
    
    # If no text was found or no mask was generated
    if not extracted_text or text_mask is None or np.sum(text_mask) == 0:
        # Fall back to the original method
        mask = create_text_mask(image_path, img.shape)
        if mask is None or np.sum(mask) == 0:
            return None
        text_mask = mask
    else:
        # Update metadata with enhanced text extraction
        metadata['extracted_text'] = extracted_text
    
    # Apply inpainting to remove text
    inpainted_img = cv2.inpaint(img, text_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Save the text-removed version to new dir
    base_name = os.path.basename(image_path) 
    text_removed_path = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}_text_removed.jpg")
    cv2.imwrite(text_removed_path, inpainted_img)
    
    print(f"Text removed image saved to: {text_removed_path}")
    
    return text_removed_path