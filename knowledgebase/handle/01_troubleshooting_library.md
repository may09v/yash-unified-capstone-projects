# Troubleshooting Library (Expanded - Generic Corporate IT)

### Issue: Email not syncing in Microsoft Outlook
- **Category:** Email
- **Symptoms:** User reports that Outlook is not updating or showing recent messages.
- **Possible Causes:** Network interruption, cached mode corruption, or outdated Exchange credentials.
- **Resolution:**
  1. Verify stable internet connection.
  2. Go to File → Account Settings → Repair.
  3. Clear Outlook cache and restart.
  4. If still unresolved, recreate Outlook profile and test connectivity to Exchange Server.
- **Priority:** High

### Issue: Outlook cannot send or receive emails
- **Category:** Email
- **Symptoms:** Messages stuck in Outbox or unable to fetch new mail.
- **Possible Causes:** Incorrect SMTP/IMAP settings, mailbox quota full, or Exchange outage.
- **Resolution:**
  1. Verify account credentials.
  2. Check server status via Microsoft 365 Admin Center.
  3. Clear the Outbox and test mail flow.
  4. If Exchange issue persists, escalate to email admin team.
- **Priority:** Critical

### Issue: VPN connection keeps dropping
- **Category:** VPN
- **Symptoms:** Cisco AnyConnect disconnects repeatedly or fails to reconnect.
- **Possible Causes:** Unstable internet, MTU size mismatch, outdated client version.
- **Resolution:**
  1. Update VPN client to latest version.
  2. Check local firewall rules and whitelist VPN gateway IP.
  3. Adjust MTU size using `netsh interface ipv4 set subinterface`.
  4. Restart device and retry connection.
- **Priority:** Medium

### Issue: VPN authentication failed
- **Category:** VPN
- **Symptoms:** User unable to authenticate using domain credentials.
- **Possible Causes:** AD account locked, expired password, or certificate mismatch.
- **Resolution:**
  1. Verify credentials and reset AD password if required.
  2. Check VPN logs for authentication failure reason.
  3. Ensure user certificate validity.
  4. Retry connection and verify access through VPN portal.
- **Priority:** High

### Issue: Wi-Fi connected but no Internet access
- **Category:** Network
- **Symptoms:** Connected to Wi-Fi but cannot browse or use applications.
- **Possible Causes:** DNS failure, gateway misconfiguration, or DHCP lease expired.
- **Resolution:**
  1. Run `ipconfig /flushdns` and `ipconfig /renew`.
  2. Manually set DNS to 8.8.8.8 and 8.8.4.4.
  3. Restart router and check if other users face similar issues.
  4. Escalate to network admin if persistent.
- **Priority:** High

### Issue: Slow internet connection
- **Category:** Network
- **Symptoms:** High latency during browsing, downloads, or Teams calls.
- **Possible Causes:** Bandwidth congestion, switch overload, or faulty cable.
- **Resolution:**
  1. Run `ping` and `tracert` to identify delay source.
  2. Connect via LAN cable for testing.
  3. If issue persists, log a ticket to network operations.
- **Priority:** Medium

### Issue: Laptop overheating
- **Category:** Hardware
- **Symptoms:** Fan noise increases and laptop shuts down unexpectedly.
- **Possible Causes:** Blocked air vents, malware using CPU, outdated BIOS.
- **Resolution:**
  1. Clean vents and apply cooling pad.
  2. Run antivirus full scan.
  3. Update BIOS and chipset drivers.
  4. If issue continues, log for hardware replacement.
- **Priority:** Medium

### Issue: System not booting
- **Category:** Hardware
- **Symptoms:** System stuck at boot logo or fails to power on.
- **Possible Causes:** Faulty RAM, disk corruption, or power adapter failure.
- **Resolution:**
  1. Perform power drain and restart.
  2. Boot into BIOS to verify hardware detection.
  3. Run diagnostics and repair disk.
  4. If hardware faulty, escalate to vendor support.
- **Priority:** Critical

### Issue: Shared network drive inaccessible
- **Category:** Network
- **Symptoms:** User cannot access mapped drive or receives permission denied.
- **Possible Causes:** Network outage, SMB service stopped, or permissions revoked.
- **Resolution:**
  1. Check network connectivity.
  2. Verify access path using `\fileserver\share`.
  3. Confirm AD group membership for shared folder.
  4. Restart device and remap drive.
- **Priority:** High

### Issue: Printer not responding
- **Category:** Hardware
- **Symptoms:** Printer shows offline or jobs remain in queue.
- **Possible Causes:** Print spooler service stopped, network printer offline.
- **Resolution:**
  1. Restart Print Spooler (`services.msc`).
  2. Power-cycle printer and reconnect network cable.
  3. Reinstall printer drivers.
  4. Print test page.
- **Priority:** Medium

### Issue: Zoom audio not working
- **Category:** Collaboration Tools
- **Symptoms:** Users cannot hear or be heard during meeting.
- **Possible Causes:** Microphone disabled, wrong audio device selected.
- **Resolution:**
  1. Go to Settings → Audio and choose correct device.
  2. Reconnect headset or restart Zoom.
  3. Test in other apps like Teams or system sound recorder.
- **Priority:** Low

### Issue: Microsoft Teams chat not syncing
- **Category:** Collaboration Tools
- **Symptoms:** Chats missing or messages delayed.
- **Possible Causes:** Cached credentials or network delay.
- **Resolution:**
  1. Sign out and re-login to Teams.
  2. Clear Teams cache from `%appdata%\Microsoft\Teams`.
  3. Restart device and test.
- **Priority:** Medium

### Issue: Password expired
- **Category:** Authentication
- **Symptoms:** Unable to log in; system prompts for password change.
- **Possible Causes:** AD password policy enforcement.
- **Resolution:**
  1. Use Ctrl + Alt + Del → Change Password.
  2. Update password on all devices (VPN, Outlook, mobile).
- **Priority:** Low

### Issue: Account locked
- **Category:** Authentication
- **Symptoms:** Login blocked on multiple systems.
- **Possible Causes:** Too many failed login attempts.
- **Resolution:**
  1. Wait 15 minutes for auto-unlock or request IT to unlock account.
  2. Ensure correct credentials are used post reset.
- **Priority:** Medium

### Issue: Blue screen error (BSOD)
- **Category:** Hardware/Software
- **Symptoms:** System crashes with blue error screen.
- **Possible Causes:** Driver incompatibility, corrupt OS files.
- **Resolution:**
  1. Boot into Safe Mode.
  2. Update drivers and uninstall recent patches.
  3. Run `sfc /scannow`.
  4. If persistent, reimage system.
- **Priority:** High

### Issue: Slow system performance
- **Category:** Software
- **Symptoms:** Lag in applications, delayed responses.
- **Possible Causes:** Too many startup programs, malware, low memory.
- **Resolution:**
  1. Disable unnecessary startup programs.
  2. Run full virus scan.
  3. Upgrade RAM if required.
- **Priority:** Medium

### Issue: Unable to access internal web portal
- **Category:** Network/Security
- **Symptoms:** Browser shows “Access Denied” or timeout.
- **Possible Causes:** Proxy misconfiguration or firewall block.
- **Resolution:**
  1. Verify proxy settings.
  2. Test access through VPN.
  3. Escalate to security operations for rule check.
- **Priority:** High

### Issue: Software installation blocked by admin policy
- **Category:** Security
- **Symptoms:** Error “Installation blocked by administrator” during setup.
- **Possible Causes:** UAC restriction or policy enforcement.
- **Resolution:**
  1. Request admin privilege for installation.
  2. Install through Company Portal or approved software catalog.
- **Priority:** Low

### Issue: Cloud drive (OneDrive) not syncing files
- **Category:** Cloud
- **Symptoms:** Files stuck at “Sync pending” in OneDrive.
- **Possible Causes:** Insufficient storage, sync app error.
- **Resolution:**
  1. Pause and resume sync.
  2. Clear cache from `%localappdata%\Microsoft\OneDrive`.
  3. Reconnect account.
- **Priority:** Medium

### Issue: Antivirus not updating
- **Category:** Security
- **Symptoms:** Endpoint antivirus definitions out of date.
- **Possible Causes:** Firewall blocking update or policy conflict.
- **Resolution:**
  1. Manually trigger update from the antivirus console.
  2. Verify connection to update server.
  3. Reinstall if corruption found.
- **Priority:** High

### Issue: Outlook search not working
- **Category:** Email
- **Symptoms:** Search returns no results.
- **Possible Causes:** Indexing service stopped or cache corruption.
- **Resolution:**
  1. Rebuild search index via Control Panel → Indexing Options.
  2. Restart Outlook.
- **Priority:** Low

### Issue: Slow VPN speed
- **Category:** VPN
- **Symptoms:** High latency and file transfer delays.
- **Possible Causes:** Low bandwidth or high gateway utilization.
- **Resolution:**
  1. Switch VPN gateway or connect via LAN.
  2. Close bandwidth-heavy applications.
- **Priority:** Medium

### Issue: Shared mailbox inaccessible in Outlook
- **Category:** Email
- **Symptoms:** Shared mailbox not visible or access denied.
- **Possible Causes:** Missing permissions or cached credentials.
- **Resolution:**
  1. Remove and re-add mailbox.
  2. Verify user assigned via Exchange Admin Center.
- **Priority:** Medium

### Issue: USB not recognized
- **Category:** Hardware
- **Symptoms:** USB drive not showing in File Explorer.
- **Possible Causes:** Corrupt driver or faulty port.
- **Resolution:**
  1. Unplug and reconnect.
  2. Update USB drivers.
  3. Try alternate port.
- **Priority:** Low

### Issue: Screen flickering after update
- **Category:** Hardware/Software
- **Symptoms:** Screen flickers intermittently after Windows update.
- **Possible Causes:** Display driver bug.
- **Resolution:**
  1. Roll back or update display driver.
  2. Adjust refresh rate.
- **Priority:** Medium

### Issue: Application crashing frequently
- **Category:** Software
- **Symptoms:** App closes unexpectedly without error.
- **Possible Causes:** Corrupted config files or outdated version.
- **Resolution:**
  1. Reinstall application.
  2. Delete config cache and relaunch.
- **Priority:** Medium

### Issue: Unable to connect to remote desktop
- **Category:** Network/Security
- **Symptoms:** RDP connection timeout.
- **Possible Causes:** Port 3389 blocked, credentials invalid.
- **Resolution:**
  1. Verify host availability via `ping`.
  2. Allow RDP in firewall.
  3. Retry connection.
- **Priority:** High
