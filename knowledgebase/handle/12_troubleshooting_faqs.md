# Troubleshooting FAQs (Expanded - Generic Corporate IT)

## 1. Overview
This document provides quick answers and self-service troubleshooting guidance for the most common IT issues faced by end users.  
It covers areas like email, VPN, network, software, hardware, collaboration tools, account management, and security.

---

## 2. Email & Outlook FAQs

### Q1: Why is my Outlook not syncing new emails?
- **Possible Cause:** Outlook data file (.OST) corruption or poor internet connection.
- **Resolution Steps:**  
  1. Close Outlook.  
  2. Open Control Panel → Mail → Email Accounts → Repair.  
  3. Restart Outlook after repair completes.  
- **Additional Tip:** Use **Outlook Web App (OWA)** if desktop sync fails.

---

### Q2: Why does Outlook keep asking for my password?
- **Possible Cause:** Cached credentials conflict or MFA token expired.
- **Resolution Steps:**  
  1. Go to Windows Credential Manager → Remove saved Outlook credentials.  
  2. Restart Outlook and re-enter credentials.  
- **Additional Tip:** Ensure VPN connection is active when using Outlook offsite.

---

### Q3: I can’t search older emails in Outlook.
- **Possible Cause:** Windows Search service stopped or Outlook index corrupted.
- **Resolution Steps:**  
  1. Restart “Windows Search” service.  
  2. Go to Control Panel → Indexing Options → Rebuild Index.  
- **Additional Tip:** Enable Cached Exchange Mode for better performance.

---

### Q4: My shared mailbox isn’t loading in Outlook.
- **Possible Cause:** Incorrect permission or profile cache issue.
- **Resolution Steps:**  
  1. Confirm Full Access and Send As rights in Exchange Admin Center.  
  2. Remove and re-add the shared mailbox.  
- **Additional Tip:** Use OWA to verify access rights.

---

### Q5: My emails are delayed or stuck in Outbox.
- **Possible Cause:** SMTP relay issue or large attachment size.
- **Resolution Steps:**  
  1. Check network connection.  
  2. Reduce attachment size (<25 MB).  
  3. Restart Outlook.  
- **Additional Tip:** Use OneDrive link instead of attachments.

---

## 3. VPN & Network FAQs

### Q6: I can’t connect to the VPN.
- **Possible Cause:** Expired credentials or outdated VPN client.
- **Resolution Steps:**  
  1. Open **Cisco AnyConnect** → Verify VPN Gateway URL.  
  2. Update client to latest version.  
  3. Retry connection.  
- **Additional Tip:** Restart system and check if your account password recently changed.

---

### Q7: My Wi-Fi keeps disconnecting.
- **Possible Cause:** Network driver outdated or signal interference.
- **Resolution Steps:**  
  1. Update Wi-Fi driver from Device Manager.  
  2. Connect to 5GHz SSID if available.  
- **Additional Tip:** Avoid connecting multiple personal devices simultaneously.

---

### Q8: I can’t access shared drives.
- **Possible Cause:** VPN not connected or SMB share misconfiguration.
- **Resolution Steps:**  
  1. Ensure VPN is active.  
  2. Reconnect shared drive via “Map Network Drive.”  
- **Additional Tip:** Use **OneDrive for Business** for temporary file access.

---

### Q9: Network is slow while on VPN.
- **Possible Cause:** Split-tunneling disabled or high network latency.
- **Resolution Steps:**  
  1. Disconnect unnecessary background applications.  
  2. Reconnect to alternate VPN gateway.  
- **Additional Tip:** Keep your VPN client updated.

---

### Q10: Can’t access intranet websites.
- **Possible Cause:** DNS cache corruption.
- **Resolution Steps:**  
  1. Open Command Prompt → Run `ipconfig /flushdns`.  
  2. Restart browser.  
- **Additional Tip:** Use Microsoft Edge for internal portals.

---

## 4. Hardware FAQs

### Q11: My laptop won’t turn on.
- **Possible Cause:** Battery drained or power adapter failure.
- **Resolution Steps:**  
  1. Connect power adapter and hold power button for 10 seconds.  
  2. Test adapter with another device.  
- **Additional Tip:** Contact IT if issue persists.

---

### Q12: My screen is flickering.
- **Possible Cause:** Graphics driver issue.
- **Resolution Steps:**  
  1. Update display driver via Device Manager.  
  2. Check refresh rate settings.  
- **Additional Tip:** Disable adaptive brightness.

---

### Q13: Printer shows “Offline.”
- **Possible Cause:** Network connectivity loss or spooler service stopped.
- **Resolution Steps:**  
  1. Restart “Print Spooler” via Services.msc.  
  2. Re-add printer using **Control Panel → Devices & Printers**.  
- **Additional Tip:** Use company print server name when mapping printers.

---

### Q14: Laptop overheating during use.
- **Possible Cause:** Dust blockage or high CPU usage.
- **Resolution Steps:**  
  1. Clean air vents.  
  2. Close background apps in Task Manager.  
- **Additional Tip:** Use a cooling pad for extended use.

---

## 5. Software FAQs

### Q15: I can’t install a software from the IT portal.
- **Possible Cause:** SCCM agent not syncing or admin rights missing.
- **Resolution Steps:**  
  1. Restart computer and open **Software Center (SCCM)**.  
  2. Retry installation.  
- **Additional Tip:** Raise a request if it requires admin installation.

---

### Q16: My application keeps crashing.
- **Possible Cause:** Missing dependencies or version mismatch.
- **Resolution Steps:**  
  1. Uninstall and reinstall the latest version.  
  2. Update system drivers.  
- **Additional Tip:** Check Event Viewer for application logs.

---

### Q17: License expired message appears.
- **Possible Cause:** Subscription renewal delay.
- **Resolution Steps:**  
  1. Check renewal status with IT.  
  2. Sign out and back into the software.  
- **Additional Tip:** Ensure system date and time are correct.

---

### Q18: System update failed.
- **Possible Cause:** Interrupted Windows update process.
- **Resolution Steps:**  
  1. Run “Windows Update Troubleshooter.”  
  2. Restart device and retry update.  
- **Additional Tip:** Keep device plugged in during updates.

---

## 6. Collaboration Tools FAQs

### Q19: Teams won’t open after login.
- **Possible Cause:** Cache corruption.
- **Resolution Steps:**  
  1. Close Teams completely.  
  2. Delete contents from `%appdata%\Microsoft\Teams\Cache`.  
  3. Restart Teams.  
- **Additional Tip:** Try the Teams web version if issue persists.

---

### Q20: Zoom audio not working.
- **Possible Cause:** Incorrect audio device selected.
- **Resolution Steps:**  
  1. Open Zoom → Settings → Audio → Select correct input/output device.  
  2. Restart system.  
- **Additional Tip:** Test using Zoom’s “Test Speaker & Microphone.”

---

### Q21: OneDrive not syncing files.
- **Possible Cause:** Low disk space or sync client paused.
- **Resolution Steps:**  
  1. Check OneDrive icon → Resume sync.  
  2. Ensure you are signed in to the correct account.  
- **Additional Tip:** Avoid using special characters in file names.

---

## 7. Account & Access FAQs

### Q22: I forgot my password.
- **Possible Cause:** Password expired or incorrect entry.
- **Resolution Steps:**  
  1. Click “Forgot Password” on login page.  
  2. Follow self-service password reset instructions.  
- **Additional Tip:** Update password on all connected devices.

---

### Q23: My account is locked.
- **Possible Cause:** Multiple failed login attempts.
- **Resolution Steps:**  
  1. Wait 15 minutes or contact Service Desk.  
  2. Verify caps lock or keyboard language.  
- **Additional Tip:** Use company password policy guidelines.

---

### Q24: MFA not prompting on login.
- **Possible Cause:** Authenticator app not synced.
- **Resolution Steps:**  
  1. Open Microsoft Authenticator → Refresh tokens.  
  2. Re-register MFA in your account security settings.  
- **Additional Tip:** Ensure device time is accurate.

---

## 8. Security FAQs

### Q25: I received a suspicious email.
- **Possible Cause:** Phishing attempt.
- **Resolution Steps:**  
  1. Don’t click links or download attachments.  
  2. Report using Outlook’s “Report Phish” button.  
- **Additional Tip:** Always check sender domain carefully.

---

### Q26: Antivirus showing threat detected.
- **Possible Cause:** Real or false positive detection.
- **Resolution Steps:**  
  1. Open Microsoft Defender → Quarantine file.  
  2. Run full scan.  
- **Additional Tip:** Don’t ignore security alerts.

---

### Q27: BitLocker asking for recovery key.
- **Possible Cause:** Hardware or BIOS change triggered key protection.
- **Resolution Steps:**  
  1. Retrieve recovery key from your Microsoft account.  
  2. Enter key and boot system.  
- **Additional Tip:** Do not disable BitLocker protection.

---

### Q28: I clicked on a phishing link accidentally.
- **Possible Cause:** User error.
- **Resolution Steps:**  
  1. Disconnect from the internet.  
  2. Contact Security Team immediately.  
  3. Run full antivirus scan.  
- **Additional Tip:** Change password immediately after reporting.

---

### Q29: My laptop shows “This copy of Windows is not genuine.”
- **Possible Cause:** Activation lost after update.
- **Resolution Steps:**  
  1. Contact IT for activation via KMS server.  
  2. Verify activation key.  
- **Additional Tip:** Avoid using third-party activation tools.

---

## 9. General Best Practices
- Keep your system updated using **Software Center (SCCM)**.  
- Always use **VPN** when accessing corporate resources remotely.  
- Store work documents only in **OneDrive** or **SharePoint**.  
- Lock your screen (Win + L) when leaving your desk.  
- Report incidents promptly to **helpdesk@company.com**.

---
