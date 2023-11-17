import os
from time import sleep
import cv2
import numpy as np
import matplotlib.pyplot as plt
from image_processing import straighten


def detect_cracks(image):
    # Convert the image to grayscale
    if image.shape[0] == 0 or image.shape[1] == 0:
        return image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Canny edge detection to find edges which might represent cracks
    edges = cv2.Canny(gray, 50, 150)

    # Dilate the edges to make the cracks more prominent
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=15)

    # Find contours of the cracks
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small contours that are unlikely to be cracks
    min_crack_length = 30
    cracks = [contour for contour in contours if cv2.arcLength(contour, True) > min_crack_length]

    return cracks


def detect_crack(img):
    if img.shape[0] == 0 or img.shape[1] == 0:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 75, 75)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray = cv2.dilate(gray, None, iterations=15)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours


def detect_crack1(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl1 = clahe.apply(img)
    # cl1 = cv2.Canny(cl1, 50, 150)

    hist = cv2.equalizeHist(img)
    hist = cv2.calcHist([cl1], [0], None, [256], [0, 256])

    # plt.subplot(1, 2, 1), plt.imshow(cl1, cmap='gray')
    # plt.title('Enhanced Image'), plt.xticks([]), plt.yticks([])
    # plt.subplot(1, 2, 2), plt.plot(hist)
    # plt.title('Histogram'), plt.xlabel('Pixel Intensity'), plt.ylabel('Frequency')
    # plt.xlim([0,256])
    if hist[3] / (img.shape[0] * img.shape[1]) > 0.3:
        print(hist[3])

    # Display the edges (potential cracks)
    # plt.subplot(2,1,1),plt.imshow(edges, cmap='gray')
    # plt.title('Detected Edges'), plt.xticks([]), plt.yticks([])
    # plt.tight_layout()
    # plt.show()

    # Apply Canny edge detection

    # plt.show()


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

    cv2.imshow("img", img)
    cv2.imshow("result", result)
    cv2.imshow("thresh", thresh)

    return crack_found



def process(frame):
    crack_found = False
    # frame = cv2.resize(frame, (480, 400))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = gray[165:-1, 0:-1]

    #gray = cv2.bilateralFilter(gray, 7, 75, 75)
    #gray = cv2.GaussianBlur(gray, (9, 9), 0)
    gray = cv2.dilate(gray, None, iterations=1)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 2)
    #thresh = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and draw bounding boxes
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)
        box[:, 1] = box[:, 1] + 165
        x, y, w, h = cv2.boundingRect(box)
        rotated = straighten.rotate_image(thresh, box)
        cv2.imshow('Rotated', rotated)
        # Filter contours based on area and aspect ratio
        if 95 < h and 135 < w < 200:
            tile = frame[y:y + h, x:x + w]
            # tile = thresh[y-165:y+h-165, x:x+w]
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            if tile.shape[0] == 0 or tile.shape[1] == 0:
                continue
            crack_found = detect_crack3(tile)
            try:
                cv2.imshow('Tile', tile)
            except:
                pass


    cv2.imshow('Frame', frame)
    cv2.imshow('Thresh', thresh)

    return crack_found


cv2.destroyAllWindows()


if __name__ == '__main__':
    os.system("python3 /home/nikolai/PycharmProjects/roboDoggo/robot_controls/server/test_server.py")