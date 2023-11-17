"""
Runs on the robot body
Receives the data from the server
"""

import socket
from walk_controller import DogController

# Define server address and port
server_ip = '192.168.12.134'  # Update with the server's IP address
server_port = 8885

# Create a socket for commands
command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_response(response):
    command_socket.send(response.encode())

# Connect to the server
command_socket.connect((server_ip, server_port))
controller = DogController(command_socket)


print("Ready")

while True:
    command = command_socket.recv(1024).decode()
    if not command:
        break
    # Add your command handling logic here
    print(f"Received command: {command}")
    controller.process(command)

# Cleanup
command_socket.close()