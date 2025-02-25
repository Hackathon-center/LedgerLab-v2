import cv2
import numpy as np

def cartoonify_image(image_path, output_path):
    try:
        # Read the image
        image = cv2.imread(image_path)
        
        # Apply cartoon effect
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(image, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        # Save the cartoonified image
        cv2.imwrite(output_path, cartoon)
        return output_path
    except Exception as e:
        print(f"Error cartoonifying image {image_path}: {e}")
        return None