# Hong Kong transportation Data MCP Server

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/hkopenai/hk-transportation-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is an MCP server that provides access to transportation related data in Hong Kong through a FastMCP interface.

## Features

### Passenger Traffic Statistics
- Get daily passenger traffic statistics at Hong Kong control points. Filter data by date ranges. Breakdown statistics by visitor types (Hong Kong Residents, Mainland Visitors, Other Visitors)

### Real time Arrival Data of Kowloon Motor Bus and Long Win Bus Services
- Get all bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services. Filter by language (English, Traditional Chinese, Simplified Chinese)

### Land Boundary Control Points Waiting Times
- Fetch current waiting times at land boundary control points in Hong Kong. Filter by language (English, Traditional Chinese, Simplified Chinese)

## Data Source

- Passenger traffic data from Hong Kong Immigration Department
- Bus route data from Kowloon Motor Bus and Long Win Bus Services

## Examples

* How many hong kong arrival yesterday through high speed railway.
* Get all KMB/LWB bus routes in Traditional Chinese.
* What are the current waiting times at Hong Kong land boundary control points?

## Setup

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python server.py
   ```

### Running Options

- Default stdio mode: `python server.py`
- SSE mode (port 8000): `python server.py --sse`

## Cline Integration

To connect this MCP server to Cline using stdio:

1. Add this configuration to your Cline MCP settings (cline_mcp_settings.json):
```json
{
  "hk-transportation": {
    "disabled": false,
    "timeout": 3,
    "type": "stdio",
    "command": "uvx",
    "args": [
      "hkopenai.hk-transportation-mcp-server"
    ]
  }
}
```

## Testing

Tests are available in the `tests/` directory. Run with:
```bash
pytest
```
