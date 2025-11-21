# Network Configurations (Expanded - Generic Corporate IT)

## Network Topology Overview
The corporate network follows a three-tier architecture designed for scalability, security, and performance.  

### 1. Core Layer
- Hosts core routing and switching infrastructure connecting data centers, headquarters, and branch offices.  
- Provides high-speed backbone connectivity and redundancy between all network segments.  
- Manages inter-VLAN routing and Layer 3 failover.  

### 2. Distribution Layer
- Aggregates traffic from access switches and enforces network policies.  
- Implements Quality of Service (QoS), VLAN routing, and network segmentation.  
- Connects to DMZ for external-facing applications and to the core routers for upstream traffic.  

### 3. Access Layer
- Provides network access to end-user devices, printers, and VoIP phones.  
- Includes Wi-Fi access points and wired ports managed via centralized controller.  

### 4. Data Center and DMZ
- Hosts mission-critical servers such as email, database, web, and VPN gateways.  
- DMZ isolates external-facing services like web applications, proxy, and mail relay.  

### 5. Remote Offices and VPN
- Employees and branch offices connect securely through VPN gateways using Cisco AnyConnect or equivalent clients.  
- VPN tunnels utilize SSL/TLS encryption with multifactor authentication.  

---

## Network Infrastructure Inventory

| Component | Hostname | Purpose | Location | Managed By |
|------------|-----------|----------|-----------|-------------|
| Core Router | core-router-01 | Routes inter-VLAN and external traffic | Data Center | Network Operations |
| Core Switch | core-switch-01 | High-speed switch backbone | Data Center | Network Operations |
| Distribution Switch | dist-switch-01 | Aggregates access traffic | HQ | Network Team |
| Firewall | fw-gateway-01 | Filters inbound/outbound network traffic | DMZ | Security Operations |
| VPN Gateway | vpn-gateway-01 | Provides remote user VPN access | HQ | Network Team |
| Email Server | mail-server-01 | Handles Exchange/SMTP relay | Data Center | IT Messaging |
| Web Proxy | proxy-server-01 | Manages internet access and content filtering | DMZ | Security Operations |
| DNS Server | dns-server-01 | Resolves internal hostnames | HQ | Infrastructure Team |
| DHCP Server | dhcp-server-01 | Assigns dynamic IP addresses | HQ | Infrastructure Team |
| Active Directory Controller | ad-server-01 | Authentication and policy enforcement | HQ | IT Operations |
| File Server | file-server-01 | Hosts shared drives and departmental folders | HQ | IT Storage |
| Print Server | print-server-01 | Manages network printer queues | HQ | IT Support |
| SCCM Server | sccm-server-01 | Device management and patch deployment | Data Center | Endpoint Team |
| Backup Server | backup-server-01 | Performs daily system and file backups | Data Center | Infrastructure |
| Database Server | db-server-01 | Hosts SQL-based enterprise databases | Data Center | Database Admins |
| Web Application Server | webapp-server-01 | Runs intranet and portal applications | DMZ | Application Team |
| Load Balancer | lb-server-01 | Distributes web and application traffic | DMZ | Network Operations |
| Wireless Controller | wlc-01 | Centralized management of Wi-Fi APs | HQ | Network Team |
| Wi-Fi Access Point | ap-hq-01 | Provides corporate wireless coverage | HQ | Network Team |
| Branch Router | branch-router-01 | Routes remote office traffic | Branch Office | Network Team |
| Network Storage (NAS) | nas-storage-01 | High-capacity storage for backups | Data Center | Storage Admin |
| Proxy Cache Server | proxy-cache-01 | Caches frequent web content | DMZ | Security Operations |
| Monitoring Server | monitor-server-01 | Network performance and uptime monitoring | HQ | Infrastructure Team |
| SIEM Server | siem-server-01 | Security log aggregation and threat detection | Data Center | Security Operations |
| Remote Access Gateway | remote-gateway-01 | Provides RDP access to internal systems | DMZ | IT Admin |
| Collaboration Server | collab-server-01 | Hosts Teams/Zoom integration modules | Data Center | IT Collaboration |
| Patch Management Server | patch-mgmt-01 | Controls OS and application updates | HQ | Endpoint Team |
| Cloud Gateway | cloud-connector-01 | Manages hybrid connectivity to cloud | Data Center | Cloud Admin |
| Version Control Server | vcs-server-01 | Hosts Git repositories for development | HQ | Development Team |

---

## Connectivity Summary

### VLAN Overview
| VLAN ID | Department | Function |
|----------|-------------|-----------|
| VLAN 10 | IT Operations | Admin devices and servers |
| VLAN 20 | Finance | Secure access to ERP and SAP systems |
| VLAN 30 | HR | HRMS and internal portal connectivity |
| VLAN 40 | General Users | Corporate end-user traffic |
| VLAN 50 | Guest Network | Isolated access for visitors |
| VLAN 60 | Voice | VoIP telephony and call manager |
| VLAN 70 | Security | Firewall management and monitoring tools |

### Routing and Segmentation
- Static and dynamic routing managed by OSPF protocol across all routers.  
- VLAN traffic segregated by distribution switches and routed via core layer.  
- DMZ separated through dual-firewall architecture ensuring one-way inbound flow.  
- External DNS and public web traffic routed via proxy gateways and load balancers.  

### DNS & DHCP Integration
- DHCP dynamically assigns IPs to clients per VLAN.  
- DNS resolves internal domains (`corp.local`, `intranet.local`) and external requests via forwarders.  
- Redundant DNS/DHCP servers configured for failover and high availability.  

---

## Network Security Summary

### Firewall Architecture
- Perimeter firewalls separate DMZ, internal, and external traffic.  
- Policies restrict outbound access to approved ports and protocols.  
- Logging and alerts integrated with central SIEM system.  

### Intrusion Detection & Prevention (IDS/IPS)
- Network traffic continuously analyzed for threats.  
- Signatures auto-updated daily from vendor repository.  
- Alerts automatically forwarded to SOC for investigation.  

### Proxy & Content Filtering
- All internet-bound traffic passes through secure web proxy.  
- HTTPS inspection and malware scanning enabled.  
- URL categories defined per department (e.g., Development, HR, Finance).  

### Network Segmentation
- Critical systems (AD, Email, Database) reside in isolated zones.  
- User networks separated by VLAN and access control lists (ACLs).  
- DMZ hosts public-facing apps with strict firewall control.  

### VPN Security
- Two-factor authentication required for VPN users.  
- SSL/TLS encryption enforced for all sessions.  
- Endpoint compliance verified prior to granting access.  

### Monitoring and Alerting
- Network monitored 24x7 via centralized NOC.  
- Automatic alerts for latency, downtime, and unauthorized access attempts.  
- Incident tickets created automatically in ITSM platform.  

---
