import os

def kill_services():
    """
    Kills the camera and speaker services running on the dog by using ssh
    """
    os.system('konsole --new-tab -e ssh -t "unitree@192.168.123.13" "source /home/unitree/server/camkiller.sh"')
    os.system('konsole --new-tab -e ssh -t "unitree@192.168.123.13" "source /home/unitree/server/speakerkiller.sh"')

def start_visual():
    """
    Starts the camera client on the dog
    """
    os.system(
        'konsole --new-tab --hold -e ssh -t "unitree@192.168.123.13" "cd /home/unitree/Unitree/sdk/UnitreeCameraSdk/bins/ && ./cpp_image_sender"')


def start_barker():
    """
    Starts the client on the dogs head connected to the speaker
    """
    os.system(
        'konsole --new-tab --hold -e ssh -t "unitree@192.168.123.13" "cd /home/unitree/Unitree/sdk/UnitreeCameraSdk/bins/ && python3 client_bark.py"')


def start_commands():
    """
    Starts the command receiving client on the raspberry pi on the dog
    """
    os.system(
        'konsole --new-tab --hold -e ssh -t "pi@192.168.12.1" "cd /home/pi/unitree_legged_sdk/example_py/ && python3 client_commands.py"')