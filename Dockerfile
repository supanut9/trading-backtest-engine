# Use a specialized uv image for speed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files and local dependencies
# Note: This Dockerfile assumes the build context is the PROJECT ROOT
COPY trading-backtest-engine/pyproject.toml trading-backtest-engine/uv.lock ./
COPY trading-strategies /app/trading-strategies
COPY trading-data-pipeline /app/trading-data-pipeline

RUN uv sync --frozen --no-install-project --no-dev

# Copy the source code
COPY trading-backtest-engine /app/backtest-engine

# Install the project
WORKDIR /app/backtest-engine
RUN uv sync --frozen --no-dev

# Expose API port
EXPOSE 8005

# Run the API
CMD ["uv", "run", "python", "-m", "backtest.api"]
