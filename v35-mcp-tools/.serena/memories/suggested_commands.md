This file contains a list of common and useful commands for developing, testing, and running the `v35-mcp-tools` project.

### Running the Application

- **Run the main server (enhanced version):**
  ```bash
  python v35-mcp-tools/mcp_server_enhanced.py
  ```
- **Run the basic server:**
  ```bash
  python v35-mcp-tools/mcp_server.py
  ```

### Code Quality & Formatting

- **Check for linting errors with Ruff:**
  ```bash
  ruff check .
  ```
- **Format code with Ruff:**
  ```bash
  ruff format .
  ```
- **Run static type checking with mypy:**
  ```bash
  mypy .
  ```

### Testing

- **Run the entire test suite with pytest:**
  ```bash
  pytest v35-mcp-tools/
  ```
- **Run a specific test file:**
  ```bash
  python v35-mcp-tools/test_mode_switching.py
  ```
- **Run the integration tests:**
  ```bash
  python v35-mcp-tools/integration_tests.py
  ```
- **Run the load tests (requires locust):**
  ```bash
  locust -f v35-mcp-tools/load_test.py --host=http://localhost:8000
  ```

### Deployment

- **Run the production deployment script (requires sudo):**
  ```bash
  sudo ./v35-mcp-tools/deploy.sh
  ```
- **Run the system using Docker Compose for production:**
  ```bash
  docker-compose -f v35-mcp-tools/docker-compose.production.yml up -d
  ```

### System Health

- **Run the health check script:**
  ```bash
  python v35-mcp-tools/health_check.py
  ```