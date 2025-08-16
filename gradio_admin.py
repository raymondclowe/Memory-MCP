"""
Gradio Admin Interface for Memory MCP - Web-based management interface.

This provides a user-friendly web interface for managing the memory system,
viewing statistics, and performing administrative tasks.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any

import gradio as gr
import structlog
import pandas as pd

from memory_core import MemoryCore

logger = structlog.get_logger()


class GradioAdminInterface:
    """Gradio-based admin interface for Memory MCP."""
    
    def __init__(self, db_path: str = "memory_graph.db"):
        self.memory_core = MemoryCore(db_path)
        self.logger = structlog.get_logger().bind(component="gradio_admin")
        
    async def store_memory_async(self, content: str, context_json: str) -> str:
        """Store a memory asynchronously."""
        try:
            context = {}
            if context_json.strip():
                context = json.loads(context_json)
            
            memory_id = await self.memory_core.store_memory(content, context)
            return f"✅ Memory stored successfully!\nMemory ID: {memory_id}"
        
        except json.JSONDecodeError:
            return "❌ Error: Invalid JSON in context field"
        except Exception as e:
            return f"❌ Error storing memory: {str(e)}"
    
    def store_memory(self, content: str, context_json: str) -> str:
        """Store a memory (sync wrapper)."""
        return asyncio.run(self.store_memory_async(content, context_json))
    
    async def search_memories_async(self, query: str, limit: int) -> Tuple[str, str]:
        """Search memories asynchronously."""
        try:
            memories = await self.memory_core.query_memories(query, limit)
            
            if not memories:
                return f"No memories found for query: '{query}'", ""
            
            # Format results
            result_text = f"Found {len(memories)} memories for '{query}':\n\n"
            
            # Create DataFrame for table
            table_data = []
            for memory in memories:
                table_data.append({
                    "ID": memory["id"][:8] + "...",
                    "Content": memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"],
                    "Priority": f"{memory['priority_score']:.2f}",
                    "Type": memory["node_type"],
                    "Created": memory["created_at"][:10]  # Just the date part
                })
            
            df = pd.DataFrame(table_data)
            return result_text, df.to_string(index=False)
        
        except Exception as e:
            return f"❌ Error searching memories: {str(e)}", ""
    
    def search_memories(self, query: str, limit: int) -> Tuple[str, str]:
        """Search memories (sync wrapper)."""
        return asyncio.run(self.search_memories_async(query, limit))
    
    async def recall_memory_async(self, memory_id: str) -> str:
        """Recall a specific memory asynchronously."""
        try:
            memory = await self.memory_core.recall_memory(memory_id)
            
            if not memory:
                return f"❌ Memory with ID '{memory_id}' not found."
            
            result = f"Memory Details:\n\n"
            result += f"ID: {memory['id']}\n"
            result += f"Content: {memory['content']}\n"
            result += f"Created: {memory['created_at']}\n"
            result += f"Last Accessed: {memory['last_accessed_at']}\n"
            result += f"Access Count: {memory['access_count']}\n"
            result += f"Priority Score: {memory['priority_score']:.2f}\n"
            result += f"Type: {memory['node_type']}\n"
            
            if memory['context']:
                result += f"Context:\n{json.dumps(memory['context'], indent=2)}\n"
            
            return result
        
        except Exception as e:
            return f"❌ Error recalling memory: {str(e)}"
    
    def recall_memory(self, memory_id: str) -> str:
        """Recall a memory (sync wrapper)."""
        return asyncio.run(self.recall_memory_async(memory_id))
    
    async def get_system_stats_async(self) -> Tuple[str, str, str]:
        """Get system statistics asynchronously."""
        try:
            health = await self.memory_core.get_health_status()
            
            # Basic stats
            stats_text = f"📊 System Statistics\n\n"
            stats_text += f"Total Memories: {health['memory_count']}\n"
            stats_text += f"Graph Size: {health['graph_size']}\n"
            stats_text += f"Database: {health['db_path']}\n"
            stats_text += f"Status: {health['status']}\n"
            
            # Recent memories
            recent_memories = await self.memory_core.query_memories("", 10)
            recent_text = "📋 Recent Memories:\n\n"
            
            if recent_memories:
                for i, memory in enumerate(recent_memories, 1):
                    recent_text += f"{i}. {memory['content'][:80]}...\n"
                    recent_text += f"   Priority: {memory['priority_score']:.2f} | Type: {memory['node_type']}\n\n"
            else:
                recent_text += "No memories found."
            
            # Context analysis
            context_text = "🏷️ Context Analysis:\n\n"
            context_types = {}
            
            for memory in recent_memories:
                for key, value in memory.get('context', {}).items():
                    if key not in context_types:
                        context_types[key] = set()
                    context_types[key].add(str(value))
            
            if context_types:
                for key, values in context_types.items():
                    context_text += f"{key.title()}: {', '.join(list(values)[:5])}\n"
            else:
                context_text += "No context data found."
            
            return stats_text, recent_text, context_text
        
        except Exception as e:
            error_msg = f"❌ Error getting system stats: {str(e)}"
            return error_msg, error_msg, error_msg
    
    def get_system_stats(self) -> Tuple[str, str, str]:
        """Get system statistics (sync wrapper)."""
        return asyncio.run(self.get_system_stats_async())
    
    def create_interface(self) -> gr.Interface:
        """Create the Gradio interface."""
        
        with gr.Blocks(title="Memory MCP Admin Interface", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🧠 Memory MCP Admin Interface")
            gr.Markdown("Intelligent memory management with temporal awareness and knowledge graph")
            
            with gr.Tabs():
                # Store Memory Tab
                with gr.Tab("📝 Store Memory"):
                    gr.Markdown("### Store a New Memory")
                    
                    with gr.Row():
                        with gr.Column(scale=3):
                            memory_content = gr.Textbox(
                                label="Memory Content",
                                placeholder="Enter the content you want to remember...",
                                lines=3
                            )
                            
                            memory_context = gr.Textbox(
                                label="Context (JSON)",
                                placeholder='{"project": "example", "type": "meeting", "tags": ["important"]}',
                                lines=2
                            )
                            
                            store_btn = gr.Button("Store Memory", variant="primary")
                        
                        with gr.Column(scale=2):
                            store_result = gr.Textbox(
                                label="Result",
                                lines=5,
                                interactive=False
                            )
                    
                    store_btn.click(
                        self.store_memory,
                        inputs=[memory_content, memory_context],
                        outputs=store_result
                    )
                
                # Search Memory Tab
                with gr.Tab("🔍 Search Memories"):
                    gr.Markdown("### Search Your Memories")
                    
                    with gr.Row():
                        with gr.Column(scale=3):
                            search_query = gr.Textbox(
                                label="Search Query",
                                placeholder="Enter search terms...",
                                lines=1
                            )
                            
                            search_limit = gr.Slider(
                                label="Maximum Results",
                                minimum=1,
                                maximum=50,
                                value=10,
                                step=1
                            )
                            
                            search_btn = gr.Button("Search", variant="primary")
                        
                        with gr.Column(scale=2):
                            search_result = gr.Textbox(
                                label="Search Results",
                                lines=6,
                                interactive=False
                            )
                    
                    search_table = gr.Textbox(
                        label="Results Table",
                        lines=10,
                        interactive=False
                    )
                    
                    search_btn.click(
                        self.search_memories,
                        inputs=[search_query, search_limit],
                        outputs=[search_result, search_table]
                    )
                
                # Recall Memory Tab
                with gr.Tab("🎯 Recall Memory"):
                    gr.Markdown("### Recall Specific Memory by ID")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            memory_id = gr.Textbox(
                                label="Memory ID",
                                placeholder="Enter the full memory ID...",
                                lines=1
                            )
                            
                            recall_btn = gr.Button("Recall Memory", variant="primary")
                        
                        with gr.Column(scale=3):
                            recall_result = gr.Textbox(
                                label="Memory Details",
                                lines=10,
                                interactive=False
                            )
                    
                    recall_btn.click(
                        self.recall_memory,
                        inputs=memory_id,
                        outputs=recall_result
                    )
                
                # System Stats Tab
                with gr.Tab("📊 System Stats"):
                    gr.Markdown("### System Statistics and Overview")
                    
                    stats_btn = gr.Button("Refresh Stats", variant="primary")
                    
                    with gr.Row():
                        with gr.Column():
                            system_stats = gr.Textbox(
                                label="System Statistics",
                                lines=8,
                                interactive=False
                            )
                        
                        with gr.Column():
                            recent_memories = gr.Textbox(
                                label="Recent Memories",
                                lines=8,
                                interactive=False
                            )
                        
                        with gr.Column():
                            context_analysis = gr.Textbox(
                                label="Context Analysis",
                                lines=8,
                                interactive=False
                            )
                    
                    stats_btn.click(
                        self.get_system_stats,
                        outputs=[system_stats, recent_memories, context_analysis]
                    )
                    
                    # Auto-load stats on interface load
                    interface.load(
                        self.get_system_stats,
                        outputs=[system_stats, recent_memories, context_analysis]
                    )
            
            gr.Markdown("---")
            gr.Markdown("💡 **Tips:**")
            gr.Markdown("- Use structured context (JSON) to organize your memories")
            gr.Markdown("- Search supports both content and context matching")
            gr.Markdown("- Memory IDs are automatically generated UUIDs")
            gr.Markdown("- Higher priority scores indicate more frequently accessed memories")
        
        return interface
    
    def launch(self, 
               host: str = "0.0.0.0", 
               port: int = 7860, 
               share: bool = False,
               debug: bool = False) -> None:
        """Launch the Gradio interface."""
        
        self.logger.info("Starting Gradio admin interface", host=host, port=port)
        
        interface = self.create_interface()
        
        interface.launch(
            server_name=host,
            server_port=port,
            share=share,
            debug=debug,
            show_error=True,
            quiet=not debug
        )


def main():
    """Main entry point for the Gradio admin interface."""
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
    host = os.getenv("GRADIO_HOST", "0.0.0.0")
    port = int(os.getenv("GRADIO_PORT", "7860"))
    db_path = os.getenv("MEMORY_DB_PATH", "memory_graph.db")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    # Create and launch interface
    admin_interface = GradioAdminInterface(db_path)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing Gradio admin interface...")
        
        # Test memory operations
        result = admin_interface.store_memory(
            "Test memory from Gradio admin",
            '{"type": "test", "source": "gradio_admin.py"}'
        )
        print(f"Store result: {result}")
        
        # Test search
        search_result, table = admin_interface.search_memories("test", 5)
        print(f"Search result: {search_result}")
        
        # Test stats
        stats, recent, context = admin_interface.get_system_stats()
        print(f"Stats: {stats}")
        
        print("Gradio admin interface tests completed!")
    else:
        print(f"🚀 Starting Memory MCP Admin Interface...")
        print(f"📍 Access at: http://{host}:{port}")
        print(f"📁 Database: {db_path}")
        print("🔧 Use Ctrl+C to stop")
        
        admin_interface.launch(
            host=host,
            port=port,
            share=share,
            debug=debug
        )


if __name__ == "__main__":
    main()