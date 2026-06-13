# Network Design and Architecture

A network architect designs the big picture rather than configuring day-to-day devices. The goal is a network that is scalable, resilient, secure, and maintainable, with a roadmap for growth.

The classic enterprise design is the hierarchical three-tier model: the access layer connects end devices, the distribution layer aggregates access switches and enforces policy, and the core layer provides high-speed backbone switching. Smaller sites collapse the core and distribution into a single layer. Modern data centers use a spine-and-leaf (Clos) fabric instead, where every leaf connects to every spine for predictable low-latency, east-west traffic.

Redundancy and high availability are central: redundant links and devices, first-hop redundancy (HSRP, VRRP), redundant power and uplinks, and no single point of failure. Capacity planning provisions for growth, often sizing for a target like 15 to 30 percent headroom.

Good design documents an IP addressing plan, VLAN and segmentation strategy, routing design, and failure domains. It balances cost, performance, and complexity, and aligns with business requirements and a technology roadmap (refresh cycles, bandwidth growth, cloud adoption).

Key competency: take business and growth requirements and produce a scalable, redundant network design with a clear addressing and segmentation plan, justifying the tradeoffs.
