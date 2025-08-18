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

## 📋 Prerequisites & System Requirements

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB, recommended 2GB+
- **Storage**: 100MB for application, additional space for database
- **OS**: Linux, macOS, Windows (WSL2 recommended for Windows)

### Required Tools
- **Git** (for source installation)
- **Python pip** (package manager)
- **Docker** (optional, for containerized deployment)

## 🚀 Complete Setup & Installation Guide

### Method 1: Quick Installation (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/raymondclowe/Memory-MCP.git
cd Memory-MCP

# 2. Create Python virtual environment (recommended)
python -m venv memory-mcp-env
source memory-mcp-env/bin/activate  # On Windows: memory-mcp-env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create configuration file
python server.py --create-env
cp .env.example .env

# 5. Test installation
python -c "import memory_core; print('✅ Installation successful!')"
```

### Method 2: Development Installation

```bash
# 1. Clone repository
git clone https://github.com/raymondclowe/Memory-MCP.git
cd Memory-MCP

# 2. Install in development mode with all dependencies
pip install -e .
pip install -r requirements.txt

# 3. Install development tools
pip install black mypy pytest pytest-asyncio

# 4. Run tests to verify installation
python test_memory_suite.py
```

### Method 3: Docker Installation (Production Ready)

```bash
# 1. Clone repository
git clone https://github.com/raymondclowe/Memory-MCP.git
cd Memory-MCP

# 2. Create data directory
mkdir -p data

# 3. Configure environment
cp .env.example .env
# Edit .env file with your settings

# 4. Deploy with Docker Compose
docker-compose up -d

# 5. Verify deployment
docker-compose logs memory-mcp
curl http://localhost:8080/health
```

## ⚙️ Configuration Setup

### Step 1: Environment Configuration

Create and customize your `.env` file:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### Step 2: Basic Configuration Options

```bash
# Server Configuration
MEMORY_HOST=0.0.0.0              # Host to bind to (0.0.0.0 for all interfaces)
MEMORY_PORT=8080                 # HTTP server port
MEMORY_LOG_LEVEL=INFO            # Logging level (DEBUG, INFO, WARNING, ERROR)

# Database Configuration
MEMORY_DB_PATH=memory_graph.db   # SQLite database file path

# Gradio Admin Interface
MEMORY_GRADIO_HOST=0.0.0.0       # Admin interface host
MEMORY_GRADIO_PORT=7860          # Admin interface port
MEMORY_GRADIO_SHARE=false        # Enable public sharing (security risk)

# Background Processing
MEMORY_DREAMER_ENABLED=true      # Enable AI background processing
MEMORY_DREAMER_INTERVAL=300      # Seconds between processing cycles
```

### Step 3: Optional AI Configuration

For enhanced AI features, configure OpenAI integration:

```bash
# AI Configuration (Optional)
MEMORY_AI_PROVIDER=openai
MEMORY_AI_API_KEY=sk-your-openai-api-key-here
MEMORY_AI_MODEL=gpt-3.5-turbo
MEMORY_AI_EMBEDDING_MODEL=text-embedding-ada-002
```

### Step 4: Advanced Configuration

```bash
# Authentication (Production Security)
MEMORY_AUTH_ENABLED=true
MEMORY_API_KEYS=secret-key-1,secret-key-2,secret-key-3

# Performance Tuning
MEMORY_CACHE_SIZE=1000           # Memory cache size
MEMORY_QUERY_TIMEOUT=30          # Query timeout in seconds
MEMORY_MAX_CONNECTIONS=10        # Max concurrent connections
```

## 🎯 Deployment Modes

### Mode 1: MCP Server (Standard Protocol)

For integration with MCP-compatible clients:

```bash
# Start MCP server (stdio communication)
python server.py --mcp

# Or use default mode
python server.py
```

**Use Case**: Integration with Claude Desktop, other MCP clients

### Mode 2: HTTP Server (Web API)

For web applications and HTTP clients:

```bash
# Start FastMCP HTTP server
python server.py --rest

# Server available at: http://localhost:8080/mcp
```

**Use Case**: Web applications, REST API integration, browser-based clients

### Mode 3: Admin Interface

For web-based management and monitoring:

```bash
# Start Gradio admin interface
python server.py --admin

# Access at: http://localhost:7860
```

**Use Case**: System administration, data visualization, manual memory management

### Mode 4: All Services

Run everything together:

```bash
# Start all services
python server.py --all

# Available endpoints:
# - MCP over HTTP: http://localhost:8080/mcp
# - Admin Interface: http://localhost:7860
```

**Use Case**: Development, testing, single-server deployment

## ✅ Installation Verification

### Step 1: Basic Functionality Test

```bash
# Test core memory functions
python -c "
import asyncio
from memory_core import MemoryCore

async def test():
    core = MemoryCore()
    health = await core.get_health_status()
    print(f'Health Status: {health}')
    
    # Store test memory
    memory_id = await core.store_memory('Test memory', {'test': True})
    print(f'Stored memory: {memory_id}')
    
    # Query memories
    results = await core.query_memories('test')
    print(f'Found {len(results)} memories')
    print('✅ Core functionality working!')

asyncio.run(test())
"
```

### Step 2: Run Comprehensive Test Suite

```bash
# Run full test suite
python test_memory_suite.py

# Expected output:
# ✅ PASS: Basic Memory Storage
# ✅ PASS: Memory Retrieval by ID
# ✅ PASS: Context-based Search
# ✅ PASS: Content Search
# ✅ PASS: Priority-based Ordering
# ✅ PASS: Memory Update and Access Tracking
# ✅ PASS: Exhaustive Search
# ✅ PASS: Health Status Monitoring
```

### Step 3: Test Each Service Mode

```bash
# Test MCP server (run in background, then test)
python server.py --mcp &
MCP_PID=$!
sleep 2
kill $MCP_PID

# Test HTTP server
python server.py --rest &
REST_PID=$!
sleep 2
curl http://localhost:8080/health
kill $REST_PID

# Test admin interface
python server.py --admin &
ADMIN_PID=$!
sleep 2
curl http://localhost:7860/
kill $ADMIN_PID

echo "✅ All services tested successfully!"
```

## 🐳 Docker Deployment Guide

### Quick Docker Deployment

```bash
# 1. Prepare environment
mkdir -p data
cp .env.example .env

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs memory-mcp
```

### Custom Docker Configuration

```bash
# Build custom image
docker build -t my-memory-mcp .

# Run with custom settings
docker run -d \
  --name memory-mcp \
  -p 8080:8080 \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env:ro \
  -e MEMORY_DB_PATH=/app/data/memory_graph.db \
  my-memory-mcp

# Monitor logs
docker logs -f memory-mcp
```

### Production Docker Setup

```bash
# 1. Create production environment file
cat > .env.production << EOF
MEMORY_HOST=0.0.0.0
MEMORY_PORT=8080
MEMORY_LOG_LEVEL=WARNING
MEMORY_DB_PATH=/app/data/memory_graph.db
MEMORY_GRADIO_HOST=0.0.0.0
MEMORY_GRADIO_PORT=7860
MEMORY_GRADIO_SHARE=false
MEMORY_DREAMER_ENABLED=true
MEMORY_DREAMER_INTERVAL=300
MEMORY_AUTH_ENABLED=true
MEMORY_API_KEYS=your-secure-api-key-here
EOF

# 2. Deploy with production settings
docker-compose -f docker-compose.yml --env-file .env.production up -d

# 3. Set up monitoring
docker-compose exec memory-mcp python -c "
import asyncio
from memory_core import MemoryCore
print(asyncio.run(MemoryCore('/app/data/memory_graph.db').get_health_status()))
"
```

## 🔧 Troubleshooting Guide

### Common Installation Issues

**Issue**: `ModuleNotFoundError: No module named 'memory_core'`
```bash
# Solution: Install dependencies and check Python path
pip install -r requirements.txt
python -c "import sys; print(sys.path)"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Issue**: `Permission denied` when creating database
```bash
# Solution: Check directory permissions
mkdir -p data
chmod 755 data
ls -la data/
```

**Issue**: `Port already in use` error
```bash
# Solution: Find and kill process using port
lsof -i :8080
kill -9 <PID>
# Or use different port
export MEMORY_PORT=8081
```

### Docker Issues

**Issue**: Container fails to start
```bash
# Check logs
docker-compose logs memory-mcp

# Common fixes:
docker-compose down
docker system prune -f
docker-compose up -d --force-recreate
```

**Issue**: Database connection errors
```bash
# Verify database path and permissions
docker-compose exec memory-mcp ls -la /app/data/
docker-compose exec memory-mcp python -c "
import sqlite3
conn = sqlite3.connect('/app/data/memory_graph.db')
print('Database accessible!')
conn.close()
"
```

### Performance Issues

**Issue**: Slow query performance
```bash
# Check database size and optimize
python -c "
import asyncio
from memory_core import MemoryCore

async def optimize():
    core = MemoryCore()
    await core.db.execute('VACUUM;')
    await core.db.execute('ANALYZE;')
    print('Database optimized!')

asyncio.run(optimize())
"
```

**Issue**: High memory usage
```bash
# Adjust cache settings in .env
MEMORY_CACHE_SIZE=500
MEMORY_MAX_CONNECTIONS=5

# Restart service
docker-compose restart memory-mcp
```

## 🔍 Health Monitoring & Maintenance

### Health Check Commands

```bash
# Basic health check
python -c "
import asyncio
from memory_core import MemoryCore
print(asyncio.run(MemoryCore().get_health_status()))
"

# Detailed system status
curl http://localhost:8080/health

# Docker health check
docker-compose exec memory-mcp python -c "
import asyncio
from memory_core import MemoryCore
status = asyncio.run(MemoryCore('/app/data/memory_graph.db').get_health_status())
print(f'Status: {status}')
"
```

### Database Maintenance

```bash
# Backup database
cp data/memory_graph.db data/memory_graph_backup_$(date +%Y%m%d).db

# Database statistics
python -c "
import asyncio, sqlite3
from memory_core import MemoryCore

async def stats():
    core = MemoryCore()
    async with core.db.execute('SELECT COUNT(*) FROM memory_nodes') as cursor:
        count = await cursor.fetchone()
        print(f'Total memories: {count[0]}')

asyncio.run(stats())
"
```

## 📊 Usage Examples

### Example 1: Basic Memory Operations

```bash
# Start server
python server.py --all &

# Test via Python
python -c "
import asyncio
from memory_core import MemoryCore

async def demo():
    core = MemoryCore()
    
    # Store user preference
    await core.store_memory(
        'User prefers dark mode UI',
        {'preference': 'ui', 'setting': 'dark_mode', 'value': True}
    )
    
    # Store project information
    await core.store_memory(
        'Working on Python automation project',
        {'project': 'automation', 'language': 'Python', 'status': 'active'}
    )
    
    # Query memories
    prefs = await core.query_memories('preference dark mode')
    projects = await core.query_memories('Python project')
    
    print(f'Found {len(prefs)} preferences')
    print(f'Found {len(projects)} projects')

asyncio.run(demo())
"
```

### Example 2: AI Chatbot Amnesia Recovery

```python
# System prompt for AI chatbots
SYSTEM_PROMPT = '''
You have amnesia and remember nothing from previous conversations.
Use the memory-mcp tools to recover your memories and context about
this user, their preferences, ongoing projects, and conversation history.
Start each session by querying your memory system to rebuild context.

Available tools:
- query_memories: Search for relevant memories
- store_memory: Save new information
- get_knowledge_overview: Get general overview
'''

# Recovery script
async def recover_context(user_id: str):
    core = MemoryCore()
    
    # Recover user preferences
    preferences = await core.search_by_context({'user_id': user_id, 'type': 'preference'})
    
    # Recover ongoing projects
    projects = await core.search_by_context({'user_id': user_id, 'status': 'active'})
    
    # Recover recent conversations
    recent = await core.query_memories(f'user:{user_id}', limit=10)
    
    return {
        'preferences': preferences,
        'active_projects': projects,
        'recent_context': recent
    }
```

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