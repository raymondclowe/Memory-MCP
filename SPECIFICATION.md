# MCP Memory Server Specification

**Version:** 1.0  
**Date:** 2024-12-19  
**Status:** Draft

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Functional Requirements](#functional-requirements)
4. [Client API](#client-api)
5. [Background Processes](#background-processes)
6. [Data Model](#data-model)
7. [Transport and Communication](#transport-and-communication)
8. [Authentication and Security](#authentication-and-security)
9. [API Endpoints](#api-endpoints)
10. [Error Handling](#error-handling)
11. [Performance Requirements](#performance-requirements)
12. [Implementation Guidelines](#implementation-guidelines)
13. [Deployment Configuration](#deployment-configuration)
14. [Examples and Workflows](#examples-and-workflows)

## Overview

The MCP (Model Context Protocol) Memory Server is a sophisticated memory-oriented knowledge graph management system designed to store, organize, and retrieve memories, facts, instructions, discussions, and conclusions. It implements a temporally-aware knowledge graph that can be queried and extended by AI models and applications.

### Key Features

- **Intelligent Memory Storage**: Stores memories as nodes in a knowledge graph with rich metadata
- **Temporal Awareness**: Prioritizes memories based on recency of access and relevance
- **Background AI Processing**: "Dreamer" mode that discovers connections and creates summaries
- **Simple Client Interface**: Intuitive commands for storing and retrieving memories
- **Flexible Transport**: Supports both local (stdin/stdout) and remote (HTTP/SSE) communication
- **Knowledge Graph**: Dynamic relationship discovery between memories

### Use Cases

- Personal knowledge management for AI assistants
- Organizational memory systems
- Context-aware AI applications
- Long-term conversation memory for chatbots
- Research and note-taking systems

## Architecture

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

## Functional Requirements

### Memory Storage and Representation

**Memory Nodes** serve as the fundamental unit of storage, representing:
- Facts and information snippets
- Instructions and procedures
- Discussion summaries
- Conclusions and insights
- Abstract summaries created by the dreamer

**Node Metadata** includes:
- Unique identifier (UUID)
- Content payload (text or structured data)
- Creation timestamp
- Last accessed timestamp
- Access frequency count
- Priority score (calculated)
- Context metadata (project, topic, location, time period, tags)
- Node type (normal, summary, abstract)

**Memory Types**:
- `normal`: Standard memory nodes created by user input
- `summary`: High-level summaries created by the dreamer
- `abstract`: Meta-summaries that aggregate multiple summaries

### Knowledge Graph

The system maintains a directed, weighted graph where:
- **Nodes** represent memory items
- **Edges** represent relationships with weights (0.0 to 1.0)
- **Relationship Types**:
  - Temporal proximity (created or accessed around the same time)
  - Contextual similarity (same project, topic, location)
  - Semantic relatedness (AI-determined content similarity)
  - Causal relationships (cause and effect)
  - Reference relationships (one memory references another)

## Client API

The client interface provides a simple, natural language-inspired command set:

### Core Commands

#### 1. Store Memory
**Format**: `I should remember (content) [context: (metadata)]`

**Purpose**: Add new memory to the system
**Parameters**:
- `content`: The memory content (required)
- `metadata`: Optional context information

**Example**:
```
I should remember "Team meeting scheduled for Friday at 2 PM" context: {project: "Launch", type: "meeting"}
```

#### 2. Query Specific Memories
**Format**: `What do I remember about (query)?`

**Purpose**: Retrieve specific memories matching the query
**Returns**: List of matching memory nodes with snippets and IDs

**Example**:
```
What do I remember about "Alice"?
```

#### 3. Query Knowledge Overview
**Format**: `What do I know about (topic)?`

**Purpose**: Get high-level overview with summaries and key insights
**Returns**: Summary nodes, clusters, and important related memories

**Example**:
```
What do I know about "project management"?
```

#### 4. Recall Full Memory
**Format**: `Recall memory (memory_id)`

**Purpose**: Retrieve complete memory details including relationships
**Returns**: Full memory content, metadata, and related memories

**Example**:
```
Recall memory 123e4567-e89b-12d3-a456-426614174000
```

#### 5. Exhaustive Search
**Format**: `Search extensively for (query)`

**Purpose**: Deep search when uncertain, returns comprehensive results
**Returns**: Extended list of potentially relevant memories

## Background Processes

### Dreamer Mode (Background AI Worker)

The dreamer operates continuously with low priority during idle periods:

#### Memory Link Discovery
- Randomly samples pairs of memory nodes
- Applies AI/semantic analysis to identify connections
- Creates or strengthens relationship edges for significant connections
- Abandons weak or irrelevant relationships
- Updates the meta-link table with weighted relationships

#### Summary Synthesis
- Monitors for clusters of highly interconnected nodes
- Synthesizes summary nodes when clusters show strong relationships
- Creates hierarchical abstractions (summaries of summaries)
- Links summary nodes to source memories with high weights
- Enables efficient high-level memory retrieval

#### Knowledge Consolidation
- Periodically reviews and optimizes the graph structure
- Identifies redundant or conflicting information
- Suggests memory merges or updates
- Maintains graph coherence and efficiency

### Temporal Awareness and Prioritization

#### Priority Scoring Algorithm
```
priority_score = recency_factor * access_frequency * content_relevance
```

Where:
- `recency_factor`: Higher for recently accessed memories
- `access_frequency`: Number of front-end accesses (not dreamer access)
- `content_relevance`: Based on content richness and connection strength

#### Access Tracking
- **Front-end Access**: Updates `last_accessed_at` and boosts priority
- **Dreamer Access**: Does NOT affect priority or access timestamps
- **Decay Function**: Priority naturally decreases over time without access

#### Pruning Strategy
- Low-priority nodes remain searchable but deprioritized
- No automatic deletion - all memories preserved
- Exhaustive search can still find low-priority memories

## Data Model

### Memory Node Schema

```json
{
  "id": "uuid",
  "content": "string | object",
  "type": "normal | summary | abstract",
  "created_at": "timestamp",
  "last_accessed_at": "timestamp",
  "access_count": "integer",
  "priority_score": "float",
  "context": {
    "project": "string",
    "topic": "string",
    "location": "string",
    "period": "string",
    "tags": ["array of strings"],
    "custom": "object"
  },
  "summary_source_ids": ["array of uuids"]  // Only for summary/abstract nodes
}
```

### Relationship Schema

```json
{
  "from_node_id": "uuid",
  "to_node_id": "uuid",
  "weight": "float (0.0-1.0)",
  "relationship_type": "temporal | contextual | semantic | causal | reference",
  "created_at": "timestamp",
  "created_by": "dreamer | user | system",
  "confidence": "float (0.0-1.0)"
}
```

## Transport and Communication

### Local Mode (stdin/stdout)
- Command-line interface for embedded systems
- JSON request/response format
- Synchronous communication
- Suitable for direct integration and testing

### Remote Mode (HTTP with SSE)
- RESTful HTTP API for requests
- Server-Sent Events for real-time updates
- WebSocket support for bidirectional streaming
- Suitable for distributed systems and web applications

### Message Format

#### Request Structure
```json
{
  "id": "request_id",
  "command": "command_name",
  "parameters": {
    "content": "string",
    "context": "object",
    "query": "string",
    "memory_id": "uuid"
  },
  "timestamp": "iso8601"
}
```

#### Response Structure
```json
{
  "id": "request_id",
  "status": "success | error",
  "data": {
    "memories": "array",
    "memory_id": "uuid",
    "summary": "string",
    "related": "array"
  },
  "error": {
    "code": "string",
    "message": "string",
    "details": "object"
  },
  "timestamp": "iso8601"
}
```

## Authentication and Security

### Authentication Methods

#### API Key Authentication
- Header: `X-Memory-Key: <api_key>`
- Query Parameter: `?key=<api_key>`
- Environment Variable: `MEMORY_API_KEY`

#### Configuration
```json
{
  "auth": {
    "enabled": true,
    "method": "api_key",
    "keys": [
      {
        "key": "hashed_key",
        "name": "client_name",
        "permissions": ["read", "write", "admin"]
      }
    ]
  }
}
```

### Security Considerations

- API keys should be cryptographically strong (minimum 32 characters)
- Keys are stored hashed in configuration
- Support for key rotation and expiration
- Rate limiting to prevent abuse
- Input validation and sanitization
- Memory content encryption at rest (optional)

## API Endpoints

### REST API Endpoints

#### POST /api/v1/memory
Store a new memory
```json
{
  "content": "Meeting with Alice about Q4 planning",
  "context": {
    "project": "Q4 Strategy",
    "type": "meeting",
    "participants": ["Alice", "Bob"]
  }
}
```

#### GET /api/v1/memory/search
Search for memories
```
GET /api/v1/memory/search?q=Alice&type=specific&limit=10
```

#### GET /api/v1/memory/knowledge
Get knowledge overview
```
GET /api/v1/memory/knowledge?topic=project%20management
```

#### GET /api/v1/memory/{id}
Retrieve specific memory by ID
```
GET /api/v1/memory/123e4567-e89b-12d3-a456-426614174000
```

#### GET /api/v1/memory/search/exhaustive
Perform exhaustive search
```
GET /api/v1/memory/search/exhaustive?q=project%20deadlines
```

#### GET /api/v1/health
Health check endpoint
```json
{
  "status": "healthy",
  "uptime": "72h15m30s",
  "memory_count": 1247,
  "graph_size": 3891
}
```

## Error Handling

### Error Response Format
```json
{
  "id": "request_id",
  "status": "error",
  "error": {
    "code": "MEMORY_NOT_FOUND",
    "message": "Memory with ID 123... not found",
    "details": {
      "memory_id": "123e4567-e89b-12d3-a456-426614174000",
      "suggestions": ["similar_id_1", "similar_id_2"]
    }
  }
}
```

### Common Error Codes
- `INVALID_REQUEST`: Malformed request data
- `MEMORY_NOT_FOUND`: Requested memory doesn't exist
- `AUTHENTICATION_FAILED`: Invalid or missing API key
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `STORAGE_ERROR`: Database or persistence layer error
- `AI_SERVICE_ERROR`: Dreamer AI service unavailable

## Performance Requirements

### Response Time Targets
- Memory storage: < 100ms
- Simple queries: < 200ms
- Knowledge overview: < 500ms
- Exhaustive search: < 2000ms

### Scalability Targets
- Support for 100,000+ memory nodes
- Handle 100+ concurrent connections
- Process 1000+ requests per minute

### Resource Requirements
- Memory usage: < 1GB for 10,000 memories
- CPU usage: < 50% during normal operation
- Storage: Efficient compression and indexing

## Implementation Guidelines

### Recommended Technology Stack

#### Graph Database Options
- **Neo4j**: Full-featured graph database with Cypher query language
- **TigerGraph**: High-performance graph analytics platform
- **Custom In-Memory**: For smaller deployments, custom graph implementation

#### AI/ML Integration
- **Embeddings**: Use sentence transformers for semantic similarity
- **Vector Database**: Pinecone, Weaviate, or Chroma for similarity search
- **LLM Integration**: OpenAI, Anthropic, or local models for relationship analysis

#### Backend Framework
- **Python**: FastAPI or Flask for rapid development
- **Node.js**: Express.js for JavaScript ecosystem integration
- **Go**: High-performance, compiled binary deployment

### Development Considerations
- Implement proper logging and monitoring
- Use async/await for non-blocking operations
- Implement circuit breakers for external AI services
- Consider eventual consistency for distributed deployments

## Deployment Configuration

### Environment Variables
```bash
# Server Configuration
MEMORY_PORT=8080
MEMORY_HOST=0.0.0.0
MEMORY_LOG_LEVEL=INFO

# Database Configuration
MEMORY_DB_TYPE=neo4j
MEMORY_DB_URL=bolt://localhost:7687
MEMORY_DB_USER=neo4j
MEMORY_DB_PASSWORD=password

# AI Configuration
MEMORY_AI_PROVIDER=openai
MEMORY_AI_API_KEY=sk-...
MEMORY_AI_MODEL=gpt-3.5-turbo

# Authentication
MEMORY_AUTH_ENABLED=true
MEMORY_API_KEYS=key1,key2,key3
```

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "server.py"]
```

### Docker Compose Example
```yaml
version: '3.8'
services:
  memory-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MEMORY_DB_URL=bolt://neo4j:7687
    depends_on:
      - neo4j

  neo4j:
    image: neo4j:5.0
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
```

## Examples and Workflows

### Complete Workflow Example

#### 1. Storing Memories
```bash
# Store a meeting memory
curl -X POST http://localhost:8080/api/v1/memory \
  -H "X-Memory-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Weekly team standup: Alice reported 80% completion on user auth module, Bob working on API documentation, need to review deployment pipeline next week",
    "context": {
      "project": "Web App Development",
      "type": "standup",
      "date": "2024-12-19",
      "participants": ["Alice", "Bob", "Charlie"]
    }
  }'
```

#### 2. Querying Specific Memories
```bash
# Find memories about Alice
curl "http://localhost:8080/api/v1/memory/search?q=Alice&type=specific" \
  -H "X-Memory-Key: your-api-key"
```

Response:
```json
{
  "status": "success",
  "data": {
    "memories": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "content": "Weekly team standup: Alice reported 80% completion...",
        "snippet": "Alice reported 80% completion on user auth module",
        "context": {
          "project": "Web App Development",
          "type": "standup"
        },
        "relevance_score": 0.95
      }
    ],
    "total": 1
  }
}
```

#### 3. Getting Knowledge Overview
```bash
# Get overview of web development project
curl "http://localhost:8080/api/v1/memory/knowledge?topic=Web%20App%20Development" \
  -H "X-Memory-Key: your-api-key"
```

#### 4. Recalling Full Memory
```bash
# Get complete memory details
curl "http://localhost:8080/api/v1/memory/123e4567-e89b-12d3-a456-426614174000" \
  -H "X-Memory-Key: your-api-key"
```

### Natural Language Command Examples

For systems that support natural language processing:

```
User: "I should remember that the database migration is scheduled for next Friday at midnight"
System: ✓ Memory stored with ID: abc123... Context: {type: "maintenance", urgency: "high"}

User: "What do I remember about database migrations?"
System: Found 3 memories:
- Database migration scheduled for Friday midnight (ID: abc123...)
- Previous migration issues with user table (ID: def456...)
- Migration rollback procedure documentation (ID: ghi789...)

User: "What do I know about system maintenance?"
System: System Maintenance Overview:
- 📅 Upcoming: Database migration (Friday midnight)
- 📋 Procedures: 5 documented processes
- ⚠️ Past Issues: 2 critical incidents resolved
- 👥 Team: Alice (DB admin), Bob (DevOps lead)

User: "Recall memory abc123..."
System: 
Memory ID: abc123...
Content: Database migration scheduled for next Friday at midnight
Created: 2024-12-19 14:30:00
Context: {type: "maintenance", urgency: "high"}
Related Memories:
- Migration rollback procedure (def456...) - weight: 0.8
- Previous migration timeline (ghi789...) - weight: 0.6
```

---

**Document Status**: This specification is a living document and will be updated as the system evolves and new requirements are identified.

**Contributing**: For specification updates or clarifications, please submit issues or pull requests to the project repository.

**License**: This specification is released under the same license as the Memory-MCP project.