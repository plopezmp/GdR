# Intro to Network Automation with Ansible

## Introduction
Ansible is an open-source automation tool used for configuration management, application deployment, and infrastructure orchestration. *It operates **without requiring agents** on the managed systems*, using SSH for Linux and WinRM for Windows. Configurations and tasks are defined in YAML files called playbooks, making it straightforward to describe system states and automate processes. Ansible follows a declarative approach, meaning users specify the desired outcome rather than the exact steps to achieve it.

The tool includes a large set of modules that support tasks such as managing cloud services, databases, and network devices. It is designed to be idempotent, applying changes only when necessary to maintain system consistency. Ansible can be used for both small-scale automation and managing complex infrastructures with thousands of nodes. It integrates with various DevOps tools, including Docker, Kubernetes, and cloud platforms like AWS, Azure, and GCP, making it suitable for a range of automation workflows.

Ansible is primarily written in Python. The core engine and most of its modules are developed in Python, making it lightweight and easily extensible. Additionally, Ansible relies on Python libraries such as paramiko for SSH connections and Jinja2 for templating.

## Installation notes on Fedora VM

We have set up a Python environment for working with Ansible in the Fedora VM used in this course. To access this environment, simply run:
```
workon ansible
```
To exit the environment, use `deactivate`. 

Ansible is already installed in this environment via the `pip` package manager (e.g., you can check the list of installed packages with `pip freeze`). In addition to ansible, other required packages are installed to enable SSH connections with the nodes and to run the examples in this repository. For instance, `paramiko` and `ansible-pylibssh` are included.

### Adaptation for global configuration 
This Section is only informative and not part of the proposed exercises. 
We have made the following _twicks_:

* **Paramiko** -> `pkey.py`
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

* `~.ssh/config` **adjustements**
  ```
  Host *
    HostKeyAlgorithms = +ssh-rsa
   # PubkeyAcceptedAlgorithms=+ssh-rsa
   # KexAlgorithms=+diffie-hellman-group-exchange-sha1
  ```

* `/etc/ssh/ssh_config.d/misshcfg.conf` **settings**

Specific algorithms for key exchange and encryption have been defined.
  ```
  KexAlgorithms=curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-   hellman-group-exchange-sha256,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1

  Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-cbc,3des-cbc
  ```

* `etc/ansible/ansible.cfg` **settings**
  ```
  [paramiko_connection]
  host_key_auto_add = True
  ```
  To allow `paramiko` remember the keys of the list of *ssh* servers.

* **Reducing cryptographic overhead**
  The following command was executed to make cryptographic operations less demanding:
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

These CLI commands are essential for enabling SSH access and are also used for the **R2V** and **switchR3** configuration, as shown below.

#### Connecting to R1
1. Ensure R1 is reachable from the Ansible host by **pinging** `172.18.0.20`.
2. Establish an SSH connection with: `ssh ansible@172.18.0.20`
3. To close the connection, type `exit`.

That should open an ssh connection to R1. If not, take a second look to the steps above. Also, can the following could be tested: `ssh -oHostKeyAlgorithms=ssh-rsa ansible@172.18.0.20`.


### R2V router
This is a vIOS router with the following configuration.

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

Besides configuring the router, we need to generate the SSH keys.
```
R2V(config)#ip ssh time-out 60

R2V(config)#crypto key generate rsa usage-keys label router-key
```
and answer 1024 to the two configuration questions that shows on.


### switchR3 (multilayer switch)
This is a vIOS switch, configured to function as a router.

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

In addition to the general setup, SSH keys must also be generated.
```
switchR3(config)#ip ssh time-out 60

switchR3(config)#crypto key generate rsa usage-keys label router-key
```
and answer 1024 to the two configuration questions that shows on.


## Ansible inventory and playbook files
Before running Ansible on the network devices, we need to set up the environment properly.

Two main files are required:
* **inventory** file
* **playbook** file

It is advisable to save these files in the same directory, _e.g._ `Ansible_projects`, similar to the one in the Fedora VM.

### Inventory file
The inventory file contains relevant information about each node in the network.

```
[Routers]
R1 ansible_host=172.18.0.20
R2V ansible_host=172.18.0.21

[Switches]
switchR3 ansible_host=172.18.0.22

[all:vars]
ansible_network_os=ios
ansible_user=ansible
ansible_password=ansible
ansible_ssh_pass=ansible
ansible_become=true
ansible_become_method=enable
ansible_become_password=cisco
```
The **pattern names** (_e.g._, `Routers`) allow you to target specific sets of devices when running commands.

The filename of the inventory file is configurable. For example, we can name it `hosts`. It is important to save this file in the same directory as the playbook .yml files.

The `all:vars` pattern in the Ansible inventory file is used to define global variables that apply to all devices listed in the inventory.

* Centralized authentication: The `ansible_user`, `ansible_password`, and `ansible_ssh_pass` variables ensure that all devices use the same SSH credentials.
* Network automation settings:
  - `ansible_network_os=ios` tells Ansible that the devices use Cisco IOS, so it applies the correct network modules.
  - `ansible_become=true` and `ansible_become_method=enable` allow privilege escalation, needed for executing commands that require administrative rights.
  - `ansible_become_password=cisco` provides the password for privilege escalation (equivalent to entering `enable` mode in Cisco CLI).

**Note:** The file `ansible.cfg` tha is in the `Ansible_projects` directory is required to easy the automation running the scripts. Contains two lines:
```
[defaults]
host_key_checking = False
```
Ansible will not prompt for confirmation when connecting to a new host via SSH. Without this setting, Ansible would require user confirmation the first time it connects to a device, which could disrupt automated workflows.


### Playbook file
Ansible is **declarative** which means we just tell what we want and not how to make it. The Playbook file has a structure of three mandatory parts:
1. **Header: YAML Document Declaration**

   `---`
   
   This is the YAML document indicator that marks the beginning of the playbook.

2. **Play**
   A play defines a set of tasks to be executed on specified hosts. A play is marked with `-`, indicating the start of a new play. Every playbook usually contains one or more plays.

   Each play has the following structure:
   ```
   - name: Play name (optional but recommended)
     hosts: target hosts (e.g., 'all', 'web_servers', 'localhost')
     gather_facts: yes/no (optional, default is 'yes')
     connection: (optional, default is 'ssh')
     tasks:
       # List of tasks to run
   ```
   **Key Fields:**
   * `name`: Descriptive name of the play (optional but recommended).
   * `hosts`: Defines the target machines or groups of machines (from your inventory).
   * `gather_facts`: Determines whether to gather system facts before executing tasks (default is yes).
   * `connection`: Defines the connection type to use (e.g., ssh, network_cli).
   * `become`: Indicates whether to escalate privileges (e.g., using sudo).

3. **Tasks**
   A task represents a unit of work to be performed. Each task is **associated with a specific Ansible module** that is responsible for performing an action (like configuring a device, installing a package, etc.).
   
   ```
   tasks:
     - name: Task description
       module_name:
         module_parameters
   ```
   * `name`: A description of what the task does (optional but helpful for readability).
   * `module_name`: The Ansible module being used (e.g., yum, ios_command, file, copy).
   * `module_parameters`: The parameters passed to the module (like the package name, configuration settings, etc.).


#### Optional parts
There are other **optional** parts in the playbook, such as 
* **handlers:** part, which are special tasks that only run when notified by other tasks. They are typically used for tasks that need to be run only when something changes (e.g., restarting a service after a configuration change).
* **vars:** Variables can be defined to make the playbook more flexible and reusable. Variables can be defined in several places: directly in the playbook, in separate variable files, or passed at runtime.
* **defaults:** A defaults section can be used to define default variables that can be overridden.
* **include:** If there are a large number of tasks or configurations, is it possible to split them into separate files and include them within a playbook.

#### Identation
Indentation is extremely important in YAML files, including Ansible playbooks. YAML uses indentation to define the structure and hierarchy of the data, so the correct indentation is critical to ensure that the file is parsed and executed correctly.

* Indentation defines structure
* Use **spaces, no tabs**
* Incorrect identation causes errors
* **Consistency**: identation with the same number of spaces (e.g. 2 spaces) 

### Example of playbook: `configure_router.yml`

#### Header and Play
```
---
- name: Configure interface g1/0 on the router
  hosts: R1
  gather_facts: no
  connection: network_cli
  tasks:
```
* `name:` This is the description of the playbook. It explains the purpose of the playbook.
* `hosts:` Specifies the target hosts to which the playbook will be applied. Here, the playbook will target the host named R1, which is defined in the Ansible inventory.
* `gather_facts:` When set to no, Ansible will not collect system facts (like OS version, memory, etc.). This can speed up the execution of the playbook when we don't need this information.
* `connection:` Defines the connection type to the target devices. In this case, it uses `network_cli`, which is suitable for network devices like routers, switches, and firewalls. It indicates that Ansible will use CLI commands for configuration.

#### Tasks
**First Task:** Configure Interface
```
    - name: Configure interface g1/0
      ios_command:
        commands:
          - configure terminal
          - interface GigabitEthernet1/0
          - ip address 192.168.2.10 255.255.255.0
          - no shutdown
          - end
          - wr
      register: output
```
* `name:` This is a description of the task. This task will configure the `GigabitEthernet1/0` interface on the router.
* `ios_command: This module is specifically used for running commands on Cisco IOS devices (routers and switches). It allows you to send configuration commands to the router.
* `register: output`  stores the result of the command execution (including the output) into a variable named `output`. This will be used in a later task to display the output.

**Second Task:** Display Command Output
```
    - name: Display command output
      debug:
        var: output.stdout_lines
```

* `debug:` The debug module is used to print information to the terminal. Here, it’s used to display the contents of the output.stdout_lines variable.
   - `var: output.stdout_lines` This specifies the output from the previous task. The `stdout_lines` attribute contains the output from the commands in a list format. This will display the commands' responses from the router.



## Examples of use
To test Ansible open a Terminal and run some of these playbooks:

```
ansible-playbook -i hosts configure_router.yml
ansible-playbook -i hosts unconfigure_router.yml
ansible-playbook -i hosts run_commands.yml
ansible-playbook -i hosts mtu.yml
ansible-playbook -i hosts uptime.yml
ansible-playbook -i hosts arp.yml
```
We pass the inventory file with the `-i` parameter and the playbook file.




