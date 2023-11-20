"""
The server that detects tiles while the dog walks around controlled remotely
Is located on a computer connected to the dogs hotspot
"""

import time
import numpy
import cv2
import socket
import threading
import ssh
from robot_controls.processing import tile_detector
from robot_controls.helpers import helper

# Kill necessary services running on the dog
ssh.kill_services()

# Start the necessary services on the dog
threading.Thread(target=ssh.start_visual).start()
threading.Thread(target=ssh.start_barker).start()

# Define server address and port
server_ip = '192.168.12.134'
server_port = 8885

# Create a socket for commands and video streaming
video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bark_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind sockets to the server address and port
video_socket.bind((server_ip, server_port + 2))
bark_socket.bind((server_ip, server_port + 1))
bark_socket.listen(1)

print("Waiting for a bark client to connect...")
bark_socket, bark_addr = bark_socket.accept()
print("Bark client connected from:", bark_addr)

# Counts the amount of cracks found in a limited time
crack_counter = 0
def _count_thread():
    """
    Method that resets the crack counter after a set amount of time
    Helps remove false positives by making the server not respond if only one one image is found to contain something in a set timeframe
    This means that there must be x amounts of crack detections in a small amount of time for a crack to be verified
    :return:
    """
    global crack_counter
    crack_counter = 0
    time.sleep(1)

# Start the counter
threading.Thread(target=_count_thread).start()


def bark():
    """
    Sends the bark command to the dogs head
    """
    bark_socket.send(b"bark")


# Create a new videowriter that will save the video of the frame
#video_writer = helper.create_videowriter("frame", (464, 400))

while True:

    # Get image size in bytes from the client
    length, _ = video_socket.recvfrom(16)

    # read image data here based on the size of the image
    try:
        stringData, addr = video_socket.recvfrom(int(length))
    except:
        continue

    # Convert to opencv image format
    data = numpy.frombuffer(stringData, dtype="uint8")
    frame = cv2.imdecode(data, -1)
    frame_copy = frame

    # Ensures that the frame is something before trying to detect anything in it
    if frame is not None:
        crack_found, crack = tile_detector.thresh_detector(frame)
        if crack is not None:

            # If something is found in the image (most likely a crack), increase the crack counter
            if crack_found:
                crack_counter += 1

            # When three cracks have been found in the set timeframe, the crack is counted as verified.
            # The server will respond accordingly
            if crack_counter >= 3:
                helper.save_crack(crack)    # Save the image of the crack
                print("Crack found")        # Print that the crack is found
                cv2.imshow("Crack", crack)  # Show the crack image
                crack_counter = 0           # Reset the crack counter
                bark()                      # Make the dog bark

    # Try writing the frame to the video
    try:
        #video_writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    except:
        pass

#video_writer.release()

cv2.destroyAllWindows()
print("Video saved")
