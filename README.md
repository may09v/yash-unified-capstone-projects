# IT Help Desk API

Intelligent ticket creation system with AI-powered categorization, prioritization, team routing, and RAG-based knowledge retrieval.

## Features

- **Natural Language Ticket Creation**: Create tickets from plain text with LLM-powered intent detection
- **Auto-Categorization**: Automatically categorizes issues (Network, Software, Hardware, Security, Database)
- **Auto-Prioritization**: Assigns priority levels (Low, Medium, High, Critical)
- **Smart Team Routing**: Routes tickets to specialized teams
- **Confirmation Workflow**: Review and confirm before finalizing tickets
- **Self-Service Suggestions**: Provides potential solutions
- **RAG Knowledge Base**: Query comprehensive IT knowledge base for instant answers
- **Vector Search**: Milvus-powered semantic search across knowledge documents
- **PostgreSQL Storage**: Confirmed tickets saved to database
- **Conversation Context**: Maintains session-based conversation history

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup PostgreSQL database:
```bash
# Create database
createdb helpdesk_db

# Or using psql
psql -U postgres
CREATE DATABASE helpdesk_db;
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Configure `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-40
DATABASE_URL=postgresql://postgres:password@localhost:5432/helpdesk_db
MILVUS_URI=your_milvus_uri
MILVUS_TOKEN=your_milvus_token
MILVUS_COLLECTION_NAME=ticket_creation_knowledge
```

5. Run the API:
```bash
python main.py
```

API will be available at `http://localhost:8000`

## Database Schema

**Tickets Table:**
- `ticket_id` (String, Primary Key)
- `user_id` (String, Indexed)
- `title` (String)
- `description` (Text)
- `category` (String)
- `priority` (String)
- `assigned_team` (String)
- `suggested_solution` (Text)
- `status` (String)
- `created_at` (DateTime)
- `confirmed_at` (DateTime)

## API Usage

### Ticket Management: `/ticket`

**Create Ticket:**
```json
POST /ticket
{
  "user_input": "My laptop won't connect to the office WiFi",
  "user_id": "john.doe@company.com"
}
```

**Response:**
```json
{
  "ticket_id": "uuid-generated-id",
  "session_id": "session-uuid",
  "status": "pending_confirmation",
  "message": "Ticket created. Please review and confirm the details.",
  "ticket_data": {
    "title": "WiFi Connection Issue",
    "description": "Laptop unable to connect to office WiFi",
    "category": "Network",
    "priority": "Medium",
    "assigned_team": "Network Infrastructure Team",
    "suggested_solution": "Check WiFi credentials and network settings"
  },
  "detected_action": "create"
}
```

**Confirm (saves to database):**
```json
POST /ticket
{
  "user_input": "Yes, that's correct",
  "user_id": "john.doe@company.com",
  "session_id": "session-id-from-previous-response"
}
```

**Modify:**
```json
POST /ticket
{
  "user_input": "Actually it's a VPN connection issue",
  "user_id": "john.doe@company.com",
  "session_id": "session-id-from-previous-response"
}
```

**Cancel:**
```json
POST /ticket
{
  "user_input": "No, cancel this ticket",
  "user_id": "john.doe@company.com",
  "session_id": "session-id-from-previous-response"
}
```

### Knowledge Base Query: `/rag/ask`

**Query Knowledge Base:**
```json
POST /rag/ask
{
  "query": "How do I reset my password?",
  "top_k": 6,
  "debug": false
}
```

**Response:**
```json
{
  "query": "How do I reset my password?",
  "result": "To reset your password, follow these steps: 1. Go to the login page...",
  "chunks_used": 3,
  "chunks": null
}
```

### Ticket Retrieval

**Get User's Tickets:**
```
GET /tickets/user/{user_id}
```

**Get Specific Ticket:**
```
GET /ticket/{ticket_id}
```

## Specialized Teams

- **Network Infrastructure Team**: Network, connectivity, VPN, firewall issues
- **Software & Applications Team**: Software installation, updates, licenses
- **Hardware Support Team**: Laptop, desktop, printer, peripheral issues
- **Security & Access Team**: Password, access, permissions, login issues
- **Database & Systems Team**: Database, server, backup, storage issues

## AI-Powered Intent Detection

The system uses LLM to automatically detect user intent from natural language:
- **Create**: New ticket requests
- **Confirm**: Approval of pending tickets
- **Modify**: Updates to existing tickets
- **Cancel**: Cancellation requests

## Knowledge Base

Comprehensive IT knowledge base with 15 specialized documents:
- Troubleshooting Library
- Known Issues Database
- Network Configurations
- Asset Registry
- Resolution Playbooks
- SLA Definitions
- Error Codes Reference
- Software Catalog
- HR IT Policies
- Security Guidelines
- Incident History
- Troubleshooting FAQs
- Permission Records
- Monitoring Logs
- System Configurations

## Project Structure

```
IT-HELP-DESK/
├── config/
│   ├── model_config.yaml
│   ├── prompt_templates.yaml
│   └── logging_config.yaml
├── src/
│   ├── database/
│   │   ├── connection.py
│   │   ├── malvius_integration.py
│   │   └── models.py
│   ├── llm/
│   │   └── base.py
│   ├── prompt_engineering/
│   │   └── templates.py
│   ├── rag/
│   │   └── rag.py
│   ├── utils/
│   │   └── config_loader.py
│   └── handlers/
│       └── ticket_handler.py
├── knowledgebase/
│   └── handle/
│       ├── 01_troubleshooting_library.md
│       ├── 02_known_issues.md
│       ├── ... (15 knowledge documents)
│       └── 15_system_configurations.md
├── data/
│   ├── cache/
│   ├── prompts/
│   ├── outputs/
│   ├── embeddings/
│   └── vector/
│       └── vector.py
├── .env
├── .env.example
├── main.py
├── requirements.txt
└── README.md
```
