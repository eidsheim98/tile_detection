import cv2
import numpy as np

def _process_image(image):
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

def process(frame):

    # Process the original image
    image = cv2.imread("../../training_images/inside/Template.png")
    #frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=20)

    original_img, cropped_org_gray, canny_org, contours_org = _process_image(frame)

    # Process the template image
    template_img, cropped_temp_gray, canny_temp, contours_template = _process_image(image)

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

if __name__ == '__main__':
    image = cv2.imread("../../training_images/inside/Frame_screenshot_06.11.2023.png")
    process(image)
    cv2.waitKey(0)