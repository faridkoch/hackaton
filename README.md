# 📡 WebSocket API — AI Agent Interaction

This document describes how to communicate with the AI agent via WebSocket in a step-based streaming mode.

---

## 🔌 WebSocket Connection

- **URL:** `ws://<host>:8765/chat/{chat_id}`
- **Example:** `ws://localhost:8765/chat/chat_id47`

> `chat_id` is a unique session identifier — one chat ID = one user dialog.

---

## 📤 Message Format (Client → Server)

### Request Message

```json
{
  "type": "client",
  "message": "get all contacts",
  "message_id": "abc123"
}
```

| Field         | Type    | Required | Description                                |
|---------------|---------|----------|--------------------------------------------|
| `type`        | string  | ✅       | Always `"client"`                          |
| `message`     | string  | ✅       | User's query or instruction                |
| `message_id`  | string  | ✅       | Unique message ID from frontend            |

---

## 📥 Server Responses

The agent replies with a **stream of step messages**, each representing an internal step. At the end, a final signal is sent.

### 1. `agent_step` — Intermediate or Final Step

```json
{
  "type": "agent_step",
  "step_type": "ActionStep",
  "message": "Execution logs...\nLast output: [...]",
  "message_id": "abc123",
  "chat_id": "chat_id47"
}
```

| Field         | Type    | Description                                                             |
|---------------|---------|-------------------------------------------------------------------------|
| `type`        | string  | Always `"agent_step"`                                                   |
| `step_type`   | string  | One of `PlanningStep`, `ActionStep`, `FinalAnswerStep`, etc.            |
| `message`     | string  | Contents of the step (plan, output, final result)                        |
| `message_id`  | string  | Refers to the original client message                                   |
| `chat_id`     | string  | Session ID                                                              |

---

### 2. `message_end` — Final Signal

```json
{
  "type": "message_end",
  "message_id": "abc123",
  "chat_id": "chat_id47"
}
```

| Field         | Type    | Description                                  |
|---------------|---------|----------------------------------------------|
| `type`        | string  | Always `"message_end"`                       |
| `message_id`  | string  | Refers to the original client message       |
| `chat_id`     | string  | Session ID                                  |

---

### 3. `agent_error` — Error Handling

```json
{
  "type": "agent_error",
  "error": "Description of the error",
  "chat_id": "chat_id47"
}
```

| Field         | Type    | Description                                  |
|---------------|---------|----------------------------------------------|
| `type`        | string  | Always `"agent_error"`                       |
| `error`       | string  | Human-readable error message                 |
| `chat_id`     | string  | Session ID                                  |

---

## 🧠 UI Recommendations

| `step_type`        | Suggested UI Display                      |
|--------------------|-------------------------------------------|
| `PlanningStep`     | 💡 Plan or internal reasoning              |
| `ActionStep`       | ⚙️ Execution logs, tool usage              |
| `FinalAnswerStep`  | ✅ Final output to be shown to the user    |
| `message_end`      | 🟢 Hide spinner / input lock               |

---

## 💬 Example Flow

1. **Client sends:**

```json
{
  "type": "client",
  "message": "get all contacts",
  "message_id": "abc123"
}
```

2. **Server replies:**

- `agent_step` (ActionStep) — logs or intermediate info  
- `agent_step` (FinalAnswerStep) — final result  
- `message_end` — signals completion

---



---

## 📚 Retrieving Chat History

In addition to WebSocket interaction, you can retrieve the full conversation history for any `chat_id` using a REST API.

### 🔗 Endpoint

```
GET /history/{chat_id}
```

- **Example:** `http://localhost:8000/history/chat_id47`

### 🔁 Response Format

```json
[
  {
    "role": "user",
    "content": "get all contacts",
    "step_type": null,
    "timestamp": "2025-04-03 20:45:12"
  },
  {
    "role": "agent",
    "content": "Execution logs...\nLast output: [...]",
    "step_type": "ActionStep",
    "timestamp": "2025-04-03 20:45:15"
  },
  {
    "role": "agent",
    "content": "[Final result array or message]",
    "step_type": "FinalAnswerStep",
    "timestamp": "2025-04-03 20:45:16"
  }
]
```

| Field       | Type    | Description                                      |
|-------------|---------|--------------------------------------------------|
| `role`      | string  | `"user"` or `"agent"`                            |
| `content`   | string  | Message content                                  |
| `step_type` | string  | Optional: Agent step type (`ActionStep`, etc.)  |
| `timestamp` | string  | ISO timestamp of the message                     |

> Useful for showing full chat log in chronological order.

---

## 🚀 Stateless REST API

You can run the AI agent in a stateless mode via a synchronous REST endpoint. This does not use or store any memory — it simply returns the reasoning steps and final result for a given task.

### 🔗 Endpoint

```
POST /agent/run
```

### 📥 Request Body

```json
{
  "chat_id": "chat_id47",
  "task": "get all contacts"
}
```

| Field     | Type    | Description                              |
|-----------|---------|------------------------------------------|
| chat_id   | ?string | Identifier for the session, not required |
| task      | string  | Instruction for the AI agent             |

### 📤 Response

Returns a list of reasoning steps in order:

```json
[
  {
    "step_type": "PlanningStep",
    "content": "I will call the tool to get contacts..."
  },
  {
    "step_type": "ActionStep",
    "content": "Execution logs:\n[{'email': ...}]"
  },
  {
    "step_type": "FinalAnswerStep",
    "content": "[{'name': ..., 'email': ...}]"
  }
]
```

---

### ▶️ Running the server

You can run it directly with Python:

```bash
python server_rest.py
```

It will start on:

```
http://localhost:8001
```

> This mode is useful for quick demo requests, stateless integrations, or calling the agent without tracking user history.

