import cv2
import numpy as np

"""
Internal method linked to Markus contour detector
"""
def process_image(image):
    # Load the image from file
    if image is None:
        print("Error: Couldn't open the image file.")
        return None, None, None, None

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Crop the image to remove the dog's legs
    cropped_gray_image = gray_image[165:, :]

    kernel = np.ones((5, 5), np.uint8)
    dilate = cv2.dilate(cropped_gray_image, kernel, iterations=2)

    # Apply Canny edge detection on the cropped grayscale image
    canny_edges = cv2.Canny(dilate, 50, 100)

    # Find contours from the Canny edges
    contours, _ = cv2.findContours(canny_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Return the resized original image, cropped grayscale image, Canny edges, and contours
    return image, cropped_gray_image, canny_edges, contours

"""
Rotate and crop an image
"""
def crop_rect_rotate(img, box):
    try:
        rect = cv2.minAreaRect(box)
    except:
        print(box)
        return None, None

    # get the parameter of the small rectangle
    center, size, angle = rect[0], rect[1], rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))

    # get row and col num in img
    height, width = img.shape[0], img.shape[1]

    # calculate the rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1)
    # rotate the original image
    img_rot = cv2.warpAffine(img, M, (width, height), flags=cv2.INTER_LINEAR)

    # now rotated rectangle becomes vertical, and we crop it
    img_crop = cv2.getRectSubPix(img_rot, size, center)

    if img_crop.shape[0] > img_crop.shape[1]:
        img_crop = cv2.rotate(img_crop, cv2.ROTATE_90_CLOCKWISE)
    return img_crop

def image_is_cut(image):
    hist = cv2.calcHist([image], [0], None, [256], [0,256])
    if hist[0] > 0:
        return True
    return False

def tile_out_of_bounds(shape, box):
    for coord in box:
        if not (0 < coord[0] < shape[1] and 0 < coord[1] < shape[0]):
            return True
    return False


