import cv2
import numpy as np

def create_masks_and_annotations(image_path, annotations_data, ignore_annotations_data):
    """
    Process annotations and create all necessary output images
    """
    # Read the original image
    original_img = cv2.imread(image_path)
    if original_img is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Get image dimensions
    h, w = original_img.shape[:2]
    
    # Convert base64 annotations to cv2 images
    annotations_img = base64_to_cv2(annotations_data)
    # print("base64 annotations")
    # print(annotations_data)
    ignore_annotations_img = base64_to_cv2(ignore_annotations_data)
    
    # Create white canvas
    white_canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    # Create masks - start with black (0)
    mask = np.zeros((h, w), dtype=np.uint8)
    ignore_mask = np.zeros((h, w), dtype=np.uint8)
    
    # Copy scribbles to both outputs
    with_scribbles = original_img.copy()
    
    # Process annotations - only copy non-white pixels (the scribbles)
    for y in range(h):
        for x in range(w):
            pixel = annotations_img[y, x]
            if not np.array_equal(pixel, [255, 255, 255]):  # If it's a scribble
                white_canvas[y, x] = pixel  # Copy scribble to white canvas
                with_scribbles[y, x] = pixel  # Copy scribble to image
                
                # Check if it's a green (ignore) scribble
                if pixel[1] > 200 and pixel[1] > pixel[0] + 50 and pixel[1] > pixel[2] + 50:
                    ignore_mask[y, x] = 255  # Mark in ignore mask
                else:
                    # If not green, it's a regular annotation
                    mask[y, x] = 255  # Mark in mask (white)
    
    return {
        'with_scribbles': with_scribbles,  # Original image with scribbles
        'annotations': white_canvas,        # White canvas with ONLY scribbles
        'mask': mask,                      # White where there are grayscale annotations
        'ignore_mask': ignore_mask         # White where there are green scribbles
    }

def base64_to_cv2(base64_string):
    """Convert base64 string to cv2 image"""
    import base64
    img_data = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def save_annotation_outputs(output_dir, image_name, images):
    """Save all annotation outputs"""
    cv2.imwrite(f'{output_dir}/{image_name}_with_scribbles.png', images['with_scribbles'])
    cv2.imwrite(f'{output_dir}/{image_name}_annotations.png', images['annotations'])
    cv2.imwrite(f'{output_dir}/{image_name}_mask.png', images['mask'])
    cv2.imwrite(f'{output_dir}/{image_name}_ignore_mask.png', images['ignore_mask']) 