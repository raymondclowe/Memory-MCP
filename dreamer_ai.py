"""
Background Dreamer AI Worker for Memory MCP.

This module implements the background AI processing that discovers relationships
between memories and creates summaries for improved knowledge organization.
"""

import asyncio
import random
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

import structlog

from memory_core import MemoryCore, MemoryNode, MemoryRelationship

logger = structlog.get_logger()


class DreamerAI:
    """Background AI worker for memory relationship discovery and summarization."""
    
    def __init__(self, memory_core: MemoryCore, enabled: bool = True, interval: int = 300):
        self.memory_core = memory_core
        self.enabled = enabled
        self.interval = interval  # Processing interval in seconds
        self.logger = structlog.get_logger().bind(component="dreamer_ai")
        self.running = False
        self.last_run = None
        
    async def start(self):
        """Start the background dreamer process."""
        if not self.enabled:
            self.logger.info("Dreamer AI is disabled")
            return
        
        self.running = True
        self.logger.info("Starting Dreamer AI background worker", interval=self.interval)
        
        while self.running:
            try:
                await self._process_cycle()
                self.last_run = datetime.now(timezone.utc)
                
                # Wait for next cycle
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                self.logger.info("Dreamer AI worker cancelled")
                break
            except Exception as e:
                self.logger.error("Error in Dreamer AI cycle", error=str(e))
                # Continue running even if one cycle fails
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    def stop(self):
        """Stop the background dreamer process."""
        self.running = False
        self.logger.info("Stopping Dreamer AI background worker")
    
    async def _process_cycle(self):
        """Run one processing cycle of the dreamer."""
        self.logger.info("Starting Dreamer AI processing cycle")
        
        # Get current memory statistics
        stats = await self.memory_core.get_health_status()
        memory_count = stats.get("memory_count", 0)
        
        if memory_count < 2:
            self.logger.info("Not enough memories for relationship discovery", count=memory_count)
            return
        
        # Perform different types of processing
        await self._discover_relationships()
        await self._create_summaries()
        await self._update_priorities()
        
        self.logger.info("Completed Dreamer AI processing cycle")
    
    async def _discover_relationships(self):
        """Discover and create relationships between memory pairs."""
        self.logger.info("Discovering memory relationships")
        
        # Get a sample of memories to analyze
        sample_memories = await self.memory_core.query_memories("", limit=50)
        
        if len(sample_memories) < 2:
            return
        
        # Randomly sample pairs for relationship analysis
        num_pairs = min(10, len(sample_memories) * (len(sample_memories) - 1) // 2)
        
        for _ in range(num_pairs):
            # Pick two random memories
            memory1, memory2 = random.sample(sample_memories, 2)
            
            # Analyze relationship
            relationship_score = await self._analyze_relationship(memory1, memory2)
            
            if relationship_score > 0.3:  # Threshold for creating relationship
                relationship_type = self._classify_relationship(memory1, memory2)
                
                # This would typically store the relationship in the database
                # For now, we'll just log it
                self.logger.info(
                    "Discovered relationship",
                    from_memory=memory1["id"][:8],
                    to_memory=memory2["id"][:8],
                    score=relationship_score,
                    type=relationship_type
                )
    
    async def _analyze_relationship(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> float:
        """Analyze the relationship strength between two memories."""
        
        # Simple relationship scoring based on context and content similarity
        score = 0.0
        
        # Context similarity
        context1 = memory1.get("context", {})
        context2 = memory2.get("context", {})
        
        common_keys = set(context1.keys()) & set(context2.keys())
        if common_keys:
            for key in common_keys:
                if context1[key] == context2[key]:
                    score += 0.2
        
        # Content similarity (simple keyword matching)
        content1_words = set(memory1["content"].lower().split())
        content2_words = set(memory2["content"].lower().split())
        
        if content1_words and content2_words:
            intersection = content1_words & content2_words
            union = content1_words | content2_words
            jaccard_similarity = len(intersection) / len(union) if union else 0
            score += jaccard_similarity * 0.5
        
        # Temporal proximity
        try:
            time1 = datetime.fromisoformat(memory1["created_at"].replace("Z", "+00:00"))
            time2 = datetime.fromisoformat(memory2["created_at"].replace("Z", "+00:00"))
            time_diff = abs((time1 - time2).total_seconds())
            
            # Boost score for memories created within 24 hours
            if time_diff < 86400:  # 24 hours
                score += 0.1
        except:
            pass
        
        return min(score, 1.0)
    
    def _classify_relationship(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> str:
        """Classify the type of relationship between two memories."""
        
        context1 = memory1.get("context", {})
        context2 = memory2.get("context", {})
        
        # Check for contextual relationships
        if context1.get("project") == context2.get("project"):
            return "project_related"
        elif context1.get("type") == context2.get("type"):
            return "type_similar"
        else:
            return "semantic"
    
    async def _create_summaries(self):
        """Create summary memories for clusters of related memories."""
        self.logger.info("Creating memory summaries")
        
        # Get memories by context to find clusters
        all_memories = await self.memory_core.query_memories("", limit=100)
        
        # Group by project context
        project_groups = {}
        for memory in all_memories:
            project = memory.get("context", {}).get("project")
            if project:
                if project not in project_groups:
                    project_groups[project] = []
                project_groups[project].append(memory)
        
        # Create summaries for projects with multiple memories
        for project, memories in project_groups.items():
            if len(memories) >= 3:  # Only summarize if enough memories
                await self._create_project_summary(project, memories)
    
    async def _create_project_summary(self, project: str, memories: List[Dict[str, Any]]):
        """Create a summary memory for a project."""
        
        # Check if summary already exists
        existing_summaries = await self.memory_core.query_memories(f"Summary of {project}")
        if existing_summaries:
            return
        
        # Create summary content
        memory_count = len(memories)
        recent_activities = []
        
        for memory in memories[-5:]:  # Last 5 memories
            content_preview = memory["content"][:50] + "..." if len(memory["content"]) > 50 else memory["content"]
            recent_activities.append(f"- {content_preview}")
        
        summary_content = f"""Summary of {project}:

Total memories: {memory_count}
Recent activities:
{chr(10).join(recent_activities)}

This is an automatically generated summary created by the Dreamer AI.
Last updated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}"""
        
        # Store the summary
        summary_context = {
            "type": "summary",
            "project": project,
            "source": "dreamer_ai",
            "summarized_count": memory_count
        }
        
        await self.memory_core.store_memory(summary_content, summary_context)
        
        self.logger.info(
            "Created project summary",
            project=project,
            memory_count=memory_count
        )
    
    async def _update_priorities(self):
        """Update priority scores for memories based on access patterns."""
        self.logger.info("Updating memory priorities")
        
        # This is a simplified priority update
        # In a full implementation, this would analyze access patterns,
        # relationship strengths, and temporal factors to update priorities
        
        # For now, we'll just log that we would update priorities
        self.logger.info("Priority update completed (placeholder)")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the dreamer."""
        return {
            "enabled": self.enabled,
            "running": self.running,
            "interval": self.interval,
            "last_run": self.last_run.isoformat() if self.last_run else None
        }


class DreamerManager:
    """Manager for the Dreamer AI background service."""
    
    def __init__(self, memory_core: MemoryCore, config: Optional[Dict[str, Any]] = None):
        self.memory_core = memory_core
        self.config = config or {}
        self.dreamer = None
        self.task = None
        self.logger = structlog.get_logger().bind(component="dreamer_manager")
    
    async def start(self):
        """Start the dreamer service."""
        enabled = self.config.get("enabled", True)
        interval = self.config.get("interval", 300)
        
        if not enabled:
            self.logger.info("Dreamer service is disabled")
            return
        
        self.dreamer = DreamerAI(
            memory_core=self.memory_core,
            enabled=enabled,
            interval=interval
        )
        
        self.task = asyncio.create_task(self.dreamer.start())
        self.logger.info("Dreamer service started")
    
    async def stop(self):
        """Stop the dreamer service."""
        if self.dreamer:
            self.dreamer.stop()
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Dreamer service stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the dreamer service."""
        if self.dreamer:
            return self.dreamer.get_status()
        else:
            return {"enabled": False, "running": False}


# Example usage
async def main():
    """Example usage of the Dreamer AI."""
    memory_core = MemoryCore("test_dreamer.db")
    
    # Store some test memories
    await memory_core.store_memory(
        "Started working on project Alpha",
        {"project": "Alpha", "type": "work"}
    )
    
    await memory_core.store_memory(
        "Meeting with team about Alpha requirements",
        {"project": "Alpha", "type": "meeting"}
    )
    
    await memory_core.store_memory(
        "Completed Alpha design phase",
        {"project": "Alpha", "type": "milestone"}
    )
    
    # Create and run dreamer for one cycle
    dreamer = DreamerAI(memory_core, enabled=True, interval=5)
    
    print("Running Dreamer AI for one cycle...")
    await dreamer._process_cycle()
    
    print("Dreamer AI cycle completed!")


if __name__ == "__main__":
    asyncio.run(main())