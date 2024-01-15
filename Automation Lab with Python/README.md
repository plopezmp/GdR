# Intro to Network Automation with Python

<!---
![Alt text](MIRED.png)
-->
<img src='figs/RED1.png' width='750'>

## Atomation station configuration
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


