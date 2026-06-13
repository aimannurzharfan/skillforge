# Threat Detection: IDS, IPS, SIEM, and MITRE ATT&CK

An IDS (Intrusion Detection System) monitors traffic or host activity and raises alerts on suspicious behavior. An IPS (Intrusion Prevention System) sits inline and can block. Detection uses two approaches: signature-based, which matches known attack patterns and is precise but blind to novel attacks, and anomaly-based, which models normal behavior and flags deviations, catching unknown attacks at the cost of more false positives.

A SIEM (Security Information and Event Management) platform centralizes logs from across the environment, correlates events, and surfaces incidents. Analysts tune detection rules to reduce alert fatigue and triage what matters.

MITRE ATT&CK is a knowledge base of real adversary behavior, organized as tactics (the attacker's goal) and techniques (how they achieve it). Tactics run roughly in order: Reconnaissance, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact. Example techniques: T1190 Exploit Public-Facing Application (Initial Access), T1021 Remote Services (Lateral Movement), T1046 Network Service Discovery (Discovery).

Mapping detections and findings to ATT&CK lets defenders reason about an attacker's likely path and identify the single control that breaks the chain earliest.

Key competency: explain signature versus anomaly detection, map an observed finding to its ATT&CK technique and tactic, and describe how chaining techniques reveals an attack path.
