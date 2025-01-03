import numpy as np
from numba import jit
import cv2
from poisson import compute_poisson
import os


@jit(nopython=True)  # Set "nopython" mode for best performance, equivalent to @njit
def euclidean_distance(p1, p2):
    """
    Compute the euclidean distance between two points
    """
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)**0.5


@jit(nopython=True)  # Set "nopython" mode for best performance, equivalent to @njit
def get_omega(img, beta, curr_pixel, neighbour_pixel):
    """
    Estimate the omega value for a given pixel and its neighbour
    """
    y, x = curr_pixel
    y_n, x_n = neighbour_pixel

    omega = np.exp(-beta * euclidean_distance(img[y, x], img[y_n, x_n]))

    return omega


@jit(nopython=True)  # Set "nopython" mode for best performance, equivalent to @njit
def test_diffusion(rgb_img, scribbles, mask, ignore_mask, beta, iterations):
    """
    Solve Poisson's equation using the Jacobi method.
    """
    # Ensure inputs are not None and have correct shape
    if scribbles is None:
        scribbles = np.zeros_like(rgb_img[:,:,0])
    if mask is None:
        mask = np.zeros_like(rgb_img[:,:,0])
    if ignore_mask is None:
        ignore_mask = np.zeros_like(rgb_img[:,:,0])
        
    h, w = scribbles.shape
    depth_map = np.ones((h, w))*255

    for iteration in range(iterations):
        if iteration % 100 == 0:
            print(f'Iteration {iteration}')
            # Calculate progress percentage
            progress = int((iteration / iterations) * 100)
            yield (progress, None)  # Yield progress with no result

        new_depth_map = depth_map.copy()

        for y in range(0, h):
            for x in range(0, w):
                curr_pixel = (y, x)
                # if annotated, then the value of depth is the same as the scribbles
                if mask[y, x] == 255:
                    new_depth_map[y, x] = scribbles[y, x]
                    continue

                if ignore_mask[y, x] == 255:
                    # ignored regions will use poisson equation
                    new_depth_map[y, x] = compute_poisson(
                        new_depth_map, curr_pixel)
                    continue

                # get neighbouring values, consider out of bounds as white
                if y > 0:
                    top = depth_map[y-1, x]
                    w_top = get_omega(rgb_img, beta, curr_pixel, (y-1, x))
                else:
                    top = 255
                    w_top = 255

                if y < h-1:
                    bottom = depth_map[y+1, x]
                    w_bottom = get_omega(
                        rgb_img, beta, curr_pixel, (y+1, x))
                else:
                    bottom = 255
                    w_bottom = 255

                if x > 0:
                    left = depth_map[y, x-1]
                    w_left = get_omega(rgb_img, beta, curr_pixel, (y, x-1))
                else:
                    left = 255
                    w_left = 255

                if x < w-1:
                    right = depth_map[y, x+1]
                    w_right = get_omega(rgb_img, beta, curr_pixel, (y, x+1))
                else:
                    right = 255
                    w_right = 255

                # update depth value with omega weights and depth values
                new_depth_map[y, x] = (w_top*top + w_bottom*bottom + w_left *
                                       left + w_right*right)/(w_top+w_bottom+w_left+w_right)
        depth_map = new_depth_map

    # Return both 100% progress and the final result
    yield (100, depth_map)


def test_anisotropic(rgb_img, scribbles, mask, ignore_mask, beta=0.1, iterations=3000, stream_progress=False):
    """
    Process the anisotropic diffusion directly with image data
    """
    try:
        # Process the image
        for progress, result in test_diffusion(rgb_img, scribbles, mask, ignore_mask, beta, iterations):
            if stream_progress:
                yield progress, result
            
    except Exception as e:
        print(f"Error in test_anisotropic: {str(e)}")
        raise e