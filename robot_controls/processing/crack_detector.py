import cv2
import numpy as np

from robot_controls.processing import image_processors
from robot_controls.helpers import helper


"""
Sondre main crack detector
"""
def detect_crack3(img):
    global count
    crack_found = False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 75, 75)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 2)

    lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, 80, minLineLength=50, maxLineGap=20)

    result = thresh.copy()
    if lines is None:
        return
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(result, (x1, y1), (x2, y2), (255, 0, 0), 1)
    img_contour, _ = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    w1 = None
    h1 = None
    for contour in img_contour:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)
        x, y, w, h = cv2.boundingRect(box)
        if 150 < w < 400 and approx.shape[0] == 4:
            cv2.drawContours(img, [approx], 0, (0, 0, 255), 2)
            if w1 is not None and h1 is not None:
                if w1 * h1 * 0.85 > w * h:
                    crack_found = True
            w1 = w
            h1 = h

    #cv2.imshow("img", img)
    cv2.imshow("result", result)
    cv2.imshow("thresh", thresh)

    return crack_found

def detect_crack4(img):
    img_crack = img[5:-5, 5:-5]
    img_crack = cv2.cvtColor(img_crack, cv2.COLOR_BGR2GRAY)
    img_crack = cv2.adaptiveThreshold(img_crack, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4)
    hist_crack = cv2.calcHist([img_crack], [0], None, [256], [0, 256])

    if hist_crack[0] > 50:
        cv2.imshow("CRACK FOUND", img)
        print(hist_crack[0])
        print("Crack found")
        return True, img
    return False, img

def histogram_detector(tile):
    crack_detected = False
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    #blur = cv2.bilateralFilter(gray, 9, 75, 75)
    sharpen = cv2.dilate(gray, None, iterations=1)
    thresh = cv2.adaptiveThreshold(sharpen, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    masked_thresh = cv2.bitwise_and(thresh, thresh, mask=mask)

    hist_crack = cv2.calcHist([masked_thresh], [0], None, [256], [0, 256])

    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) <= 0:
        return False, None

    if hist_crack[0] > 50:
        for contour in contours:
            if cv2.contourArea(contour) > 20:
                crack_detected = True
                cv2.drawContours(tile, [contour], 0, (0, 255, 0), 2)

    #cv2.imshow("tilethresh", thresh)
    #cv2.imshow("crack", tile)

    return crack_detected, tile


"""
Markus test crack detector
"""
def mask_detector(img):
    mask = np.zeros_like(img[:, :, 0])  # Assuming img is a 3-channel image, we take only one channel for the mask.
    #cv2.drawContours(mask, [contour], 0, 255, -1)  # Use 255 for white in a single-channel mask.
    edges_mask = cv2.Canny(mask, 50, 150)
    edges_mask = cv2.resize(edges_mask, (img.shape[1], img.shape[0]))
    masked_edges = cv2.bitwise_and(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), edges_mask)
    contours, hierarchy = cv2.findContours(masked_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Filter out contours that are too small to be cracks.
    long_crack_contours = [c for c in contours if cv2.arcLength(c, False) > 200]

    if long_crack_contours:
        print(f"Found {len(long_crack_contours)} long cracks")

        # Draw the long contours on the original image.
        for c in long_crack_contours:
            cv2.drawContours(img, [c], 0, (0, 0, 255), 2)

        cv2.imshow('Cracks', img)
        return True
    return False

def contour_detector_canny(tile):
    crack_detected = False
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    gray = cv2.dilate(gray, None, iterations=1)
    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 4)
    """for i in range(7,50):
        for j in range(7, 50):
            thresh = cv2.Canny(gray, i, j)
            cv2.imshow("test", thresh)
            print(i, j)
            cv2.waitKey(0)"""
    thresh = cv2.Canny(gray, 20, 50)

    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    masked_thresh = cv2.bitwise_and(thresh, thresh, mask=mask)

    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) < 0:
        return False, None

    for contour in contours:
        if cv2.contourArea(contour) > 20:
            crack_detected = True
            cv2.drawContours(tile, [contour], -1, (0, 255, 0), 2)
            cv2.imshow("crack", tile)

    cv2.imshow("thresh", thresh)
    cv2.imshow("masked", masked_thresh)

    return crack_detected, tile

def contour_detector_thresh(tile):
    crack_detected = False
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    sharpen = cv2.dilate(gray, None, iterations=1)
    thresh = cv2.adaptiveThreshold(sharpen, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (15, 15), (mask.shape[1]-15, mask.shape[0]-15), 255, -1)

    masked_thresh = cv2.bitwise_and(thresh, thresh, mask=mask)

    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) < 0:
        return False, None

    for contour in contours:
        if cv2.contourArea(contour) > 20:
            crack_detected = True
            cv2.drawContours(tile, [contour], 0, (0, 255, 0), 2)

    return crack_detected, tile
