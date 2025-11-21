# Resolution Playbooks (Expanded - Generic Corporate IT)

## 1. User Account and Authentication

### Playbook: Reset a User’s Forgotten Password
- **Scenario:** Employee cannot log in due to an expired or forgotten password.
- **Objective:** Reset the user’s password securely and restore access.
- **Tools Required:** Active Directory Users and Computers (ADUC), ITSM Portal, Email/Chat tool.
- **Steps to Resolve:**
  1. Authenticate requester’s identity using employee ID or email verification.
  2. Open ADUC → Locate the user under the correct OU.
  3. Right-click → Reset Password → Generate a secure temporary password.
  4. Select “User must change password at next logon.”
  5. Communicate the temporary password via a secure channel.
- **Verification:** Confirm the user can log in and successfully change the password.
- **Escalation Path:** If password policy issues arise, escalate to the AD Admin Team.

---

### Playbook: Unlock a Locked Account
- **Scenario:** User account is locked after multiple incorrect login attempts.
- **Objective:** Unlock the account and restore access.
- **Tools Required:** Active Directory Console, ITSM Portal.
- **Steps to Resolve:**
  1. Verify user identity.
  2. Search for the account in ADUC → Right-click → Unlock Account.
  3. Instruct the user to retry logging in with correct credentials.
  4. Check for repeated failed logins in AD logs (potential security concern).
- **Verification:** User successfully authenticates without lockout recurrence.
- **Escalation Path:** If issue persists, forward to Security Operations.

---

### Playbook: Re-register Multi-Factor Authentication (MFA)
- **Scenario:** User lost access to their authenticator app or phone.
- **Objective:** Re-enroll MFA securely.
- **Tools Required:** Microsoft 365 Admin Center, Authenticator Admin Portal.
- **Steps to Resolve:**
  1. Verify identity through alternate method (email or manager confirmation).
  2. Reset MFA for the user in the admin console.
  3. Guide user through re-enrollment steps.
  4. Test login with MFA to confirm setup.
- **Verification:** Successful MFA validation during login attempt.
- **Escalation Path:** Report MFA system errors to Cloud Security Team.

---

## 2. Email and Collaboration Tools

### Playbook: Fix Outlook Not Syncing
- **Scenario:** Outlook not updating new emails or folders.
- **Objective:** Restore Outlook synchronization with Exchange.
- **Tools Required:** Outlook Desktop App, Control Panel → Mail, Command Prompt.
- **Steps to Resolve:**
  1. Check internet connectivity and Exchange server status.
  2. Go to File → Account Settings → Repair.
  3. Clear cache and restart Outlook.
  4. Recreate user profile if sync issue persists.
- **Verification:** Confirm latest emails are visible and synced.
- **Escalation Path:** If Exchange issue, escalate to Messaging Team.

---

### Playbook: Resolve Teams Meeting Join Failure
- **Scenario:** User cannot join Teams meeting via link.
- **Objective:** Restore Teams meeting functionality.
- **Tools Required:** Microsoft Teams App, Web Browser.
- **Steps to Resolve:**
  1. Sign out and re-login to Teams.
  2. Clear Teams cache folder from `%appdata%\Microsoft\Teams`.
  3. Restart the device and try joining via browser.
  4. Update Teams client to latest version.
- **Verification:** User can join and participate in Teams calls.
- **Escalation Path:** If authentication errors persist, escalate to Collaboration Admin.

---

### Playbook: Configure Shared Mailbox in Outlook
- **Scenario:** User requests access to a shared mailbox.
- **Objective:** Provide mailbox access without creating new credentials.
- **Tools Required:** Exchange Admin Center, Outlook Desktop App.
- **Steps to Resolve:**
  1. Verify user’s authorization for mailbox access.
  2. Assign Full Access and Send As permissions in Exchange.
  3. Restart Outlook → Add shared mailbox manually.
  4. Verify access and email send/receive.
- **Verification:** User can access and send emails from the shared mailbox.
- **Escalation Path:** Messaging Admin for mailbox permission issues.

---

## 3. VPN and Network

### Playbook: Resolve VPN Connection Failure
- **Scenario:** VPN client unable to connect to corporate network.
- **Objective:** Restore secure VPN connectivity.
- **Tools Required:** Cisco AnyConnect, Command Prompt, Network Logs.
- **Steps to Resolve:**
  1. Check internet connection and VPN credentials.
  2. Update AnyConnect client to latest version.
  3. Flush DNS and reset IP configuration.
  4. Retry connection; if issue persists, test alternate gateway.
- **Verification:** User successfully connects via VPN.
- **Escalation Path:** VPN Gateway Admin Team.

---

### Playbook: Fix Slow Wi-Fi Connection
- **Scenario:** Wi-Fi speed drops or frequent disconnections reported.
- **Objective:** Stabilize and optimize wireless performance.
- **Tools Required:** Wireless Controller Dashboard, Ping Tool, Laptop/Device Logs.
- **Steps to Resolve:**
  1. Validate signal strength and noise ratio.
  2. Move client to 5GHz SSID if supported.
  3. Reboot AP if performance issue localized.
  4. Test connectivity post changes.
- **Verification:** Speed and stability improved.
- **Escalation Path:** Network Infrastructure Team.

---

## 4. Hardware and Devices

### Playbook: Troubleshoot Printer Offline Issue
- **Scenario:** Network printer displays “Offline” and print jobs stuck in queue.
- **Objective:** Bring printer online and clear backlog.
- **Tools Required:** Print Management Console, Services.msc, Command Prompt.
- **Steps to Resolve:**
  1. Restart Print Spooler service.
  2. Ping printer hostname to confirm network availability.
  3. Remove and re-add printer using correct IP.
  4. Test print a sample document.
- **Verification:** Printer status shows “Online” and prints successfully.
- **Escalation Path:** Hardware Support Team.

---

### Playbook: Fix Laptop Overheating
- **Scenario:** Laptop shuts down during heavy use.
- **Objective:** Reduce system overheating and maintain performance.
- **Tools Required:** Task Manager, Device Manager, BIOS Utility.
- **Steps to Resolve:**
  1. Clean air vents and apply cooling pad.
  2. Check CPU usage and close resource-heavy apps.
  3. Update BIOS and chipset drivers.
  4. Perform stress test post maintenance.
- **Verification:** System temperature stabilized under load.
- **Escalation Path:** Hardware Vendor if thermal issue persists.

---

## 5. Software Installation and Patch Management

### Playbook: Deploy Software via SCCM
- **Scenario:** User requests new software deployment.
- **Objective:** Install application remotely using SCCM.
- **Tools Required:** Microsoft SCCM Console, ITSM Ticket.
- **Steps to Resolve:**
  1. Verify software license availability.
  2. Add system to appropriate deployment collection.
  3. Initiate install and monitor progress.
  4. Confirm installation success from SCCM logs.
- **Verification:** Application visible in Programs and Features.
- **Escalation Path:** Endpoint Management Team.

---

### Playbook: Manual Software Installation
- **Scenario:** Software unavailable in company portal.
- **Objective:** Perform manual installation with admin privileges.
- **Tools Required:** Installation Media, Command Prompt, Admin Rights.
- **Steps to Resolve:**
  1. Download verified installer.
  2. Run setup as administrator.
  3. Configure license key or authentication.
  4. Test application functionality.
- **Verification:** Application runs without error.
- **Escalation Path:** Software Deployment Team.

---

## 6. Security and Compliance

### Playbook: Handle Antivirus Alert
- **Scenario:** Endpoint antivirus detects a potential threat.
- **Objective:** Quarantine and analyze threat.
- **Tools Required:** Endpoint Protection Console, VirusTotal, File Explorer.
- **Steps to Resolve:**
  1. Open antivirus console → Review detection logs.
  2. Quarantine or delete infected file.
  3. Run full system scan.
  4. Submit suspicious file to Security Team for analysis.
- **Verification:** No further detections in logs.
- **Escalation Path:** Security Operations Center (SOC).

---

### Playbook: Respond to Phishing Email
- **Scenario:** User reports suspicious email requesting credentials.
- **Objective:** Contain and educate users against phishing attacks.
- **Tools Required:** Outlook, Exchange Admin Center, Security Awareness Portal.
- **Steps to Resolve:**
  1. Block sender domain and purge email organization-wide.
  2. Advise user to not click or download attachments.
  3. Update spam filter rules.
  4. Report incident in ITSM.
- **Verification:** No recurrence of phishing emails.
- **Escalation Path:** Security Awareness Team.

---

## 7. Server and Backup Management

### Playbook: Fix Backup Job Failure
- **Scenario:** Scheduled backup failed overnight.
- **Objective:** Restore backup functionality.
- **Tools Required:** Backup Console, Windows Event Viewer, PowerShell.
- **Steps to Resolve:**
  1. Check storage availability and error logs.
  2. Restart backup service and rerun job manually.
  3. Validate destination path access.
  4. Mark job as “Recovered” in logs.
- **Verification:** Backup job completes successfully.
- **Escalation Path:** Storage Admin.

---

### Playbook: Restore Deleted File from Backup
- **Scenario:** User accidentally deleted critical file.
- **Objective:** Retrieve file from latest backup snapshot.
- **Tools Required:** Backup Management Console, File Explorer.
- **Steps to Resolve:**
  1. Locate backup job by date and file path.
  2. Restore file to user’s folder or shared drive.
  3. Confirm file integrity.
- **Verification:** User verifies restored file.
- **Escalation Path:** Storage and Backup Team.

---

## 8. Incident Escalation Flow

### Playbook: Escalate Unresolved IT Issues
- **Scenario:** Technician unable to resolve within SLA window.
- **Objective:** Escalate issue through proper channels.
- **Tools Required:** ITSM Portal, Communication Tools (Teams, Email).
- **Steps to Resolve:**
  1. Update ticket with troubleshooting summary.
  2. Change status to “Awaiting Escalation.”
  3. Assign to next-level support group (L2/L3).
  4. Notify supervisor of escalation.
- **Verification:** Ticket visible under new support queue.
- **Escalation Path:** IT Operations Manager.
