#!/home/lab/.virtualenvs/gns3/bin/python -W ignore
# Basic S1 script
import getpass
import telnetlib

HOST = "172.18.0.250"
user = input("Enter your telnet username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"enable\n")
tn.write(b"cisco\n")

tn.write(b"conf t\n")
tn.write(b"vlan 2\n")
tn.write(b"name Python_vlan_2\n")
# tn.write(b"vlan 3\n")
# tn.write(b"name Python_vlan_3\n")
# tn.write(b"vlan 4\n")
# tn.write(b"name Python_vlan_4\n")
# tn.write(b"vlan 5\n")
# tn.write(b"name Python_vlan_5\n")
# tn.write(b"vlan 6\n")
# tn.write(b"name Python_vlan_6\n")
tn.write(b"exit\n")
tn.write(b"end\n")
tn.write(b"exit\n")
tn.write(b"write\n")

print(tn.read_all().decode('ascii'))