# Intro to Network Automation with Python
This lab aims to use Python programs to make a basic configuration of network nodes. The [telnetlib](https://docs.python.org/3/library/telnetlib.html) library seves to open a Telnet session and send configuration commands to the remote node.

<!---
![Alt text](MIRED.png)
-->
<img src='figs/RED1.png' width='750'>

## Atomation station
Network Automation is a docker system with linux and Ansible installed. The GNS3 appliance is in [Network Automation link](https://gns3.com/marketplace/appliances/network-automation).

The network interfaces are configured as follows:
```
#
# This is a sample network config uncomment lines to configure the network
#
# Static config for eth0
#auto eth0
#iface eth0 inet static
#	address 192.168.0.2
#	netmask 255.255.255.0
#	gateway 192.168.0.1
#	up echo nameserver 192.168.0.1 > /etc/resolv.conf
# DHCP config for eth0
 auto eth0
 iface eth0 inet dhcp
```

#### R1
We need to set an IP to 

```
conf t
hostanme R1 
enable password cisco
username plm password cisco

int g0/0
ip add 192.168.122.251 255.255.255.0
no sh
exit
line vty 0 4
login local
transport input all
end
```

