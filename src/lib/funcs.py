import os

import cv2
import numpy as np
import pytesseract

from pygame import mixer


# https://stackoverflow.com/a/47248339 - Rotate image around center without cropping
def rotate_image(mat, angle):

    height, width = mat.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def image_improve(img):
    # Replace red with white
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([0, 155, 135], dtype="uint16")
    upper_bound = np.array([20, 255, 255], dtype="uint16")
    mask1 = cv2.inRange(hsv, lower_bound, upper_bound)
    lower_bound = np.array([164, 155, 135], dtype="uint16")
    upper_bound = np.array([179, 255, 255], dtype="uint16")
    mask2 = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = mask2 + mask1
    img[mask == 255] = (255, 255, 255)

    # cv2.imshow('mask0',img)
    # cv2.waitKey()
    return img


def image_improve_rotation(img):
    # Inspired by line detection code here: https://stackoverflow.com/a/45560545
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 100  # minimum number of pixels making up a line
    max_line_gap = 5  # maximum gap in pixels between connectable line segments

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)
    # line_image = np.copy(img) * 0

    degrees = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            # only horizontalish lines
            if x1 < x2 and abs(y1 - y2) < 50:
                # cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)
                # Calculate rotation so that line would be horizontal
                deltaY = y2 - y1
                deltaX = x2 - x1
                angleInDegrees = np.arctan(deltaY / deltaX) * 180 / np.pi
                degrees.append(angleInDegrees)

    # Get mean/avg of rotation degrees
    rotation_degree = np.median(degrees)
    # Rotate image
    img_rotated = rotate_image(img, rotation_degree)

    # cv2.imshow('', line_image)
    # cv2.waitKey()
    return img_rotated, rotation_degree


def detect_text(img):
    # Adding custom options
    custom_config = r'--psm 6' # -l eng'
    d = pytesseract.image_to_string(img, config=custom_config)
    lines = d.split('\n')
    return lines


def play_audio(path):
    if os.name == 'nt':
        # Wait on previous message
        # while mixer.music.get_busy():
        #     time.sleep(0.01)
        # Unload old messages
        mixer.music.unload()
        # Windows audio play
        mixer.music.load(path)
        mixer.music.set_volume(0.75)
        mixer.music.play()


# img = cv2.imread(path_to_png)
# image_improve_rotation(img)