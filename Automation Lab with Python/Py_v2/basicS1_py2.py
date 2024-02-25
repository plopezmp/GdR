import getpass
import telnetlib

HOST = "172.16.0.250"
user = raw_input("Enter your telnet username: ")  # Use raw_input() for Python 2
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
tn.write("vlan 2\n")
tn.write("name Python_vlan_2\n")
# tn.write("vlan 3\n")
# tn.write("name Python_vlan_3\n")
# tn.write("vlan 4\n")
# tn.write("name Python_vlan_4\n")
# tn.write("vlan 5\n")
# tn.write("name Python_vlan_5\n")
# tn.write("vlan 6\n")
# tn.write("name Python_vlan_6\n")
tn.write("exit\n")
tn.write("end\n")
tn.write("exit\n")
tn.write("write\n")

print tn.read_all()  # No need to decode from 'ascii'
