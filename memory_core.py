"""
MCP Memory Server - A sophisticated memory management system implementing the Model Context Protocol.

This module provides intelligent memory storage with temporal awareness and background AI processing
for discovering relationships between memories in a knowledge graph structure.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
import sqlite3
import os
from pathlib import Path

import structlog
from pydantic import BaseModel, Field

# Configure structured logging
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

logger = structlog.get_logger()


class MemoryNode(BaseModel):
    """Represents a memory node in the knowledge graph."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    priority_score: float = 1.0
    node_type: str = "normal"  # normal, summary, abstract
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryRelationship(BaseModel):
    """Represents a relationship between two memory nodes."""
    
    from_node_id: str
    to_node_id: str
    weight: float = Field(ge=0.0, le=1.0)
    relationship_type: str  # temporal, contextual, semantic
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryDatabase:
    """SQLite-based storage for the memory graph."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.db_path = db_path
        self.logger = structlog.get_logger().bind(component="database")
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Memory nodes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_nodes (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        context TEXT,
                        created_at TEXT NOT NULL,
                        last_accessed_at TEXT NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        priority_score REAL DEFAULT 1.0,
                        node_type TEXT DEFAULT 'normal'
                    )
                """)
                
                # Memory relationships table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_relationships (
                        from_node_id TEXT,
                        to_node_id TEXT,
                        weight REAL,
                        relationship_type TEXT,
                        created_at TEXT,
                        PRIMARY KEY (from_node_id, to_node_id),
                        FOREIGN KEY (from_node_id) REFERENCES memory_nodes (id),
                        FOREIGN KEY (to_node_id) REFERENCES memory_nodes (id)
                    )
                """)
                
                # Indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_priority ON memory_nodes (priority_score DESC)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_accessed ON memory_nodes (last_accessed_at DESC)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_weight ON memory_relationships (weight DESC)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error("Failed to initialize database", error=str(e))
            raise
    
    async def store_memory(self, memory: MemoryNode) -> str:
        """Store a memory node in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO memory_nodes 
                    (id, content, context, created_at, last_accessed_at, access_count, priority_score, node_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    json.dumps(memory.context),
                    memory.created_at.isoformat(),
                    memory.last_accessed_at.isoformat(),
                    memory.access_count,
                    memory.priority_score,
                    memory.node_type
                ))
                conn.commit()
                
                self.logger.info("Memory stored", memory_id=memory.id, content_length=len(memory.content))
                return memory.id
                
        except Exception as e:
            self.logger.error("Failed to store memory", error=str(e))
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryNode]:
        """Retrieve a memory node by ID and update access statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memory_nodes WHERE id = ?", (memory_id,))
                row = cursor.fetchone()
                
                if row:
                    # Update access statistics
                    now = datetime.now(timezone.utc)
                    cursor.execute("""
                        UPDATE memory_nodes 
                        SET last_accessed_at = ?, access_count = access_count + 1
                        WHERE id = ?
                    """, (now.isoformat(), memory_id))
                    conn.commit()
                    
                    memory = MemoryNode(
                        id=row[0],
                        content=row[1],
                        context=json.loads(row[2]) if row[2] else {},
                        created_at=datetime.fromisoformat(row[3]),
                        last_accessed_at=now,
                        access_count=row[5] + 1,
                        priority_score=row[6],
                        node_type=row[7]
                    )
                    
                    self.logger.info("Memory retrieved", memory_id=memory_id)
                    return memory
                
                return None
                
        except Exception as e:
            self.logger.error("Failed to retrieve memory", memory_id=memory_id, error=str(e))
            raise
    
    async def search_memories(self, query: str, limit: int = 10) -> List[MemoryNode]:
        """Search memories by content with priority ordering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM memory_nodes 
                    WHERE content LIKE ? OR context LIKE ?
                    ORDER BY priority_score DESC, last_accessed_at DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
                memories = []
                for row in cursor.fetchall():
                    memory = MemoryNode(
                        id=row[0],
                        content=row[1],
                        context=json.loads(row[2]) if row[2] else {},
                        created_at=datetime.fromisoformat(row[3]),
                        last_accessed_at=datetime.fromisoformat(row[4]),
                        access_count=row[5],
                        priority_score=row[6],
                        node_type=row[7]
                    )
                    memories.append(memory)
                
                self.logger.info("Memory search completed", query=query, results_count=len(memories))
                return memories
                
        except Exception as e:
            self.logger.error("Failed to search memories", query=query, error=str(e))
            raise
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get database statistics for health checks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM memory_nodes")
                memory_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM memory_relationships")
                relationship_count = cursor.fetchone()[0]
                
                return {
                    "memory_count": memory_count,
                    "relationship_count": relationship_count,
                    "graph_size": memory_count + relationship_count
                }
                
        except Exception as e:
            self.logger.error("Failed to get memory stats", error=str(e))
            raise


class MemoryCore:
    """Core memory management system."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.db = MemoryDatabase(db_path)
        self.logger = structlog.get_logger().bind(component="memory_core")
        
    async def store_memory(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Store a new memory with optional context."""
        memory = MemoryNode(
            content=content,
            context=context or {}
        )
        
        memory_id = await self.db.store_memory(memory)
        self.logger.info("Memory stored via core", memory_id=memory_id)
        return memory_id
    
    async def query_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query memories and return formatted results."""
        memories = await self.db.search_memories(query, limit)
        
        results = []
        for memory in memories:
            results.append({
                "id": memory.id,
                "content": memory.content,
                "context": memory.context,
                "created_at": memory.created_at.isoformat(),
                "priority_score": memory.priority_score,
                "node_type": memory.node_type
            })
        
        return results
    
    async def recall_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Recall a specific memory by ID."""
        memory = await self.db.get_memory(memory_id)
        
        if memory:
            return {
                "id": memory.id,
                "content": memory.content,
                "context": memory.context,
                "created_at": memory.created_at.isoformat(),
                "last_accessed_at": memory.last_accessed_at.isoformat(),
                "access_count": memory.access_count,
                "priority_score": memory.priority_score,
                "node_type": memory.node_type
            }
        
        return None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health and statistics."""
        stats = await self.db.get_memory_stats()
        
        return {
            "status": "healthy",
            "memory_count": stats["memory_count"],
            "graph_size": stats["graph_size"],
            "db_path": self.db.db_path
        }


if __name__ == "__main__":
    # Basic testing
    async def test_memory_core():
        core = MemoryCore("test_memory.db")
        
        # Store some test memories
        memory_id1 = await core.store_memory(
            "Meeting with Alice about Q4 planning",
            {"project": "Q4 Strategy", "type": "meeting", "participants": ["Alice", "Bob"]}
        )
        
        memory_id2 = await core.store_memory(
            "Database migration scheduled for Friday midnight",
            {"type": "maintenance", "urgency": "high", "date": "2024-12-20"}
        )
        
        # Search memories
        results = await core.query_memories("Alice")
        print(f"Search results for 'Alice': {len(results)} memories found")
        for result in results:
            print(f"- {result['content']}")
        
        # Recall specific memory
        memory = await core.recall_memory(memory_id1)
        print(f"\nRecalled memory: {memory['content']}")
        
        # Health check
        health = await core.get_health_status()
        print(f"\nHealth status: {health}")
    
    asyncio.run(test_memory_core())