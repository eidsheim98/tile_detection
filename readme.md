# Tile detection using machine vision systems and the Unitree Go1 Edu robotic dog

This code repository contains the source code and test data from the project

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


## Manual control
```bash
python3 robot_controls/server/server_manual.py
```

## Automatic walking
```bash
python3 robot_controls/server/server_automous.py
```