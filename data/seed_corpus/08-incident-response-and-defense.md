# Incident Response and Defensive Architecture

Incident response follows a lifecycle. The widely used NIST model has four phases: Preparation, Detection and Analysis, Containment Eradication and Recovery, and Post-Incident Activity. SANS describes six steps (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned), which map to the same idea. Preparation (playbooks, logging, access) determines how well the later phases go.

Containment buys time: isolate affected hosts, often by network segmentation, before eradicating the root cause and recovering clean systems. The post-incident review is blameless and focuses on what to change so it does not recur.

The NIST Cybersecurity Framework organizes security into five functions: Identify, Protect, Detect, Respond, Recover. It is a way to structure a security program, not a checklist of controls.

Defense in depth layers controls so no single failure is catastrophic: perimeter firewalls, network segmentation, host hardening, least-privilege access, monitoring, and backups. Network segmentation limits lateral movement; if one segment is breached, the attacker cannot freely reach the rest. Sensitive services such as databases and management interfaces should never be exposed to untrusted networks.

Key competency: walk an incident through the NIST lifecycle, explain how segmentation contains it, and place a set of controls into the five CSF functions.
