# Cloud Networking

Cloud networking extends traditional networking concepts into providers like Azure and AWS, and connects on-premises networks to the cloud for hybrid and multicloud designs.

The building block is a virtual network: an Azure VNet or an AWS VPC. You divide it into subnets, assign private address ranges (the same RFC 1918 rules apply), and control traffic with security rules. Azure uses Network Security Groups; AWS uses security groups and network ACLs. These act like stateful and stateless firewalls around subnets and interfaces.

Routing inside a cloud network uses route tables. Connecting networks together uses peering (VNet peering, VPC peering) for private connectivity between virtual networks. Reaching the internet uses gateways and public IPs, and egress is often controlled through a NAT gateway.

Hybrid connectivity links on-premises to cloud over an encrypted site-to-site VPN (over the internet) or a dedicated private circuit (Azure ExpressRoute, AWS Direct Connect) for higher bandwidth and lower latency. Design concerns include non-overlapping address spaces, DNS resolution across environments, and segmentation between workloads.

Key competency: design a cloud virtual network with subnets and security rules, connect it privately to other networks via peering, and link it to an on-premises site with a VPN or dedicated circuit.
