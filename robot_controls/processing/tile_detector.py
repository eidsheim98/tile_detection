import cv2
import numpy as np

from robot_controls.processing import crack_detector
from robot_controls.processing import image_processors
from robot_controls.helpers import helper

thresh_writer = helper.create_videowriter("thresh", (463, 209))

"""
Sondre main tile processor
"""
def thresh_detector(frame):
    crack_found = False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = gray[165:-1, 0:-1]

    gray = cv2.dilate(gray, None, iterations=1)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 4)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and draw bounding boxes
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)
        box[:, 1] = box[:, 1] + 165
        x, y, w, h = cv2.boundingRect(box)
        # Filter contours based on area and aspect ratio
        if 95 < h and 135 < w < 200:
            tile = frame[y:y + h, x:x + w]
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            if tile.shape[0] == 0 or tile.shape[1] == 0:
                continue
            crack_found = crack_detector.detect_crack3(tile)
            try:
                cv2.imshow('Tile', tile)
            except:
                pass


    cv2.imshow('Frame', frame)
    cv2.imshow('Thresh', thresh)

    return crack_found

"""
Markus main tile detector
"""
def contour_detector(frame):

    # Process the original image
    image = cv2.imread("../../training_images/inside/Template.png")
    #frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=20)

    original_img, cropped_org_gray, canny_org, contours_org = image_processors.process_image(frame)

    # Process the template image
    template_img, cropped_temp_gray, canny_temp, contours_template = image_processors.process_image(image)

    # Initialize an empty image with the same dimensions as the cropped image to draw the contours
    cropped_org_color = np.zeros((cropped_org_gray.shape[0], cropped_org_gray.shape[1], 3), dtype=np.uint8)

    # Check if there are contours found in the template
    if contours_template:
        contour_template = max(contours_template, key=cv2.contourArea)
        # Draw the largest contour on the cropped template for visualization
        cv2.drawContours(cropped_temp_gray, [contour_template], -1, (0, 255, 0), 3)
    else:
        print("No contours found in the template.")

    # Compare contours and draw bounding box on the cropped original image with another color (e.g., green)
    for i, contour in enumerate(contours_org):
        contourArea = cv2.contourArea(contour)
        if contourArea > 22000:
            continue
        if contourArea < 15000:  # Filter out small contours
            continue
        # Check similarity using the template contour
        similarity = cv2.matchShapes(contour, contour_template, 1, 0.0)
        print(f"Contour {i}: similarity = {similarity}, size = {contourArea}")  # Print out the similarity
        if similarity < 1:  # Adjust similarity threshold as needed
            # Get the minimum area rectangle that bounds the contour
            rect = cv2.minAreaRect(contour)
            # Get the box points and convert them to integers
            box = cv2.boxPoints(rect).astype('int')
            # Draw the bounding box
            cv2.drawContours(cropped_org_color, [box], 0, (0, 255, 0), 2)
            # Label the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                label = f"C{i}"
                cv2.putText(cropped_org_color, label, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            # Draw non-matching contours in red
            cv2.drawContours(cropped_org_color, [contour], -1, (0, 0, 255), 1)
            # Label the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                label = f"C{i}"
                cv2.putText(cropped_org_color, label, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Overlay the color image with the contours onto the cropped grayscale image
    cropped_org_with_contours = cv2.addWeighted(cropped_org_color, 1, cv2.cvtColor(cropped_org_gray, cv2.COLOR_GRAY2BGR), 0.5, 0)

    # Show the results
    cv2.imshow('Detected Tiles', cropped_org_with_contours)
    #cv2.imshow('Template', cropped_temp_gray)
    cv2.imshow('Original Canny Edges', canny_org)
    cv2.imshow('Template Canny Edges', canny_temp)



"""
The working modified thresh detector
"""
def thresh_detector_2(frame):
    crack_found = False
    crack = None
    frame_copy = frame.copy()
    # frame = cv2.resize(frame, (480, 400))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = gray[165:-1, 0:-1]
    gray = gray[190:-1, 0:-1]

    #gray = cv2.bilateralFilter(gray, 7, 75, 75)
    #gray = cv2.GaussianBlur(gray, (9, 9), 0)
    gray = cv2.dilate(gray, None, iterations=1)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 4)
    #thresh = cv2.Canny(gray, 20, 21)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and draw bounding boxes
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = np.intp(box)
        box[:, 1] = box[:, 1] + 190
        x, y, w, h = cv2.boundingRect(box)
        # Filter contours based on area and aspect ratio
        x1 = 0
        y1 = abs(box[0][1] - box[1][1])
        x2 = abs(box[1][0] - box[0][0])
        y2 = 0
        x3 = abs(box[2][0] - box[0][0])
        y3 = abs(box[2][1] - box[1][1])
        x4 = abs(box[3][0] - box[0][0])
        y4 = abs(box[3][1] - box[1][1])
        min_width = 80
        max_width = 205
        min_height = 80
        max_height = 205

        hyp1 = np.sqrt(abs(x4-x1)**2+abs(y4-y1)**2)
        hyp2 = np.sqrt(abs(x2-x1)**2+abs(y2-y1)**2)

        if (min_width < hyp1 < max_width and
            min_height < hyp2 < max_height) or \
            (min_width < hyp2 < max_width and
             min_height < hyp1 < max_height):

            tilebox = np.array([
                [x1, y1],
                [x2, y2],
                [x3, y3],
                [x4, y4]],
                dtype=np.int64
            )
            tile = frame_copy[y:y + h, x:x + w]
            # tile = thresh[y-165:y+h-165, x:x+w]
            if tile.shape[0] == 0 or tile.shape[1] == 0:
                continue

            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            cv2.imshow("Not Rotated", tile)

            tile = image_processors.crop_rect_rotate(tile, tilebox)
            cv2.imshow("Rotated", tile)

            #if image_processors.tile_out_of_bounds(frame.shape, box):
            #    cv2.imshow("Out of bounds", tile)
            #    continue

            crack_found, crack = crack_detector.histogram_detector(tile)

    thresh_writer.write(thresh)

    cv2.imshow('Frame', frame)
    cv2.imshow('Thresh', thresh)

    return crack_found, crack