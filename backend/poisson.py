from numba import jit


@jit(nopython=True)
def compute_poisson(depth_map, pixel_pt):
    """
    Solve Poisson's equation using the average of the pixel's 4 neighbours
    """
    h, w = depth_map.shape
    y, x = pixel_pt

    # get neighbouring values, consider out of bounds as white
    top = depth_map[y-1, x] if y > 0 else 1
    bottom = depth_map[y+1, x] if y < h-1 else 1
    left = depth_map[y, x-1] if x > 0 else 1
    right = depth_map[y, x+1] if x < w-1 else 1

    # get the avg from 4 neighbors
    curr_depth_val = (1/4) * \
        ((top + bottom + left + right))

    # This value will be used in anisotropic for ignored regions
    return (curr_depth_val)
