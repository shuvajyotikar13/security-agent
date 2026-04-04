# Stateless Security Agent 🛡️

An event-driven, serverless Data Agent designed to triage enterprise security alerts in real-time. 

This repository demonstrates a foundational **agentic design pattern**: building a highly stateful, context-aware AI agent on a stateless runtime (Google Cloud Run). It decouples compute from memory, allowing the agent to scale from zero to thousands of concurrent investigations without losing its mind or exhausting database connections.

Built with **LangGraph**, **Google Vertex AI**, and the **Model Context Protocol (MCP)**.

## 🏗️ Architecture: The Stateless Paradox

To survive unpredictable, spikey SOC workloads, the agent operates as a pure function: `$f(CurrentState, NewEvent) = (NewState, Action)`. 

We achieve this through a "Mixture of Memories" and Late-Binding Tool execution:

1. **The Scratchpad (RAM):** Intermediate reasoning steps and chain-of-thought live purely in the Cloud Run container's memory during a single HTTP request lifecycle.
2. **Short-Term Memory (External Checkpointer):** Conversational state is hydrated from a fast external database (SQLite locally, Firestore/Postgres in prod) at the start of an execution and persisted at the end.
3. **Long-Term Memory (Semantic):** Episodic knowledge (threat intel, past post-mortems) is retrieved via Vector Search only when relevant.
4. **Late-Binding Tools (MCP):** To avoid serverless timeout and latency bloat, tool schemas are cached and injected into the LLM. The actual MCP connection (via Stdio or SSE) is only established if the model decides a tool must be executed.

## 📂 Repository Structure

```text
stateless-security-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI webhook receiver
│   ├── config.py               # Environment variables & setup
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py            # LangGraph State definition
│   │   ├── graph.py            # Graph compilation and routing
│   │   └── nodes.py            # Execution nodes (LLM, RAG, Tools)
│   └── tools/
│       ├── __init__.py
│       └── mcp_client.py       # Ephemeral MCP connection manager
├── Dockerfile                  # Cloud Run deployment configuration
├── requirements.txt
└── .env.example
```
## 🚀 Quick Start (Local Demo)
This repository is configured out-of-the-box to run a local demonstration using SQLite for memory and npx (Stdio) for local MCP tool execution.

Prerequisites
Python 3.11+

Node.js & npm (Required for the local SQLite MCP server demo)

Google Cloud SDK (gcloud) authenticated to a project with Vertex AI enabled.

### 1. Installation
Clone the repository and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Authentication
Authenticate with Google Cloud so the Vertex AI SDK can access the Gemini models:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Prepare the Mock Tool Environment
Create a dummy SQLite database that our MCP server will query during the demo:

```bash
sqlite3 local_logs.db "CREATE TABLE network_logs (ip TEXT, action TEXT); INSERT INTO network_logs VALUES ('10.0.0.5', 'CONNECTION_REFUSED');"
```

### 4. Run the Agent
Start the FastAPI server:

```bash
uvicorn app.main:api --reload --port 8000
```

### 5. Trigger an Investigation
In a new terminal window, send a webhook simulating an incoming security alert:

```bash
curl -X POST http://localhost:8000/webhook/triage \
     -H "Content-Type: application/json" \
     -d '{
           "incident_id": "INC-001",
           "telemetry": "Alert: Anomalous traffic detected. Can you check the logs for IP 10.0.0.5?"
         }'
```

The agent will hydrate its state, dynamically spin up the MCP server, query local_logs.db, summarize the finding, and save its state.

You can follow up on the same thread:

```bash
curl -X POST http://localhost:8000/webhook/triage \
     -H "Content-Type: application/json" \
     -d '{
           "incident_id": "INC-001",
           "telemetry": "What did you just find?"
         }'
```

## ☁️ Moving to Production (Google Cloud Run)
To take this from the laptop to a secure, enterprise deployment, three architectural shifts are required:

1. **Swap the Checkpointer**: Change SqliteSaver in app/agent/graph.py to AsyncPostgresSaver (connected to Cloud SQL) or a Firestore-backed checkpointer. This provides the necessary Optimistic Concurrency Control (OCC) to prevent race conditions during scale-out.

2. **Implement Connection Pooling**: If using Postgres for short/long-term memory, route your container connections through PgBouncer or the Cloud SQL Auth Proxy to prevent the serverless instances from exhausting database connections.

3. **Secure the MCP Transport**: Move away from stdio_client. Host your MCP servers independently and connect your agent to them using the sse_client over HTTPS, secured by Google Cloud IAM service-to-service authentication.
