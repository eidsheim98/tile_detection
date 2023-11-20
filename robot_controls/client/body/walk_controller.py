"""
The processor that makes the dog perform actions based on commands
Is based on the dog SDK code
Located on the dog head
"""

import sys
import time
import math
from threading import Thread

sys.path.append('../lib/python/arm64')
import robot_interface as sdk


class DogController():
    def __init__(self, callback):
        self._next_rotation_dir = "right"
        self._status = "stop"
        self._start_runner()
        self._callback = callback
        self.called = False
        self._start_radians = 0.0

    def _change_dir(self):
        """
        Changes the direction the dog will turn
        """
        if self._next_rotation_dir == "right":
            self._next_rotation_dir = "left"
        else:
            self._next_rotation_dir = "right"

    def get_status(self):
        """
        Get the current status of the dog, e.g walking or turning
        """
        return self._status

    def process(self, command):
        """
        Checks that the incoming command is valid, and forwards it if it is
        :param command: The command to process
        """

        if command == "forward":
            print("Moving forward")
        elif command == "turn":
            self._change_dir()
            print(f"Turning {self._next_rotation_dir}")
        elif command == "stop":
            print("Stopping")
        elif command == "bark":
            print("Barking")
        elif command == "calibrate":
            pass
        else:
            print(f"Command not found: {command}")
            return

        self._status = command

    def calculate_adjustment(self):
        """
        Calculates the rotation the dog has to make to rotate correctly based on starting position
        :return: The radians left to rotate
        """
        if self._start_radians > 0:
            correct_radians = self._start_radians - math.pi
        else:
            correct_radians = self._start_radians + math.pi

        return correct_radians

    def _start_runner(self):
        """
        Starts the main thread to run the robot in the loop
        """
        t = Thread(target=self._run_bot)
        t.start()

    def _run_bot(self):
        """
        The main function running the robot dog
        """

        # Initialize all sensors
        HIGHLEVEL = 0xee
        LOWLEVEL = 0xff

        udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)

        cmd = sdk.HighCmd()
        state = sdk.HighState()
        udp.InitCmdData(cmd)
        print("Dog ready")

        # Run a loop
        while True:
            time.sleep(0.002)

            # Initialize the start radians based on information from the IMU
            if self._start_radians == 0.0:
                self._start_radians = state.imu.rpy[2]

            udp.Recv()
            udp.GetRecv(state)

            # Reset more of the sensors
            # This comes from the SDK
            cmd.mode = 0  # 0:idle, default stand      1:forced stand     2:walk continuously
            cmd.gaitType = 0
            cmd.speedLevel = 0
            cmd.footRaiseHeight = 0
            cmd.bodyHeight = 0
            cmd.euler = [0, 0, 0]
            cmd.velocity = [0, 0]
            cmd.yawSpeed = 0.0
            cmd.reserve = 0

            """
            Functionality to make the dog turn
            This is done by calculating how far it is from turning pi radians 
            To make sure it would stop at approximately pi radians and not just keep turning, we have set an upper and 
            lower boundary that the rotated angle must be between to be accepted 
            """
            if self._status == "turn":
                # Get the current adjustment and set upper and lower level
                c = self.calculate_adjustment()
                lower = c - math.pi * 0.01
                upper = c + math.pi * 0.01

                # If the current rotated state is between these levels, the rotation is a success
                if lower < state.imu.rpy[2] < upper or \
                        lower > state.imu.rpy[2] > upper:
                    print("Adjusted")

                    # Reset the start radians to this rotation and stop the turning of the dog
                    self._start_radians = c
                    self._status = "stop"

                # The actual rotation is handled here
                # If the rotated angle exceeds 90% of desired angle, slow down the rotation to make it
                # more accurate
                elif c - math.pi * 0.1 < state.imu.rpy[2] < c + math.pi * 0.1 or \
                        c - math.pi * 0.1 > state.imu.rpy[2] > c + math.pi * 0.1:
                    cmd.mode = 2
                    cmd.gaitType = 1
                    if self._next_rotation_dir == "left":
                        print("Attempting turn left")

                        cmd.yawSpeed = math.pi / 8
                        cmd.velocity = [0.1, -0.0]  # -1  ~ +1
                    else:
                        print("Attempting turn right")

                        cmd.yawSpeed = -math.pi / 8
                        cmd.velocity = [0.1, 0.0]  # -1  ~ +1
                    cmd.footRaiseHeight = 0.1

                # The basic rotation of the dog before it reaches 90% finished rotation
                else:
                    cmd.mode = 2
                    cmd.gaitType = 1
                    if self._next_rotation_dir == "left":
                        print("Attempting turn left")

                        cmd.yawSpeed = math.pi / 2
                        cmd.velocity = [0.2, -0.5]  # -1  ~ +1
                    else:
                        print("Attempting turn right")

                        cmd.yawSpeed = -math.pi / 2
                        cmd.velocity = [0.2, 0.5]  # -1  ~ +1
                    cmd.footRaiseHeight = 0.1

            # Making the dog walk straight
            elif self._status == "forward":
                cmd.mode = 2
                cmd.gaitType = 1
                cmd.velocity = [0.2, - state.velocity[1]]  # -1  ~ +1
                cmd.footRaiseHeight = 0.1
                cmd.euler[0] *= -1

            # Calibrate the sensors
            elif self._status == "calibrate":
                self._start_radians = state.imu.rpy[2]
                print("Start position reset")
                self._status = ""


            # Stop the dog
            else:
                cmd.mode = 0

            udp.SetSend(cmd)
            udp.Send()


if __name__ == '__main__':
    D = DogController(None)
    # time.sleep(5)
    while True:
        # continue
        D.process("forward")
        time.sleep(10)
        # D.process("stop")
        # time.sleep(1)
        # D.process("turn")
        # time.sleep(5)
        # D.process("stop")
        # time.sleep(1)