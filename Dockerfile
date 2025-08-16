FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8080 7860

# Set environment variables
ENV MEMORY_HOST=0.0.0.0
ENV MEMORY_PORT=8080
ENV MEMORY_GRADIO_HOST=0.0.0.0
ENV MEMORY_GRADIO_PORT=7860
ENV MEMORY_DB_PATH=/app/data/memory_graph.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from memory_core import MemoryCore; asyncio.run(MemoryCore().get_health_status())" || exit 1

# Default command (can be overridden)
CMD ["python", "server.py", "--all"]