# IP Addressing and Subnetting

An IPv4 address is 32 bits, written as four octets (for example 192.168.10.20). A subnet mask separates the network portion from the host portion. CIDR notation expresses the mask as a prefix length, so /24 means the first 24 bits are the network and the last 8 are hosts.

A /24 gives 256 addresses, 254 usable (one for the network address, one for broadcast). Each step changes the count: /25 is 128 addresses, /26 is 64, /27 is 32, /30 is 4 (2 usable, common for point-to-point links).

Private ranges (RFC 1918) are not routable on the internet: 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. These are used inside organizations and translated to public addresses by NAT.

VLSM (Variable Length Subnet Masking) lets you size subnets to need rather than wasting addresses. A campus block such as 172.18.0.0/20 can be carved into department subnets of different sizes: a /24 for 200 workstations, a /26 for a smaller team, a /30 for a router link. Always allocate from largest to smallest to avoid overlap.

To subnet: decide how many subnets or hosts you need, choose the prefix length that provides it, then list the network address, first usable, last usable, and broadcast for each block.

Key competency: given a base network and a set of host requirements, design a VLSM scheme with no overlaps and minimal waste.
