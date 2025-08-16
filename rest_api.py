"""
REST API Server for Memory MCP - FastAPI implementation for HTTP mode.

This server provides HTTP REST endpoints alongside the MCP protocol for broader compatibility.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from memory_core import MemoryCore

logger = structlog.get_logger()


class StoreMemoryRequest(BaseModel):
    """Request model for storing a memory."""
    content: str = Field(..., description="The content to remember")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Optional context metadata")


class StoreMemoryResponse(BaseModel):
    """Response model for storing a memory."""
    memory_id: str
    message: str


class MemoryResponse(BaseModel):
    """Response model for a memory item."""
    id: str
    content: str
    context: Dict[str, Any]
    created_at: str
    last_accessed_at: str
    access_count: int
    priority_score: float
    node_type: str


class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    memories: List[Dict[str, Any]]
    total_found: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    uptime: str
    memory_count: int
    graph_size: int
    timestamp: str


class RESTAPIServer:
    """FastAPI REST server for the Memory MCP system."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.memory_core = MemoryCore(db_path)
        self.logger = structlog.get_logger().bind(component="rest_api")
        self.start_time = time.time()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Memory MCP REST API",
            description="Intelligent memory management with temporal awareness and knowledge graph",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.app.post("/api/v1/memory", response_model=StoreMemoryResponse)
        async def store_memory(request: StoreMemoryRequest):
            """Store a new memory with optional context."""
            try:
                memory_id = await self.memory_core.store_memory(
                    content=request.content,
                    context=request.context
                )
                
                self.logger.info("Memory stored via REST API", memory_id=memory_id)
                
                return StoreMemoryResponse(
                    memory_id=memory_id,
                    message="Memory stored successfully"
                )
                
            except Exception as e:
                self.logger.error("Failed to store memory via REST API", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/memory/search", response_model=SearchResponse)
        async def search_memories(
            q: str = Query(..., description="Search query"),
            type: str = Query("specific", description="Search type (specific, knowledge, exhaustive)"),
            limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
        ):
            """Search for memories based on content or context."""
            try:
                if type == "exhaustive":
                    limit = min(limit, 100)  # Higher limit for exhaustive search
                
                memories = await self.memory_core.query_memories(q, limit)
                
                self.logger.info("Memory search via REST API", query=q, type=type, results=len(memories))
                
                return SearchResponse(
                    query=q,
                    memories=memories,
                    total_found=len(memories)
                )
                
            except Exception as e:
                self.logger.error("Failed to search memories via REST API", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/memory/knowledge")
        async def get_knowledge_overview(
            topic: Optional[str] = Query(None, description="Optional topic to focus on")
        ):
            """Get knowledge overview, optionally focused on a topic."""
            try:
                if topic:
                    # Search for memories related to the topic
                    memories = await self.memory_core.query_memories(topic, 50)
                    
                    # Analyze context types
                    context_types = {}
                    for memory in memories:
                        for key, value in memory.get('context', {}).items():
                            if key not in context_types:
                                context_types[key] = set()
                            context_types[key].add(str(value))
                    
                    # Convert sets to lists for JSON serialization
                    context_summary = {
                        key: list(values)[:10]  # Limit to avoid too much data
                        for key, values in context_types.items()
                    }
                    
                    overview = {
                        "topic": topic,
                        "total_memories": len(memories),
                        "context_summary": context_summary,
                        "top_memories": [
                            {
                                "id": memory["id"],
                                "content": memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"],
                                "priority_score": memory["priority_score"]
                            }
                            for memory in memories[:10]
                        ]
                    }
                else:
                    # General overview
                    health = await self.memory_core.get_health_status()
                    recent_memories = await self.memory_core.query_memories("", 5)
                    
                    overview = {
                        "total_memories": health["memory_count"],
                        "graph_size": health["graph_size"],
                        "recent_memories": [
                            {
                                "id": memory["id"],
                                "content": memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"],
                                "created_at": memory["created_at"]
                            }
                            for memory in recent_memories
                        ]
                    }
                
                self.logger.info("Knowledge overview requested via REST API", topic=topic)
                return overview
                
            except Exception as e:
                self.logger.error("Failed to get knowledge overview via REST API", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/memory/{memory_id}", response_model=MemoryResponse)
        async def get_memory(memory_id: str):
            """Retrieve a specific memory by ID."""
            try:
                memory = await self.memory_core.recall_memory(memory_id)
                
                if not memory:
                    raise HTTPException(status_code=404, detail="Memory not found")
                
                self.logger.info("Memory recalled via REST API", memory_id=memory_id)
                
                return MemoryResponse(**memory)
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Failed to recall memory via REST API", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/memory/search/exhaustive")
        async def exhaustive_search(
            q: str = Query(..., description="Search query"),
            limit: int = Query(100, ge=1, le=100, description="Maximum number of results")
        ):
            """Perform exhaustive search across all memories."""
            try:
                memories = await self.memory_core.query_memories(q, limit)
                
                self.logger.info("Exhaustive search via REST API", query=q, results=len(memories))
                
                return {
                    "query": q,
                    "total_found": len(memories),
                    "memories": memories
                }
                
            except Exception as e:
                self.logger.error("Failed to perform exhaustive search via REST API", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            try:
                health = await self.memory_core.get_health_status()
                uptime_seconds = time.time() - self.start_time
                
                # Format uptime
                hours, remainder = divmod(uptime_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{int(hours)}h{int(minutes)}m{int(seconds)}s"
                
                return HealthResponse(
                    status=health["status"],
                    uptime=uptime_str,
                    memory_count=health["memory_count"],
                    graph_size=health["graph_size"],
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                
            except Exception as e:
                self.logger.error("Health check failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                "name": "Memory MCP REST API",
                "version": "1.0.0",
                "description": "Intelligent memory management with temporal awareness",
                "endpoints": {
                    "store_memory": "POST /api/v1/memory",
                    "search_memories": "GET /api/v1/memory/search",
                    "knowledge_overview": "GET /api/v1/memory/knowledge",
                    "get_memory": "GET /api/v1/memory/{id}",
                    "exhaustive_search": "GET /api/v1/memory/search/exhaustive",
                    "health": "GET /api/v1/health"
                },
                "documentation": {
                    "swagger": "/docs",
                    "redoc": "/redoc"
                }
            }
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the REST API server."""
        self.logger.info("Starting Memory MCP REST API server", host=host, port=port)
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Main entry point for the REST API server."""
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
    
    # Create and start server
    server = RESTAPIServer(db_path)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - run some basic tests
        print("Testing REST API functionality...")
        
        # Store a test memory
        memory_id = await server.memory_core.store_memory(
            "REST API test memory",
            {"type": "test", "source": "rest_api.py"}
        )
        print(f"Stored test memory: {memory_id}")
        
        # Search memories
        memories = await server.memory_core.query_memories("test")
        print(f"Found {len(memories)} memories")
        
        # Health check
        health = await server.memory_core.get_health_status()
        print(f"Health: {health}")
        
        print("REST API tests completed successfully!")
    else:
        # Start the server
        await server.start_server(host, port)


if __name__ == "__main__":
    asyncio.run(main())