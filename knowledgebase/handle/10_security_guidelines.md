# Security Guidelines (Expanded - Generic Corporate IT)

## 1. Purpose and Scope
These security guidelines define the minimum standards required to protect the organization’s digital, physical, and information assets.  
They apply to all employees, contractors, vendors, and third parties who access corporate systems, data, or networks.  
Compliance with these guidelines is mandatory to maintain confidentiality, integrity, and availability of company information.

---

## 2. Password and Account Security

### Objective
To enforce strong authentication practices and prevent unauthorized system access.

### Guidelines
- Passwords must contain at least 12 characters, including uppercase, lowercase, numbers, and symbols.  
- Avoid using personal information (name, birthdate, etc.) in passwords.  
- Passwords must not be shared or written down.  
- Multi-Factor Authentication (MFA) is mandatory for all Microsoft 365, VPN, and cloud logins.  
- Accounts that remain inactive for 90 days will be disabled automatically.  
- Passwords expire every 90 days and must not repeat the last five passwords.  

### Tools Used
- Microsoft 365 MFA  
- Okta Identity Cloud  
- Active Directory Password Policy Management  

---

## 3. Device and Endpoint Security

### Objective
To ensure all endpoints are secured, updated, and monitored.

### Guidelines
- All company laptops and desktops must use **Microsoft Defender** and **CrowdStrike Falcon** for endpoint protection.  
- Full-disk encryption via **BitLocker** (Windows) or **FileVault** (macOS) is mandatory.  
- Operating system updates are pushed weekly through **Microsoft SCCM**.  
- Unauthorized USB drives and external media are blocked by policy.  
- Devices must automatically lock after 10 minutes of inactivity.  
- Only IT-approved software may be installed.  

### Tools Used
- Microsoft Defender ATP  
- CrowdStrike Falcon Console  
- Microsoft SCCM (System Center Configuration Manager)  

---

## 4. Email and Phishing Protection

### Objective
To minimize the risk of phishing, spoofing, and email-based attacks.

### Guidelines
- Employees must not open attachments or links from unknown senders.  
- Report suspicious messages immediately using the **“Report Phish”** add-in in Outlook.  
- All inbound emails are scanned through **Proofpoint Email Security** for malicious links and attachments.  
- External email warnings (“[EXTERNAL]”) are added automatically to help identify non-company senders.  
- Do not reply to emails requesting credentials or financial details.  

### Tools Used
- Proofpoint Email Security  
- Microsoft Defender for Office 365  
- Outlook “Report Phish” Plugin  

---

## 5. Data Security and Encryption

### Objective
To protect sensitive company data from loss, theft, or unauthorized exposure.

### Guidelines
- All confidential data must be stored in approved locations such as **OneDrive for Business** or **SharePoint Online**.  
- External sharing of documents must be approved through the IT Governance Team.  
- Sensitive files must be encrypted before being transferred externally.  
- Use **7-Zip AES-256 encryption** for password-protected archives.  
- Removable media (USB, HDD) must use BitLocker encryption.  
- Screen sharing during meetings should be limited to necessary windows only.  

### Tools Used
- Microsoft OneDrive / SharePoint  
- BitLocker / 7-Zip  
- Microsoft Information Protection Labels  

---

## 6. Physical Security

### Objective
To protect company assets and ensure authorized access to physical locations.

### Guidelines
- All employees must wear their ID badges visibly inside office premises.  
- Visitor access requires prior approval and escort by authorized personnel.  
- Server rooms and network closets are restricted to IT staff only.  
- Doors, drawers, and storage units containing sensitive material must remain locked.  
- Laptops and mobile devices must not be left unattended in public or shared areas.  

### Tools Used
- Electronic Access Control System (Badge Access)  
- CCTV Surveillance (24x7 Monitoring)  

---

## 7. Network and VPN Security

### Objective
To secure internal and external network access and safeguard remote connections.

### Guidelines
- Only **Cisco AnyConnect VPN** is permitted for remote access.  
- VPN sessions must use SSL/TLS encryption.  
- Split tunneling is disabled to prevent bypass of corporate security controls.  
- Wi-Fi connections should use WPA3 encryption where supported.  
- Public Wi-Fi should only be used with VPN active.  
- Network traffic is continuously monitored through **SolarWinds** and **Fortinet Firewalls**.  

### Tools Used
- Cisco AnyConnect VPN  
- Fortinet Firewall / FortiGate  
- SolarWinds Network Performance Monitor  

---

## 8. Incident Reporting and Response

### Objective
To ensure all security incidents are promptly detected, contained, and reported.

### Guidelines
- Any suspected data breach, phishing attempt, or malware detection must be reported immediately to **security@company.com**.  
- Employees must not attempt to investigate or delete suspicious files independently.  
- Incident response follows a structured 5-step process: **Detection → Containment → Eradication → Recovery → Review**.  
- Incident tracking and RCA (Root Cause Analysis) are managed via **ServiceNow**.  
- Major security incidents trigger a formal Post-Incident Review (PIR).  

### Tools Used
- ServiceNow ITSM  
- CrowdStrike Falcon  
- Splunk SIEM for log analysis  

---

## 9. Software and Patch Management

### Objective
To maintain up-to-date systems and reduce vulnerability exposure.

### Guidelines
- All devices must receive automated updates via **SCCM** or **Intune**.  
- Third-party software (Adobe, Java, Chrome) must be updated monthly.  
- Patches rated as “Critical” must be deployed within 48 hours.  
- Unsupported or end-of-life software must be removed immediately.  
- Patch compliance is reviewed weekly by the Endpoint Management Team.  

### Tools Used
- Microsoft SCCM  
- Windows Update for Business  
- Red Hat Satellite (for Linux servers)  

---

## 10. Security Awareness and Training

### Objective
To create a culture of continuous security awareness across the organization.

### Guidelines
- All employees must complete annual cybersecurity training.  
- Quarterly phishing simulation exercises will be conducted.  
- Security newsletters and advisories are distributed monthly.  
- Managers are accountable for ensuring team participation in awareness campaigns.  
- Repeated failures in phishing simulations will trigger mandatory retraining.  

### Tools Used
- KnowBe4 Security Awareness Platform  
- LMS (Learning Management System)  
- Microsoft Forms for user acknowledgment tracking  

---

## 11. Enforcement

Violations of these security guidelines may result in disciplinary actions including revocation of access privileges, suspension, or termination depending on severity.  
IT Security reserves the right to audit user activity logs, network connections, and system configurations without prior notice.

---

## 12. Summary

By following these guidelines, employees contribute to maintaining a secure, resilient, and trusted IT environment.  
Cybersecurity is a shared responsibility, and every individual must act diligently to protect company systems and data.

