# Julia's Final Project for CS4365

Welcome to my final project! This is a program that is based on the Computational Depth-of-Field Project Topic, and was built on a MacOS development environment with Python3.

## Deploy

To deploy this

1. Install all project dependencies, ideally do this in a python3 virtual environment

```bash
  pip install -r requirements.txt
```

2. Run the main.py file that lives in the root directory, this is where you can select which parts of the program to run and what parameters to use.

```bash
  python main.py
```

## Run

1. Select an image from /images to run and set the variable "input" in main.py to reflect this. For new images, simply add the image file to /images.
2. Select the parts to the program that you would like to run.

- run_annotations will start the UI for users to make annotations on
- run_anisotropic will take those annotations and produce a depth map with them
- run_focus will open a new UI window with the input image for the user to select an area to focus

```python

    # Select which parts to run
    run_annotations = True
    run_anisotropic = True
    run_focus = True
```

3. The variables that can be optimized are

```python

    # Variables to define for anisotropic
    beta = 0.1
    iterations = 3000

    # Variables to define and modify for focus
    gaus_sigma = 60
    depth_range = 0.1  # Depth range to use for the focus algorithm
    # Kernel size for the gaussian filter, used to smooth the depth map for a more realistic effect of blurring later
    kernel_size_gaus = 5
    # (Aperture) Kernel size for the bilateral filter, used for the bluring effect of the image itself
    kernel_size_bf = 5

    sigma_color = 60  # Filter sigma in the color space
    sigma_space = 60  # Filter sigma in the coordinate space
```

4. Depth map and annotation results will appear in /outputs and focussing outputs in /focus_outputs

##

Gitlab URL:
https://gitlab.ewi.tudelft.nl/cgv/cs4365/student-repositories/2023-2024/cs436523juliaju
