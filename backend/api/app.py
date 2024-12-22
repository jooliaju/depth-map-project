from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from scribble_process import create_masks_and_annotations, save_annotation_outputs

app = Flask(__name__)
# Configure CORS
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type"],
         "supports_credentials": True
     }})

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure folders with absolute paths
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'outputs')

# Create the directories if they don't exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@app.route('/api/upload-image', methods=['POST', 'OPTIONS'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Ensure filename is safe
        filename = secure_filename(os.path.splitext(file.filename)[0])
        
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, f'{filename}.png')
        file.save(file_path)
        
        print(f"Saved image to: {file_path}")
        
        response = jsonify({
            'status': 'success',
            'filename': filename
        })
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/save-annotations', methods=['POST'])
def save_annotations():
    try:
        data = request.json
        image_name = data['imageName']
        annotations = data['annotations']
        ignore_annotations = data.get('ignoreAnnotations', annotations)  # Use annotations as fallback
        
        # Get paths
        image_path = os.path.join(UPLOAD_FOLDER, f'{image_name}.png')
        
        # Process annotations
        images = create_masks_and_annotations(
            image_path,
            annotations,
            ignore_annotations
        )
        
        # Save all outputs
        save_annotation_outputs(OUTPUT_FOLDER, image_name, images)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Error in save_annotations: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)