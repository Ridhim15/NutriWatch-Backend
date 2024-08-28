from flask import Flask, request, jsonify, send_file
import requests

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Check if an image file is provided
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided."}), 400
        
        image = request.files['image']

        # Step 1: Send image to the first server (localhost:3000/upload)
        upload_response = requests.post('http://localhost:3000/upload', files={'image': image})
        
        if upload_response.status_code != 200:
            return jsonify({"error": "Failed to upload image to the first server."}), 500
        
        # Step 2: Get the response from the first server
        upload_data = upload_response.json()

        # Step 3: Send response from the first server to the second server (localhost:3001/analyze)
        analyze_response = requests.post('http://localhost:3001/analyze', json=upload_data)

        if analyze_response.status_code != 200:
            return jsonify({"error": "Failed to analyze data on the second server."}), 500

        # Step 4: Get the response from the second server and send it back to the user
        analyze_data = analyze_response.json()

        return jsonify(analyze_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002)  # Run on port 3002
