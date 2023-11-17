import socket
import struct
import time
import cv2
import threading
from robot_controls.server import ssh
from robot_controls.helpers import helper
from robot_controls.processing import tile_detector
from robot_controls.processing import tape_detector
import numpy


# Define server address and port
server_ip = '0.0.0.0'  # Use '0.0.0.0' to listen on all available network interfaces
server_port = 8885

# Create a socket for commands and video streaming
command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bark_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind sockets to the server address and port
command_socket.bind((server_ip, server_port))
video_socket.bind((server_ip, server_port + 2))
bark_socket.bind((server_ip, server_port + 1))

# Listen for incoming connections
command_socket.listen(1)
bark_socket.listen(2)

ssh.kill_services()

threading.Thread(target=ssh.start_commands).start()

print("Waiting for a command client to connect...")
command_conn, command_addr = command_socket.accept()
print("Command client connected from:", command_addr)

threading.Thread(target=ssh.start_barker).start()

print("Waiting for a bark client to connect...")
bark_socket, bark_addr = bark_socket.accept()
print("Bark client connected from:", bark_addr)

threading.Thread(target=ssh.start_visual).start()


class CommandController():
    def __init__(self):
        self.last_command = ""
        self.command = ""
        self.ready = True


controller = CommandController()


# Function to handle command client
def handle_command_client():
    while True:
        controller.command = input("Enter a command: ")


def handle_frame_commands(client_socket):
    while True:
        if controller.command != "":
            if controller.command != controller.last_command:
                client_socket.send(controller.command.encode())
                controller.last_command = controller.command
        time.sleep(0.1)

def bark():
    bark_socket.send("bark".encode())


# Start a thread to handle the command client
command_thread = threading.Thread(target=handle_command_client)
command_thread.start()
frame_thread = threading.Thread(target=handle_frame_commands, args=(command_conn,))
frame_thread.start()

# Video socket stuff

data = b''
payload_size = struct.calcsize("L")


def _timer(seconds):
    controller.ready = False
    time.sleep(seconds)
    controller.ready = True


def start_timer(seconds):
    timer = threading.Thread(target=_timer, args=(seconds,))
    timer.start()


crack_counter = 0
canny_counter = 0


def _count_thread():
    global crack_counter
    global canny_counter
    while True:
        crack_counter = 0
        canny_counter = 0
        time.sleep(1)


threading.Thread(target=_count_thread).start()
videowriter = helper.create_videowriter("frame", (464, 400))

turn = False

while True:

    try:
        # Get image size here
        length, addr = video_socket.recvfrom(16)

        # read image data here
        stringData, _ = video_socket.recvfrom(int(length))

        d = numpy.frombuffer(stringData, dtype="uint8")
        frame = cv2.imdecode(d, -1)
        global_frame = frame
        videowriter.write(frame)
    except:
        continue

    # ------------------------ Processing is handled here -----------------------------

    tape_found, frame2 = tape_detector.tape_found(frame)
    crack_found_thresh, crack_thresh, crack_found_canny, crack_canny = tile_detector.thresh_detector_2(frame)

    if crack_thresh is not None and controller.command != "turn":
        if crack_found_thresh:
            crack_counter += 1

        if crack_counter >= 3:
            helper.save_crack(crack_thresh, "thresh")
            print("Crack found")
            cv2.imshow("Crack", crack_thresh)
            crack_counter = 0
            bark()

    if crack_canny is not None and controller.command != "turn":
        if crack_found_canny:
            canny_counter += 1

        if canny_counter >= 3:
            helper.save_crack(crack_canny, "canny")
            print("Crack found")
            cv2.imshow("Crack", crack_canny)
            canny_counter = 0
            bark()

    if tape_found and controller.ready:
        start_timer(10)
        turn = not turn
        if turn:
            controller.command = "turn"
            print("Turn")
        else:
            controller.command = "forward"
            print("Forward")

    # ------------------------ End processing -----------------------------

    cv2.waitKey(1)
    data = b''
