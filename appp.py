from flask import Flask, request, jsonify
import requests
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_images'
CSV_FILE = 'image_outputs.csv'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize CSV file if not exists
if not os.path.isfile(CSV_FILE):
    df = pd.DataFrame(columns=['filename', 'output'])
    df.to_csv(CSV_FILE, index=False)

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Check if an image file is provided
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided."}), 400
        
        image = request.files['image']
        filename = secure_filename(image.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath)
        
        # Step 1: Send image to the first server (localhost:3000/upload)
        with open(filepath, 'rb') as img_file:
            upload_response = requests.post('http://localhost:3000/upload', files={'image': img_file})
        
        if upload_response.status_code != 200:
            return jsonify({"error": "Failed to upload image to the first server."}), 500
        
        # Step 2: Get the response from the first server
        upload_data = upload_response.json()

        # Step 3: Send response from the first server to the second server (localhost:3001/analyze)
        analyze_response = requests.post('http://localhost:3001/analyze', json=upload_data)

        if analyze_response.status_code != 200:
            return jsonify({"error": "Failed to analyze data on the second server."}), 500

        # Step 4: Get the response from the second server
        analyze_data = analyze_response.json()

        # Update CSV file with the image path and output
        df = pd.read_csv(CSV_FILE)
        new_row = pd.DataFrame([{'filename': filepath, 'output': str(analyze_data)}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        return jsonify(analyze_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3002)  # Run on port 3002
