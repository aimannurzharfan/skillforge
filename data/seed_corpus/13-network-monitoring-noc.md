# Network Monitoring and NOC Operations

A Network Operations Center (NOC) keeps networks running, often around the clock. NOC engineers are the first responders to alerts: they detect, triage, and either resolve or escalate issues, and they track everything through tickets.

Monitoring collects health and performance data. SNMP polls devices for metrics like interface utilization, CPU, memory, and errors. Syslog streams event messages. NetFlow and similar tell you who is talking to whom and how much. Platforms (for example Zabbix, PRTG, SolarWinds, or cloud-native monitors) visualize this and raise alerts when thresholds are crossed or a device stops responding.

Good monitoring defines baselines so anomalies stand out, and tunes thresholds to avoid alert fatigue. Alerts feed dashboards and notification channels. When something breaks, the engineer triages by severity and impact, follows a runbook, and escalates if it is beyond first-line resolution.

Operations run to service level agreements (SLAs) that define targets for uptime, response time, and resolution time. Metrics like mean time to detect and mean time to resolve measure how well the NOC performs. Clear documentation, runbooks, and handoffs keep a 24/7 operation consistent across shifts.

Key competency: set up monitoring for key metrics, define sensible alert thresholds and baselines, and triage an incoming alert by severity, following a runbook to resolve or escalate.
