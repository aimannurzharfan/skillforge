# NAT, ACLs, and Firewalls

NAT (Network Address Translation) maps private internal addresses to public addresses so internal hosts can reach the internet. Static NAT is a one-to-one mapping. Dynamic NAT uses a pool. PAT (Port Address Translation, also called NAT overload) maps many internal hosts to one public address by tracking port numbers, which is what most home and office networks use.

ACLs (Access Control Lists) filter traffic by matching criteria and permitting or denying it. Standard ACLs match source address only. Extended ACLs match source and destination address, protocol, and ports, so they are far more precise. ACLs are processed top to bottom, first match wins, and there is an implicit deny at the end, so order matters and you must explicitly permit what you need.

Apply ACLs close to the source for extended lists to drop unwanted traffic early, and remember direction (inbound or outbound on an interface).

Firewalls enforce policy between security zones. Stateful firewalls track connection state and allow return traffic for established sessions automatically. Next-generation firewalls add application awareness, intrusion prevention, and identity. The principle of least privilege applies: deny by default, permit only what is required.

Key competency: write an extended ACL that permits required services and denies the rest, configure PAT for internet access, and explain placement and direction.
