"""
Performs the crack detection on the specified tile
"""

import cv2
import numpy as np

def histogram_detector(tile):
    """
    The histogram detector. Uses a combination of threshold and histogram to detect the cracks
    :param tile: The image of the rotated tile
    :return: True if a crack was detected, and the tile image with a drawn contour on it. If not, it returns False and no tile image
    """
    crack_detected = False

    # Convert to grayscale
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    # Make the edges pop more by dilating
    dilated = cv2.dilate(gray, None, iterations=1)

    # Create a threshold based on the sharpened image
    thresh = cv2.adaptiveThreshold(dilated, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    # Create a mask
    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    # Create a new masked threshold
    masked_thresh = cv2.bitwise_and(thresh, thresh, mask=mask)
    cv2.imshow("masked_thresh", masked_thresh)

    # Calculate the histogram of the masked threshold
    hist_crack = cv2.calcHist([masked_thresh], [0], None, [256], [0, 256])

    # Find contours in the masked thresholded image
    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If there are no contours, there is no crack to show
    if len(contours) <= 0:
        return False, None

    # If there are more than 50 white pixels in the threshold image, some anomaly (most likely a crack) is detected
    if hist_crack[255] > 50:
        for contour in contours:
            if cv2.contourArea(contour) > 20:
                crack_detected = True
                cv2.drawContours(tile, [contour], 0, (0, 255, 0), 2)

    return crack_detected, tile

def contour_detector_canny(tile):
    """
    The canny crack detector
    :param tile: The image of the rotated tile
    :return: True if a crack was detected, and the tile image with a drawn contour on it. If not, it returns False and no tile image
    """
    crack_detected = False

    # Convert the image to grayscale
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    # Make the edges pop more by dilating
    gray = cv2.dilate(gray, None, iterations=1)

    # Perform canny edge detection
    canny = cv2.Canny(gray, 20, 50)

    # Create a mask
    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    # Create a new threshold with this mask
    masked_thresh = cv2.bitwise_and(canny, canny, mask=mask)

    # Find contours based on the masked threshold
    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If there are no contours, no crack was found
    if len(contours) <= 0:
        return False, None

    # Draw the contours onto the tile image
    for contour in contours:
        if cv2.contourArea(contour) > 20:
            crack_detected = True
            cv2.drawContours(tile, [contour], -1, (0, 255, 0), 2)

    return crack_detected, tile

def contour_detector_thresh(tile):
    """
    The canny crack detector
    :param tile: The image of the rotated tile
    :return: True if a crack was detected, and the tile image with a drawn contour on it. If not, it returns False and no tile image
    """

    crack_detected = False

    # Convert to grayscale
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    # Dilate the image to make the edges pop more
    dilated = cv2.dilate(gray, None, iterations=1)

    # Create a new threshold based on the dilated image
    thresh = cv2.adaptiveThreshold(dilated, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    # Create a mask
    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    # Create a new threshold with this mask
    masked_thresh = cv2.bitwise_and(thresh, thresh, mask=mask)
    cv2.imshow("Tile Threshold", masked_thresh)

    # Find the contours from the masked threshold
    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If there are no contours, no crack was found
    if len(contours) < 0:
        return False, None

    # Draw the contours onto the tile image
    for contour in contours:
        if cv2.contourArea(contour) > 20:
            crack_detected = True
            cv2.drawContours(tile, [contour], 0, (0, 255, 0), 2)

    return crack_detected, tile
