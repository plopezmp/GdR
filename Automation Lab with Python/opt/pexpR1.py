#!/home/lab/.virtualenvs/gns3/bin/python -W ignore

import pexpect
import getpass

HOST = "172.18.0.251"
user = input("Enter your telnet username: ")
password = getpass.getpass()

tn = pexpect.spawn(f"telnet {HOST}")

tn.expect("Username:")
tn.sendline(user)

tn.expect("Password:")
tn.sendline(password)

# Enter enable mode
tn.expect(r">")  # Expect user mode prompt
tn.sendline("enable")

tn.expect("Password:")
tn.sendline("cisco")  # Enable password

tn.expect(r"#")  # Expect privileged exec mode

# Configure interface Loopback0
tn.sendline("conf t")
tn.expect(r"#")
tn.sendline("int l0")
tn.expect(r"#")
tn.sendline("ip add 1.1.1.1 255.255.255.255")
tn.expect(r"#")
tn.sendline("end")

tn.expect(r"#")
tn.sendline("sh ip int brief")
tn.expect(r"#")

# Save configuration
tn.sendline("write")
tn.expect(r"#")

print(tn.before.decode('ascii'))  # Print output before last expect

tn.close()
