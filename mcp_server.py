"""
MCP Memory Server - Implements the Model Context Protocol for intelligent memory management.

This server provides tools and resources for storing, querying, and managing memories
in a knowledge graph with temporal awareness and background AI processing.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Sequence
from contextlib import asynccontextmanager

import structlog
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    GetPromptRequest,
    GetPromptResult,
    PromptMessage,
    Role,
    ListPromptsRequest,
    ListPromptsResult,
    Prompt,
    ListResourcesRequest,
    ListResourcesResult,
    Resource,
    ReadResourceRequest,
    ReadResourceResult,
    TextContent,
)

from memory_core import MemoryCore

logger = structlog.get_logger()


class MCPMemoryServer:
    """MCP Memory Server implementation."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.memory_core = MemoryCore(db_path)
        self.logger = structlog.get_logger().bind(component="mcp_server")
        
        # Initialize MCP server
        self.server = Server("memory-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available memory management tools."""
            return [
                Tool(
                    name="store_memory",
                    description="Store a new memory with optional context metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to remember"
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional context metadata (project, type, tags, etc.)",
                                "additionalProperties": True
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="query_memories",
                    description="Search for memories based on content or context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant memories"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of memories to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="recall_memory",
                    description="Retrieve a specific memory by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "The unique ID of the memory to recall"
                            }
                        },
                        "required": ["memory_id"]
                    }
                ),
                Tool(
                    name="get_knowledge_overview",
                    description="Get an overview of stored knowledge and memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Optional topic to focus the overview on"
                            }
                        }
                    }
                ),
                Tool(
                    name="exhaustive_search",
                    description="Perform a comprehensive search across all memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for exhaustive search"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "store_memory":
                    content = arguments["content"]
                    context = arguments.get("context", {})
                    
                    memory_id = await self.memory_core.store_memory(content, context)
                    
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✓ Memory stored successfully with ID: {memory_id}"
                            )
                        ]
                    )
                
                elif name == "query_memories":
                    query = arguments["query"]
                    limit = arguments.get("limit", 10)
                    
                    memories = await self.memory_core.query_memories(query, limit)
                    
                    if not memories:
                        response = f"No memories found for query: '{query}'"
                    else:
                        response = f"Found {len(memories)} memories for '{query}':\n\n"
                        for i, memory in enumerate(memories, 1):
                            response += f"{i}. {memory['content']}\n"
                            response += f"   ID: {memory['id']}\n"
                            response += f"   Priority: {memory['priority_score']:.2f}\n"
                            if memory['context']:
                                response += f"   Context: {json.dumps(memory['context'])}\n"
                            response += "\n"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=response)]
                    )
                
                elif name == "recall_memory":
                    memory_id = arguments["memory_id"]
                    
                    memory = await self.memory_core.recall_memory(memory_id)
                    
                    if not memory:
                        response = f"Memory with ID '{memory_id}' not found."
                    else:
                        response = f"Memory ID: {memory['id']}\n"
                        response += f"Content: {memory['content']}\n"
                        response += f"Created: {memory['created_at']}\n"
                        response += f"Last Accessed: {memory['last_accessed_at']}\n"
                        response += f"Access Count: {memory['access_count']}\n"
                        response += f"Priority Score: {memory['priority_score']:.2f}\n"
                        response += f"Type: {memory['node_type']}\n"
                        if memory['context']:
                            response += f"Context: {json.dumps(memory['context'], indent=2)}\n"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=response)]
                    )
                
                elif name == "get_knowledge_overview":
                    topic = arguments.get("topic")
                    
                    if topic:
                        # Search for memories related to the topic
                        memories = await self.memory_core.query_memories(topic, 50)
                        response = f"Knowledge Overview for '{topic}':\n\n"
                    else:
                        # Get general overview
                        health = await self.memory_core.get_health_status()
                        response = f"Knowledge Base Overview:\n\n"
                        response += f"📊 Total Memories: {health['memory_count']}\n"
                        response += f"🔗 Graph Size: {health['graph_size']}\n"
                        response += f"💾 Database: {health['db_path']}\n\n"
                        
                        # Get recent memories
                        recent_memories = await self.memory_core.query_memories("", 5)
                        if recent_memories:
                            response += "Recent Memories:\n"
                            for memory in recent_memories:
                                response += f"- {memory['content'][:100]}...\n"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=response)]
                        )
                    
                    if memories:
                        # Analyze context types
                        context_types = {}
                        for memory in memories:
                            for key, value in memory.get('context', {}).items():
                                if key not in context_types:
                                    context_types[key] = set()
                                context_types[key].add(str(value))
                        
                        response += f"📋 Found {len(memories)} related memories\n"
                        for key, values in context_types.items():
                            response += f"🏷️ {key.title()}: {', '.join(list(values)[:5])}\n"
                        
                        response += "\nTop Memories:\n"
                        for i, memory in enumerate(memories[:10], 1):
                            response += f"{i}. {memory['content'][:80]}...\n"
                    else:
                        response += f"No memories found related to '{topic}'"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=response)]
                    )
                
                elif name == "exhaustive_search":
                    query = arguments["query"]
                    
                    # Perform broader search with higher limit
                    memories = await self.memory_core.query_memories(query, 100)
                    
                    response = f"Exhaustive Search Results for '{query}':\n\n"
                    response += f"Found {len(memories)} total memories\n\n"
                    
                    for i, memory in enumerate(memories, 1):
                        response += f"{i}. {memory['content']}\n"
                        response += f"   ID: {memory['id']}\n"
                        response += f"   Priority: {memory['priority_score']:.2f}\n"
                        response += f"   Created: {memory['created_at']}\n"
                        if memory['context']:
                            response += f"   Context: {json.dumps(memory['context'])}\n"
                        response += "\n"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=response)]
                    )
                
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )
                        ]
                    )
            
            except Exception as e:
                self.logger.error("Tool call failed", tool=name, error=str(e))
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error executing {name}: {str(e)}"
                        )
                    ]
                )
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Prompt]:
            """List available prompts."""
            return [
                Prompt(
                    name="memory_assistant",
                    description="A helpful assistant for managing and querying your memories",
                    arguments=[
                        {
                            "name": "context",
                            "description": "Current context or topic of conversation",
                            "required": False
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict) -> GetPromptResult:
            """Get a specific prompt."""
            if name == "memory_assistant":
                context = arguments.get("context", "general")
                
                health = await self.memory_core.get_health_status()
                
                system_message = f"""You are a helpful memory management assistant. You have access to a knowledge base with {health['memory_count']} memories.

Current context: {context}

You can help users:
- Store new memories with appropriate context
- Search and retrieve existing memories
- Get overviews of their knowledge base
- Recall specific memories by ID

Always be helpful and suggest relevant memory operations when appropriate. When users mention something they might want to remember, offer to store it as a memory."""

                return GetPromptResult(
                    description="Memory management assistant prompt",
                    messages=[
                        PromptMessage(
                            role=Role.user,
                            content=TextContent(type="text", text=system_message)
                        )
                    ]
                )
            
            raise ValueError(f"Unknown prompt: {name}")
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="memory://health",
                    name="System Health",
                    description="Current health and statistics of the memory system",
                    mimeType="application/json"
                ),
                Resource(
                    uri="memory://recent",
                    name="Recent Memories",
                    description="Recently accessed memories",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Read a specific resource."""
            if uri == "memory://health":
                health = await self.memory_core.get_health_status()
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=json.dumps(health, indent=2)
                        )
                    ]
                )
            
            elif uri == "memory://recent":
                recent_memories = await self.memory_core.query_memories("", 10)
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=json.dumps(recent_memories, indent=2)
                        )
                    ]
                )
            
            raise ValueError(f"Unknown resource: {uri}")
    
    async def run_stdio(self):
        """Run the MCP server over stdio."""
        from mcp.server.stdio import stdio_server
        
        self.logger.info("Starting MCP Memory Server on stdio")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="memory-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point for the MCP memory server."""
    import sys
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Get database path from environment
    db_path = os.getenv("MEMORY_DB_PATH", "memory_graph.db")
    
    # Create and run server
    server = MCPMemoryServer(db_path)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        await server.run_stdio()
    else:
        print("MCP Memory Server")
        print("Usage: python mcp_server.py --stdio")
        print("   or: python mcp_server.py")
        print("\nFor stdio mode (MCP protocol), use --stdio")
        print("For testing, run without arguments")
        
        # Test the server functionality
        print("\nTesting server functionality...")
        
        # Test the memory core directly
        memory_core = server.memory_core
        
        # Store a test memory
        memory_id = await memory_core.store_memory(
            "Test memory for MCP server",
            {"type": "test", "source": "mcp_server.py"}
        )
        print(f"Stored memory with ID: {memory_id}")
        
        # Query memories
        memories = await memory_core.query_memories("test")
        print(f"Found {len(memories)} memories for 'test' query")
        
        # Get overview
        health = await memory_core.get_health_status()
        print(f"Health status: {health}")
        
        print("\nMCP Server ready for --stdio mode!")


if __name__ == "__main__":
    asyncio.run(main())