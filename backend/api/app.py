from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import cv2
import numpy as np
import os
import json
from werkzeug.utils import secure_filename
from scribble_process import create_masks_and_annotations, save_annotation_outputs
from focus import test_focus
from anisotropic import test_anisotropic

app = Flask(__name__)

# Configure CORS once
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"]
    }
})

# Directory setup
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'outputs')
FOCUS_OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'focus_outputs')

# Create directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, FOCUS_OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Routes
@app.route('/api/upload-image', methods=['POST', 'OPTIONS'])
def upload_image():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = secure_filename(os.path.splitext(file.filename)[0])
        file_path = os.path.join(UPLOAD_FOLDER, f'{filename}.png')
        file.save(file_path)
        
        return jsonify({
            'status': 'success',
            'filename': filename
        })
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/save-annotations', methods=['POST', 'OPTIONS'])
def save_annotations():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        image_name = data['imageName']
        annotations = data['annotations']
        ignore_annotations = data.get('ignoreAnnotations', annotations)
        
        images = create_masks_and_annotations(
            os.path.join(UPLOAD_FOLDER, f'{image_name}.png'),
            annotations,
            ignore_annotations
        )
        
        save_annotation_outputs(OUTPUT_FOLDER, image_name, images)
        
        return jsonify({
            'status': 'success',
            'images': {
                'annotations': {
                    'src': f'http://127.0.0.1:5000/outputs/{image_name}_annotations.png',
                    'title': 'Annotations'
                },
                'withScribbles': {
                    'src': f'http://127.0.0.1:5000/outputs/{image_name}_with_scribbles.png',
                    'title': 'With Scribbles'
                },
                'mask': {
                    'src': f'http://127.0.0.1:5000/outputs/{image_name}_mask.png',
                    'title': 'Mask'
                },
                'ignoreMask': {
                    'src': f'http://127.0.0.1:5000/outputs/{image_name}_ignore_mask.png',
                    'title': 'Ignore Mask'
                }
            }
        })
    except Exception as e:
        print(f"Error in save_annotations: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_progress(image_name, beta, iterations):
    try:
        for progress in test_anisotropic(image_name, beta, iterations, stream_progress=True):
            yield f"data: {json.dumps({'progress': progress})}\n\n"
        
        # Send the final result
        result = {
            'status': 'success',
            'images': {
                'anisotropic': {
                    'src': f'http://127.0.0.1:5000/outputs/{image_name}_anisotropic.png',
                    'title': 'Anisotropic Diffusion'
                }
            }
        }
        yield f"data: {json.dumps(result)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

@app.route('/api/process-anisotropic', methods=['POST', 'OPTIONS'])
def process_anisotropic():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        image_name = data['imageName']
        beta = data.get('beta', 0.1)
        iterations = data.get('iterations', 3000)
        
        def generate():
            try:
                # Get the generator
                anisotropic_gen = test_anisotropic(image_name, beta, iterations, stream_progress=True)
                
                # Stream progress updates
                for progress in anisotropic_gen:
                    yield f"data: {json.dumps({'progress': progress})}\n\n"
                
                # Send final result
                result = {
                    'status': 'success',
                    'images': {
                        'anisotropic': {
                            'src': f'http://127.0.0.1:5000/outputs/{image_name}_anisotropic.png',
                            'title': 'Anisotropic Diffusion'
                        }
                    }
                }
                yield f"data: {json.dumps(result)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        
        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        return response
        
    except Exception as e:
        print(f"Error in process_anisotropic: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/process-focus', methods=['POST'])
def process_focus():
    try:
        image_name = request.form['imageName']
        focus_point = json.loads(request.form['focusPoint'])
        
        test_focus(
            image_name, 
            float(request.form.get('depthRange', 0.1)),
            int(request.form.get('kernelSizeGaus', 5)),
            int(request.form.get('kernelSizeBf', 5)),
            float(request.form.get('sigmaColor', 200)),
            float(request.form.get('sigmaSpace', 200)),
            float(request.form.get('gausSigma', 60)),
            focus_point
        )
        
        return jsonify({
            'status': 'success',
            'images': {
                'depthNorm': {
                    'src': f'http://127.0.0.1:5000/focus_outputs/{image_name}_depth_norm.png',
                    'title': 'Depth Normalized'
                },
                'mask': {
                    'src': f'http://127.0.0.1:5000/focus_outputs/{image_name}_mask.png',
                    'title': 'Mask'
                },
                'maskBlur': {
                    'src': f'http://127.0.0.1:5000/focus_outputs/{image_name}_mask_blur.png',
                    'title': 'Mask Blur'
                },
                'bf': {
                    'src': f'http://127.0.0.1:5000/focus_outputs/{image_name}_bf.png',
                    'title': 'Bilateral Filter'
                },
                'blended': {
                    'src': f'http://127.0.0.1:5000/focus_outputs/{image_name}_blended.png',
                    'title': 'Final Result'
                }
            }
        })
    except Exception as e:
        print(f"Error in process_focus: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/focus_outputs/<path:filename>')
def serve_focus_output(filename):
    return send_from_directory(FOCUS_OUTPUT_FOLDER, filename)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # If your React app calls http://127.0.0.1:5000,
    # make sure you use 127.0.0.1 here, or else switch React to localhost.
    app.run(debug=True, host='127.0.0.1', port=5000)