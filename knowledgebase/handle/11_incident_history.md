# Incident History (Expanded - Generic Corporate IT)

## 1. Overview
This document maintains a historical record of IT incidents to support proactive analysis, faster root cause identification, and improved service reliability.  
Each record summarizes the issue, underlying cause, resolution approach, and key lessons learned for future prevention.

---

## 2. Major Incidents (P1/P2)

### Incident ID: INC-1001
- **Category:** Network
- **Summary:** Corporate VPN inaccessible to all remote users.
- **Root Cause:** VPN gateway certificate expired, preventing authentication.
- **Resolution:** Reissued SSL certificate and restarted VPN gateway service.
- **Lessons Learned:** Implement automated certificate renewal alerts.

---

### Incident ID: INC-1002
- **Category:** Email
- **Summary:** Exchange Online users unable to send emails.
- **Root Cause:** Misconfigured mail flow rule triggered message quarantine.
- **Resolution:** Disabled faulty rule and released quarantined messages.
- **Lessons Learned:** Review and approve new rules through change control.

---

### Incident ID: INC-1003
- **Category:** Storage
- **Summary:** Shared drive unavailable across multiple teams.
- **Root Cause:** File server service crashed due to disk I/O overload.
- **Resolution:** Restarted file server and moved archives to secondary NAS.
- **Lessons Learned:** Monitor disk performance thresholds proactively.

---

### Incident ID: INC-1004
- **Category:** Infrastructure
- **Summary:** Power outage affected primary data center servers.
- **Root Cause:** UPS unit failed to switch to battery mode.
- **Resolution:** Activated standby UPS system and restored server cluster.
- **Lessons Learned:** Schedule regular UPS maintenance checks.

---

### Incident ID: INC-1005
- **Category:** Security
- **Summary:** Phishing campaign targeting internal users.
- **Root Cause:** External spoofed domain bypassed basic spam filter.
- **Resolution:** Blocked domain in Proofpoint and conducted awareness training.
- **Lessons Learned:** Strengthen inbound email rule configurations.

---

### Incident ID: INC-1006
- **Category:** Application
- **Summary:** ERP system login failures reported organization-wide.
- **Root Cause:** Authentication server unresponsive due to database lock.
- **Resolution:** Restarted SQL service and reindexed authentication tables.
- **Lessons Learned:** Implement automatic DB lock detection scripts.

---

## 3. Moderate Incidents (P3)

### Incident ID: INC-2001
- **Category:** Collaboration Tools
- **Summary:** Microsoft Teams channels not loading.
- **Root Cause:** Cached authentication tokens expired unexpectedly.
- **Resolution:** Cleared Teams cache and reauthenticated users.
- **Lessons Learned:** Automate cache cleanup via startup script.

---

### Incident ID: INC-2002
- **Category:** Software Deployment
- **Summary:** SCCM failed to push monthly Windows updates.
- **Root Cause:** WSUS synchronization failure between servers.
- **Resolution:** Re-synced WSUS and retriggered patch deployment.
- **Lessons Learned:** Monitor SCCM-WSUS sync logs regularly.

---

### Incident ID: INC-2003
- **Category:** Network
- **Summary:** Wi-Fi users experiencing intermittent disconnections.
- **Root Cause:** Channel interference between multiple access points.
- **Resolution:** Adjusted AP frequencies and optimized controller settings.
- **Lessons Learned:** Conduct wireless survey every quarter.

---

### Incident ID: INC-2004
- **Category:** Email
- **Summary:** Shared mailbox access delays during peak hours.
- **Root Cause:** Throttling limits reached in Exchange Online.
- **Resolution:** Increased concurrency limit in admin center.
- **Lessons Learned:** Review mailbox access thresholds for high-use groups.

---

### Incident ID: INC-2005
- **Category:** Endpoint
- **Summary:** Antivirus alerts triggered false positives.
- **Root Cause:** Incorrect malware signature update.
- **Resolution:** Rolled back signature file and updated database.
- **Lessons Learned:** Stage antivirus updates in test environment first.

---

### Incident ID: INC-2006
- **Category:** Authentication
- **Summary:** Some users unable to log in via SSO.
- **Root Cause:** Misalignment between identity provider and Okta configuration.
- **Resolution:** Synchronized metadata and revalidated SAML certificates.
- **Lessons Learned:** Schedule quarterly SSO configuration audits.

---

## 4. Minor Incidents (P4)

### Incident ID: INC-3001
- **Category:** Hardware
- **Summary:** Laptop not powering on after sleep mode.
- **Root Cause:** BIOS setting caused power state hang.
- **Resolution:** Updated BIOS firmware to latest version.
- **Lessons Learned:** Include BIOS updates in patch cycle.

---

### Incident ID: INC-3002
- **Category:** Printer
- **Summary:** Print jobs stuck in queue.
- **Root Cause:** Print spooler service stopped.
- **Resolution:** Restarted spooler and cleared queue files.
- **Lessons Learned:** Enable automatic service restart policy.

---

### Incident ID: INC-3003
- **Category:** VPN
- **Summary:** Remote user connection drops intermittently.
- **Root Cause:** Idle session timeout misconfigured.
- **Resolution:** Adjusted session timeout to 8 hours.
- **Lessons Learned:** Document and standardize VPN settings.

---

### Incident ID: INC-3004
- **Category:** Outlook
- **Summary:** Search not returning recent emails.
- **Root Cause:** Windows indexing service stopped.
- **Resolution:** Restarted search service and rebuilt index.
- **Lessons Learned:** Monitor Outlook indexing service status.

---

### Incident ID: INC-3005
- **Category:** Browser
- **Summary:** Web app not loading correctly in Chrome.
- **Root Cause:** Cached session cookies causing redirect loops.
- **Resolution:** Cleared browser cache and cookies.
- **Lessons Learned:** Educate users on cache clearing best practices.

---

### Incident ID: INC-3006
- **Category:** Software
- **Summary:** Application crash on startup.
- **Root Cause:** Missing DLL file after partial installation.
- **Resolution:** Reinstalled missing components.
- **Lessons Learned:** Use automated software validation scripts.

---

## 5. Post-Incident Review (PIR)

### Common Themes Identified
- Configuration drift between production and staging environments.  
- Insufficient alerting thresholds on critical services.  
- Outdated SSL certificates not renewed proactively.  
- User awareness gaps leading to phishing and credential errors.  
- Patch cycles not aligned with dependency testing.  

### Preventive Actions
- Implement centralized alerting through monitoring dashboard (e.g., SolarWinds).  
- Automate SSL certificate monitoring and renewal.  
- Standardize configuration baselines for all servers.  
- Increase phishing simulation training frequency.  
- Introduce weekly patch validation checkpoints.  

### Conclusion
Consistent documentation and review of incidents help improve system resilience and service reliability.  
The IT Operations and Security teams jointly own the task of tracking incidents, reviewing patterns, and applying preventive measures proactively.

---
