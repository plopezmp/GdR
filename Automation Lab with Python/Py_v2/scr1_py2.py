#!/usr/bin/env python
"""
This script is executable.
This script configure 5 loopback interfaces in R1 and OSPF announcing any network.
"""
import getpass
import telnetlib
import time

HOST = "172.16.0.254"
user = raw_input("Enter your telnet username:")  # Use raw_input() for Python 2
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ")  # No need to use b""
tn.write(user + "\n")  # No need to encode to 'ascii'
if password:
    tn.read_until("Password: ")  # No need to use b""
    tn.write(password + "\n")  # No need to encode to 'ascii'

tn.write("enable\n")
tn.write("cisco\n")

for i in range(1, 6):
    tn.write("conf t\nint l0%d\nip add %d.%d.%d.%d 255.255.255.255\nend\n" % (i, i, i, i, i))


# Configure OSPF
tn.write("conf t\n")
tn.write("router ospf 1\n")
tn.write("network 0.0.0.0 255.255.255.255 area 0\n")
tn.write("end\n")
time.sleep(2)

tn.write("sh ip int brief\n")
tn.write("sh ip ospf neighbor\n") 
tn.write("exit\n")
tn.write("write\n")

print tn.read_all().decode('ascii')  # No need to decode from 'ascii'
