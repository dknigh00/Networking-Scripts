#/usr/bin/python
# Author:   Derek Knight
# Title:    SSH ASA VPN Parser
# Version:  1.0

# Imports
from netmiko import ConnectHandler
import sys

# instructions
#####################
# $ pip install netmiko
# $ python VPN.py <VPN PEER IP>
#####################


def main():
    ########################################
    # Variable Declaration - SSH Connections  
    ########################################
    BOULDER_ASA = {
    'device_type':  'cisco_asa',
    'ip':           'x',  	#FIREWALL IP 
    'username':     'xx',	#USERNAME
    'password':     'xx',	#PASSWORD
    'port':          22,
    'secret':       'x', 	#ENABLE PASSWORD
    'verbose':       False,
    }
    all_devices = [BOULDER_ASA]
    peer_ip = str(sys.argv[1])         
    vpn_info = []
    ########################################


    vpn_info.append("\n" + '{:*^80}'.format(" " + peer_ip + " "))
    for x in all_devices:
        net_connect = ConnectHandler(**x)
        seq_num = parse_map(net_connect.send_command("show run | in peer " + peer_ip))
        output = net_connect.send_command("sh run all | in map " + seq_num)
        crypto_map = output
        output = net_connect.send_command("show run all tunnel-group " + peer_ip)
        tunnel_group = output
        acl = acl_name(net_connect.send_command("sh run | in map " + seq_num + " match"))
        output = net_connect.send_command("sh run | in access-list " + acl)
        local, remote = parse_multi_acl(output)
        access_list = output
        for l_obj in local:
            output = net_connect.send_command("sh run object-group id " + l_obj)
            output = nat_lookup(output, net_connect)  # Add IP Maps
            vpn_info.append(output + "\n!")
        for r_obj in remote:
            output = net_connect.send_command("sh run object-group id " + r_obj)
            vpn_info.append(output + "\n!")
        vpn_info.append(access_list + "\n!\n" + crypto_map + "\n!\n" + tunnel_group)
        vpn_info.append('{:*^80}'.format(" " + peer_ip + " "))
        print '\n'.join(vpn_info)


def parse_map(x):
    map = x.split(' ')
    return map[3]


def acl_name(x):
    acl_name = x.split(' ')
    return acl_name[6]


def parse_multi_acl(x):
    l, r = [], []
    if x.__contains__('\n'):
        for line in x.split('\n'):
            l.append(local_object(line))
            r.append(remote_object(line))
        set1 = set(l)  # Removes
        l = list(set1)  # Duplicates
        set1 = set(r)  # Removes
        r = list(set1)  # Duplicates
    else:
        l.append(local_object(x))
        r.append(remote_object(x))
    return l, r


def local_object(x):
    acl_name = x.split(' ')
    return acl_name[6]


def remote_object(x):
    acl_name = x.split(' ')
    return acl_name[8]


def nat_lookup(x, y):
    map = list(x.split("\n"))
    map2 = []
    map2.append(map.pop(0))  # remove the object name
    for obj_nat in map:
        nat_out = y.send_command("sh nat | in " + obj_nat.split(' ')[3] + " ")
        nat_in = y.send_command("sh run obj in | in network " + nat_out.split(' ')[6] + " ")
        nat_ext = y.send_command("sh run obj in | in network " + nat_out.split(' ')[7] + " ")
        inter =  nat_in.split(" ")[4]
        exter =  nat_ext.split(" ")[4]
        map2.append("%-45s !EXT =%-20s INT =%10s" % (obj_nat, exter, inter))
    print list(map2)
    return '\n'.join(map2)


if __name__ == "__main__": main()
