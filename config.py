"""
Configuration management for Memory MCP.

Handles environment variables, settings, and configuration loading.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MemoryMCPConfig(BaseSettings):
    """Configuration settings for Memory MCP."""
    
    model_config = SettingsConfigDict(
        env_prefix="MEMORY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8080, description="Server port number")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Database Configuration
    db_type: str = Field(default="sqlite", description="Database type")
    db_path: str = Field(default="memory_graph.db", description="SQLite database path")
    db_url: Optional[str] = Field(default=None, description="Database URL (for non-SQLite)")
    db_user: Optional[str] = Field(default=None, description="Database username")
    db_password: Optional[str] = Field(default=None, description="Database password")
    
    # AI Configuration
    ai_provider: str = Field(default="openai", description="AI provider (openai, anthropic, local)")
    ai_api_key: Optional[str] = Field(default=None, description="AI provider API key")
    ai_model: str = Field(default="gpt-3.5-turbo", description="AI model to use")
    ai_embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model")
    
    # Authentication
    auth_enabled: bool = Field(default=False, description="Enable API authentication")
    api_keys: Optional[str] = Field(default=None, description="Comma-separated API keys")
    
    # Gradio Configuration
    gradio_host: str = Field(default="0.0.0.0", description="Gradio admin interface host")
    gradio_port: int = Field(default=7860, description="Gradio admin interface port")
    gradio_share: bool = Field(default=False, description="Enable Gradio sharing")
    
    # Background Processing
    dreamer_enabled: bool = Field(default=True, description="Enable background Dreamer AI")
    dreamer_interval: int = Field(default=300, description="Dreamer processing interval in seconds")
    max_connections: int = Field(default=10, description="Maximum concurrent connections")
    
    # Performance Settings
    memory_cache_size: int = Field(default=1000, description="Memory cache size")
    query_timeout: int = Field(default=30, description="Query timeout in seconds")
    
    def get_api_keys(self) -> list[str]:
        """Get list of valid API keys."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "type": self.db_type,
            "path": self.db_path,
            "url": self.db_url,
            "user": self.db_user,
            "password": self.db_password
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration."""
        return {
            "provider": self.ai_provider,
            "api_key": self.ai_api_key,
            "model": self.ai_model,
            "embedding_model": self.ai_embedding_model
        }


def load_config() -> MemoryMCPConfig:
    """Load configuration from environment and files."""
    
    # Look for .env file in current directory and parent directories
    env_file = None
    current_dir = Path.cwd()
    
    for dir_path in [current_dir] + list(current_dir.parents):
        env_path = dir_path / ".env"
        if env_path.exists():
            env_file = str(env_path)
            break
    
    # Create config with discovered .env file
    if env_file:
        config = MemoryMCPConfig(_env_file=env_file)
    else:
        config = MemoryMCPConfig()
    
    return config


def create_sample_env_file(path: str = ".env.example") -> None:
    """Create a sample environment file with all configuration options."""
    
    sample_content = """# Memory MCP Configuration

# Server Configuration
MEMORY_HOST=0.0.0.0
MEMORY_PORT=8080
MEMORY_LOG_LEVEL=INFO

# Database Configuration (SQLite by default)
MEMORY_DB_TYPE=sqlite
MEMORY_DB_PATH=memory_graph.db
# For other databases:
# MEMORY_DB_URL=bolt://localhost:7687
# MEMORY_DB_USER=username
# MEMORY_DB_PASSWORD=password

# AI Configuration
MEMORY_AI_PROVIDER=openai
MEMORY_AI_API_KEY=your-openai-api-key-here
MEMORY_AI_MODEL=gpt-3.5-turbo
MEMORY_AI_EMBEDDING_MODEL=text-embedding-ada-002

# Authentication (optional)
MEMORY_AUTH_ENABLED=false
MEMORY_API_KEYS=key1,key2,key3

# Gradio Admin Interface
MEMORY_GRADIO_HOST=0.0.0.0
MEMORY_GRADIO_PORT=7860
MEMORY_GRADIO_SHARE=false

# Background Processing
MEMORY_DREAMER_ENABLED=true
MEMORY_DREAMER_INTERVAL=300
MEMORY_MAX_CONNECTIONS=10

# Performance Settings
MEMORY_CACHE_SIZE=1000
MEMORY_QUERY_TIMEOUT=30
"""
    
    with open(path, "w") as f:
        f.write(sample_content)
    
    print(f"Sample configuration file created: {path}")
    print("Copy this to .env and customize your settings.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-env":
        create_sample_env_file()
    else:
        # Test configuration loading
        config = load_config()
        print("Current configuration:")
        print(f"Host: {config.host}")
        print(f"Port: {config.port}")
        print(f"Database: {config.db_type} at {config.db_path}")
        print(f"AI Provider: {config.ai_provider}")
        print(f"Gradio Port: {config.gradio_port}")
        print(f"Dreamer Enabled: {config.dreamer_enabled}")