# basicR1.py con Python 2

import getpass
import telnetlib

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

tn.write("conf t\n")
tn.write("int l0\n")
tn.write("ip add 1.1.1.1 255.255.255.255\n")
tn.write("end\n")
tn.write("sh ip int brief\n")
tn.write("exit\n")
tn.write("write\n")

print tn.read_all()  # No need to decode from 'ascii'


