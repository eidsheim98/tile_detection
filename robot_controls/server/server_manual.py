import time
import numpy
import cv2
import socket
import threading
from robot_controls.server import ssh
from robot_controls.processing import tile_detector
from robot_controls.helpers import helper

ssh.kill_services()

threading.Thread(target=ssh.start_visual).start()
threading.Thread(target=ssh.start_barker).start()

# Define server address and port
server_ip = '192.168.12.134'  # Use '0.0.0.0' to listen on all available network interfaces
server_port = 8885

video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bark_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

video_socket.bind((server_ip, server_port + 2))
bark_socket.bind((server_ip, server_port + 1))
bark_socket.listen(1)

print("Waiting for a bark client to connect...")
bark_socket, bark_addr = bark_socket.accept()
print("Bark client connected from:", bark_addr)

crack_counter = 0
def _count_thread():
    global crack_counter
    crack_counter = 0
    time.sleep(1)


threading.Thread(target=_count_thread).start()


def bark():
    bark_socket.send(b"bark")


# Video writer stuff
video_writer = helper.create_videowriter("frame", (464, 400))

while True:

    # Get image size here
    length, _ = video_socket.recvfrom(16)

    # read image data here
    try:
        stringData, addr = video_socket.recvfrom(int(length))
    except:
        continue

    # Convert to opencv image format
    # data = numpy.fromstring(stringData, dtype='uint8')
    data = numpy.frombuffer(stringData, dtype="uint8")
    frame = cv2.imdecode(data, -1)
    frame_copy = frame

    if frame is not None:
        crack_found, crack = tile_detector.thresh_detector_2(frame)
        if crack is not None:
            if crack_found:
                crack_counter += 1

            if crack_counter >= 3:
                helper.save_crack(crack)
                print("Crack found")
                cv2.imshow("Crack", crack)
                bark()
                crack_counter = 0

    try:
        video_writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    except:
        pass

video_writer.release()

cv2.destroyAllWindows()
print("Video saved")
