"""
The server that runs the robot autonomously
Is located on a computer connected to the dogs hotspot
"""

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
server_ip = '0.0.0.0'
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

# Kill necessary services running on the dog
ssh.kill_services()

# Start the command TCP client on the dogs raspberry pi
threading.Thread(target=ssh.start_commands).start()

print("Waiting for a command client to connect...")
command_conn, command_addr = command_socket.accept()
print("Command client connected from:", command_addr)

threading.Thread(target=ssh.start_barker).start()

# Start the command TCP client on the dogs head unit
print("Waiting for a bark client to connect...")
bark_socket, bark_addr = bark_socket.accept()
print("Bark client connected from:", bark_addr)

# Start the visual UDP client running on the dog
threading.Thread(target=ssh.start_visual).start()


class CommandController():
    """
    The class for controlling commands sent to the dog, and the state of the dog
    """
    def __init__(self):
        self.last_command = ""
        self.command = ""
        self.ready = True

# Initialize the controller
controller = CommandController()

# Function to handle command client
def handle_command_client():
    """
    Makes it possible to type commands to the dog via keyboard
    """
    while True:
        controller.command = input("Enter a command: ")


def handle_frame_commands(client_socket):
    """
    Handles the sending of the commands that the server has processed
    :param client_socket:
    :return:
    """
    while True:
        if controller.command != "":
            # Make sure it does not spam the same command
            if controller.command != controller.last_command:
                client_socket.send(controller.command.encode())
                controller.last_command = controller.command

        time.sleep(0.1)

def bark():
    """
    Sends the bark command to the dogs head
    """
    bark_socket.send("bark".encode())


# Start the thread to handle incoming commands from the keyboard
command_thread = threading.Thread(target=handle_command_client)
command_thread.start()

# Start the thread to handle sending of commands from the server
frame_thread = threading.Thread(target=handle_frame_commands, args=(command_conn,))
frame_thread.start()

# Video socket initialization stuff
data = b''
payload_size = struct.calcsize("L")


def _timer(seconds):
    """
    A timer that sets the server in a state where it will process new commands for x seconds
    :param seconds: The seconds to wait
    """
    controller.ready = False
    time.sleep(seconds)
    controller.ready = True


def start_timer(seconds):
    """
    Method to start the timer that sets the server in a state where it will process new commands for x seconds
    :param seconds: The seconds to wait
    """
    timer = threading.Thread(target=_timer, args=(seconds,))
    timer.start()

# Counts the amount of cracks found in a limited time
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

# Create a new videowriter that will save the video of the frame
#videowriter = helper.create_videowriter("frame", (464, 400))

turn = False

while True:

    try:
        # Get image size in bytes from the client
        length, addr = video_socket.recvfrom(16)

        # read image data here based on the size of the image
        stringData, _ = video_socket.recvfrom(int(length))

        # Convert the data from bytes to an image
        d = numpy.frombuffer(stringData, dtype="uint8")
        frame = cv2.imdecode(d, -1)
        global_frame = frame
    except:
        continue

    # ------------------------ Processing is handled here -----------------------------

    # Detect tape and cracks
    tape_found, frame2 = tape_detector.tape_found(frame)
    crack_found, crack = tile_detector.thresh_detector(frame)

    # Makes sure that a crack is not falsely detected if the dog is turning
    if crack is not None and controller.command != "turn":

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

    # If tape is found and the dog is ready
    if tape_found and controller.ready:
        # Start a timer for 10 seconds. This will ensure that the dog does not detect any cracks or tape during this
        # period, so it will not start walking or turning again unless it is ready
        start_timer(10)
        turn = not turn

        if turn:
            controller.command = "turn"
            print("Turn")
        else:
            controller.command = "forward"
            print("Forward")

    # ------------------------ End processing -----------------------------

    # Write the frame to the video
    #videowriter.write(frame)

    cv2.waitKey(1)
    data = b''
