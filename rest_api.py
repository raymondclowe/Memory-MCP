"""
FastMCP HTTP Server for Memory MCP - Implements MCP protocol over HTTP with SSE.

This server provides MCP protocol over HTTP Server-Sent Events (SSE) for web compatibility.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import structlog
from fastmcp import FastMCP, Context

from memory_core import MemoryCore

logger = structlog.get_logger()


class FastMCPMemoryServer:
    """FastMCP Memory Server - MCP over HTTP with SSE."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.memory_core = MemoryCore(db_path)
        self.logger = structlog.get_logger().bind(component="fastmcp_server")
        
        # Initialize FastMCP server
        self.app = FastMCP("Memory MCP Server")
        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()
    
    def _setup_tools(self):
        """Set up memory management tools."""
        
        @self.app.tool()
        async def store_memory(content: str, context: Optional[Dict[str, Any]] = None) -> str:
            """Store a new memory with optional context metadata."""
            if context is None:
                context = {}
            
            memory_id = await self.memory_core.store_memory(content, context)
            self.logger.info("Memory stored via FastMCP", memory_id=memory_id)
            
            return f"✓ Memory stored successfully with ID: {memory_id}"
        
        @self.app.tool()
        async def query_memories(query: str, limit: int = 10) -> str:
            """Search for memories based on content or context."""
            if limit < 1 or limit > 100:
                limit = min(max(limit, 1), 100)
            
            memories = await self.memory_core.query_memories(query, limit)
            
            if not memories:
                return f"No memories found for query: '{query}'"
            
            response = f"Found {len(memories)} memories for '{query}':\n\n"
            for i, memory in enumerate(memories, 1):
                response += f"{i}. {memory['content']}\n"
                response += f"   ID: {memory['id']}\n"
                response += f"   Priority: {memory['priority_score']:.2f}\n"
                if memory['context']:
                    response += f"   Context: {json.dumps(memory['context'])}\n"
                response += "\n"
            
            self.logger.info("Memory search via FastMCP", query=query, results=len(memories))
            return response
        
        @self.app.tool()
        async def recall_memory(memory_id: str) -> str:
            """Retrieve a specific memory by its ID."""
            memory = await self.memory_core.recall_memory(memory_id)
            
            if not memory:
                return f"Memory with ID '{memory_id}' not found."
            
            response = f"Memory ID: {memory['id']}\n"
            response += f"Content: {memory['content']}\n"
            response += f"Created: {memory['created_at']}\n"
            response += f"Last Accessed: {memory['last_accessed_at']}\n"
            response += f"Access Count: {memory['access_count']}\n"
            response += f"Priority Score: {memory['priority_score']:.2f}\n"
            response += f"Type: {memory['node_type']}\n"
            if memory['context']:
                response += f"Context: {json.dumps(memory['context'], indent=2)}\n"
            
            self.logger.info("Memory recalled via FastMCP", memory_id=memory_id)
            return response
        
        @self.app.tool()
        async def get_knowledge_overview(topic: Optional[str] = None) -> str:
            """Get an overview of stored knowledge and memories."""
            if topic:
                # Search for memories related to the topic
                memories = await self.memory_core.query_memories(topic, 50)
                response = f"Knowledge Overview for '{topic}':\n\n"
                
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
            
            self.logger.info("Knowledge overview requested via FastMCP", topic=topic)
            return response
        
        @self.app.tool()
        async def exhaustive_search(query: str) -> str:
            """Perform a comprehensive search across all memories."""
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
            
            self.logger.info("Exhaustive search via FastMCP", query=query, results=len(memories))
            return response
    
    def _setup_resources(self):
        """Set up memory resources."""
        
        @self.app.resource("memory://health")
        async def get_health() -> str:
            """Get system health status."""
            health = await self.memory_core.get_health_status()
            return json.dumps(health, indent=2)
        
        @self.app.resource("memory://overview")
        async def get_overview() -> str:
            """Get knowledge base overview."""
            health = await self.memory_core.get_health_status()
            recent_memories = await self.memory_core.query_memories("", 10)
            
            overview = {
                "total_memories": health["memory_count"],
                "graph_size": health["graph_size"],
                "db_path": health["db_path"],
                "recent_memories": [
                    {
                        "id": memory["id"],
                        "content": memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"],
                        "created_at": memory["created_at"],
                        "priority_score": memory["priority_score"]
                    }
                    for memory in recent_memories
                ]
            }
            
            return json.dumps(overview, indent=2)
        
        @self.app.resource("memory://memory/{memory_id}")
        async def get_memory_by_id(memory_id: str) -> str:
            """Get a specific memory by ID."""
            memory = await self.memory_core.recall_memory(memory_id)
            
            if not memory:
                return json.dumps({"error": f"Memory with ID '{memory_id}' not found"})
            
            return json.dumps(memory, indent=2)
    
    def _setup_prompts(self):
        """Set up memory-related prompts."""
        
        @self.app.prompt()
        async def memory_context_prompt(topic: str) -> str:
            """Generate a prompt with memory context for a given topic."""
            memories = await self.memory_core.query_memories(topic, 10)
            
            if not memories:
                return f"I don't have any specific memories about '{topic}'. Please provide context or ask me to learn about it."
            
            prompt = f"Based on my memories about '{topic}', here's what I know:\n\n"
            for i, memory in enumerate(memories, 1):
                prompt += f"{i}. {memory['content']}\n"
                if memory['context']:
                    prompt += f"   Context: {json.dumps(memory['context'])}\n"
                prompt += "\n"
            
            prompt += f"Please use this context to respond about '{topic}'."
            return prompt
        
        @self.app.prompt()
        async def summarize_knowledge_prompt() -> str:
            """Generate a prompt to summarize all stored knowledge."""
            health = await self.memory_core.get_health_status()
            recent_memories = await self.memory_core.query_memories("", 20)
            
            prompt = f"I have {health['memory_count']} memories stored in my knowledge base. "
            prompt += "Here are some recent and important memories:\n\n"
            
            for i, memory in enumerate(recent_memories, 1):
                prompt += f"{i}. {memory['content'][:150]}...\n"
                prompt += f"   Priority: {memory['priority_score']:.2f}\n"
                if memory['context']:
                    prompt += f"   Tags: {', '.join(memory['context'].keys())}\n"
                prompt += "\n"
            
            prompt += "Please provide a comprehensive summary of my knowledge base and suggest areas for improvement."
            return prompt
    
    async def run_http_async(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the FastMCP server with HTTP transport asynchronously."""
        self.logger.info("Starting FastMCP Memory Server with HTTP transport", host=host, port=port)
        
        # Use FastMCP's built-in async HTTP runner
        await self.app.run_streamable_http_async(host=host, port=port)
    
    def run_http(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the FastMCP server with HTTP transport."""
        self.logger.info("Starting FastMCP Memory Server with HTTP transport", host=host, port=port)
        
        # Run with HTTP transport (supports SSE)
        self.app.run(transport="http", host=host, port=port)
    
    async def run_stdio_async(self):
        """Run the FastMCP server with stdio transport asynchronously."""
        self.logger.info("Starting FastMCP Memory Server with stdio transport")
        
        # Use FastMCP's built-in async stdio runner
        await self.app.run_stdio_async()
    
    def run_stdio(self):
        """Run the FastMCP server with stdio transport."""
        self.logger.info("Starting FastMCP Memory Server with stdio transport")
        
        # Run with stdio transport
        self.app.run(transport="stdio")


async def main():
    """Main entry point for the FastMCP memory server."""
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
    
    # Get configuration from environment
    host = os.getenv("MEMORY_HOST", "0.0.0.0")
    port = int(os.getenv("MEMORY_PORT", "8080"))
    db_path = os.getenv("MEMORY_DB_PATH", "memory_graph.db")
    
    # Create server
    server = FastMCPMemoryServer(db_path)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--http":
            # Run with HTTP transport
            await server.run_http_async(host, port)
        elif sys.argv[1] == "--stdio":
            # Run with stdio transport
            await server.run_stdio_async()
        elif sys.argv[1] == "--test":
            # Test mode - run some basic tests
            print("Testing FastMCP functionality...")
            
            # Store a test memory
            memory_id = await server.memory_core.store_memory(
                "FastMCP test memory",
                {"type": "test", "source": "fastmcp_server"}
            )
            print(f"Stored test memory: {memory_id}")
            
            # Search memories
            memories = await server.memory_core.query_memories("test")
            print(f"Found {len(memories)} memories")
            
            # Health check
            health = await server.memory_core.get_health_status()
            print(f"Health: {health}")
            
            print("FastMCP tests completed successfully!")
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python rest_api.py [--http|--stdio|--test]")
    else:
        # Default to HTTP mode
        print("FastMCP Memory Server")
        print("Usage: python rest_api.py [--http|--stdio|--test]")
        print(f"\nStarting HTTP server at http://{host}:{port}")
        print("The server will provide MCP protocol over HTTP with SSE support")
        
        await server.run_http_async(host, port)


if __name__ == "__main__":
    asyncio.run(main())