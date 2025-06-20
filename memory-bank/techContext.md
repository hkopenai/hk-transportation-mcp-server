# Technical Context

## Technologies Used
- **Python**: The primary programming language for the MCP server, chosen for its robust ecosystem in data handling and web development.
- **MCP Framework**: The protocol and library used to structure the server and ensure compatibility with other MCP tools and resources.
- **HTTP Libraries**: Libraries like `requests` for fetching data from external APIs or web scraping for data collection.
- **Testing Frameworks**: Tools such as `pytest` for unit and integration testing to validate tool functionality.

## Development Setup
- **Project Directory**: Located at `hkopenai/hk-transportation-mcp-server`.
- **Environment**: Development and testing are conducted in a virtual environment to isolate dependencies.
- **Version Control**: Git is used for source code management, with a `.gitignore` file to exclude unnecessary files from the repository.
- **Build Tools**: Managed through `pyproject.toml` for dependency specification and project metadata.

## Technical Constraints
- **Data Source Reliability**: Dependence on external APIs or web scraping means potential delays or data unavailability if sources change or are offline.
- **Language Support**: Must handle multiple languages (English, Traditional Chinese, Simplified Chinese), requiring careful encoding and formatting considerations.
- **Performance**: Need to optimize data fetching and processing to handle high-frequency requests without significant latency.

## Dependencies
- **External Libraries**: Specific Python packages for HTTP requests, JSON parsing, and data manipulation as listed in `pyproject.toml`.
- **MCP Server Dependencies**: Core MCP libraries or modules required for server operation and tool integration.

## Tool Usage Patterns
- **Tool Structure**: Each tool (e.g., `tool_passenger_traffic.py`, `tool_bus_kmb.py`) is designed as a standalone module with clear input schemas and output formats.
- **Execution**: Tools are invoked through the MCP server interface, with parameters passed via JSON objects adhering to defined schemas.
- **Testing**: Each tool has corresponding test files in the `tests/` directory to ensure functionality and handle edge cases.
