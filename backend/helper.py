import cv2
import numpy as np
from numba import jit


@jit(nopython=True)
def gaussian_kernel(size, sigma):
    """Create a Gaussian kernel given size and sigma."""
    kernel = np.zeros((size, size))

    for i in range(0, size):
        for j in range(0, size):
            # x is the distance from the center in the x direction
            x = i - size // 2
            y = j - size // 2
            kernel[j, i] = np.exp(-(x ** 2 +
                                  y ** 2) / (2 * sigma ** 2))
    kernel /= kernel.sum()
    return kernel


@jit(nopython=True)
def gaussian_filter(image, kernel_size, sigma):
    kernel = gaussian_kernel(kernel_size, sigma)

    width = image.shape[1]
    height = image.shape[0]

    offset = kernel_size // 2
    output = np.zeros_like(image)
    # start from offset to avoid edges
    for y in range(height):
        for x in range(width):
            for c in range(0, 3):
                sum_val = 0.0
                # norm_factor = 0.0

                for ky in range(-offset, offset + 1):
                    for kx in range(-offset, offset + 1):
                        # get the image pixel value, need to offset by kernel size
                        j = y+ky
                        i = x+kx

                        # Skip out-of-bounds pixels
                        if j < 0 or i < 0 or j >= height or i >= width:
                            continue

                        sum_val += image[j,
                                         i, c] * kernel[ky + offset, kx + offset]

                        # norm factor is the sum of all kernel values
                        # norm_factor += kernel[ky, kx]
                # convolution complete, assign to output
                output[y, x, c] = int(sum_val)

    return output


@jit(nopython=True)
def bilateral_filter(image, kernel_size, sigma_space, sigma_range):
    # sigma range is the sigma for the intensity difference
    # sigma space is the sigma for the spatial difference

    offset = kernel_size // 2
    output = np.zeros_like(image)
    spatial_weights = gaussian_kernel(kernel_size, sigma_space)

    width = image.shape[1]
    height = image.shape[0]
    for y in range(height):
        for x in range(width):
            for c in range(0, 3):
                weighted_sum = 0.0
                norm_factor = 0.0
                center_intensity = image[y, x, c]

                for ky in range(-offset, offset + 1):
                    for kx in range(-offset, offset + 1):
                        j = y + ky
                        i = x + kx

                        # Skip out-of-bounds pixels
                        if j < 0 or i < 0 or j >= height or i >= width:
                            continue

                        neighbour_intensity = image[j, i, c]
                        intensity_diff = center_intensity - neighbour_intensity

                        # range weight is the gaussian of the intensity difference
                        range_weight = np.exp(-(intensity_diff **
                                              2) / (2 * sigma_range**2))

                        total_weight = spatial_weights[ky +
                                                       offset, kx + offset] * range_weight
                        weighted_sum += neighbour_intensity * total_weight
                        # norm factor is the sum of all kernel values
                        norm_factor += total_weight

                output[y, x, c] = weighted_sum / norm_factor

    return output


def run_show_results(input, run_annotations, run_anisotropic, run_focus):

    # Load the three images
    images = []
    if run_annotations:
        rgb_scribbles_img = cv2.imread(f'./outputs/{input}_with_scribbles.png')
        images.append(rgb_scribbles_img)
    if run_anisotropic:
        diffusion_img = cv2.imread(f'./outputs/{input}_anisotropic.png')
        images.append(diffusion_img)
    if run_focus:
        focus_img = cv2.imread(f'./focus_outputs/{input}_blended.png')
        images.append(focus_img)

    if any(image is None for image in images):
        print("Failed to load an image, or nothing was run.")
    else:
        # Get the dimensions of the images
        height = images[0].shape[0]
        width = images[0].shape[1]

        window_width = width * 3
        cv2.namedWindow("Results", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Results", window_width, height)

        # canvas to place the images side by side
        canvas = np.zeros((height, window_width, 3), dtype=np.uint8)

        # Paste each image onto the canvas
        for i in range(len(images)):
            image = images[i]
            canvas[:, i*width:(i+1)*width, :] = image

        cv2.imshow("Results", canvas)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
