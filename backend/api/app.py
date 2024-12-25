from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import cv2
import numpy as np
import os
import json
from werkzeug.utils import secure_filename
from scribble_process import create_masks_and_annotations
from focus import test_focus
from anisotropic import test_anisotropic
from config import Config
import base64

app = Flask(__name__)
config = Config()

# Use only the CORS middleware with simpler configuration
CORS(app, 
     origins=config.FRONTEND_URL,
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Remove the after_request CORS handler and keep only the security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Directory setup
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'outputs')
FOCUS_OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'focus_outputs')

# Create directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, FOCUS_OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Helper function to get image URLs
def get_image_url(filename, folder='outputs'):
    return f"{config.BACKEND_URL}/{folder}/{filename}"

# Add these helper functions before the routes
def decode_base64_image(base64_string):
    """Convert base64 string to cv2 image"""
    try:
        # Remove the data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 string
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image data")
            
        return img
    except Exception as e:
        print(f"Error decoding base64 image: {str(e)}")
        return None

def encode_image_to_base64(image):
    """Convert cv2 image to base64 string"""
    try:
        # Encode image to png
        _, buffer = cv2.imencode('.png', image)
        # Convert to base64 string
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image to base64: {str(e)}")
        return None

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
        image_data = data['imageData']  # Base64 image from frontend
        annotations = data['annotations']
        ignore_annotations = data.get('ignoreAnnotations', annotations)
        
        # Convert base64 to cv2 image
        image = decode_base64_image(image_data)
        if image is None:
            raise ValueError("Could not decode image data")
        
        # Process annotations using existing logic
        images = create_masks_and_annotations(
            image,
            annotations,
            ignore_annotations
        )
        
        # Convert results back to base64 and return to frontend
        return jsonify({
            'status': 'success',
            'images': {
                'annotations': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(images["annotations"])}',
                    'title': 'Input Annotations'
                },
                'withScribbles': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(images["with_scribbles"])}',
                    'title': 'With Scribbles'
                },
                'mask': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(images["mask"])}',
                    'title': 'Mask'
                },
                'ignoreMask': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(images["ignore_mask"])}',
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
        image_data = data['imageData']
        annotations_data = data['annotations']
        mask_data = data['mask']
        ignore_mask_data = data['ignoreMask']
        beta = data.get('beta', 0.1)
        iterations = data.get('iterations', 3000)
        
        # Convert base64 to cv2 images
        image = decode_base64_image(image_data)
        annotations = cv2.cvtColor(decode_base64_image(annotations_data), cv2.COLOR_BGR2GRAY)
        mask = cv2.cvtColor(decode_base64_image(mask_data), cv2.COLOR_BGR2GRAY)
        ignore_mask = cv2.cvtColor(decode_base64_image(ignore_mask_data), cv2.COLOR_BGR2GRAY)
        
        def generate():
            try:
                last_progress = 0
                result = None
                
                # Get the generator
                anisotropic_gen = test_anisotropic(
                    image, 
                    annotations,
                    mask,
                    ignore_mask,
                    beta, 
                    iterations, 
                    stream_progress=True
                )
                
                # Stream progress updates
                for progress, current_result in anisotropic_gen:
                    try:
                        # Only send progress update if it's changed significantly
                        if progress - last_progress >= 1 or progress >= 100:
                            last_progress = progress
                            progress_data = json.dumps({'progress': progress})
                            yield f"data: {progress_data}\n\n"
                        
                        # Store the result
                        if current_result is not None:
                            result = current_result
                    except Exception as e:
                        print(f"Error in progress update: {str(e)}")
                        continue
                
                # Always send final result
                if result is not None:
                    try:
                        result_base64 = encode_image_to_base64(result)
                        final_result = {
                            'status': 'success',
                            'images': {
                                'anisotropic': {
                                    'src': f'data:image/png;base64,{result_base64}',
                                    'title': 'Anisotropic Diffusion'
                                }
                            }
                        }
                        yield f"data: {json.dumps(final_result)}\n\n"
                    except Exception as e:
                        print(f"Error encoding final result: {str(e)}")
                        raise
                else:
                    raise ValueError("No result generated")
                        
            except Exception as e:
                print(f"Error in generate: {str(e)}")
                error_data = json.dumps({'status': 'error', 'message': str(e)})
                yield f"data: {error_data}\n\n"
        
        response = Response(generate(), mimetype='text/event-stream')
        response.headers.update({
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
            'Content-Type': 'text/event-stream'
        })
        return response
        
    except Exception as e:
        print(f"Error in process_anisotropic: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/process-focus', methods=['POST', 'OPTIONS'])
def process_focus():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        image_data = data['imageData']  # Original image
        anisotropic_data = data['anisotropicResult']  # Anisotropic result image
        focus_point = data['focusPoint']
        
        # Convert base64 to cv2 images
        rgb_img = decode_base64_image(image_data)
        depth_map = decode_base64_image(anisotropic_data)
        
        if rgb_img is None or depth_map is None:
            raise ValueError("Could not decode image data")

        # Process focus
        result_images = test_focus(
            rgb_img=rgb_img,
            depth_map=depth_map,
            focus_point=focus_point,
            depth_range=float(data.get('depthRange', 0.1)),
            kernel_size_gaus=int(data.get('kernelSizeGaus', 5)),
            kernel_size_bf=int(data.get('kernelSizeBf', 5)),
            sigma_color=float(data.get('sigmaColor', 200)),
            sigma_space=float(data.get('sigmaSpace', 200)),
            gaus_sigma=float(data.get('gausSigma', 60))
        )
        
        # Convert results back to base64 and return to frontend
        return jsonify({
            'status': 'success',
            'images': {
                'depthNorm': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(result_images["depth_norm"])}',
                    'title': 'Depth Normalized'
                },
                'mask': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(result_images["mask"])}',
                    'title': 'Focus Mask'
                },
                'bf': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(result_images["bf"])}',
                    'title': 'Bilateral Filter'
                },
                'blended': {
                    'src': f'data:image/png;base64,{encode_image_to_base64(result_images["blended"])}',
                    'title': 'Final Result'
                }
            }
        })
    except Exception as e:
        print(f"Error in process_focus: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'v1'})

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    if config.ENV == 'production':
        # good for concurrency
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='127.0.0.1', port=5000)
