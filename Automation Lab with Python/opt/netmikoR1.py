#!/home/lab/.virtualenvs/gns3/bin/python

from netmiko import ConnectHandler
import getpass

HOST = "172.18.0.251"
user = input("Enter your telnet username: ")
password = getpass.getpass()

device = {
    "device_type": "cisco_ios_telnet",
    "host": HOST,
    "username": user,
    "password": password,
    "secret": "cisco",  # Enable password
    "global_delay_factor": 2,  # Helps with slow response times
    "timeout": 10,  # Increases timeout for network response
}

net_connect = ConnectHandler(**device)

# Enter enable mode
net_connect.enable()

# Configure interface Loopback10
commands = [
    "int l10",
    "ip address 10.10.10.10 255.255.255.255",
    "exit",
]

output = net_connect.send_config_set(commands)
print(output)

# Show interface status
print(net_connect.send_command("show ip interface brief"))

# Save the configuration (using `send_command_timing` to avoid prompt detection issues)
net_connect.send_command_timing("write memory")

net_connect.disconnect()
