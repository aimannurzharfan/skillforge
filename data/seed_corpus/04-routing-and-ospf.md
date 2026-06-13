# Routing and OSPF

Routers move packets between networks using a routing table. Routes come from three sources: directly connected networks, static routes configured by hand, and dynamic routes learned from a routing protocol. When multiple routes to the same destination exist, the router prefers the longest prefix match, then administrative distance, then metric.

Static routing is simple and predictable but does not scale or adapt to failures. Dynamic routing protocols exchange information automatically. OSPF (Open Shortest Path First) is a link-state interior gateway protocol widely used in enterprises.

OSPF builds a map of the network by flooding link-state advertisements, then runs the Dijkstra shortest-path algorithm to compute the best routes. Its metric is cost, derived from interface bandwidth. OSPF groups routers into areas to limit flooding; area 0 is the backbone, and all other areas connect to it. Single-area OSPF is common in smaller designs.

Routers form adjacencies (neighbor relationships) before exchanging routes, and they must agree on parameters such as area, hello and dead timers, and authentication. OSPF converges quickly after a topology change because each router recalculates from the updated map.

Key competency: configure single-area OSPF across several routers, verify neighbor adjacencies and the routing table, and explain how OSPF chooses a path and reconverges after a link goes down.
