import cv2
import numpy as np

from robot_controls.processing import crack_detector
from robot_controls.processing import image_processors
from robot_controls.helpers import helper

#thresh_writer = helper.create_videowriter("thresh", (463, 209))

def thresh_detector(frame):
    """
    Threshold detector for tile detection and isolation
    :param frame: The image to detect tiles in
    :return: The data from the crack detector
    """

    crack_found = False
    crack = None

    # Create a copy of the frame which wont get the red squares
    frame_copy = frame.copy()

    # Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop away the dogs legs
    gray = gray[190:-1, 0:-1]

    # Make the edges pop more by dilating
    gray = cv2.dilate(gray, None, iterations=1)

    # Create a thresholded image from the dilated one
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 4)

    # Get the contours from this threshold image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Write each frame to the video to be saved for further reference
    #thresh_writer.write(thresh)

    # Iterate through contours and draw bounding boxes
    for contour in contours:
        # Create the bounding boxes
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)

        # The box is calculated based on the cropped thresholded image, so it has to be moved to fit on the original
        box[:, 1] = box[:, 1] + 190

        # This codeblock calculates the locations of the corners of the tile, and makes sure it has the correct size
        # This is done using the pythagorean theorem
        x, y, w, h = cv2.boundingRect(box)
        x1 = 0
        y1 = abs(box[0][1] - box[1][1])
        x2 = abs(box[1][0] - box[0][0])
        y2 = 0
        x3 = abs(box[2][0] - box[0][0])
        y3 = abs(box[2][1] - box[1][1])
        x4 = abs(box[3][0] - box[0][0])
        y4 = abs(box[3][1] - box[1][1])

        # Set the max and min heights of the tiles
        min_width = 80
        max_width = 205
        min_height = 80
        max_height = 205

        # Calculates the sides of the square (hyothenuses)
        hyp1 = np.sqrt(abs(x4-x1)**2+abs(y4-y1)**2)
        hyp2 = np.sqrt(abs(x2-x1)**2+abs(y2-y1)**2)

        # Chacks that the lines are between the set height and width
        if (min_width < hyp1 < max_width and
            min_height < hyp2 < max_height) or \
            (min_width < hyp2 < max_width and
             min_height < hyp1 < max_height):

            # Create a new tilebox based on these coordinates
            # This tilebox is later used to turn and crop the image of the tile
            tilebox = np.array([
                [x1, y1],
                [x2, y2],
                [x3, y3],
                [x4, y4]],
                dtype=np.int64
            )

            # Crop the image of the tile out of the original image
            tile = frame_copy[y:y + h, x:x + w]

            # Check that the tile actually got a size, and that it is usable
            if tile.shape[0] == 0 or tile.shape[1] == 0:
                continue

            # draw the contours onto the frame, and show it
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            cv2.imshow("Not Rotated", tile)

            # Rotate and crop the image of the tile based on the tilebox
            tile = image_processors.crop_rect_rotate(tile, tilebox)
            cv2.imshow("Rotated", tile)

            # Check if a crack is detected
            crack_found, crack = crack_detector.histogram_detector(tile)

    # Show the frame and the thresh
    cv2.imshow('Frame', frame)
    cv2.imshow('Thresh', thresh)

    return crack_found, crack
