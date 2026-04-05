from fastapi import FastAPI
from pydantic import BaseModel
from app.agent.graph import agent_app

api = FastAPI()

class AlertPayload(BaseModel):
    incident_id: str
    telemetry: str

@api.post("/webhook/triage")
async def triage_alert(payload: AlertPayload):
    # Hydrate state using the incident_id
    config = {"configurable": {"thread_id": payload.incident_id}}
    user_message = {"role": "user", "content": payload.telemetry}
    
    # Run the graph statelessly
    final_state = await agent_app.ainvoke({"messages": [user_message]}, config=config)
    
    return {
        "incident_id": payload.incident_id,
        "agent_response": final_state["messages"][-1].content
    }
