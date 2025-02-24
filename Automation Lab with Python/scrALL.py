#!/home/lab/.virtualenvs/gns3/bin/python -W ignore
# src1.py
"""
This script is executable.
This script intends to merge 'scr1.py' and 'scr2.py' and
read common parameter inputs from the 'data.cfg' file.
"""
import getpass
import telnetlib
import time

def configure_device(host, user, password, config_commands):
    tn = telnetlib.Telnet(host)

    tn.read_until(b"Username: ")
    tn.write(user.encode('ascii') + b"\n")

    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")

    tn.write(b"enable\n")
    tn.write(b"cisco\n")
    tn.write(b"conf t\n")

    for command in config_commands:
        tn.write(command.encode('ascii') + b"\n")

    tn.write(b"exit\n")
    tn.write(b"end\n")
    tn.write(b"exit\n")

    print(tn.read_all().decode('ascii'))

def main():
    with open("data.cfg") as file:
        lines = file.read().splitlines()

    user = lines[-2].strip()  # Second-from-last line
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
        configure_device(ip, user, password, s1_commands if "250" in ip else r1_commands)

if __name__ == "__main__":
    main()
