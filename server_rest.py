from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from agent_manager import get_agent
from smolagents.memory import ActionStep, PlanningStep, FinalAnswerStep
import uvicorn

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

@app.post("/agent/run", response_model=List[AgentStep])
def run_agent(request: AgentRequest):
    try:
        agent = get_agent(request.chat_id)
        stream = agent.run(task=request.task, stream=True, reset=True)

        steps = []
        for step in stream:
            step_type = type(step).__name__

            if isinstance(step, PlanningStep):
                content = step.plan
            elif isinstance(step, ActionStep):
                content = step.observations or ""
            elif isinstance(step, FinalAnswerStep):
                content = step.final_answer or ""
            else:
                content = str(step)

            steps.append(AgentStep(step_type=step_type, content=content))

        return steps

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Use /docs to explore the API."}


# === Самозапуск ===
if __name__ == "__main__":
    print("🚀 Starting REST server on http://localhost:8001")
    uvicorn.run("server_rest:app", host="0.0.0.0", port=8001, reload=False)
