"""
Simple helper file to aid the processing server
"""

import cv2
import datetime

__now__ = datetime.datetime.now().timestamp()

def create_videowriter(outputfolder, size):
    """
    Creates a videowriter in the specified folder
    :param outputfolder: The folder to place the video in
    :param size: The width and height of the video in a tuple format (x, y)
    :return: The videowriter
    """

    writer = cv2.VideoWriter(f"../../output/video/{outputfolder}/{__now__}.avi",
                             cv2.VideoWriter.fourcc("M", "J", "P", "G"), 10, size)
    return writer

def save_crack(frame):
    """
    Saves the image of the crack with the name set to the current epoch timestamp
    :param frame: The image to save
    """
    now = datetime.datetime.now().timestamp()
    cv2.imwrite(f"../../output/img/cracks/{now}.jpg", frame)

