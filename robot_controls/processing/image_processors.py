import cv2
import numpy as np

def crop_rect_rotate(img, box):
    """
    Rotate the image of the tile and crop it
    :param img: The image of the tile
    :param box: The coordinates of the corners of the tile
    :return: The cropped image
    """

    # If it is not possible to create a rectangle from the coordinates, just return
    try:
        rect = cv2.minAreaRect(box)
    except:
        print(box)
        return None, None

    # Get the parameter of the small rectangle
    center, size, angle = rect[0], rect[1], rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))

    # Get row and col num in img
    height, width = img.shape[0], img.shape[1]

    # Calculate the rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1)
    # Rotate the original image
    img_rot = cv2.warpAffine(img, M, (width, height), flags=cv2.INTER_LINEAR)

    # Now rotated rectangle becomes vertical, so we crop it
    img_crop = cv2.getRectSubPix(img_rot, size, center)

    # Lay the tile down horizontally if it got rotated to a vertical state
    if img_crop.shape[0] > img_crop.shape[1]:
        img_crop = cv2.rotate(img_crop, cv2.ROTATE_90_CLOCKWISE)
    return img_crop


