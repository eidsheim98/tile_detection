"""
Lets you run the tile and crack detection on a video
"""

import threading

import cv2
import time
from robot_controls.helpers import helper
from robot_controls.processing import tile_detector, tape_detector


filename = "../../output/video/frame/testvideo.avi"

crack_counter = 0

def _count_thread():
    """
    Method that resets the crack counter after a set amount of time
    Helps remove false positives by making the server not respond if only one one image is found to contain something in a set timeframe
    This means that there must be x amounts of crack detections in a small amount of time for a crack to be verified
    """
    global crack_counter
    while True:
        crack_counter = 0
        time.sleep(1)

# Start the counter
threading.Thread(target=_count_thread).start()

# Load the video
cap = cv2.VideoCapture(filename)

while cap.isOpened():
    ret, frame = cap.read()

    # If the video is not playable, or finished
    if frame is None:
        break

    # Detect tiles and cracks
    crack_found, crack = tile_detector.thresh_detector(frame)

    # If something is found in the image (most likely a crack), increase the crack counter
    if crack_found:
        crack_counter += 1

    # When three cracks have been found in the set timeframe, the crack is counted as verified.
    # The server will respond accordingly
    if crack_counter >= 3:
        helper.save_crack(crack)  # Save the image of the crack
        print("Crack found")  # Print that the crack is found
        cv2.imshow("Crack", crack)  # Show the crack image
        crack_counter = 0  # Reset the crack counter

    cv2.waitKey(100)

cv2.destroyAllWindows()
cap.release()