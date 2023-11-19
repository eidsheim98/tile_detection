"""

"""
import cv2
import time
from robot_controls.helpers import helper
from robot_controls.processing import tile_detector
from robot_controls.processing import image_processors
from robot_controls.helpers.tile import TileInfo

filename = "../../output/video/frame/testframe.avi"

crack_counter = 0

def _count_thread():
    global crack_counter
    while True:
        crack_counter = 0
        time.sleep(1)

cap = cv2.VideoCapture(filename)

while cap.isOpened():
    ret, frame = cap.read()

    #crack_found, crack = tile_detector.thresh_detector_2(frame)
    tiles = tile_detector.thresh_detector_2(frame)
    for tile in tiles:
        rotated = image_processors.crop_rect_rotate(tile)



    if crack_counter >= 3:
        helper.save_crack(crack)
        print("Crack found")
        cv2.imshow("Crack", crack)
        crack_counter = 0

    #cv2.imshow("frame", frame)
    cv2.waitKey(100)

cv2.destroyAllWindows()

