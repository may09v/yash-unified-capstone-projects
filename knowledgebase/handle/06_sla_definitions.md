# SLA Definitions (Expanded - Generic Corporate IT)

## 1. Overview
This Service Level Agreement (SLA) defines the timeframes and commitments for resolving IT incidents and service requests within the organization.  
It ensures accountability, consistent service delivery, and measurable performance across IT operations.

All SLAs apply to incidents raised through the official IT Service Management (ITSM) platform. Exceptions require managerial approval.

---

## 2. SLA Categories

| Priority | Description |
|-----------|--------------|
| **Critical (P1)** | System-wide outage or major business-impacting incident. Example: Email server down, VPN failure, or ERP outage. |
| **High (P2)** | Significant degradation impacting multiple users or departments. Example: Shared drive or printer outage. |
| **Medium (P3)** | Isolated issue affecting one or few users without major disruption. Example: Outlook not syncing, application crash. |
| **Low (P4)** | Minor issue or information request not impacting operations. Example: UI glitch, access clarification. |
| **Service Request (SR)** | Routine user request such as software install, password reset, or account creation. |

---

## 3. SLA Resolution Matrix

| Category | Priority | Resolution Target | Example |
|-----------|-----------|------------------|----------|
| **Incident** | Critical | 4 Hours | VPN Gateway down for all users |
| **Incident** | High | 8 Hours | Email delivery delay for department |
| **Incident** | Medium | 24 Hours | Outlook search not working |
| **Incident** | Low | 3 Business Days | Printer queue error |
| **Service Request** | Standard | 2 Business Days | Software installation or shared drive access |
| **Change Request** | Scheduled | 5 Business Days | Server patch deployment |
| **Security Incident** | Urgent | 6 Hours | Malware detection or phishing attack |
| **Backup Failure** | High | 12 Hours | Failed daily backup job |

---

## 4. Escalation Matrix

| Escalation Level | Team / Role | Description |
|------------------|--------------|--------------|
| **Level 1 (L1)** | Service Desk | Initial triage, logging, and basic troubleshooting |
| **Level 2 (L2)** | Technical Support | Handles specialized technical issues (network, hardware, software) |
| **Level 3 (L3)** | System Administrators | Advanced root cause analysis, configuration, and patching |
| **Level 4 (L4)** | Vendor / OEM Support | Escalated to product vendors for unresolved or product-specific issues |

Escalation triggers automatically if resolution target exceeds 75% of SLA window.

---

## 5. SLA Measurement and Breach Policy
- SLA compliance is measured monthly by total incidents resolved within target times.  
- Breach alerts automatically sent to assigned technician and manager.  
- Repeated SLA violations reviewed in quarterly performance meetings.  
- High-severity breaches generate an automatic post-incident review (PIR).  
- Metrics tracked in ITSM reports:  
  - SLA Compliance %  
  - Mean Time to Resolve (MTTR)  
  - Escalation Rate  

---

## 6. Service Categories and SLA Examples

| Service Category | Example Issues | SLA Target |
|------------------|----------------|-------------|
| **Email & Collaboration** | Outlook not syncing, Teams login failure | 24 Hours |
| **Network & Connectivity** | VPN failure, Wi-Fi outage | 8 Hours |
| **Hardware Support** | Laptop overheating, printer offline | 2 Business Days |
| **Application Support** | ERP timeout, SAP performance issue | 24 Hours |
| **Security Incidents** | Malware detection, phishing attack | 6 Hours |
| **Cloud Services** | OneDrive not syncing, Azure login issue | 24 Hours |
| **User Account Management** | New user creation, access modification | 2 Business Days |
| **Infrastructure Maintenance** | Server backup issue, patching | 12 Hours |

---

## 7. Business Hours and Coverage Policy

| Coverage Type | Hours | Days | Notes |
|----------------|--------|------|--------|
| **Business Hours** | 9:00 AM – 6:00 PM | Monday – Friday | SLA clock paused during weekends and holidays |
| **24x7 Critical Support** | 24 Hours | All Days | Applicable to P1 incidents and data center issues |
| **After-Hours Support** | On-Call Basis | Weekends & Holidays | L2/L3 support available for urgent incidents only |

Holiday calendars are maintained regionally in ITSM and integrated into SLA calculations automatically.

---

## 8. SLA Case Examples

### Example 1: Email Outage (P1)
- **Scenario:** Exchange Server unavailable organization-wide.  
- **Resolution:** Restored within 3 hours after restarting queue services.  
- **SLA Status:** Met.  
- **Follow-Up:** Root cause analysis submitted.

### Example 2: VPN Connection Timeout (P2)
- **Scenario:** Remote users unable to connect during peak hours.  
- **Resolution:** Load balancing applied to gateway nodes.  
- **SLA Status:** Met.  

### Example 3: Printer Offline (P4)
- **Scenario:** Shared printer unavailable for HR department.  
- **Resolution:** Reinstalled drivers and reset network connection in 2 days.  
- **SLA Status:** Met.  

### Example 4: Malware Detection (Security Incident)
- **Scenario:** Endpoint antivirus detected ransomware.  
- **Resolution:** Device quarantined and restored from backup within 5 hours.  
- **SLA Status:** Met.  
- **Follow-Up:** Security awareness email sent to all users.

---

### Notes
- SLA clocks start when a valid ticket is created and assigned.  
- User acknowledgment resets the clock for resolved tickets pending confirmation.  
- Service Desk reviews SLA metrics weekly to ensure proactive compliance.

---
