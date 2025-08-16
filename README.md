# Memory-MCP

An intelligent memory management server implementing the Model Context Protocol (MCP) for AI applications and personal knowledge systems.

## Overview

Memory-MCP is a sophisticated memory-oriented knowledge graph management system designed to store, organize, and retrieve memories, facts, instructions, discussions, and conclusions. It implements a temporally-aware knowledge graph that can be queried and extended by AI models and applications.

### 🌟 Key Features

- **🧠 Intelligent Memory Storage**: Stores memories as nodes in a knowledge graph with rich metadata
- **⏰ Temporal Awareness**: Prioritizes memories based on recency of access and relevance  
- **🤖 Background AI Processing**: "Dreamer" mode that discovers connections and creates summaries
- **🔌 Simple Client Interface**: Intuitive commands for storing and retrieving memories
- **🌐 Flexible Transport**: Supports both local (stdin/stdout) and remote (HTTP/SSE) communication
- **📊 Knowledge Graph**: Dynamic relationship discovery between memories
- **🎛️ Admin Interface**: Web-based Gradio interface for system management
- **📡 MCP over HTTP**: FastMCP server with SSE support for web integration
- **🐳 Docker Ready**: Easy deployment with Docker and Docker Compose

### 🎯 Use Cases

- Personal AI assistants with long-term memory
- Organizational knowledge management  
- Research and note-taking systems
- Context-aware chatbots
- Documentation and insight discovery
- Project tracking and workflow management

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/raymondclowe/Memory-MCP.git
cd Memory-MCP

# Install dependencies
pip install -r requirements.txt

# Create sample configuration (optional)
python server.py --create-env
```

### Basic Usage

#### 1. MCP Server (Default)
```bash
# Run MCP server for stdio communication
python server.py --mcp
# or simply
python server.py
```

#### 2. FastMCP HTTP Server
```bash
# Run FastMCP HTTP server (MCP over HTTP with SSE)
python server.py --rest

# Server runs at:
# http://localhost:8080/mcp
```

#### 3. Admin Interface  
```bash
# Run Gradio admin interface
python server.py --admin

# Access web interface at:
# http://localhost:7860
```

#### 4. All Services
```bash
# Run both FastMCP HTTP and admin interface
python server.py --all
```

### Docker Deployment

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t memory-mcp .
docker run -p 8080:8080 -p 7860:7860 -v ./data:/app/data memory-mcp
```

## 🏗️ Architecture

The system consists of three main components:

1. **Client Interface Layer**: Handles user commands and responses
2. **Memory Management Core**: Manages the knowledge graph and memory operations  
3. **Background Processor (Dreamer)**: Discovers relationships and creates summaries

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client API    │───▶│  Memory Core    │───▶│  Graph Storage  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   Dreamer AI    │
                       │  (Background)   │
                       └─────────────────┘
```

## 🛠️ Core Commands

- **Store Memory**: `I should remember (content) [context: (metadata)]`
- **Query Memories**: `What do I remember about (query)?`
- **Knowledge Overview**: `What do I know about (topic)?`
- **Recall Memory**: `Recall memory (memory_id)`
- **Deep Search**: `Search extensively for (query)`

## 📡 API Reference

### MCP Tools & Resources

The MCP server provides these tools:

- `store_memory` - Store a new memory with optional context
- `query_memories` - Search for memories based on content or context
- `recall_memory` - Retrieve a specific memory by ID
- `get_knowledge_overview` - Get an overview of stored knowledge
- `exhaustive_search` - Perform comprehensive search across all memories

And these MCP resources:
- `memory://health` - System health status
- `memory://overview` - Knowledge base overview  
- `memory://memory/{id}` - Individual memory by ID

### MCP Prompts

The server also provides context-generation prompts:
- `memory_context_prompt` - Generate contextual information for topics
- `summarize_knowledge_prompt` - Create knowledge base summaries

### FastMCP HTTP Access

When running in HTTP mode, the server provides MCP protocol over HTTP with SSE support:

```bash
# MCP server endpoint
http://localhost:8080/mcp

# The server implements the full MCP protocol including:
# - Tools for memory operations
# - Resources for data access  
# - Prompts for context generation
# - Server-Sent Events for real-time communication
```

## ⚙️ Configuration

Configure via environment variables or `.env` file:

```bash
# Server Configuration
MEMORY_HOST=0.0.0.0
MEMORY_PORT=8080  
MEMORY_LOG_LEVEL=INFO

# Database Configuration  
MEMORY_DB_PATH=memory_graph.db

# AI Configuration (optional)
MEMORY_AI_PROVIDER=openai
MEMORY_AI_API_KEY=your-openai-api-key
MEMORY_AI_MODEL=gpt-3.5-turbo

# Gradio Admin Interface
MEMORY_GRADIO_HOST=0.0.0.0
MEMORY_GRADIO_PORT=7860

# Background Processing  
MEMORY_DREAMER_ENABLED=true
MEMORY_DREAMER_INTERVAL=300
```

## 🧪 Examples

See `example_usage.py` for comprehensive examples:

```bash
python example_usage.py
```

### Basic Memory Operations

```python
from memory_core import MemoryCore

# Initialize
memory_core = MemoryCore("my_memory.db")

# Store a memory
memory_id = await memory_core.store_memory(
    "Important project deadline is next Friday",
    {"project": "Alpha", "type": "deadline", "urgency": "high"}
)

# Search memories  
memories = await memory_core.query_memories("project deadline")

# Recall specific memory
memory = await memory_core.recall_memory(memory_id)
```

## 🧰 Technology Stack

- **Backend**: Python with FastMCP and asyncio
- **Database**: SQLite (with support for other databases)  
- **AI/ML**: Sentence transformers for embeddings, OpenAI integration
- **Admin Interface**: Gradio for web-based management
- **Protocol**: Model Context Protocol (MCP) with FastMCP framework
- **Transport**: HTTP with Server-Sent Events (SSE) support
- **Deployment**: Docker and Docker Compose ready

## 🔧 Development

### Running Tests

```bash
# Test core functionality
python memory_core.py

# Test MCP server  
python mcp_server.py

# Test FastMCP HTTP server
python rest_api.py --test

# Test admin interface
python gradio_admin.py --test

# Test Dreamer AI
python dreamer_ai.py
```

### Code Structure

```
Memory-MCP/
├── server.py           # Main server entry point
├── memory_core.py      # Core memory management
├── mcp_server.py       # MCP protocol implementation  
├── rest_api.py         # FastMCP HTTP server
├── gradio_admin.py     # Web admin interface
├── dreamer_ai.py       # Background AI processing
├── config.py           # Configuration management
├── example_usage.py    # Usage examples
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── SPECIFICATION.md    # Detailed technical specification
```

## 📚 Documentation

- [Complete Specification](SPECIFICATION.md) - Detailed technical specification
- [FastMCP Documentation](https://gofastmcp.com) - FastMCP framework documentation
- [Examples](example_usage.py) - Comprehensive usage examples

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services  
docker-compose down
```

### Manual Docker

```bash
# Build image
docker build -t memory-mcp .

# Run with data persistence
docker run -d \
  -p 8080:8080 \
  -p 7860:7860 \
  -v ./data:/app/data \
  -e MEMORY_DB_PATH=/app/data/memory_graph.db \
  memory-mcp
```

## 🔍 Health Monitoring

Check system health:

```bash
# Via MCP tool (if using MCP client)
# The server provides get_knowledge_overview tool for health monitoring

# Via command line
python -c "import asyncio; from memory_core import MemoryCore; print(asyncio.run(MemoryCore().get_health_status()))"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 📄 License

[MIT License](LICENSE) - see LICENSE file for details.

## 🆘 Support

- [GitHub Issues](https://github.com/raymondclowe/Memory-MCP/issues) - Bug reports and feature requests
- [Discussions](https://github.com/raymondclowe/Memory-MCP/discussions) - Questions and community
- [Specification](SPECIFICATION.md) - Technical details

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: December 2024

Built with ❤️ using the Model Context Protocol