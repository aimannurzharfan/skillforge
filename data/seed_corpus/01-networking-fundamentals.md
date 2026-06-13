# Networking Fundamentals

Modern networks are described by two layered models. The OSI model has seven layers: Physical, Data Link, Network, Transport, Session, Presentation, and Application. The TCP/IP model collapses these into four: Link, Internet, Transport, and Application. Most practical work happens at the Network layer (IP addressing and routing), the Transport layer (TCP and UDP), and the Application layer.

TCP is connection-oriented and reliable: it uses a three-way handshake (SYN, SYN-ACK, ACK), sequence numbers, and retransmission. UDP is connectionless and lightweight, used for DNS, DHCP, VoIP, and streaming where speed matters more than guaranteed delivery.

Common ports a network professional should recognize: 22 SSH, 23 Telnet (insecure, avoid), 25 SMTP, 53 DNS, 80 HTTP, 443 HTTPS, 3389 RDP, 445 SMB, 21 FTP, 161 SNMP, 3306 MySQL, 1521 Oracle.

The data flow from host to host: an application produces data, the transport layer segments it and adds ports, the network layer adds source and destination IP addresses, and the data link layer adds MAC addresses for the local hop. Routers operate at the network layer and forward between networks; switches operate at the data link layer and forward within a network using MAC tables.

Key competencies: read a packet capture in Wireshark, identify the protocol and port, and explain whether traffic is expected or anomalous.
