import numpy as np
import cv2
from numba import jit
from helper import *

@jit(nopython=True)
def blend_images(rgb_image, bf_img, gradient_mask):
    """
    Blend the original and the filtered images based on the gradient mask
    """

    # empty image is instantialized to be filled with the blended image values
    depth_based_blurred_image = np.zeros_like(rgb_image)

    for y in range(rgb_image.shape[0]):
        for x in range(rgb_image.shape[1]):
            for c in range(rgb_image.shape[2]):
                # Blend the values based on the mask intensity
                intensity = gradient_mask[y, x]
                depth_based_blurred_image[y, x, c] = ((1-intensity) * bf_img[y, x, c] +
                                                      (intensity) * rgb_image[y, x, c])

    return depth_based_blurred_image

def test_focus(rgb_img, depth_map, focus_point, depth_range=0.1, kernel_size_gaus=5, 
               kernel_size_bf=5, sigma_color=200, sigma_space=200, gaus_sigma=60):
    """
    Process the focus effect using provided image data
    """
    try:
        # Get image dimensions
        height, width = rgb_img.shape[:2]
        
        # print("RGB Image shape: ", rgb_img.shape)
        # print("Depth map shape: ", depth_map.shape)
        
        # Convert normalized coordinates (0-1) to image coordinates
        focus_x = int(round(focus_point['x'] * width))
        focus_y = int(round(focus_point['y'] * height))
        
        # print('Using focus point:', (focus_x, focus_y))

        # Create a mask with depth map
        norm_depth_map = cv2.normalize(
            depth_map, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        # print("Normalized depth map shape: ", norm_depth_map.shape)

        # Setting the focal point and depth range
        focal_depth_value = norm_depth_map[focus_y, focus_x]
        
        # Create the new mask based on the depth range
        in_focus = (norm_depth_map >= (focal_depth_value - depth_range)) & \
            (norm_depth_map <= (focal_depth_value + depth_range))
        # print("In focus mask shape: ", in_focus.shape)

        # Create depth mask (single channel)
        depth_mask = (in_focus * 255).astype(np.uint8)
        # print("Depth mask shape: ", depth_mask.shape)

        # Apply gaussian filter to create gradient mask
        gradient_mask = gaussian_filter(depth_mask, kernel_size_gaus, gaus_sigma)
        # print("After gaussian filter shape: ", gradient_mask.shape)
        
        gradient_mask = cv2.cvtColor(gradient_mask, cv2.COLOR_BGR2GRAY)/255
        # print("After grayscale conversion shape: ", gradient_mask.shape)

        # Apply bilateral filter
        bf_img = bilateral_filter(rgb_img, kernel_size_bf,
                                sigma_color, sigma_space)
        # print("Bilateral filter output shape: ", bf_img.shape)

        # Create final blended image
        blended_img = blend_images(rgb_img, bf_img, gradient_mask)
        # print("Final blended image shape: ", blended_img.shape)

        # Return all processed images
        result = {
            'depth_norm': (norm_depth_map * 255).astype(np.uint8), # normalizing the depth map
            'mask': depth_mask,
            'bf': bf_img,
            'blended': blended_img
        }
            
        return result

    except Exception as e:
        print(f"Error in test_focus: {str(e)}")
        raise e
