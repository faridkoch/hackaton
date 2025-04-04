import asyncio
import websockets
import json
import os
import random
import string
from dotenv import load_dotenv
from history import save_message
from agent_manager import get_agent, save_memory
from history import init_db, get_history
load_dotenv()


def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def start_agent(task, websocket, chat_id):
    agent = get_agent(chat_id)
    print(task)
    save_message(chat_id, "user", task, message_id=generate_random_string(), step_type="user_message")
    stream = agent.run(task=task, stream=True, reset=False)
    message_id = generate_random_string()

    async def send_step(step):
        step_type = type(step).__name__
        payload = {
            "type": "agent_step",
            "step_type": step_type,
            "message": None,
            "message_id": message_id,
            "chat_id": chat_id,
        }

        if hasattr(step, "plan"):
            payload["message"] = step.plan
        elif hasattr(step, "observations"):
            payload["message"] = step.observations
        elif hasattr(step, "final_answer"):
            payload["message"] = step.final_answer

        await websocket.send(json.dumps(payload))

    try:
        for step in stream:
            await send_step(step)
            save_memory(agent, chat_id)
            content = getattr(step, "plan", None) or getattr(step, "observations", None) or getattr(step,
                                                                                                    "final_answer",
                                                                                                    None)
            if content:
                save_message(chat_id, "agent", content, message_id, step_type=type(step).__name__)
        await websocket.send(json.dumps({
            "type": "message_end",
            "message_id": message_id,
            "chat_id": chat_id,
        }))

    except Exception as e:
        await websocket.send(json.dumps({
            "type": "agent_error",
            "error": str(e),
            "chat_id": chat_id,
        }))


async def handle_client(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)

            path = websocket.request.path
            if path.startswith("/chat/"):
                chat_id = path.split("/chat/")[1]
                print(f"Chat ID: {chat_id}")
            else:
                print(f"Unexpected path: {path}")
                await websocket.close(code=1008, reason="Invalid path")
                return
            if data["type"] == "get_history":
                history = get_history(chat_id)
                await websocket.send(json.dumps({
                    "type": "chat_history",
                    "chat_id": chat_id,
                    "history": history,
                }))
                continue
            if not all(k in data for k in ["message", "type", "message_id"]):
                await websocket.send(json.dumps({"error": "Missing fields in JSON"}))
                continue

            await start_agent(task=data["message"], websocket=websocket, chat_id=chat_id)

        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON format"}))


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765, ping_interval=None, ping_timeout=None, max_size=2**20):
        print("✅ WebSocket server started on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    init_db()
    asyncio.run(main())
