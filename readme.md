# Tile detection using machine vision systems and the Unitree Go1 Edu robotic dog

This code repository contains the source code and test data from the project
The code is only tested on Linux, (specifically KDE Neon, but Ubuntu should be fine) as we had problems connecting to the dog using other operating systems

## Prerequisites
### Installation requirements
This project uses the Linux command emulator Konsole to display data on the dog via the SSH connection. You may use any terminal emulator you want, but will then have to change the command strings using the emulator commands in ```robot_controls/server/ssh.py```.

Konsole can be installed using 
```bash
sudo apt install konsole
```

You will then have to install the python requirements by running
```bash
python3 install -r requirements.txt
```

### Setup of SSH
The clients in the dog will be started automatically over ssh by the server. To make this possible, you must add some configuration to your /.ssh/config file

```
Host dog_pi
        HostName 192.168.12.1
        User pi

Host dog_head
        HostName 192.168.123.13
        User unitree
        ProxyCommand ssh -q -W %h:%p dog_pi
```

Then add your ssh key to the dog by running 
```bash
ssh-copy-id dog_pi
ssh-copy-id dog_head
```

The password for both devices are 123

## Usage
1. Put the dog on the ground, and position the rear legs in the same position as the front legs were in the box
2. Start the dog by first clicking the on/off button on the side once, and then holding it in until the lights start flashing
3. Wait until the robot starts and goes into standing position
4. Connect to the Unitree hotspot created by the dog

### Manual control
Start the ```server_manual.py``` file

### Automatic walking
Start the ```server_autonomous.py``` file

The autonomous server is also able to receive commands directly from the terminal. These include

**Forward:** Dog starts walking <br/>
**Stop:** Dog stops walking <br/>
**Turn:** Dog starts turning in the next determined direction
**Calibrate:** Dog resets all sensors based on its current location

### Testing on a video
It is also possible to test the detection system on a video by running the Start the ```video_loader.py``` file
