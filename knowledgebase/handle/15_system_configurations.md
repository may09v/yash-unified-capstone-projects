# System Configurations (Expanded - Generic Corporate IT)

## 1. Overview
This document defines the standard configurations for core IT systems, applications, databases, and infrastructure components.  
It ensures consistency, reliability, and maintainability across all environments — including production, testing, and development.  
All configurations are managed under a version-controlled **Configuration Management Database (CMDB)** and updated through approved **Change Management** processes.

---

## 2. Server Configuration Standards

| Parameter | Description |
|------------|--------------|
| **OS Baseline** | Windows Server 2022 / Red Hat Enterprise Linux 9 |
| **Naming Convention** | [Dept]-[Function]-[Location]-[Number] (e.g., FIN-DB-DC01) |
| **Patch Policy** | Monthly patch cycle via SCCM (2nd Saturday) |
| **Antivirus** | Microsoft Defender ATP / CrowdStrike Falcon |
| **Backup Tool** | Veeam Backup & Replication (Daily Incremental, Weekly Full) |
| **Monitoring** | SolarWinds Orion / Datadog |
| **Time Sync** | NTP via Domain Controller |
| **User Access** | AD-based group membership only |
| **Local Admins** | Restricted to IT Infrastructure Team |

### Dependencies
- Backup → Veeam Server → Storage Repository (NAS01)
- Monitoring → SolarWinds Agent → Central Dashboard
- Patching → SCCM → Windows Update Repository

---

## 3. Network Configuration Summary

| Component | Configuration Details |
|------------|-----------------------|
| **Core Switches** | Cisco Catalyst (Layer 3) |
| **Edge Switches** | HP Aruba (Layer 2) |
| **Routers** | Cisco ISR with dual redundant uplinks |
| **Firewall** | FortiGate HA Cluster (Active-Passive) |
| **VPN Gateway** | Cisco ASA (SSL VPN, LDAP Integration) |
| **Wireless Controllers** | Cisco 9800 Series |
| **DNS Servers** | Active Directory Integrated DNS |
| **DHCP Servers** | Redundant DHCP Failover Config |
| **Network Segmentation** | VLAN-based isolation for HR, Finance, IT, Guest |
| **Proxy** | Cloud-based Secure Web Gateway |

### Dependencies
- VPN → Cisco ASA → LDAP → AD Authentication  
- DNS → AD Replication → Domain Controllers  
- Internet Access → Proxy → Firewall Rules → ISP Uplink  

---

## 4. Database Configurations

| Database | Engine | Purpose | Backup Frequency | Authentication |
|-----------|---------|----------|------------------|----------------|
| **SQLServer01** | MS SQL 2019 | ERP, ServiceNow backend | Daily full | Windows Auth |
| **Postgres01** | PostgreSQL 15 | Jira & Confluence | Daily incremental | Local User Auth |
| **MongoDB01** | MongoDB 7 | Web Apps, Analytics | Every 6 hours | Key-based Auth |
| **OracleDB01** | Oracle 19c | HRMS System | Daily full | Role-based Auth |

### Dependencies
- ERP → SQLServer01 → SMTP (Mail Notifications)  
- Jira → Postgres01 → LDAP (SSO Login)  
- WebApp → MongoDB01 → REST API Layer  
- HRMS → OracleDB01 → SFTP (Payroll Export)  

---

## 5. Application Stack Configurations

| Application | Platform | Hosting | Authentication | Monitoring | Notes |
|--------------|-----------|-----------|----------------|-------------|--------|
| **ERP System** | .NET Core | IIS on AppServer01 | AD SSO | Datadog Agent | Connected to SQLServer01 |
| **Jira Software** | Java (Tomcat) | AppServer02 | Okta SSO | Nagios | Uses Postgres01 DB |
| **ServiceNow** | SaaS Cloud | Hosted by Vendor | SAML | Built-in | Linked with AD via SCIM |
| **HRMS Portal** | Java EE | WebServer02 | LDAP | SolarWinds | Uses OracleDB01 |
| **CRM (Salesforce)** | SaaS | Cloud-hosted | OAuth | Built-in | Integrates with Outlook |
| **Intranet Portal** | SharePoint Online | Microsoft 365 | AD | Microsoft 365 Admin | Uses OneDrive Backend |
| **Backup Console (Veeam)** | Windows Service | BackupServer01 | AD | SolarWinds | Linked with NAS Storage |

### Dependencies
- ERP → SQL Server → SMTP → Backup  
- Jira → Postgres → Email Notifications → LDAP  
- HRMS → OracleDB → SFTP → Payroll Export  
- CRM → Outlook → API Integration  

---

## 6. Security Configurations

| Component | Configuration | Description |
|------------|----------------|--------------|
| **Antivirus** | Microsoft Defender + CrowdStrike Falcon | Managed centrally through cloud console |
| **Firewall** | FortiGate Cluster | Intrusion Prevention + App Control + VPN |
| **Endpoint Encryption** | BitLocker (Windows) / FileVault (Mac) | Enforced by MDM policy |
| **Web Filtering** | Proxy Gateway | URL category and malware filtering |
| **MFA** | Okta + Microsoft 365 | Enforced for all external logins |
| **Email Security** | Proofpoint | Spam, phishing, and DLP protection |
| **DLP Policies** | Configured via Microsoft Purview | Restricts file transfers to external domains |

### Dependencies
- Email → Proofpoint → Exchange → AD User Authentication  
- VPN → FortiGate → AD → MFA (Okta)  
- Endpoint → Defender → SCCM → Patch Compliance Dashboard  

---

## 7. Cloud & Virtualization Settings

| Environment | Platform | Configuration | Managed By |
|--------------|-----------|----------------|-------------|
| **Azure Cloud** | Azure Resource Manager | 6 Resource Groups (Prod, Dev, Test, Backup, Monitoring, Security) | CloudOps Team |
| **VMware vCenter** | v8.0 Cluster | 20 Virtual Machines with HA | Infrastructure Team |
| **Storage Accounts** | Azure Blob + On-Prem NAS | Lifecycle policy: 90 days active → cold tier | Storage Team |
| **Virtual Network (VNet)** | 3 Subnets: App, DB, Mgmt | Enforced NSGs | Cloud Security |
| **Azure AD Sync** | Every 30 mins | Syncs On-Prem AD to Azure | Identity Team |

### Dependencies
- Azure VMs → vCenter Templates → SCCM → Patch Baseline  
- Storage → Veeam → Azure Blob (Offsite Backup)  
- Azure AD → On-Prem AD → MFA → Okta SSO  

---

## 8. Backup & Disaster Recovery

| Component | Backup Frequency | Retention | Tool | Storage |
|------------|------------------|------------|-------|----------|
| **File Servers** | Daily Incremental / Weekly Full | 60 Days | Veeam | NAS01 + Cloud Archive |
| **Databases** | Daily Full / Hourly Log | 30 Days | Veeam Agent | NAS02 |
| **Applications (ERP, Jira)** | Weekly Image Backup | 30 Days | Veeam | Azure Blob |
| **VMs** | Snapshot every 6 hours | 14 Days | VMware vCenter | On-Prem |
| **Email (M365)** | Continuous | 30 Days | Built-in Retention | Microsoft Cloud |

### Dependencies
- Backup → NAS → Azure Blob Archive  
- DR → VM Replication → Secondary Data Center  
- Alerts → Veeam Monitor → IT Operations |

---

## 9. Configuration Management & Documentation

### Change Control Process
- All configuration changes must follow the **ITIL Change Management process**.  
- Requests are logged in **ServiceNow Change Module**.  
- Changes undergo **technical peer review** and **CAB approval** before implementation.  
- Post-change validation required before closing ticket.

### Configuration Tracking
- Server & Network configs stored in **CMDB (ServiceNow)**.  
- Version control for scripts and templates via **GitHub Enterprise**.  
- Quarterly configuration audits performed by the **Infrastructure Team**.

### Tools Used
- **ServiceNow CMDB** – Asset and dependency mapping  
- **GitHub Enterprise** – Configuration version control  
- **SolarWinds** – Auto-discovery and monitoring configuration  
- **Datadog** – Real-time application and service dependency mapping  

---

## 10. Summary
All system configurations are standardized to ensure security, compliance, and scalability.  
Interdependencies between servers, databases, and applications are documented and continuously monitored through CMDB integration.  
Change control, version tracking, and automation tools ensure consistent configuration management across the enterprise environment.

---
