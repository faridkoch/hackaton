from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from agent_manager import get_agent
from smolagents.memory import ActionStep, PlanningStep, FinalAnswerStep
import uvicorn
import json

app = FastAPI(
    title="Stateless AI Agent REST API",
    description="A stateless API that returns reasoning steps of the agent for each task.",
    version="1.0.0"
)

class AgentRequest(BaseModel):
    chat_id: str = "default_chat_id"
    task: str

class AgentStep(BaseModel):
    step_type: str
    content: str

@app.post("/agent/run")
def run_agent(request: AgentRequest):
    try:
        agent = get_agent(request.chat_id)
        stream = agent.run(task=request.task, stream=True, reset=True)

        content = {"message": "No content"}
        for step in stream:
            step_type = type(step).__name__

            if isinstance(step, FinalAnswerStep):
                content = step.final_answer or ""
                content = normalize_content(content)

        return content

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Use /docs to explore the API."}

def normalize_content(content):
    if isinstance(content, (dict, list)):
        return content  # уже JSON-совместимый объект

    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return {"message": str(content)}

if __name__ == "__main__":
    print("🚀 Starting REST server on http://localhost:8001")
    uvicorn.run("server_rest:app", host="0.0.0.0", port=8001, reload=False)
