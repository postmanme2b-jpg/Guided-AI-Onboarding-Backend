# Challenge Spec Generator AI Agent API Documentation

This API provides real-time and historical message-based interaction with an AI Agent via WebSocket and HTTP.

---

## 🌐 Base URLs

| Type         | URL                                 |
|--------------|--------------------------------------|
| HTTP (GET)   | `http://{AI_AGENT_SERVER_HOST}`      |
| WebSocket    | `ws://{AI_AGENT_SERVER_HOST}`        |

---

## 📥 1. HTTP Endpoint — Get Message History

### `GET /messages?session={sessionId}`

Retrieve all messages exchanged in a session.

- **Method:** `GET`
- **Query Param:** `session` — Session ID (UUID)

### 🔄 Example Request

```http
GET http://{AI_AGENT_SERVER_HOST}/messages?session=d6aab878-1bc9-4ef4-ac14-5eb18bd35f3a
```

### 📦 Response Format

```json
{
  "session": "d6aab878-1bc9-4ef4-ac14-5eb18bd35f3a",
  "messages": [
    {
      "role": "assistant",
      "content": "Welcome message",
      "timestamp": 1751292291
    },
    {
      "role": "user",
      "content": "User's message",
      "timestamp": 1751292540
    }
  ]
}
```

### 📝 Fields

| Field     | Type     | Description                        |
|-----------|----------|------------------------------------|
| session   | `string` | Unique session ID                  |
| messages  | `array`  | List of exchanged messages         |
| role      | `string` | `user` or `assistant`              |
| content   | `string` | Message body (Markdown supported)  |
| timestamp | `number` | Unix timestamp (seconds)           |

---

## 🔌 2. WebSocket Endpoint — Real-Time Messaging

### `ws://{AI_AGENT_SERVER_HOST}/ws?session={sessionId}`

Establish a real-time WebSocket connection to exchange messages within a specific session.

- **Protocol:** WebSocket
- **Query Param:** `session` — Session ID (UUID)

### Connection Example (JavaScript)

```js
const socket = new WebSocket("ws://{AI_AGENT_SERVER_HOST}/ws?session=YOUR_SESSION_ID");

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);
};
```

---

### Client → Server Message Format

Send a message from the client to the AI Agent.

```json
{
  "role": "user",
  "content": "Hi, I want to build a web app for my personal library."
}
```

| Field   | Type     | Description                        |
|---------|----------|------------------------------------|
| role    | `string` | Must be `"user"`                   |
| content | `string` | Message text                       |

---

### Server → Client Response Format

The AI Agent will respond with a message:

```
  "🤖 AI: That sounds like a great project! ..."
```

---

## Example Session Flow

1. Client get the session id or create a new one
2. Client fetches past messages (if any) using HTTP `GET /messages?session={sessionId}`
3. Client opens a WebSocket connection:  
   `ws://{AI_AGENT_SERVER_HOST}/ws?session={sessionId}`
4. Client sends a message with role `"user"`
5. Server responds with a message from `"assistant"`
6. Messages are appended to the session and retrievable via HTTP

---