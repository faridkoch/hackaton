import os
import pickle
from typing import Dict
from dotenv import load_dotenv

from sn_smolagent_tools_demo import (
    SignNowSmolagentsCodeAgent,
    access_token_from_login_password, SignNowSmolagentsToolCallingAgent
)
from smolagents.monitoring import AgentLogger
from smolagents.memory import AgentError, TaskStep


AGENTS: Dict[str, SignNowSmolagentsToolCallingAgent] = {}
ACCESS_TOKEN_CACHE = None
MEMORY_DIR = "agent_memory"
params=load_dotenv('.env')

def ensure_memory_dir():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)


def memory_file_path(chat_id: str) -> str:
    ensure_memory_dir()
    return os.path.join(MEMORY_DIR, f"{chat_id}.pkl")


def get_agent(chat_id: str) -> SignNowSmolagentsToolCallingAgent:
    global ACCESS_TOKEN_CACHE

    if chat_id not in AGENTS:
        if ACCESS_TOKEN_CACHE is None:
            ACCESS_TOKEN_CACHE = access_token_from_login_password(
                os.environ.get("SIGNNOW_LOGIN"),
                os.environ.get("SIGNNOW_PASSWORD"),
                os.environ.get("SIGNNOW_BASIC_AUTH")
            )

        agent = SignNowSmolagentsToolCallingAgent(
            access_token=ACCESS_TOKEN_CACHE,
            model=agent_model(),
            planning_interval=10,
            verbosity_level=2,
            max_steps=20,
        )
        load_memory(agent, chat_id)
        AGENTS[chat_id] = agent

    return AGENTS[chat_id]


def agent_model():
    from smolagents import OpenAIServerModel

    return OpenAIServerModel(
        model_id="gpt-4o",
        api_base="https://api.openai.com/v1",
        api_key=os.environ.get("OPENAI_API_KEY")
    )


def save_memory(agent: SignNowSmolagentsToolCallingAgent, chat_id: str):
    path = memory_file_path(chat_id)
    with open(path, "wb") as f:
        pickle.dump(agent.memory, f)


def load_memory(agent: SignNowSmolagentsToolCallingAgent, chat_id: str):
    path = memory_file_path(chat_id)
    if not os.path.exists(path):
        print(f"🆕 No memory for chat_id: {chat_id}")
        return


    with open(path, "rb") as f:
        memory = pickle.load(f)

        # Подменим logger
        memory.logger = agent.logger

        for step in memory.steps:
            if hasattr(step, "error") and isinstance(step.error, AgentError):
                step.error.logger = agent.logger

        agent.memory = memory
        agent.step_number = len(memory.steps) + 1

        # 🧠 Найдём последний Task
        task_found = False
        for step in reversed(memory.steps):
            if isinstance(step, TaskStep) and step.task:
                agent.task = step.task
                task_found = True
                break

        if hasattr(agent.memory, "state"):
            agent.state = agent.memory.state

        if not task_found:
            print(f"⚠️ Task not restored for chat_id {chat_id}, run may not work properly.")

        print(f"✅ Loaded memory for chat_id: {chat_id}")

