import numpy as np
import cv2
from numba import jit
from helper import *

focus_point = None
focus_set = False
rgb_copy = None

# Loop over each pixel and blend the original and the filtered images based on the gradient mask


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

# defines the click event


def click_event(event, x, y, flags, param):
    global focus_point, focus_set, rgb_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        # Draw a circle around the point the user clicked
        cv2.circle(rgb_copy, (x, y), 10, (0, 255, 0), 2)

        # Update the display with the circle
        cv2.imshow("Select Focus", rgb_copy)

        # Set the flag indicating that the focus has been set
        focus_set = True

        focus_point = (x, y)
        print("Focus set to: ", focus_point)


def test_focus(input, depth_range, kernel_size_gaus, kernel_size_bf, sigma_color, sigma_space, gaus_sigma):
    """
    This function tests the focusing and apeture algorithm
    """
    global rgb_copy, focus_point

    print("Starting focus algorithm")

    # Read the image and depth map
    rgb_img = cv2.imread(f"./images/{input}.png")

    # Copy the rgb_img to another variable so that we can draw on it without modifying the original
    rgb_copy = rgb_img.copy()

    # Set the mouse callback function for the window
    cv2.imshow("Select Focus", rgb_copy)
    cv2.setMouseCallback("Select Focus", click_event)

    while True:
        key = cv2.waitKey(1) & 0xFF

        # If the 'r' key is pressed, reset the image and the focus_set flag
        if key == ord('r'):
            rgb_copy = rgb_img.copy()
            focus_set = False
            cv2.imshow("Selet Focus", rgb_copy)

        # If the 'esc' key is pressed, break from the loop
        # If the 'enter' key is pressed, break from the loop
        elif key == 27 or key == 13:
            break
    cv2.destroyAllWindows()

    print('Final focus point: ', focus_point)

    # create a mask with depth map
    depth_map = cv2.imread(
        f"./outputs/{input}_anisotropic.png")
    norm_depth_map = cv2.normalize(
        depth_map, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    # save normalized depth map
    cv2.imwrite(f"./focus_outputs/{input}_depth_norm.png",
                norm_depth_map*255)

    focus_x = focus_point[0]
    focus_y = focus_point[1]
    # setting the focal point and depth range
    focal_depth_value = norm_depth_map[focus_y, focus_x]
    # Depth values within +/- depth_range from the focal point will remain in focus

    # Create the new mask based on the depth range
    in_focus = (norm_depth_map >= (focal_depth_value - depth_range)) & \
        (norm_depth_map <= (focal_depth_value + depth_range))

    # save the initial mask
    cv2.imwrite(f"./focus_outputs/{input}_mask.png",
                in_focus*255)

    depth_mask = cv2.imread(
        f"./focus_outputs/{input}_mask.png", cv2.IMREAD_GRAYSCALE)
    # reshape depth mask to be 3 channels instead of 1 to work with gaussian filter
    depth_mask = np.repeat(depth_mask[:, :, np.newaxis], 3, axis=2)

    gradient_mask = gaussian_filter(depth_mask, kernel_size_gaus, gaus_sigma)
    # save gradient mask
    cv2.imwrite(f"./focus_outputs/{input}_mask_blur.png", gradient_mask)

    # read_gradient_mask = cv2.imread("./focus_outputs/{input}_mask.png")

    # print("gradient mask shape: ", gradient_mask.shape)
    bf_img = bilateral_filter(rgb_img, kernel_size_bf,
                              sigma_color, sigma_space)
    cv2.imwrite(f"./focus_outputs/{input}_bf.png", bf_img)

    # turn gradient mask to single channel
    gradient_mask = cv2.cvtColor(gradient_mask, cv2.COLOR_BGR2GRAY)/255

    # save gradient mask
    cv2.imwrite(f"./focus_outputs/{input}_mask_blur.png", gradient_mask)

    blended_img = blend_images(
        rgb_img, bf_img, gradient_mask)

    # save blended image
    cv2.imwrite(f"./focus_outputs/{input}_blended.png", blended_img)
