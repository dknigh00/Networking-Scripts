### VPN.py
######*This is for [CISCO ASA] Parsing out a VPN config for Tickets or Troubleshooting.*
---
1. pip install netmiko
2. edit config variables for your ASA.
3. $ python VPN.py *PEER IP OF VPN*

#####Output

```
******************************* <Peer IP> *********************************
object-group network <LOCAL HOSTS OBJ>
 network-object object xxx       !EXT =< external IP >         INT =< INTERNAL IP >
!
object-group network <REMOTE HOSTS OBJ>
 network-object host xxx
!
access-list <VPN ACL> extended permit ip object-group <LOCAL HOSTS OBJ> object-group <REMOTE HOSTS OBJ>
!
crypto map vpn_map <map_seq> match address <VPN ACL>
crypto map vpn_map <map_seq> set connection-type bi-directional
crypto map vpn_map <map_seq> set peer <PEER IP> 
crypto map vpn_map <map_seq> set ikev1 phase1-mode main
crypto map vpn_map <map_seq> set ikev1 transform-set ESP-AES-256-SHA
crypto map vpn_map <map_seq> set security-association lifetime seconds 28800
crypto map vpn_map <map_seq> set reverse-route
!
tunnel-group <PEER IP>1 type ipsec-l2l
tunnel-group <PEER IP> general-attributes
 no accounting-server-group
 default-group-policy DfltGrpPolicy
tunnel-group <PEER IP> ipsec-attributes
 ikev1 pre-shared-key *****
 peer-id-validate req
 no chain
 no ikev1 trust-point
 isakmp keepalive disable
 no ikev2 remote-authentication
 no ikev2 local-authentication
******************************** < PEER IP > *********************************
```

---
