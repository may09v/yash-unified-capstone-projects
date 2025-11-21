# Known Issues (Expanded - Generic Corporate IT)

### Issue: Outlook email delivery delays
- **Category:** Email
- **Symptoms:** Outgoing emails take longer than usual to reach recipients.
- **Root Cause:** Temporary throttling on Microsoft 365 Exchange Online.
- **Workaround:** Use Outlook Web App (OWA) for urgent communication.
- **Resolution:** Microsoft patch pending for queue optimization.
- **Status:** Monitoring

### Issue: VPN authentication intermittently fails
- **Category:** VPN
- **Symptoms:** Users receive “Authentication Failed” randomly while connecting.
- **Root Cause:** Load imbalance across VPN gateways.
- **Workaround:** Retry connection or use alternate VPN gateway.
- **Resolution:** Gateway reconfiguration in progress.
- **Status:** Open

### Issue: Teams messages not syncing
- **Category:** Collaboration Tools
- **Symptoms:** Chat messages delayed or missing.
- **Root Cause:** Background service cache corruption.
- **Workaround:** Sign out, clear Teams cache, and re-login.
- **Resolution:** Teams client update scheduled.
- **Status:** Monitoring

### Issue: Wi-Fi instability in office area
- **Category:** Network
- **Symptoms:** Devices disconnect intermittently from corporate Wi-Fi.
- **Root Cause:** Channel interference and high device density.
- **Workaround:** Connect to 5GHz band or wired LAN.
- **Resolution:** Network optimization and AP realignment planned.
- **Status:** Open

### Issue: Shared drive access failure
- **Category:** Network
- **Symptoms:** “Access Denied” or “Network Path Not Found” while accessing shared folders.
- **Root Cause:** SMB service instability on file server.
- **Workaround:** Use OneDrive or SharePoint as temporary access points.
- **Resolution:** File server reboot and patch deployment planned.
- **Status:** Open

### Issue: SAP performance degradation
- **Category:** Application
- **Symptoms:** Slow transactions and unresponsive dashboards.
- **Root Cause:** Database indexing issue in SAP backend.
- **Workaround:** Use batch processing for large data sets.
- **Resolution:** Database re-indexing under process.
- **Status:** Open

### Issue: Zoom video call drops
- **Category:** Collaboration Tools
- **Symptoms:** Users disconnected during long meetings.
- **Root Cause:** ISP routing latency affecting video stability.
- **Workaround:** Disable HD video to reduce bandwidth.
- **Resolution:** Working with ISP for improved routing.
- **Status:** Monitoring

### Issue: OneDrive sync errors
- **Category:** Cloud Storage
- **Symptoms:** Files stuck in “Sync pending” state.
- **Root Cause:** API request throttling by Microsoft servers.
- **Workaround:** Pause and resume sync.
- **Resolution:** Microsoft confirmed fix in next service cycle.
- **Status:** Open

### Issue: Email spam filtering failure
- **Category:** Security/Email
- **Symptoms:** Spam emails appearing in user inbox.
- **Root Cause:** Spam signature updates delayed.
- **Workaround:** Manually block sender domain.
- **Resolution:** Signature update deployed by security operations.
- **Status:** Resolved

### Issue: Antivirus reporting false positives
- **Category:** Security
- **Symptoms:** Legitimate executables marked as malicious.
- **Root Cause:** Heuristic engine bug in antivirus client.
- **Workaround:** Exclude file path temporarily.
- **Resolution:** Updated antivirus definitions deployed.
- **Status:** Resolved

### Issue: High CPU usage on application server
- **Category:** Infrastructure
- **Symptoms:** Web application responds slowly due to CPU spikes.
- **Root Cause:** Memory leak in application service.
- **Workaround:** Restart service during non-peak hours.
- **Resolution:** Hotfix release from vendor under testing.
- **Status:** Open

### Issue: Email search indexing disabled
- **Category:** Email
- **Symptoms:** Users unable to search older mails.
- **Root Cause:** Windows Search service stopped on client machines.
- **Workaround:** Re-enable Windows Search manually.
- **Resolution:** IT pushing script via Endpoint Manager.
- **Status:** Monitoring

### Issue: MFA (Multi-Factor Authentication) delay
- **Category:** Authentication
- **Symptoms:** Delayed OTP or verification prompt timeout.
- **Root Cause:** Third-party MFA provider latency.
- **Workaround:** Retry after 60 seconds.
- **Resolution:** Provider infrastructure upgrade planned.
- **Status:** Open

### Issue: Printer queue frozen
- **Category:** Hardware
- **Symptoms:** Print jobs not clearing after completion.
- **Root Cause:** Print spooler service crash on print server.
- **Workaround:** Manually clear queue from spool folder.
- **Resolution:** Service patched and monitored.
- **Status:** Resolved

### Issue: ServiceNow ticket auto-routing failure
- **Category:** Application
- **Symptoms:** New tickets remain unassigned in queue.
- **Root Cause:** Workflow rule misconfiguration.
- **Workaround:** Manual assignment until rules fixed.
- **Resolution:** Rules corrected by IT admin.
- **Status:** Resolved

### Issue: Shared mailbox permissions error
- **Category:** Email
- **Symptoms:** Users unable to open shared mailbox.
- **Root Cause:** Incorrect role assignment in Exchange Admin Center.
- **Workaround:** Access mailbox via OWA.
- **Resolution:** Admin re-applied correct permission group.
- **Status:** Resolved

### Issue: VPN client upgrade required
- **Category:** VPN
- **Symptoms:** Connection fails with version mismatch error.
- **Root Cause:** Gateway updated; client incompatible.
- **Workaround:** Download latest Cisco AnyConnect client.
- **Resolution:** Version 5.0 deployed organization-wide.
- **Status:** Resolved

### Issue: Outlook add-in crashing
- **Category:** Application
- **Symptoms:** Outlook freezes when add-in loads.
- **Root Cause:** Corrupt registry entry in add-in configuration.
- **Workaround:** Disable add-in from safe mode.
- **Resolution:** Add-in reinstalled successfully.
- **Status:** Resolved

### Issue: ERP system login timeout
- **Category:** Application
- **Symptoms:** Users unable to log in; timeout message displayed.
- **Root Cause:** DB connection pool saturation.
- **Workaround:** Retry after 5 minutes.
- **Resolution:** Increased connection pool size.
- **Status:** Monitoring

### Issue: Proxy authentication pop-up looping
- **Category:** Network/Security
- **Symptoms:** Browser repeatedly asks for credentials.
- **Root Cause:** Policy conflict in proxy authentication settings.
- **Workaround:** Use Edge browser temporarily.
- **Resolution:** Proxy policy fixed on central gateway.
- **Status:** Resolved

### Issue: Endpoint Manager sync errors
- **Category:** Infrastructure
- **Symptoms:** Devices not receiving updates or patches.
- **Root Cause:** Agent heartbeat timeout.
- **Workaround:** Restart agent service.
- **Resolution:** Fixed after database maintenance.
- **Status:** Monitoring

### Issue: Slow login at Windows startup
- **Category:** System
- **Symptoms:** Login takes over 5 minutes to load profile.
- **Root Cause:** GPO script delay and roaming profile sync.
- **Workaround:** Disable large file sync at login.
- **Resolution:** GPO optimization planned.
- **Status:** Open

### Issue: Software deployment failures
- **Category:** Infrastructure
- **Symptoms:** Application not installing via SCCM.
- **Root Cause:** Distribution point misconfiguration.
- **Workaround:** Install manually from IT portal.
- **Resolution:** Re-synced SCCM content library.
- **Status:** Resolved

### Issue: Remote desktop disconnects frequently
- **Category:** Network
- **Symptoms:** RDP sessions dropping randomly.
- **Root Cause:** Idle session timeout in GPO.
- **Workaround:** Extend timeout in local policy.
- **Resolution:** Policy corrected by IT operations.
- **Status:** Resolved

### Issue: Jira dashboards not loading
- **Category:** Application
- **Symptoms:** Users see “500 internal server error.”
- **Root Cause:** API rate limit exceeded.
- **Workaround:** Refresh after few minutes.
- **Resolution:** Increased API threshold.
- **Status:** Monitoring

### Issue: Wi-Fi authentication error
- **Category:** Network
- **Symptoms:** Devices show “Cannot join network.”
- **Root Cause:** Expired RADIUS certificate.
- **Workaround:** Connect via guest network.
- **Resolution:** Certificate renewed and verified.
- **Status:** Resolved

### Issue: Phishing simulation reports delayed
- **Category:** Security
- **Symptoms:** Training completion data missing from dashboard.
- **Root Cause:** API sync issue with reporting portal.
- **Workaround:** Generate manual report.
- **Resolution:** API fix under validation.
- **Status:** Open

### Issue: Email signature template missing
- **Category:** Email
- **Symptoms:** Auto-signature not appearing in Outlook new messages.
- **Root Cause:** Add-in policy not applied.
- **Workaround:** Manually insert signature.
- **Resolution:** Re-applied company signature policy.
- **Status:** Resolved

### Issue: File backup delay
- **Category:** Infrastructure
- **Symptoms:** Nightly backup jobs exceed expected duration.
- **Root Cause:** Large incremental data and limited throughput.
- **Workaround:** Stagger backups by department.
- **Resolution:** Backup window adjusted.
- **Status:** Monitoring
