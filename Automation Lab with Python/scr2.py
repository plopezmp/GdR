#!/home/lab/.virtualenvs/gns3/bin/python -W ignore
# src2.py
"""
This script is executable.
This script configures vlan's 2 to 6 in switch S1 and the OSPF protocol.
"""
import getpass
import telnetlib
import time

HOST = "172.18.0.250"
user = input("Enter your telnet username:")
password = getpass.getpass()

vlan_list = [2, 3, 4, 5, 6]

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"enable\n")
tn.write(b"cisco\n")

tn.write(b"conf t\n")

for vlan_id in vlan_list:
    tn.write(f"vlan {vlan_id}\n".encode('ascii'))
    tn.write(f"name Python_vlan_{vlan_id}\n".encode('ascii'))

# Configure OSPF
tn.write(b"router ospf 1\n")
tn.write(b"network 0.0.0.0 255.255.255.255 area 0\n")
tn.write(b"end\n")
time.sleep(2)

tn.write(b"exit\n")
tn.write(b"sh ip ospf neighbor\n")
tn.write(b"exit\n")
tn.write(b"write\n")

print(tn.read_all().decode('ascii'))
