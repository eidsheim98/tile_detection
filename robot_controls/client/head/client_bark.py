"""
Runs on the robot body
Receives the data from the server
"""

import socket
import os

# Define server address and port
server_ip = '192.168.12.134'  # Update with the server's IP address
server_port = 8886

# Create a socket for commands
command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
command_socket.connect((server_ip, server_port))

print("Barking ready")

while True:
    command = command_socket.recv(1024).decode()
    if not command:
        break
    # Add your command handling logic here
    if command == "bark":
        print("Barking")
        os.system("aplay -D plughw:2,0 ~/Music/audio_files/dog.wav")

# Cleanup
command_socket.close()