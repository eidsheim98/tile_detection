from time import sleep
import cv2
import numpy as np


def detect_cracks(img, contour):
    mask = np.zeros_like(img[:, :, 0])  # Assuming img is a 3-channel image, we take only one channel for the mask.
    cv2.drawContours(mask, [contour], 0, 255, -1)  # Use 255 for white in a single-channel mask.
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



def process(frame):
    cracks = False
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_cropped = img_gray[165:-1, 0:-1]

    bi_blur = cv2.bilateralFilter(img_cropped, 7, 75, 75)
    gaussian_blur_img = cv2.GaussianBlur(bi_blur, (9, 9), 0)
    dilate_img = cv2.dilate(gaussian_blur_img, None, iterations=3)
    thresh = cv2.adaptiveThreshold(dilate_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and draw bounding boxes
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)
        box[:, 1] = box[:, 1] + 165
        x, y, w, h = cv2.boundingRect(box)
        # Filter contours based on area and aspect ratio
        if 165 < h and 165 < w < 275:
            tile = frame[y:y + h, x:x + w]
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            if tile.shape[0] == 0 or tile.shape[1] == 0:
                continue
            cracks = detect_cracks(tile, contour)
            try:
                cv2.imshow('Tile', tile)
            except:
                pass

    cv2.imshow('Frame', frame)
    cv2.imshow('Thresh', thresh)

    return cracks

