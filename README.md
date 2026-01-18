# telegram-mcp-api

Telegram integration with both MCP (Model Context Protocol) and HTTP API support. Based on [telegram-mcp](https://github.com/chigwell/telegram-mcp) with added HTTP API for local script automation.

## Features

- **MCP Server**: Full Telegram integration for Claude Desktop, Cursor, and MCP-compatible clients
- **HTTP API**: REST endpoints for local scripts and automation
- **Python Client**: Simple client library for programmatic access
- **Docker Compose**: Run both services in containers

## Quick Start

### Prerequisites

1. Get Telegram API credentials from https://my.telegram.org
2. Create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Generate session string:
   ```bash
   pip install -r requirements.txt
   python session_string_generator.py
   # Add the output to .env as TELEGRAM_SESSION_STRING
   ```

### Option 1: HTTP API (for local scripts)

```bash
docker compose up telegram-api --build -d
```

Use from Python:
```python
from telegram_client import TelegramClient

client = TelegramClient()  # http://localhost:8080
print(client.get_chats())
client.send_message(chat_id=123, message="Hello!")
client.close()
```

Or via curl:
```bash
curl http://localhost:8080/chats
curl -X POST http://localhost:8080/messages/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123, "message": "Hello!"}'
```

### Option 2: MCP Server (for Claude/Cursor)

```bash
# Register with Claude Code
claude mcp add telegram-mcp -- uv run --directory /path/to/telegram-mcp-api python main.py
```

### Option 3: Both

```bash
docker compose up --build -d
```

## Services

| Service | Purpose | Access |
|---------|---------|--------|
| `telegram-mcp` | MCP server for Claude/Cursor | stdio |
| `telegram-api` | HTTP API for scripts | `http://localhost:8080` |

## HTTP API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/me` | GET | Current user info |
| `/chats` | GET | List chats (paginated) |
| `/chats/list` | GET | List chats with filters |
| `/chats/{id}` | GET | Get chat details |
| `/chats/{id}/messages` | GET | Get messages |
| `/messages/send` | POST | Send message |
| `/messages/search` | POST | Search messages |
| `/contacts` | GET | List contacts |
| `/drafts/save` | POST | Save draft |

See `api.py` for full endpoint documentation.

## Examples

See the `examples/` directory for ready-to-use scripts:
- `example_usage.py` - Basic operations demo
- `send_message.py` - Send messages via CLI
- `search_messages.py` - Search messages in a chat

## Project Structure

```
telegram-mcp-api/
├── main.py                 # MCP server (original)
├── telegram_core.py        # Shared Telegram functionality
├── api.py                  # FastAPI HTTP API
├── telegram_client.py      # Python client library
├── Dockerfile              # MCP server container
├── Dockerfile.api          # HTTP API container
├── docker-compose.yml      # Container orchestration
├── requirements.txt        # Python dependencies
├── session_string_generator.py
└── examples/
    ├── example_usage.py
    ├── send_message.py
    └── search_messages.py
```

## Credits

Based on [telegram-mcp](https://github.com/chigwell/telegram-mcp) by [chigwell](https://github.com/chigwell).

## License

MIT
