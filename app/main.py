from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agent.graph import workflow

# This global variable will hold our compiled graph
agent_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    global agent_app
    # Open the async SQLite connection
    async with AsyncSqliteSaver.from_conn_string("short_term_memory.db") as saver:
        # Compile the graph using the async checkpointer
        agent_app = workflow.compile(checkpointer=saver)
        yield
    # --- Shutdown ---
    # The connection safely closes automatically when the server stops

api = FastAPI(lifespan=lifespan)

class AlertPayload(BaseModel):
    incident_id: str
    telemetry: str

@api.post("/webhook/triage")
async def triage_alert(payload: AlertPayload):
    # Hydrate state using the incident_id
    config = {"configurable": {"thread_id": payload.incident_id}}
    user_message = {"role": "user", "content": payload.telemetry}
    
    # Run the graph asynchronously
    final_state = await agent_app.ainvoke({"messages": [user_message]}, config=config)
    
    return {
        "incident_id": payload.incident_id,
        "agent_response": final_state["messages"][-1].content
    }
