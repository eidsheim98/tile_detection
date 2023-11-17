import cv2
import datetime

__now__ = datetime.datetime.now().timestamp()

def create_videowriter(outputfolder, size):
    writer = cv2.VideoWriter(f"../../output/video/{outputfolder}/{__now__}.avi",
                             cv2.VideoWriter.fourcc("M", "J", "P", "G"), 10, size)
    return writer

def save_crack(frame):
    now = datetime.datetime.now().timestamp()
    cv2.imwrite(f"../../output/img/cracks/{now}.jpg", frame)

