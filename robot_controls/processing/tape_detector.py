"""
Code to detect tape boundary to keep the dog inside of
"""

import numpy as np
import cv2

from robot_controls.helpers import helper

#videowriter = helper.create_videowriter("tape", (103, 208))

def tape_found(image):
    # Convert the image to the HSV color space
    image = image[190:-1, 0:-1]
    left = int(image.shape[1]/9*4)
    right = int(image.shape[1]/9*6)

    image = image[0:-1, left:right]
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the yellow color in HSV
    lower_yellow = np.array([20, 100, 100])  # Lower bound for yellow in HSV
    upper_yellow = np.array([30, 255, 255])  # Upper bound for yellow in HSV

    # Create a mask for the yellow color
    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    cv2.imshow("Tape", image)
    #videowriter.write(image)

    # Check if yellow color is detected
    if np.any(yellow_mask > 0):
        return True, image

    return False, image

if __name__ == '__main__':
    image = cv2.imread('../../training_images/tape/tape.jpg')
    print(tape_found(image))

