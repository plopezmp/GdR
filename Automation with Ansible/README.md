# Intro to Network Automation with Ansible

## Introduction
Ansible is an open-source automation tool used for configuration management, application deployment, and infrastructure orchestration. *It operates **without requiring agents** on the managed systems*, using SSH for Linux and WinRM for Windows. Configurations and tasks are defined in YAML files called playbooks, making it straightforward to describe system states and automate processes. Ansible follows a declarative approach, meaning users specify the desired outcome rather than the exact steps to achieve it.

The tool includes a large set of modules that support tasks such as managing cloud services, databases, and network devices. It is designed to be idempotent, applying changes only when necessary to maintain system consistency. Ansible can be used for both small-scale automation and managing complex infrastructures with thousands of nodes. It integrates with various DevOps tools, including Docker, Kubernetes, and cloud platforms like AWS, Azure, and GCP, making it suitable for a range of automation workflows.

Ansible is primarily written in Python. The core engine and most of its modules are developed in Python, making it lightweight and easily extensible. Additionally, Ansible relies on Python libraries such as paramiko for SSH connections and Jinja2 for templating.

## Installation notes on Fedora MV

We have created a Python environment to work with Ansible in the Fedora MV of this course. To access this environment just run 
```
workon ansible
```
To leave the environment use `deactivate`. 

Ansible is already installed in this environment the `pip` package manager (e.g. check the list of installed packages with `pip freeze`). Besides `ansible`, there are some packages installed needed to make _ssh_ connections with the nodes, and to run the examples contained in this repository. For example, `paramiko` and `ansible-pylibssh`.

### Adaptation for global configuration 
This Section is only informative and not part of the proposed exercises. 
We have made the following _twicks_:

* _Paramiko->pkey.py_
```
/home/lab/.virtualenvs/ansible/lib/python3.12/site-packages/paramiko/pkey.py
```
In `CYPHER_TABLE = {...` modification of DES part removing the string `algorithms.`. 
Must be like this:
```
"DES-EDE3-CBC": {
            "cipher": TripleDES,
            "keysize": 24,
            "blocksize": 8,
            "mode": modes.CBC,
          },
```

* `~.ssh/config` must be
  ```
  Host *
    HostKeyAlgorithms = +ssh-rsa
   # PubkeyAcceptedAlgorithms=+ssh-rsa
   # KexAlgorithms=+diffie-hellman-group-exchange-sha1
  ```

* `/etc/ssh/ssh_config.d/misshcfg.conf`
  ```
  KexAlgorithms=curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-   hellman-group-exchange-sha256,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1

  Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-cbc,3des-cbc
  ```

* `etc/ansible/ansible.cfg`
  ```
  [paramiko_connection]
  host_key_auto_add = True
  ```
  To allow `paramiko` remember the keys of the list of *ssh* servers.

* To make cryptography coding _less demanding_
  ```
  sudo update-crypto-policies --set LEGACY
  reboot
  ``` 


## Preliminaries: Network preparation
The topology we are using is the following,

<img src='figs/MIREDans.jpg' width='470'>

### R1 router
R1 is a Cisco 7200 (*c7200-adventerprisek9-mz.124-24.T5.image*)

Configuration through CLI:
```
conf t
hostname R1
int gi0/0
ip add 172.18.0.20 255.255.255.0
no sh
end
wr

conf t
ip domain-name upct
username ansible privilege 15 secret ansible

line vty 0 15
login local
transport input all
exit

enable secret cisco
line console 0
passw cisco
login 
exit

end
write memory
```

Check if `ssh` will works:
```
show ip ssh
```
ssh activation:
```
R1(config)#ip ssh time-out 60
R1(config)#crypto key generate rsa usage-keys label router-key
```
The CLI will ask for the size of the key.
The key should have `1024 bits`. Thus, we answer both questions with `1024`.

#### Notes on the CLI configuration
* `ip domain name upct` typically required for features like SSH key generation and authentication.
* `username ansible privilege 15 secret ansible`:
   - user/password _ansible/ansible_.
   - `privilege 15` gives the user **full administrative** access (equivalent to enable mode). 
* `line vty 0 15`: Configures all 16 virtual terminal lines (VTY 0-15), which are used for remote access via Telnet or SSH.
* `login local`: Requires a local user account (like ansible) for authentication.
* `transport input all`: Allows all remote access protocols (SSH, Telnet, etc.).
* `enable secret cisco`: This password is used to enter privileged EXEC mode (enable mode).

These are standard CLI lines needed for SSH connections and are also used in R2V and switchR3 configuration as it is shown below.

#### Connection to R1
1. Check R1 is reachable from Ansible host, e.g., PING to `172.18.0.20`.
2. Then make the `ssh` connection: `ssh ansible@172.18.0.20`
3. To close the connection  run `exit`.

That should open an ssh connection to R1. If not, take a second look to the steps above. Also, can the following could be tested: `ssh -oHostKeyAlgorithms=ssh-rsa ansible@172.18.0.20`.


### R2V router
This a vIOS router. The configuration is as follows:

```
conf t
hostname R2V
int gi0/0
ip add 172.18.0.21 255.255.255.0
no sh
end
wr

conf t
ip domain-name upct
username ansible privilege 15 secret ansible

line vty 0 15
login local
transport input all
exit

enable secret cisco
line console 0
passw cisco
login 
exit

end
write memory
```

Besides, we must set the keys in the router:
```
R2V(config)#ip ssh time-out 60

R2V(config)#crypto key generate rsa usage-keys label router-key
```
and answer 1024 to the two configuration questions that shows on.


### switchR3 multilayer (L2/L3) switch
Also vIOS. We would configure it as a router.

```
enable
conf t
hostname switchR3
end
sh int desc

configure terminal
 ip routing
 interface g0/0
 no switchport
 ip address 172.18.0.22 255.255.255.0
 no shutdown
 end

conf t
ip domain name upct
username ansible privilege 15 secret ansible

line vty 0 15
login local
transport input all
exit

enable secret cisco
line console 0
passw cisco
login 
exit

end
write memory
```

Besides, we must set the keys:
```
switchR3(config)#ip ssh time-out 60

switchR3(config)#crypto key generate rsa usage-keys label router-key
```
and answer 1024 to the two configuration questions that shows on.




## Examples of use
The topology we are using is as follows


