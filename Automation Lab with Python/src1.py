#!/home/lab/.virtualenvs/gns3/bin/python -W ignore
# src1.py
"""
This script is executable.
This script configure 5 loopback interfaces in outer R1 and OSPF announcing any network.
"""
import getpass
import telnetlib
import time

HOST = "172.18.0.251"
user = input("Enter your telnet username:")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"enable\n")
tn.write(b"cisco\n")

for i in range(1, 6):
    tn.write(f"conf t\nint l0{i}\nip add {i}.{i}.{i}.{i} 255.255.255.255\nend\n".encode('ascii'))

# Configure OSPF
tn.write(b"conf t\n")
tn.write(b"router ospf 1\n")
tn.write(b"network 0.0.0.0 255.255.255.255 area 0\n")
tn.write(b"end\n")
time.sleep(2)

tn.write(b"sh ip int brief\n")
tn.write(b"sh ip ospf neighbor\n") 
tn.write(b"exit\n")
tn.write(b"write\n")

print(tn.read_all().decode('ascii'))