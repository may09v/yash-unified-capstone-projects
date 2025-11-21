# Permission Records (Expanded - Generic Corporate IT)

## 1. Overview
This document outlines the access permissions, user roles, and approval workflows across corporate systems, applications, and file repositories.  
Access is managed through centralized identity services (Active Directory and Azure AD) to ensure least-privilege principles and compliance with company security policies.

---

## 2. User Role Matrix

| Role | Description | Typical Access Level |
|------|--------------|----------------------|
| **System Administrator** | Manages servers, user accounts, and configurations. | Full administrative rights to all IT systems. |
| **Power User** | Departmental IT support or advanced users. | Elevated permissions within their department. |
| **Standard User** | Regular employees across all departments. | Access to daily tools (email, VPN, file share). |
| **Contractor** | Temporary users or external partners. | Restricted access to project-related folders only. |
| **Manager** | Department heads and team leads. | Access to team data, reports, and dashboards. |
| **Service Account** | Non-human accounts used for automation. | Limited to specific service functions only. |

---

## 3. File Share Permissions

| Drive/Folder | Department | Access Type | Authorized Users | Notes |
|---------------|-------------|--------------|------------------|--------|
| `\\corp-server\FinanceShare` | Finance | Read/Write | John Carter (Finance Analyst), Ananya Gupta (Finance Manager) | Access restricted to Finance users only. |
| `\\corp-server\HRShare` | HR | Read/Write | Priya Mehta (HR Coordinator), Alex Thomas (HR Admin) | Stores employee records and policy documents. |
| `\\corp-server\ITDocs` | IT | Full Control | Ravi Kumar (System Admin), David Smith (Network Lead) | Access restricted to IT Operations. |
| `\\corp-server\Projects` | Engineering | Read/Write | Rahul Iyer (DevOps Engineer), Sneha Patel (Developer) | Shared development repository. |
| `\\corp-server\MarketingAssets` | Marketing | Read/Write | Sarah Lee (Marketing Executive), Daniel Parker (Creative Lead) | Contains campaign and media materials. |
| `\\corp-server\Public` | All Departments | Read Only | All Employees | Common announcements and forms. |

---

## 4. Application Access Records

| Application | Access Level | Authorized Users | Managed By |
|--------------|--------------|------------------|-------------|
| Microsoft 365 | Standard User | All Employees | IT Operations |
| SAP HANA | Finance Module Access | John Carter (Finance Analyst), Ananya Gupta (Finance Manager) | Finance Systems Team |
| Jira Software | Developer, QA | Rahul Iyer (DevOps Engineer), Sneha Patel (Developer) | Development Team |
| ServiceNow | IT Agents | Ravi Kumar (System Admin), Priya Mehta (HR Coordinator - limited HR module) | ITSM Admin |
| Salesforce CRM | Read/Write | Sarah Lee (Sales Manager), Daniel Parker (Marketing Lead) | CRM Team |
| Zoom Cloud Meetings | User License | All Employees | IT Collaboration |
| Teams Admin Portal | Admin Access | Ravi Kumar (System Admin), David Smith (Network Lead) | IT Collaboration |
| Okta Admin Console | Read/Write | Security Admins | Security Operations |
| SCCM Console | Admin | Endpoint Management Team | IT Infrastructure |

---

## 5. System and Server Access

| System | Type | Access Level | Authorized Users | Authentication Method |
|---------|------|---------------|------------------|-----------------------|
| AD Domain Controllers | Core Infrastructure | Admin | Ravi Kumar, David Smith | Domain Admin credentials |
| File Server | Windows Server | Full Control | IT Operations | AD-based |
| VPN Gateway | Cisco ASA | Admin | Network Team | Local + LDAP |
| Database Server | SQL | DBA Access | Database Team | AD Group: SQL_Admins |
| Backup Server | Veeam | Operator | Backup Team | Local User |
| SCCM Server | Windows Server | Full Control | Endpoint Team | AD Integration |
| HRMS Server | Web App | Read/Write | HR Admins | Azure AD SSO |
| Git Repository | Cloud | Write Access | Developers | GitHub SSO |
| Print Server | Windows Server | Read/Write | IT Support | Domain Auth |

---

## 6. Cloud Services Permissions

| Service | Access Role | Authorized Users | Access Description |
|----------|--------------|------------------|--------------------|
| OneDrive for Business | Owner | All Employees | Each user owns their personal cloud storage. |
| SharePoint HR Site | Contributor | Priya Mehta (HR Coordinator) | Can upload HR policies and employee docs. |
| SharePoint IT Site | Owner | Ravi Kumar (System Admin), David Smith (Network Lead) | Manage IT documentation. |
| SharePoint Finance Site | Editor | Ananya Gupta (Finance Manager) | Edit and approve finance documents. |
| Azure Portal | Contributor | Cloud Admins | Manage virtual machines and cloud resources. |
| Teams Channel “Engineering” | Member | Rahul Iyer, Sneha Patel | Can share project updates. |
| Teams Channel “All Staff” | Member | All Employees | Company-wide communication. |
| Outlook Shared Mailbox “Helpdesk” | Full Access | Service Desk Team | Used for incoming IT support requests. |

---

## 7. Access Request and Approval Workflow

### Workflow Steps:
1. **User Submission:** Employee submits access request via **ServiceNow** → “Access Management” form.  
2. **Manager Approval:** Manager reviews and approves access based on job relevance.  
3. **System Owner Review:** Application or system owner validates justification.  
4. **IT Implementation:** IT assigns access through **Active Directory** or **Azure AD Group**.  
5. **Confirmation:** User receives email confirmation and is asked to validate access.  

### Common Access Request Types:
- File Share Access (Read / Write)
- Application Access (SAP, Jira, ServiceNow)
- VPN Access for Remote Work
- Admin or Elevated Rights Request
- Temporary Access (Project Duration)

---

## 8. Quarterly Review and Revocation Policy

### Review Policy
- Departmental access is reviewed every **90 days** by department heads.  
- HR initiates review for onboarding and offboarding users.  
- All admin-level accounts must undergo **bi-monthly** review by the Security Team.

### Revocation Process
- When an employee leaves, access is automatically revoked via **HR-IT Integration workflow**.  
- Expired contractor accounts are disabled immediately.  
- Shared access (e.g., project folders) is revoked after project closure.  

### Tools Used
- Active Directory (Group Membership Management)  
- Azure AD Access Review  
- ServiceNow Access Audit Reports  

---

## 9. Notes and Recommendations
- Maintain least-privilege access for all roles.  
- Ensure MFA is enabled for privileged accounts.  
- Log all access changes in **ServiceNow Change Records**.  
- Review permissions before departmental transfers.  
- Report unauthorized access immediately to **security@company.com**.

---
