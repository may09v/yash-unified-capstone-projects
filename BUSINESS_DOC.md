# Corporate Travel Agent - Business Documentation

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Audience**: Business Stakeholders, Project Managers, Approvers, Travel Desk Users

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Objectives](#business-objectives)
3. [System Overview](#system-overview)
4. [User Roles & Responsibilities](#user-roles--responsibilities)
5. [Business Processes](#business-processes)
6. [Travel Policy Integration](#travel-policy-integration)
7. [Benefits & ROI](#benefits--roi)
8. [User Workflows](#user-workflows)
9. [Data Management](#data-management)
10. [Compliance & Governance](#compliance--governance)

---

## Executive Summary

The **Corporate Travel Agent** is an AI-powered system designed to streamline and automate corporate travel management across enterprise organizations. It replaces manual travel request processing with an intelligent, role-based workflow that:

- ✅ **Reduces processing time** from days to minutes
- ✅ **Ensures policy compliance** through automated checks
- ✅ **Improves employee experience** with natural language interface
- ✅ **Provides complete visibility** into travel spend and approvals
- ✅ **Enables self-service** travel planning and booking

The system manages the complete travel lifecycle: from initial travel requests through multiple approval stages to final booking and completion, serving **9 distinct user roles** in an enterprise.

---

## Business Objectives

### Primary Objectives

1. **Streamline Travel Requisition Process**
   - Reduce manual data entry by 80%
   - Enable employees to submit requests in <5 minutes
   - Automatic form validation and compliance checking

2. **Accelerate Approvals**
   - Multi-level approval chain with clear routing
   - Automated status tracking and escalations
   - Reduce approval cycle from 7 days to 2 days

3. **Ensure Policy Compliance**
   - Intelligent policy QA for employee questions
   - Automatic cost validation against budgets
   - Complete audit trail for all decisions

4. **Optimize Travel Spend**
   - Preferred vendor pricing and discounts
   - Real-time flight/hotel inventory
   - Cost forecasting and analytics

5. **Improve User Experience**
   - Conversational AI for natural interactions
   - Multi-device access (web, mobile)
   - Self-service tools with expert guidance

---

## System Overview

### What is the Corporate Travel Agent?

An AI-powered platform that acts as a **travel advisor, policy expert, and workflow coordinator**:

```
┌────────────────────────────────────────────────────────────────┐
│          CORPORATE TRAVEL AGENT PLATFORM                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  AI Assistant    │  │  Policy Expert  │  │  Booking     │ │
│  │  (LangGraph)     │  │  (RAG + LLM)    │  │  Engine      │ │
│  └──────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                    │                    │         │
│           └────────────────────┴────────────────────┘         │
│                        │                                      │
│              ┌─────────▼──────────┐                          │
│              │  Multi-Role Engine │                          │
│              │  (9 User Roles)    │                          │
│              └─────────┬──────────┘                          │
│                        │                                      │
│  ┌─────────────────────┼─────────────────────┐              │
│  │                     │                     │              │
│  ▼                     ▼                     ▼              │
│ Workflow           Database           Inventory           │
│ Manager            (PostgreSQL)       (Flights/Hotels)   │
│                                                            │
└────────────────────────────────────────────────────────────────┘
```

### Key Capabilities

| Capability | Description | Benefit |
|-----------|-------------|---------|
| **Natural Language Interface** | Chat-based travel requests and queries | Reduces training; improves adoption |
| **Multi-Level Approvals** | 9-role approval chain with comments | Maintains control; ensures compliance |
| **Policy QA System** | Intelligent answers to policy questions | Reduces support tickets; improves compliance |
| **Travel Inventory** | Real-time flights and hotels with pricing | Faster booking; better rates |
| **Session Memory** | Maintains conversation context | Seamless multi-turn interactions |
| **Document Upload** | Store and index policy documents | Centralized policy repository |
| **Cost Tracking** | Budget monitoring and reporting | Better financial control |

---

## User Roles & Responsibilities

### 1. Employee
**Who**: Staff members traveling for business  
**Key Responsibilities**:
- Create travel requisitions via chat interface
- Provide travel details (destination, dates, purpose, budget)
- Query travel policies before planning
- Submit requests for approval
- Save draft requests for later submission
- Track approval status

**Tools Available**:
- `create_trf_draft` - Start travel request
- `submit_trf` - Submit for approval
- `list_employee_drafts` - View saved drafts
- `list_employee_trfs` - View all submissions
- `get_trf_status` - Check approval progress
- `get_trf_approval_details` - View detailed status
- `policy_qa` - Ask policy questions

**Example Interaction**:
```
Employee: "I need to travel to New York for a client meeting next month"
Agent: "I'd be happy to help! Let me collect the details...
        - Travel type: Domestic ✓
        - Dates: December 15-20, 2024
        - Purpose: Client meeting
        - Estimated cost: $2,500
        
        I've created draft TRF DRAFT-TRF202500001.
        Ready to submit or make changes?"
```

---

### 2-9. Approvers (IRM → SRM → BUH → SSUH → BGH → SSGH → CFO → Travel Desk)

**Approval Chain Flow**:

```
┌─────┐    ┌─────┐    ┌─────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌─────┐    ┌──────────┐
│ EMP │───→│ IRM │───→│ SRM │───→│ BUH  │───→│ SSUH │───→│ BGH  │───→│SSGH │───→│   CFO   │───→
└─────┘    └─────┘    └─────┘    └──────┘    └──────┘    └──────┘    └─────┘    └──────────┘
             First    Second     Business    Strategic   Business    Senior    Final Finance
             Manager   Manager    Head        Head      Group Head    Group      Review
                                                        Head
```

#### IRM (Immediate Reporting Manager)
- **Authority**: First-level approval
- **Decision Point**: Employee's direct manager approval
- **Key Considerations**: Direct oversight of traveler
- **Approval Window**: Within 24 hours
- **Tools**: `get_pending_irm_applications`, `approve_trf`, `reject_trf`, `get_trf_status`

#### SRM (Senior/Second Reporting Manager)
- **Authority**: Second-level approval
- **Decision Point**: Senior management oversight
- **Key Considerations**: Team budget alignment
- **Approval Window**: Within 48 hours
- **Tools**: Same as IRM + `list_employee_trfs`

#### BUH (Business Unit Head)
- **Authority**: Third-level approval (business unit)
- **Decision Point**: Budget and operational impact
- **Key Considerations**: Unit budget utilization, travel frequency
- **Approval Window**: Within 72 hours
- **Tools**: Same as SRM

#### SSUH (Senior/Secondary Unit Head)
- **Authority**: Strategic unit-level approval
- **Decision Point**: Strategic business value
- **Key Considerations**: Strategic alignment, business criticality
- **Approval Window**: Within 48 hours

#### BGH (Business Group Head)
- **Authority**: Group-level leadership
- **Decision Point**: Group-wide strategy alignment
- **Key Considerations**: Group compliance, cost visibility
- **Approval Window**: Within 72 hours

#### SSGH (Senior/Secondary Group Head)
- **Authority**: Senior leadership
- **Decision Point**: Company-wide strategic alignment
- **Key Considerations**: Executive approval for high-value requests
- **Approval Window**: Within 48 hours

#### CFO (Chief Financial Officer)
- **Authority**: Final financial review
- **Decision Point**: Overall company financial impact
- **Key Considerations**: Total cost, financial policy compliance
- **Approval Window**: Within 24 hours
- **Action**: Approves and routes to Travel Desk for execution

#### Travel Desk
- **Authority**: Execution and booking
- **Key Responsibilities**:
  - Review approved travel requests
  - Search for best flight/hotel options
  - Complete bookings with preferred vendors
  - Coordinate special arrangements
  - Update employee with itinerary
- **Tools**: `search_flights`, `confirm_flight_booking`, `search_hotels`, `confirm_hotel_booking`, `complete_travel_plan`

---

## Business Processes

### Process 1: Travel Request Creation & Approval

**Trigger**: Employee needs to travel  
**Duration**: 2-7 days (from submission to final approval)

**Steps**:

1. **Employee Creates Request** (5-10 min)
   - Chat interface collects: destination, dates, purpose, estimated cost
   - System validates cost against policy limits
   - Draft saved automatically
   - TRF number generated: `DRAFT-TRF202500001`

2. **Employee Submits Request** (1 min)
   - Employee confirms details
   - System routes to IRM automatically
   - Status: `PENDING_IRM`
   - IRM notified via email

3. **IRM Reviews & Approves** (4-24 hours)
   - Views pending applications
   - Reviews employee details, travel purpose, cost
   - Adds approval comments (e.g., "Direct report for client engagement")
   - Approves or rejects
   - If approved: routes to SRM (status: `PENDING_SRM`)
   - If rejected: Employee notified; can modify and resubmit

4. **Sequential Approvals** (IRM → SRM → BUH → SSUH → BGH → SSGH → CFO)
   - Each level performs review within SLA
   - Each can add comments and evidence
   - Automatic escalation if SLA breached
   - If any approver rejects: Workflow stops, employee notified

5. **Travel Desk Execution** (1-24 hours)
   - CFO approval routes to Travel Desk
   - Status: `PENDING_TRAVEL_DESK`
   - Travel Desk searches flights/hotels
   - Books with preferred vendors
   - Generates itinerary
   - Status: `COMPLETED`

**Approval Statuses**:
```
DRAFT 
  ↓
PENDING_IRM → APPROVED by IRM
  ↓
PENDING_SRM → APPROVED by SRM
  ↓
PENDING_BUH → APPROVED by BUH
  ↓
PENDING_SSUH → APPROVED by SSUH
  ↓
PENDING_BGH → APPROVED by BGH
  ↓
PENDING_SSGH → APPROVED by SSGH
  ↓
PENDING_CFO → APPROVED by CFO
  ↓
PENDING_TRAVEL_DESK → COMPLETED
  ↓
COMPLETED
```

**Rejection Flow**: At any stage, approver can reject with reason → Employee notified → Employee can modify and resubmit

---

### Process 2: Policy Question & Guidance

**Trigger**: Employee or approver has policy question  
**Duration**: Immediate (< 5 seconds)

**Steps**:

1. **User Asks Question**
   ```
   Employee: "What's the maximum daily allowance for New York?"
   or
   "Are flights in business class allowed for T-E2 grade employees?"
   ```

2. **System Retrieves Policies**
   - Search policy documents using embeddings
   - Find relevant policy sections
   - Identify applicable rules and rates

3. **AI Generates Answer**
   - Synthesize information from policy documents
   - Provide clear, concise answer
   - Include source references
   - Suggest next steps if needed

4. **User Gets Guidance**
   ```
   Agent: "For NYC (Tier I city):
   - Maximum daily allowance: $300 (M1+), $200 (E6-E8), $150 (E3-E5)
   - Business class is approved only for flights >6 hours duration
   - Your employee grade determines your tier
   
   Source: Travel Policy Section 3.2.1"
   ```

**Policy Topics Covered**:
- Travel eligibility by employee grade
- Daily allowance rates by city/region
- Accommodation and airline entitlements
- Per diem eligibility
- Travel advance limits
- Advance booking requirements
- Reimbursement documentation
- Special scenarios (client reimbursement, family emergencies)

---

### Process 3: Flight & Hotel Booking

**Trigger**: Travel Desk receives approved TRF  
**Duration**: 1-4 hours

**Steps**:

1. **Search for Flights**
   - Travel Desk specifies: origin, destination, departure date, cabin class
   - System queries flight inventory
   - Results include: flight times, duration, pricing, airline, availability

2. **Select & Book Flight**
   - Travel Desk reviews options against policy (preferred airlines, pricing)
   - Selects best option
   - System books and generates PNR (Passenger Name Record)
   - Confirmation sent to employee

3. **Search for Hotels**
   - Travel Desk specifies: city, check-in, check-out dates
   - System queries hotel inventory
   - Results include: hotel name, rating, price/night, room types, amenities

4. **Select & Book Hotel**
   - Travel Desk reviews options against budget and policy
   - Selects appropriate hotel and room type
   - System books and generates confirmation number
   - Confirmation sent to employee

5. **Complete Travel Plan**
   - Generate full itinerary:
     - Flight details (flight number, times, seats)
     - Hotel details (address, check-in/out, room number)
     - Estimated total cost
     - Emergency contacts
   - Send to employee with all confirmations
   - Update status to `COMPLETED`

---

## Travel Policy Integration

### Policy Framework

The system includes an intelligent **Policy QA** module that answers questions about:

#### A. Employee Grade Categories
- **M1+**: Managing Director and above
- **E6-E8**: Senior employees
- **E3-E5**: Mid-level employees
- **T-E2**: Entry-level employees

#### B. Travel Types

**Domestic Travel**:
- Defined by country borders
- Lower cost tiers
- Tier I cities: Major metros (Delhi, Mumbai, Bangalore) → Higher allowances
- Tier II cities: Secondary cities → Lower allowances
- Coverage: Air, rail, bus by grade

**International Travel**:
- Defined by country borders
- Higher cost allowances
- Regional multipliers:
  - **Americas**: High-cost tier
  - **Europe**: Medium-high tier
  - **Asia (excl. India)**: Medium tier
  - **Africa**: Medium tier
  - **Oceania**: High-cost tier

#### C. Daily Allowance (Per Diem)

**Domestic (Tier I Cities)**:
- M1+: $300/day
- E6-E8: $200/day
- E3-E5: $150/day
- T-E2: $100/day

**International (by region)**:
- Americas: 1.5x base rate
- Europe: 1.3x base rate
- Asia: 1.2x base rate
- Africa: 1.2x base rate
- Oceania: 1.5x base rate

#### D. Accommodation Entitlements

**Domestic**:
- 4-5 star hotels in Tier I cities
- 3-4 star hotels in Tier II cities
- Preferred hotel chains with corporate discounts

**International**:
- 4-5 star hotels in major cities
- Room class based on employee grade
- City-tier multipliers on room rates

#### E. Airline Entitlements

**Cabin Class by Duration**:
- Domestic: Economy (all) / Premium Economy (>2.5 hours, M1+/E6+)
- <6 hours: Economy / Premium Economy (senior grades)
- 6-12 hours: Business (M1+/E6-E8) / Premium Economy (E3-E5) / Economy (T-E2)
- >12 hours: Business (M1+) / Premium Economy (E6-E8) / Economy (E3-E5/T-E2)

**Preferred Airlines**:
- Domestic: Air India, IndiGo (corporate discounts)
- International: Partner airlines with negotiated rates

#### F. Advance Booking Requirements

- Domestic: Minimum 7 days advance
- International: Minimum 14 days advance
- Exceptions: Emergency travel (with VP approval)

#### G. Reimbursement Process

- Require original receipts for expenses >$50
- Submit within 30 days of travel completion
- Manager approval required for reimbursement
- Finance processes within 5 business days

#### H. Special Scenarios

**Client-Borne Expenses**: 
- Pre-approval required from CFO
- Documented billing arrangement

**Family Emergency Travel**:
- Compassionate leave with standard entitlements
- No budget approval required (discretionary)

**Accompanying Family Member**:
- Only for international travel >7 days
- M1+ employees only
- At employee's personal expense (no reimbursement)

---

## Benefits & ROI

### Quantified Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|------------|
| **Avg. Processing Time** | 7 days | 2 days | 71% faster |
| **Manual Data Entry** | 100% | 20% | 80% reduction |
| **Policy Compliance Rate** | 85% | 99% | 16% improvement |
| **Employee Self-Service Rate** | 10% | 90% | 9x increase |
| **Approval Cycle Time** | 72 hours | 24 hours | 67% faster |
| **Travel Desk Booking Time** | 4 hours | 1 hour | 75% faster |

### Financial Impact

**Annual Savings** (for 1000 employees, 30 trips/year average):

```
Direct Labor Savings:
- Reduction in manual processing: 1 FTE (≈$60,000/year)
- Reduction in support tickets: 0.5 FTE (≈$30,000/year)
- Total Labor: $90,000/year

Indirect Savings:
- Better vendor compliance: 5-8% savings on airfare/hotels
  = 30,000 trips × avg $1,500 × 6% = $2,700,000/year
- Reduced last-minute bookings: 3-5% savings
  = $450,000/year
- Improved policy compliance: <2% overspending
  = $300,000/year

Total Annual Savings: ≈ $3.5M+ (for large enterprise)
```

### Non-Financial Benefits

✅ **Improved Employee Experience**: Self-service, chat-based interface reduces friction  
✅ **Better Compliance**: Automated policy enforcement and audit trails  
✅ **Leadership Visibility**: Real-time tracking and analytics  
✅ **Risk Mitigation**: Reduced human error, complete audit trails  
✅ **Scalability**: Handle growth without adding headcount  
✅ **Data-Driven Decisions**: Travel spend analytics and trends  

---

## User Workflows

### Workflow 1: Employee Creates Travel Request

```
┌─ Employee ─────────────────────────────────────────────┐
│                                                        │
│  Step 1: Chat with Agent                              │
│  ───────────────────────────────────────────────────   │
│  "I need to travel to NYC for a client meeting        │
│   on December 15-20, 2024"                            │
│                                                        │
│  Step 2: Provide Details                              │
│  ───────────────────────────────────────────────────   │
│  Agent asks:                                          │
│  - Travel type? → Domestic                            │
│  - Purpose? → Client engagement                       │
│  - Estimated cost? → $2,500                           │
│  - Hotel needed? → Yes                                │
│                                                        │
│  Step 3: Review Draft                                 │
│  ───────────────────────────────────────────────────   │
│  "Draft created: DRAFT-TRF202500001                   │
│   Details confirmed. Submit now or save draft?"       │
│                                                        │
│  Step 4: Submit or Save                               │
│  ───────────────────────────────────────────────────   │
│  - Submit → Routes to IRM (PENDING_IRM)              │
│  - Save Draft → Saved for later editing               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Workflow 2: Manager Reviews & Approves

```
┌─ IRM (Approver) ───────────────────────────────────────┐
│                                                        │
│  Step 1: Check Pending Applications                   │
│  ───────────────────────────────────────────────────   │
│  "Show my pending approvals"                          │
│  → List: TRF202500001, TRF202500002, ...              │
│                                                        │
│  Step 2: Review Details                               │
│  ───────────────────────────────────────────────────   │
│  "Get details for TRF202500001"                       │
│  → Full TRF with: employee info, dates, cost,        │
│    purpose, policy compliance status                  │
│                                                        │
│  Step 3: Make Decision                                │
│  ───────────────────────────────────────────────────   │
│  "Approve TRF202500001 - Direct report for           │
│   client engagement, NYC is key market"               │
│                                                        │
│  Step 4: Confirmation                                 │
│  ───────────────────────────────────────────────────   │
│  "✅ TRF202500001 approved by IRM                      │
│   Routes to SRM for next review"                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Workflow 3: Travel Desk Completes Booking

```
┌─ Travel Desk ──────────────────────────────────────────┐
│                                                        │
│  Step 1: Get Pending Travel Desk Applications         │
│  ───────────────────────────────────────────────────   │
│  "Show pending applications ready for booking"        │
│  → TRF202500001 (NYC, Dec 15-20)                     │
│                                                        │
│  Step 2: Search Flights                               │
│  ───────────────────────────────────────────────────   │
│  "Search flights NYC December 15-20, economy"         │
│  → Options: AI 101 (9am), UA 202 (11am), AA 303 (2pm) │
│                                                        │
│  Step 3: Book Flight                                  │
│  ───────────────────────────────────────────────────   │
│  "Book flight UA 202"                                 │
│  ✅ Booked! PNR: ABC123, Seat: 12A                    │
│                                                        │
│  Step 4: Search Hotels                                │
│  ───────────────────────────────────────────────────   │
│  "Search hotels NYC Dec 15-20 near Times Square"      │
│  → Marriott Marquis, Hilton Midtown, ...             │
│                                                        │
│  Step 5: Book Hotel                                   │
│  ───────────────────────────────────────────────────   │
│  "Book Hilton Midtown room 1250"                      │
│  ✅ Booked! Conf#: HT1234567                          │
│                                                        │
│  Step 6: Complete & Confirm                           │
│  ───────────────────────────────────────────────────   │
│  "Complete travel plan"                               │
│  → Generates itinerary, sends to employee             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Data Management

### Data Collection

The system collects and manages:

**Employee Data**:
- Employee ID, name, email, phone
- Department, designation, location
- Grade level (for policy entitlements)
- Manager information

**Travel Data**:
- Travel purpose and business justification
- Origin/destination cities
- Travel dates
- Travel type (domestic/international)
- Estimated costs and budgets

**Approval Data**:
- Approver comments and decisions
- Timestamps for each approval stage
- Rejection reasons (if applicable)
- Budget utilization tracking

**Booking Data**:
- Flight selections (airline, flight number, cabin class)
- Hotel selections (property, room type, dates)
- Pricing and discounts applied
- Passenger/guest names and confirmations

**Policy Data**:
- Travel policies (in document form)
- Daily allowance rates by grade and city
- Airline/hotel preferences
- Approval limits by role

### Data Security

- **Encryption**: All data encrypted in transit (HTTPS) and at rest (PostgreSQL encryption)
- **Access Control**: Role-based access; users see only their own data
- **Audit Trail**: All actions logged with timestamps
- **Compliance**: GDPR and data retention policies enforced
- **Backup**: Daily automated backups to secure storage

---

## Compliance & Governance

### Policy Compliance

✅ **Automatic Validation**:
- Cost estimates against policy limits
- Travel type eligibility checks
- Grade-based entitlement verification
- Advance booking requirement checks

✅ **Audit Trail**:
- Complete history of all approvals
- Comments and rationale documented
- Rejection reasons recorded
- Final booking confirmation

✅ **Exception Handling**:
- Emergency travel approvals (executive override)
- Budget exceptions (with CFO approval)
- Policy variances (with business justification)

### Governance Framework

**Roles & Responsibilities**:
- **CEO/CFO**: Oversee travel spend trends, set policy
- **Business Heads**: Approve high-value requests, manage unit budgets
- **IRM/SRM**: First-level approvals, ensure business criticality
- **Travel Desk**: Execute approved bookings, vendor management
- **IT/Compliance**: System maintenance, policy enforcement

**KPIs & Metrics**:
- **Processing KPI**: Avg approval cycle < 48 hours
- **Compliance KPI**: 98%+ policy adherence
- **Cost KPI**: 5-8% savings vs. previous year
- **Satisfaction KPI**: 4.5+/5.0 employee satisfaction
- **Utilization KPI**: 90%+ of employees using self-service

**Escalation Process**:
- SLA breach → Automatic escalation to next level
- Missing approval > 48 hours → CFO notification
- Policy variance → Compliance team alert
- Budget overrun → Finance team alert

---

## Frequently Asked Questions

### For Employees

**Q: How long does approval take?**  
A: Typically 2-3 days from submission to Travel Desk booking. Can be faster with responsive approvers.

**Q: Can I edit my travel request after submitting?**  
A: Not after submission. Save as draft if you need flexibility, or wait for rejection to modify.

**Q: What if my request is rejected?**  
A: You'll receive rejection reason. Modify your request and resubmit.

**Q: How do I ask policy questions?**  
A: Chat with the agent using natural language: "What's the max allowance for Dubai?"

**Q: Will my travel be booked automatically?**  
A: Not automatically, but Travel Desk will book within 24 hours of CFO approval.

### For Approvers

**Q: What if I have questions about the TRF?**  
A: You can view full details including employee background, manager approval, and travel purpose.

**Q: What's my approval authority limit?**  
A: No hard limit; your role determines your position in approval chain. CFO is final finance review.

**Q: Can I comment on my approval?**  
A: Yes, comments are recorded and visible to all subsequent approvers for context.

**Q: What if budget is exceeded?**  
A: Flag in comments; CFO will review with Finance team.

### For Travel Desk

**Q: How do I get the best fares?**  
A: System shows preferred airlines/hotels with built-in discounts. Book with these for cost savings.

**Q: Can I book alternative dates?**  
A: Only if approved TRF explicitly allows flexibility. Otherwise, book as requested.

**Q: What if flights/hotels are fully booked?**  
A: Contact Travel Coordinator; escalate to employee to adjust dates.

---

## Support & Escalation

**Support Channels**:
- **Email**: travel-support@company.com
- **Chat**: In-app support chat (Mon-Fri, 9am-6pm)
- **Phone**: +1-XXX-TRAVEL-HELP
- **Portal**: travel.company.com/help

**Escalation**:
1. **Level 1**: Travel Desk support (4-hour response)
2. **Level 2**: Travel Manager (8-hour response)
3. **Level 3**: Director of Travel (24-hour response)

---

## Appendix: Glossary

- **TRF**: Travel Requisition Form - Request for travel approval
- **PNR**: Passenger Name Record - Flight booking confirmation
- **IRM**: Immediate Reporting Manager - Direct manager
- **SRM**: Senior Reporting Manager - Manager's manager
- **BUH**: Business Unit Head - Business unit leader
- **CFO**: Chief Financial Officer - Finance executive
- **Per Diem**: Daily allowance for meals and incidentals
- **Preferred Vendor**: Airlines/hotels with corporate negotiated rates
- **Policy QA**: Question-Answering system for policy guidance
- **RAG**: Retrieval-Augmented Generation - AI method for policy QA

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Next Review**: May 2026  
**Contact**: travel-program@company.com
