#!/usr/bin/env python
"""
This script is executable.
This script configures vlan's 2 to 6 in switch S1 and the OSPF protocol.
"""
import getpass
import telnetlib
import time

HOST = "172.167.0.250"
user = raw_input("Enter your telnet username:")  # Use raw_input() for Python 2
password = getpass.getpass()

vlan_list = [2, 3, 4, 5, 6]

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ")  # No need to use b""
tn.write(user + "\n")  # No need to encode to 'ascii'
if password:
    tn.read_until("Password: ")  # No need to use b""
    tn.write(password + "\n")  # No need to encode to 'ascii'

tn.write("enable\n")
tn.write("cisco\n")

tn.write("conf t\n")

for vlan_id in vlan_list:
    tn.write("vlan %d\n" % vlan_id)
    tn.write("name Python_vlan_%d\n" % vlan_id)

# Configure OSPF
tn.write("router ospf 1\n")
tn.write("network 0.0.0.0 255.255.255.255 area 0\n")
tn.write("end\n")
time.sleep(2)

tn.write("exit\n")
tn.write("sh ip ospf neighbor\n")
tn.write("exit\n")
tn.write("write\n")

print tn.read_all().decode('ascii')  # No need to decode from 'ascii'
