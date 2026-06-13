# Network Automation

Network automation replaces repetitive manual configuration with code, improving speed, consistency, and reliability. Instead of logging into devices one by one, an engineer defines the desired state and a tool applies it everywhere.

Core tools and skills: Python for scripting and API calls (libraries such as Netmiko and NAPALM for device access, and Nornir for orchestration), and Ansible for declarative, agentless configuration management using playbooks and inventories. YAML and Jinja2 templates render consistent configs from variables.

Modern devices expose APIs. REST APIs and increasingly model-driven interfaces (NETCONF and RESTCONF with YANG data models) let automation read and write configuration programmatically rather than scraping the command line. Infrastructure as Code applies software practices to the network: configurations live in version control (Git), changes are reviewed in pull requests, and pipelines test and deploy them.

The payoff is provisioning that used to take hours done in minutes, fewer human errors, and configurations that are auditable and repeatable. The risk is that a bad change propagates fast, so testing, dry-runs, and rollback plans matter.

Key competency: write a script or playbook that configures or audits many devices from a single source of truth, using version control and a test step before applying changes.
