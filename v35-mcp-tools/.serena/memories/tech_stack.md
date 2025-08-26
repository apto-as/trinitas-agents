The v35-mcp-tools project is built on a modern, asynchronous Python stack designed for high performance and production readiness.

- **Programming Language:** Python 3.9+
- **Core Framework:** FastAPI (via the `fastmcp` library), used for creating the high-performance API server.
- **Asynchronous Operations:** `asyncio` is used extensively for non-blocking I/O, making the server highly concurrent.
- **HTTP Client:** `aiohttp` is used for making asynchronous HTTP requests, particularly in `local_llm_client.py` to communicate with local LLM servers.
- **Data Validation:** Pydantic is used (often implicitly through FastAPI) for data validation and settings management.
- **Caching:** The system includes a sophisticated multi-level caching mechanism that can use in-memory, disk, and Redis caches.
- **System Monitoring:** `psutil` is used for accessing system-level metrics like CPU and memory usage.
- **Testing:** The testing framework appears to be a mix of `pytest` and the standard `unittest` library. `locust` is used for load testing.
- **Linting/Formatting:** `Ruff` is used for linting and formatting, and `mypy` for type checking.