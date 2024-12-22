import requests
import base64
import os

BASE_URL = 'http://localhost:5000/api'

def test_upload_image():
    # Test image upload
    image_path = './images/church.png'  # Use one of your existing test images
    with open(image_path, 'rb') as img:
        files = {'image': ('church.png', img, 'image/png')}
        response = requests.post(f'{BASE_URL}/upload-image', files=files)
    print('Upload response:', response.json())
    return response.json()

def test_save_annotations():
    # Create a simple test annotation (white square on black background)
    test_annotation = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC"
    
    data = {
        'imageName': 'church',
        'annotations': test_annotation,
        'ignoreAnnotations': test_annotation
    }
    response = requests.post(f'{BASE_URL}/save-annotations', json=data)
    print('Save annotations response:', response.json())
    return response.json()

def test_process_depth():
    data = {
        'imageName': 'church',
        'beta': 0.1,
        'iterations': 100  # Reduced for testing
    }
    response = requests.post(f'{BASE_URL}/process-depth', json=data)
    print('Process depth response:', response.json())
    return response.json()

def test_process_focus():
    data = {
        'imageName': 'church',
        'focusPoint': {'x': 100, 'y': 100},
        'depthRange': 0.1,
        'kernelSizeGaus': 5,
        'kernelSizeBf': 5,
        'sigmaColor': 200,
        'sigmaSpace': 200,
        'gausSigma': 60
    }
    response = requests.post(f'{BASE_URL}/process-focus', json=data)
    print('Process focus response:', response.json())
    return response.json()

def run_all_tests():
    print("Testing API endpoints...")
    print("\n1. Testing image upload:")
    test_upload_image()
    
    print("\n2. Testing save annotations:")
    test_save_annotations()
    
    print("\n3. Testing depth processing:")
    test_process_depth()
    
    print("\n4. Testing focus processing:")
    test_process_focus()

if __name__ == '__main__':
    run_all_tests() 