#!/usr/bin/python

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
        if self._next_rotation_dir == "right":
            self._next_rotation_dir = "left"
        else:
            self._next_rotation_dir = "right"

    def get_status(self):
        return self._status

    def process(self, command):
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
        if self._start_radians > 0:
            correct_radians = self._start_radians - math.pi
        else:
            correct_radians = self._start_radians + math.pi

        return correct_radians

    def _start_runner(self):
        t = Thread(target=self._run_bot)
        t.start()

    def _run_bot(self):

        HIGHLEVEL = 0xee
        LOWLEVEL = 0xff

        udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)

        cmd = sdk.HighCmd()
        state = sdk.HighState()
        udp.InitCmdData(cmd)
        print("Dog ready")

        while True:
            time.sleep(0.002)

            if self._start_radians == 0.0:
                self._start_radians = state.imu.rpy[2]

            udp.Recv()
            udp.GetRecv(state)

            cmd.mode = 0  # 0:idle, default stand      1:forced stand     2:walk continuously
            cmd.gaitType = 0
            cmd.speedLevel = 0
            cmd.footRaiseHeight = 0
            cmd.bodyHeight = 0
            cmd.euler = [0, 0, 0]
            cmd.velocity = [0, 0]
            cmd.yawSpeed = 0.0
            cmd.reserve = 0


            if self._status == "turn":
                c = self.calculate_adjustment()
                lower = c - math.pi * 0.01
                upper = c + math.pi * 0.01

                if lower < state.imu.rpy[2] < upper or \
                        lower > state.imu.rpy[2] > upper:
                    print("Adjusted")
                    self._start_radians = c
                    self._status = "stop"

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

            # Straight OK
            elif self._status == "forward":
                cmd.mode = 2
                cmd.gaitType = 1
                cmd.velocity = [0.2, - state.velocity[1]]  # -1  ~ +1
                cmd.footRaiseHeight = 0.1
                cmd.euler[0] *= -1

            elif self._status == "calibrate":
                self._start_radians = state.imu.rpy[2]
                print("Start position reset")
                self._status = ""


            # Stop
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