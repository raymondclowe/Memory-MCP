# Memory-MCP

An intelligent memory management server implementing the Model Context Protocol (MCP) for AI applications and personal knowledge systems.

## Overview

Memory-MCP is a sophisticated memory-oriented knowledge graph management system that stores, organizes, and retrieves memories, facts, instructions, and conclusions. It features a temporally-aware knowledge graph with an AI-powered "dreamer" process that discovers relationships and creates intelligent summaries.

## Key Features

- **Intelligent Memory Storage**: Memories stored as nodes in a dynamic knowledge graph
- **Temporal Awareness**: Smart prioritization based on access patterns and relevance
- **AI-Powered Relationships**: Background "dreamer" discovers connections between memories
- **Simple API**: Natural language-inspired commands for easy integration
- **Flexible Transport**: Both local (stdin/stdout) and remote (HTTP/SSE) communication
- **Knowledge Synthesis**: Automatic creation of summaries and abstractions

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/raymondclowe/Memory-MCP.git
cd Memory-MCP

# Install dependencies (implementation-specific)
pip install -r requirements.txt  # Python
# or
npm install  # Node.js
```

### Basic Usage

```bash
# Start the server
python memory_server.py
# or
node memory_server.js

# Store a memory
curl -X POST http://localhost:8080/api/v1/memory \
  -H "X-Memory-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"content": "Meeting with Alice about project X", "context": {"project": "X"}}'

# Query memories
curl "http://localhost:8080/api/v1/memory/search?q=Alice" \
  -H "X-Memory-Key: your-api-key"
```

## Architecture

The system consists of three main components:

1. **Client Interface**: Handles natural language-inspired commands
2. **Memory Core**: Manages the knowledge graph and memory operations
3. **Dreamer AI**: Background processor that discovers relationships and creates summaries

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

## Core Commands

- **Store Memory**: `I should remember (content) [context: (metadata)]`
- **Query Memories**: `What do I remember about (query)?`
- **Knowledge Overview**: `What do I know about (topic)?`
- **Recall Memory**: `Recall memory (memory_id)`
- **Deep Search**: `Search extensively for (query)`

## Use Cases

- Personal AI assistants with long-term memory
- Organizational knowledge management
- Research and note-taking systems
- Context-aware chatbots
- Documentation and insight discovery

## Documentation

- [Complete Specification](SPECIFICATION.md) - Detailed technical specification
- [API Reference](docs/api.md) - Complete API documentation
- [Deployment Guide](docs/deployment.md) - Installation and configuration
- [Development Guide](docs/development.md) - Contributing guidelines

## Configuration

Basic configuration via environment variables:

```bash
MEMORY_PORT=8080
MEMORY_DB_TYPE=neo4j
MEMORY_DB_URL=bolt://localhost:7687
MEMORY_AI_PROVIDER=openai
MEMORY_API_KEYS=your-api-key
```

See [SPECIFICATION.md](SPECIFICATION.md) for complete configuration options.

## Contributing

We welcome contributions! Please see:

1. [Specification](SPECIFICATION.md) for technical details
2. [Issues](https://github.com/raymondclowe/Memory-MCP/issues) for bugs and feature requests
3. [Pull Requests](https://github.com/raymondclowe/Memory-MCP/pulls) for code contributions

## Technology Stack

- **Graph Database**: Neo4j, TigerGraph, or custom in-memory graph
- **AI/ML**: Embeddings, vector similarity, LLM integration
- **Backend**: Python (FastAPI), Node.js (Express), or Go
- **Transport**: HTTP REST API with SSE, stdin/stdout for local mode

## License

[MIT License](LICENSE) - see LICENSE file for details.

## Support

- [GitHub Issues](https://github.com/raymondclowe/Memory-MCP/issues)
- [Discussions](https://github.com/raymondclowe/Memory-MCP/discussions)
- [Specification](SPECIFICATION.md)

---

**Status**: Active Development  
**Version**: 1.0 (Specification)  
**Last Updated**: December 2024