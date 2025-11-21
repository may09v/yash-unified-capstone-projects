# Error Codes (Expanded - Generic Corporate IT)

## 1. Overview
This document standardizes error codes used across IT operations for consistent incident classification, reporting, and troubleshooting.  
Each category has a unique prefix (e.g., MAIL-, VPN-, NET-, SEC-, etc.) to identify the system or domain where the error originates.

---

## 2. Error Categories and Codes

### **Email & Messaging (MAIL-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| MAIL-101 | Outlook cannot connect to Exchange server | Network latency or Exchange service down | Check Exchange health, restart Outlook, reauthenticate profile |
| MAIL-102 | Email stuck in Outbox | SMTP connection blocked or authentication failure | Clear Outbox, check credentials, restart Outlook |
| MAIL-103 | Shared mailbox access denied | Incorrect permissions | Verify Full Access rights in Exchange Admin Center |
| MAIL-104 | Email search indexing failed | Corrupted Outlook cache | Rebuild search index via Control Panel → Indexing Options |
| MAIL-105 | Auto-discover not resolving | DNS or SSL misconfiguration | Verify DNS entries, test with `Test E-mail AutoConfiguration` |
| MAIL-106 | Teams meeting link missing | Add-in disabled | Re-enable Teams add-in in Outlook COM Add-ins |

---

### **Network (NET-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| NET-301 | Network cable unplugged | Physical disconnection | Reconnect cable and verify link lights |
| NET-302 | IP address conflict detected | Duplicate DHCP lease | Release and renew IP, check DHCP scope |
| NET-303 | No internet access | DNS failure or gateway misconfig | Run `ipconfig /flushdns`, verify gateway route |
| NET-304 | Slow network performance | Bandwidth congestion | Run speed test, check switch utilization |
| NET-305 | Proxy authentication loop | Cached credentials invalid | Clear browser cache, re-login, reset proxy settings |
| NET-306 | VPN DNS not resolving | Split-tunnel misconfiguration | Modify VPN DNS policy or switch full-tunnel mode |

---

### **VPN & Remote Access (VPN-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| VPN-201 | Connection timeout | Gateway overloaded or unreachable | Retry after 5 mins, test alternate gateway |
| VPN-202 | SSL handshake failed | Expired VPN certificate | Renew or reimport VPN client certificate |
| VPN-203 | Authentication failure | Incorrect domain credentials | Reset password, verify AD sync |
| VPN-204 | Tunnel drops intermittently | MTU mismatch or unstable network | Adjust MTU to 1300, reboot client |
| VPN-205 | Client version unsupported | Outdated AnyConnect client | Upgrade to latest version |
| VPN-206 | Split-tunnel configuration error | Policy mismatch | Sync VPN policy with network admin |

---

### **Application (APP-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| APP-701 | Application initialization failed | Missing dependency or DLL | Reinstall app and verify runtime libraries |
| APP-702 | Unhandled exception | Code crash or memory overflow | Clear cache, update app, check event viewer |
| APP-703 | Database connection error | Invalid credentials or timeout | Check DB config, test ODBC connection |
| APP-704 | Configuration file missing | File deletion or corruption | Restore from backup or reinstall |
| APP-705 | API call failed | Endpoint unavailable | Check API gateway status |
| APP-706 | License expired | Subscription expired | Renew license or contact vendor |

---

### **Security (SEC-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| SEC-501 | Unauthorized access attempt | Invalid credentials or brute force | Lock account, notify Security Ops |
| SEC-502 | Malware detected | Infected file or process | Quarantine and run full scan |
| SEC-503 | Phishing email identified | Malicious sender domain | Block domain, educate users |
| SEC-504 | Firewall policy violation | Unauthorized port access | Review firewall logs, update rules |
| SEC-505 | SSL certificate expired | Expired or untrusted cert | Renew certificate and deploy |
| SEC-506 | Endpoint encryption disabled | Policy misapplied | Re-enable BitLocker or MDM policy |

---

### **Hardware (HW-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| HW-601 | Hard drive SMART failure | Disk health degraded | Replace drive and restore from backup |
| HW-602 | Printer spooler crash | Service error | Restart spooler service and clear queue |
| HW-603 | Laptop overheating | Dust or fan malfunction | Clean vents, replace thermal paste |
| HW-604 | Display flickering | GPU driver issue | Update display driver |
| HW-605 | USB device not recognized | Faulty port or driver | Update driver, test alternate port |
| HW-606 | BIOS update failed | Power interruption | Reflash BIOS via recovery utility |

---

### **Authentication (AUTH-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| AUTH-801 | Invalid credentials | User mistyped password | Reset password and reattempt login |
| AUTH-802 | Account locked | Too many failed attempts | Unlock via AD or wait 15 minutes |
| AUTH-803 | Password expired | Password policy enforced | Prompt user to change password |
| AUTH-804 | MFA challenge failed | Wrong OTP or device unsynced | Re-register MFA device |
| AUTH-805 | SSO token expired | Session timeout | Clear browser cache and re-login |
| AUTH-806 | LDAP server not responding | Directory service offline | Restart LDAP service |

---

### **Backup & Storage (BKP-)**

| Code | Description | Root Cause | Resolution Steps |
|------|--------------|-------------|------------------|
| BKP-901 | Backup job failed | Storage quota full | Free up space and rerun job |
| BKP-902 | Backup verification failed | CRC error | Validate media integrity |
| BKP-903 | Snapshot creation failed | Insufficient permissions | Update backup agent credentials |
| BKP-904 | Incremental backup skipped | Source file locked | Retry after hours |
| BKP-905 | Restore job failed | Invalid backup set | Rebuild index and retry |
| BKP-906 | Backup schedule missed | Scheduler service stopped | Restart backup scheduler |

---

## 3. System-Level Notes
- All errors follow a standardized format: **<Category Prefix>-<Numeric Code>**.  
- Each detected error automatically maps to a corresponding ITSM incident category.  
- Technicians must include the error code in ticket summaries for accurate SLA tracking.  
- Codes are cross-referenced with RMM and SIEM alerts to ensure unified reporting.

---

## 4. Common Troubleshooting Patterns
- **Authentication & VPN Errors**: Often related to password expiry or AD sync issues.  
- **Network & DNS Errors**: Usually caused by misconfigured gateway or DHCP conflicts.  
- **Application Errors**: Resolve by clearing cache or reinstalling corrupted dependencies.  
- **Security Errors**: Require immediate escalation to the SOC team.  
- **Hardware Errors**: Always verify warranty before performing replacements.  
- **Backup Errors**: Commonly linked to permissions or quota exhaustion.

---

## 5. Usage in ITSM
When logging an incident in the ITSM system:  
1. Include the error code in the summary line (e.g., “VPN Connection Failed – VPN-203”).  
2. Attach screenshots or logs for context.  
3. Select appropriate service category automatically mapped by the code prefix.  
4. Monitor SLA metrics tied to each error family.  

---
