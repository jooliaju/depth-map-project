import sys
from PyQt5.QtWidgets import QApplication
import cv2
from helper import run_show_results
from scribble import MainWindow
from anisotropic import test_anisotropic
from focus import test_focus

###
# Run this file to start the program
###


def annotation_UI(input):
    """
    This function starts the annotation UI
    """

    image_file = input + '.png'
    output_path = './outputs/'
    image_path = './images/'

    app = QApplication(sys.argv)
    window = MainWindow(image_path, output_path, image_file)
    window.show()

    app.exec_()


if __name__ == '__main__':

    # Ensure the input name is the name before the .png
    # input = 'pony'
    # input = 'another_horse'
    # input = 'pearl'
    # input = 'arizona'
    input = 'church'
    # input = 'horse'

    # Select which parts to run
    run_annotations = True
    run_anisotropic = True
    run_focus = True
    show_results = True

    # Variables to define for anisotropic
    beta = 0.1
    iterations = 3000

    # Variables to define and modify for focus
    gaus_sigma = 60
    depth_range = 0.1  # Depth range to use for the focus algorithm
    # Kernel size for the gaussian filter, used to smooth the depth map for a more realistic effect of blurring later
    kernel_size_gaus = 5
    # (Apeture) Kernel size for the bilateral filter, used for the bluring effect of the image itself
    kernel_size_bf = 5

    sigma_color = 200  # Filter sigma in the color space
    sigma_space = 200  # Filter sigma in the coordinate space

    if run_annotations:

        annotation_UI(input)

    if run_anisotropic:
        test_anisotropic(input, beta, iterations)

    if run_focus:
        test_focus(input, depth_range, kernel_size_gaus, kernel_size_bf,
                   sigma_color, sigma_space, gaus_sigma)

    if show_results:
        run_show_results(input, run_annotations,
                         run_anisotropic, run_focus)
