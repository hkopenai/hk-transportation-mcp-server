# System Patterns

## System Architecture
The Hong Kong Transportation MCP Server is built as a modular Python application following the Model Context Protocol (MCP) framework. The architecture is designed to separate concerns between data retrieval, processing, and API exposure:
- **Data Layer**: Responsible for fetching data from external sources such as government APIs or transportation service providers.
- **Processing Layer**: Handles data transformation, aggregation, and formatting to ensure consistency and usability.
- **API Layer**: Exposes processed data through MCP-compatible endpoints for integration with other systems.

## Key Technical Decisions
- **Python as Primary Language**: Chosen for its extensive library support for web scraping, data processing, and API development.
- **MCP Framework Compliance**: Ensures interoperability with other MCP servers and tools, adhering to standardized communication protocols.
- **Modular Tool Structure**: Each data retrieval function (e.g., passenger stats, bus routes) is encapsulated as a distinct tool within the server for maintainability and scalability.

## Design Patterns in Use
- **Decorator Pattern**: Utilized in tool implementations to add logging, caching, or authentication without modifying core logic (see `decorators.py`).
- **Factory Pattern**: Considered for future expansions to dynamically instantiate data source connectors based on configuration or runtime needs.
- **Singleton Pattern**: Applied to certain shared resources or configuration managers to ensure a single point of access across the application.

## Component Relationships
- **App Core (`server.py`)**: Central hub that initializes and manages all tools and resources, serving as the entry point for MCP interactions.
- **Tools (`tool_*.py`)**: Independent modules for specific data types, each interacting with the data layer to fetch and process information, then returning results to the app core for API exposure.
- **Tests (`tests/`)**: Comprehensive test suite that validates individual tool functionality and overall system integration.

## Critical Implementation Paths
- **Data Fetching Workflow**: External data sources -> Data Layer (HTTP requests or scraping) -> Processing Layer (data cleaning and structuring) -> API Layer (formatted response).
- **Error Handling**: Centralized error handling in `app.py` to manage exceptions from tools, ensuring consistent error reporting through MCP endpoints.
- **Language Support**: Tools support multiple languages (English, Traditional Chinese, Simplified Chinese) for data output, managed through parameters in API calls.
