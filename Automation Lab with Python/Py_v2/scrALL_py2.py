#!/usr/bin/env python
"""
This script is executable.
This script intend to merge 'scr1.py' and 'scr2.py' and
read common parameter inputs from the 'data.cfg' file.
"""
import getpass
import telnetlib
import time

def configure_device(host, user, password, config_commands):
    tn = telnetlib.Telnet(host)

    tn.read_until("Username: ")

    tn.write(user + "\n")

    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    tn.write("enable\n")
    tn.write("cisco\n")
    tn.write("conf t\n")

    for command in config_commands:
        tn.write(command + "\n")

    tn.write("exit\n")
    tn.write("end\n")
    tn.write("exit\n")

    print tn.read_all().decode('ascii')

def main():
    file = open("data.cfg")
    lines = file.read().splitlines()
    file.close()

    user = lines[-2].strip()  # Second-to-last line
    password = lines[-1].strip()  # Last line

    ips = [ip.strip() for ip in lines[:-2]]

    r1_commands = [
        "interface lo10",
        "ip address 10.10.10.10 255.255.255.255",
        "no shutdown"
    ]

    s1_commands = [
        "vlan 2",
        "name Python_vlan_2",
        "vlan 3",
        "name Python_vlan_3",
        "vlan 4",
        "name Python_vlan_4",
        "vlan 5",
        "name Python_vlan_5",
        "vlan 6",
        "name Python_vlan_6",
    ]

    for ip in ips:
        if "250" in ip:
            commands = s1_commands
        else:
            commands = r1_commands
        configure_device(ip, user, password, commands)
    

if __name__ == "__main__":
    main()
