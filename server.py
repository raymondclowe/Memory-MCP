#!/usr/bin/env python3
"""
Memory MCP Server - Main entry point for the Memory Management Server.

This server implements the Model Context Protocol with intelligent memory management,
temporal awareness, and background AI processing for relationship discovery.

Usage:
    python server.py [mode] [options]

Modes:
    --mcp                Run MCP server on stdio (default)
    --rest               Run REST API server 
    --admin              Run Gradio admin interface
    --all                Run all services (REST API + Admin interface)
    --help               Show this help message

Environment Variables:
    MEMORY_HOST          Server host (default: 0.0.0.0)
    MEMORY_PORT          REST API port (default: 8080)  
    MEMORY_GRADIO_PORT   Admin interface port (default: 7860)
    MEMORY_DB_PATH       Database file path (default: memory_graph.db)
    MEMORY_AI_API_KEY    OpenAI API key for embeddings
"""

import asyncio
import signal
import sys
import os
from typing import List, Optional
import threading
import time

import structlog

from config import load_config
from memory_core import MemoryCore
from mcp_server import MCPMemoryServer
from rest_api import RESTAPIServer
from gradio_admin import GradioAdminInterface

logger = structlog.get_logger()


class MemoryMCPMain:
    """Main server orchestrator for Memory MCP."""
    
    def __init__(self):
        self.config = load_config()
        self.logger = structlog.get_logger().bind(component="main")
        self.running = True
        self.services = []
        
        # Configure logging based on config
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure structured logging."""
        log_level = getattr(structlog.stdlib, self.config.log_level.upper(), structlog.stdlib.INFO)
        
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
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            logger_level=log_level
        )
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info("Received shutdown signal", signal=signum)
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_mcp_server(self):
        """Run the MCP server on stdio."""
        self.logger.info("Starting MCP server on stdio")
        
        server = MCPMemoryServer(self.config.db_path)
        await server.run_stdio()
    
    async def run_rest_api(self):
        """Run the REST API server."""
        self.logger.info("Starting REST API server", host=self.config.host, port=self.config.port)
        
        server = RESTAPIServer(self.config.db_path)
        await server.start_server(self.config.host, self.config.port)
    
    def run_gradio_admin(self):
        """Run the Gradio admin interface."""
        self.logger.info("Starting Gradio admin interface", 
                        host=self.config.gradio_host, 
                        port=self.config.gradio_port)
        
        admin_interface = GradioAdminInterface(self.config.db_path)
        admin_interface.launch(
            host=self.config.gradio_host,
            port=self.config.gradio_port,
            share=self.config.gradio_share,
            debug=self.config.log_level.upper() == "DEBUG"
        )
    
    async def run_all_services(self):
        """Run REST API and admin interface together."""
        self.logger.info("Starting all services")
        
        # Start Gradio in a separate thread
        gradio_thread = threading.Thread(target=self.run_gradio_admin, daemon=True)
        gradio_thread.start()
        
        # Give Gradio time to start
        await asyncio.sleep(2)
        
        # Start REST API in the main event loop
        await self.run_rest_api()
    
    def print_startup_info(self):
        """Print startup information."""
        print("\n" + "="*60)
        print("🧠 Memory MCP Server")
        print("="*60)
        print(f"📁 Database: {self.config.db_path}")
        print(f"🔧 Log Level: {self.config.log_level}")
        print(f"🤖 AI Provider: {self.config.ai_provider}")
        print(f"🔄 Dreamer: {'Enabled' if self.config.dreamer_enabled else 'Disabled'}")
        print("="*60)
        print("🚀 Services:")
    
    def print_service_info(self, mode: str):
        """Print service-specific information."""
        if mode == "mcp":
            print("   📡 MCP Server: stdio mode")
            print("   💡 Connect using MCP-compatible clients")
        elif mode == "rest":
            print(f"   🌐 REST API: http://{self.config.host}:{self.config.port}")
            print(f"   📖 Documentation: http://{self.config.host}:{self.config.port}/docs")
        elif mode == "admin":
            print(f"   🎛️  Admin Interface: http://{self.config.gradio_host}:{self.config.gradio_port}")
        elif mode == "all":
            print(f"   🌐 REST API: http://{self.config.host}:{self.config.port}")
            print(f"   📖 API Docs: http://{self.config.host}:{self.config.port}/docs")
            print(f"   🎛️  Admin Interface: http://{self.config.gradio_host}:{self.config.gradio_port}")
        
        print("="*60)
        print("🛑 Press Ctrl+C to stop")
        print()
    
    async def health_check(self):
        """Perform initial health check."""
        try:
            memory_core = MemoryCore(self.config.db_path)
            health = await memory_core.get_health_status()
            self.logger.info("Health check passed", **health)
            return True
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return False
    
    async def run(self, mode: str = "mcp"):
        """Run the server in the specified mode."""
        self._setup_signal_handlers()
        
        # Perform health check
        if not await self.health_check():
            print("❌ Health check failed. Please check your configuration.")
            return 1
        
        # Print startup information
        self.print_startup_info()
        self.print_service_info(mode)
        
        try:
            if mode == "mcp":
                await self.run_mcp_server()
            elif mode == "rest":
                await self.run_rest_api()
            elif mode == "admin":
                # Run in a thread since Gradio blocks
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.run_gradio_admin)
            elif mode == "all":
                await self.run_all_services()
            else:
                print(f"❌ Unknown mode: {mode}")
                return 1
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down gracefully")
        except Exception as e:
            self.logger.error("Server error", error=str(e))
            return 1
        
        return 0


def show_help():
    """Show help message."""
    print(__doc__)


def main():
    """Main entry point."""
    
    # Parse command line arguments
    mode = "mcp"  # default mode
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["--help", "-h", "help"]:
            show_help()
            return 0
        elif arg in ["--mcp", "mcp"]:
            mode = "mcp"
        elif arg in ["--rest", "rest", "--api", "api"]:
            mode = "rest"
        elif arg in ["--admin", "admin", "--gradio", "gradio"]:
            mode = "admin"
        elif arg in ["--all", "all", "--full", "full"]:
            mode = "all"
        elif arg in ["--create-env"]:
            from config import create_sample_env_file
            create_sample_env_file()
            return 0
        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use --help for usage information")
            return 1
    
    # Create and run server
    server = MemoryMCPMain()
    
    try:
        return asyncio.run(server.run(mode))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())