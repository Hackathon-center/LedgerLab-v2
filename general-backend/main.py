from app import create_app
from flask import jsonify
import pandas as pd

app = create_app()

import os
import sys

# Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ai-integration', 'microservices', 'image_processing')))
CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ai-integration', 'microservices', 'scraper', 'memes_posts.csv'))

from image_process import process_memes_with_metadata

@app.route("/", methods=["GET", "POST"])
def home():
    return "Welcome to the API"

@app.route("/processAPI", methods=["GET", "POST"])
def process_API():
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({"success": False, "error": "CSV file not found"}), 404
        
        df = pd.read_csv(CSV_FILE)
        processed_memes = process_memes_with_metadata(df)
        
        return jsonify({"success": True, "processed_memes": processed_memes,}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
