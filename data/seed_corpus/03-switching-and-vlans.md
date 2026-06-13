# Switching and VLANs

Switches forward frames within a LAN using a MAC address table they build by learning source addresses. A VLAN (Virtual LAN) logically segments one physical switch into multiple broadcast domains, so devices in VLAN 10 cannot reach VLAN 20 without a router or layer-3 switch. VLANs improve security and reduce broadcast traffic.

Access ports carry a single VLAN and connect to end devices. Trunk ports carry multiple VLANs between switches and use 802.1Q tagging, which inserts a 4-byte tag with the VLAN ID into each frame. The native VLAN on a trunk is untagged; mismatched native VLANs cause connectivity and security problems.

Spanning Tree Protocol (STP, 802.1D and its faster successor RSTP) prevents layer-2 loops by blocking redundant paths and electing a root bridge. Without STP, a loop floods the network with broadcasts and brings it down.

Inter-VLAN routing connects VLANs. Common methods are router-on-a-stick (one trunk to a router with subinterfaces) and a layer-3 switch with switched virtual interfaces (SVIs).

Security practices: disable unused ports, avoid using VLAN 1 for user traffic, restrict trunking to known links, and use port security to limit MAC addresses per port.

Key competency: design a multi-VLAN campus, configure trunks with 802.1Q, and explain how inter-VLAN routing and STP keep it stable.
