#!/usr/bin/env python3
"""
Example usage of Memory MCP in different modes.

This script demonstrates how to use the Memory MCP system programmatically.
"""

import asyncio
import json
from memory_core import MemoryCore


async def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Memory MCP Usage ===\n")
    
    # Initialize memory core
    memory_core = MemoryCore("example_memory.db")
    
    # Store some memories
    print("Storing memories...")
    
    memory_id1 = await memory_core.store_memory(
        "Meeting with Alice about Q4 planning for Project X",
        {
            "project": "Project X",
            "type": "meeting",
            "participants": ["Alice", "Bob"],
            "priority": "high"
        }
    )
    print(f"Stored memory 1: {memory_id1}")
    
    memory_id2 = await memory_core.store_memory(
        "Database migration scheduled for Friday midnight",
        {
            "type": "maintenance",
            "urgency": "high",
            "scheduled_date": "2024-12-20",
            "database": "production"
        }
    )
    print(f"Stored memory 2: {memory_id2}")
    
    memory_id3 = await memory_core.store_memory(
        "Project X requirements document completed",
        {
            "project": "Project X", 
            "type": "milestone",
            "status": "completed",
            "document": "requirements.pdf"
        }
    )
    print(f"Stored memory 3: {memory_id3}")
    
    print("\n" + "="*50 + "\n")
    
    # Query memories
    print("Searching for memories...")
    
    # Search by project
    project_memories = await memory_core.query_memories("Project X")
    print(f"Found {len(project_memories)} memories for 'Project X':")
    for memory in project_memories:
        print(f"- {memory['content']}")
    
    print()
    
    # Search by type
    meeting_memories = await memory_core.query_memories("meeting")
    print(f"Found {len(meeting_memories)} memories for 'meeting':")
    for memory in meeting_memories:
        print(f"- {memory['content']}")
    
    print("\n" + "="*50 + "\n")
    
    # Recall specific memory
    print("Recalling specific memory...")
    recalled_memory = await memory_core.recall_memory(memory_id1)
    if recalled_memory:
        print(f"Memory: {recalled_memory['content']}")
        print(f"Context: {json.dumps(recalled_memory['context'], indent=2)}")
        print(f"Access count: {recalled_memory['access_count']}")
    
    print("\n" + "="*50 + "\n")
    
    # Get system health
    health = await memory_core.get_health_status()
    print("System status:")
    print(f"- Total memories: {health['memory_count']}")
    print(f"- Graph size: {health['graph_size']}")
    print(f"- Status: {health['status']}")


async def example_advanced_usage():
    """Advanced usage example with context analysis."""
    print("\n=== Advanced Memory MCP Usage ===\n")
    
    memory_core = MemoryCore("example_memory.db")
    
    # Store memories with rich context
    contexts = [
        {
            "content": "Implemented user authentication system",
            "context": {
                "project": "WebApp",
                "type": "development", 
                "feature": "authentication",
                "priority": "high",
                "technology": "OAuth2"
            }
        },
        {
            "content": "Fixed critical security vulnerability in login",
            "context": {
                "project": "WebApp",
                "type": "bugfix",
                "feature": "authentication", 
                "priority": "critical",
                "cve": "CVE-2024-1234"
            }
        },
        {
            "content": "Deployed WebApp v2.1 to production",
            "context": {
                "project": "WebApp",
                "type": "deployment",
                "version": "v2.1",
                "environment": "production",
                "status": "success"
            }
        },
        {
            "content": "User reported login issues on mobile",
            "context": {
                "project": "WebApp",
                "type": "issue",
                "feature": "authentication",
                "platform": "mobile",
                "priority": "medium"
            }
        }
    ]
    
    print("Storing memories with rich context...")
    for item in contexts:
        memory_id = await memory_core.store_memory(item["content"], item["context"])
        print(f"Stored: {item['content'][:50]}...")
    
    print("\n" + "="*50 + "\n")
    
    # Analyze memories by different dimensions
    print("Analyzing memories by context...")
    
    # By project
    webapp_memories = await memory_core.query_memories("WebApp")
    print(f"\nWebApp memories ({len(webapp_memories)}):")
    for memory in webapp_memories:
        memory_type = memory['context'].get('type', 'unknown')
        priority = memory['context'].get('priority', 'normal')
        print(f"- [{memory_type.upper()}] {memory['content']} (Priority: {priority})")
    
    # By feature
    auth_memories = await memory_core.query_memories("authentication")
    print(f"\nAuthentication-related memories ({len(auth_memories)}):")
    for memory in auth_memories:
        memory_type = memory['context'].get('type', 'unknown')
        print(f"- [{memory_type.upper()}] {memory['content']}")
    
    print("\n" + "="*50 + "\n")
    
    # Demonstrate priority-based retrieval
    print("Memories by priority:")
    all_memories = await memory_core.query_memories("", 20)
    
    priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "normal": 1}
    sorted_memories = sorted(
        all_memories, 
        key=lambda m: priority_order.get(m['context'].get('priority', 'normal'), 1),
        reverse=True
    )
    
    for memory in sorted_memories:
        priority = memory['context'].get('priority', 'normal')
        memory_type = memory['context'].get('type', 'unknown')
        print(f"[{priority.upper()}] [{memory_type.upper()}] {memory['content']}")


async def example_workflow():
    """Example workflow: Software development project tracking."""
    print("\n=== Workflow Example: Project Tracking ===\n")
    
    memory_core = MemoryCore("project_memory.db")
    
    # Simulate a software development workflow
    workflow_memories = [
        ("Project kickoff meeting", {
            "project": "MobileApp", "type": "meeting", "phase": "planning",
            "participants": ["Alice", "Bob", "Charlie"], "date": "2024-12-01"
        }),
        ("Requirements gathering completed", {
            "project": "MobileApp", "type": "milestone", "phase": "planning",
            "deliverable": "requirements.md", "status": "completed"
        }),
        ("UI/UX design mockups created", {
            "project": "MobileApp", "type": "milestone", "phase": "design",
            "deliverable": "mockups.fig", "status": "completed"
        }),
        ("Backend API development started", {
            "project": "MobileApp", "type": "development", "phase": "implementation", 
            "component": "backend", "technology": "FastAPI"
        }),
        ("Database schema designed", {
            "project": "MobileApp", "type": "development", "phase": "implementation",
            "component": "database", "technology": "PostgreSQL"
        }),
        ("User authentication implemented", {
            "project": "MobileApp", "type": "development", "phase": "implementation",
            "component": "backend", "feature": "authentication"
        }),
        ("Mobile app frontend 50% complete", {
            "project": "MobileApp", "type": "progress", "phase": "implementation",
            "component": "frontend", "completion": 50
        }),
        ("Security audit scheduled", {
            "project": "MobileApp", "type": "planning", "phase": "testing",
            "activity": "security_audit", "scheduled_date": "2024-12-15"
        })
    ]
    
    print("Storing project workflow memories...")
    for content, context in workflow_memories:
        await memory_core.store_memory(content, context)
        print(f"+ {content}")
    
    print("\n" + "="*50 + "\n")
    
    # Query by different project aspects
    print("Project analysis:")
    
    # By phase
    phases = ["planning", "design", "implementation", "testing"]
    for phase in phases:
        phase_memories = await memory_core.query_memories(phase)
        print(f"\n{phase.title()} phase ({len(phase_memories)} items):")
        for memory in phase_memories:
            print(f"  - {memory['content']}")
    
    # By component
    print(f"\nBackend development:")
    backend_memories = await memory_core.query_memories("backend")
    for memory in backend_memories:
        tech = memory['context'].get('technology', '')
        feature = memory['context'].get('feature', '')
        detail = f" ({tech})" if tech else f" ({feature})" if feature else ""
        print(f"  - {memory['content']}{detail}")
    
    # Overall project status
    print(f"\nProject Overview:")
    all_project_memories = await memory_core.query_memories("MobileApp")
    
    phase_counts = {}
    for memory in all_project_memories:
        phase = memory['context'].get('phase', 'unknown')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    for phase, count in phase_counts.items():
        print(f"  - {phase.title()}: {count} activities")
    
    print(f"  - Total activities: {len(all_project_memories)}")


async def main():
    """Run all examples."""
    await example_basic_usage()
    await example_advanced_usage()
    await example_workflow()
    
    print("\n" + "="*60)
    print("🎉 Examples completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Try the MCP server: python server.py --mcp")
    print("2. Try the REST API: python server.py --rest")
    print("3. Try the admin interface: python server.py --admin")
    print("4. Try all services: python server.py --all")


if __name__ == "__main__":
    asyncio.run(main())