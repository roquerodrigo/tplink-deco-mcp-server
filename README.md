# tplink-deco-mcp-server

[![CI](https://github.com/roquerodrigo/tplink-deco-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/tplink-deco-mcp-server/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tplink-deco-mcp-server)](https://pypi.org/project/tplink-deco-mcp-server/)

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white&style=for-the-badge)](https://github.com/sponsors/roquerodrigo)

[Model Context Protocol](https://modelcontextprotocol.io) server that exposes a
**TP-Link Deco** mesh Wi-Fi network as tools an LLM client (Claude Desktop,
Claude Code, etc.) can call. It talks to the router on your local network
through the [`tplink-deco-api`](https://github.com/roquerodrigo/tplink-deco-api)
SDK — no cloud account involved.

## Tools

| Tool | What it does |
| --- | --- |
| `list_deco_nodes` | Deco units of the mesh: model, role, IP, firmware, internet status, backhaul signal. |
| `get_router_performance` | Gateway CPU and memory usage, online clients and total traffic right now. |
| `get_internet_status` | WAN cable, IPv4/IPv6 connection state, public address, gateway and DNS. |
| `get_system_log` | One page of the router's system log (newest by default): time, facility, level, process and message, filterable by minimum severity. |
| `get_wifi_configuration` | Every SSID (main, guest, IoT, MLO) with its bands, plus each radio's channel settings. Passwords only with `include_passwords: true`. |
| `list_clients` | Devices known to the mesh: name, MAC, IP, network, band, category, current traffic. Filter: `online_only`. |
| `update_client` | Rename a device and optionally change its category. |
| `remove_client` | Forget an offline device. |
| `list_blocked_clients` | Devices blocked from the internet. |
| `block_client` / `unblock_client` | Cut a device off from the internet, or let it back in. |
| `list_address_reservations` | Fixed IPs reserved by the DHCP server, with the device names. |
| `add_address_reservation` / `update_address_reservation` / `remove_address_reservation` | Reserve, move or release a device's fixed IP. |

Tools that change settings are annotated as such, so clients can ask for
confirmation before running them.

## Install

```sh
pip install tplink-deco-mcp-server
```

Requires Python ≥ 3.14 and a Deco router reachable on the local network.

## Configuration

The server reads the router credentials from environment variables:

| Variable | Required | Default |
| --- | --- | --- |
| `DECO_HOST` | yes | — (IP of the main Deco, such as `192.168.68.1`) |
| `DECO_PASSWORD` | yes | — (the router's local admin password) |
| `DECO_USERNAME` | no | `admin` |
| `DECO_TIMEOUT` | no | `10` (seconds per router request) |

> [!NOTE]
> The router keeps a single session per account. Every login — from this
> server, the Deco app or another integration — ends the previous one. The
> server logs in again by itself when its session is taken over, but the Deco
> app may ask you to log in again after the server has been used.

## Use with Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "deco": {
      "command": "uvx",
      "args": ["tplink-deco-mcp-server"],
      "env": {
        "DECO_HOST": "192.168.68.1",
        "DECO_PASSWORD": "your-password"
      }
    }
  }
}
```

## Run with Docker

A multi-arch image (`linux/amd64`, `linux/arm64`) is published to GitHub
Container Registry on every release, tagged with the release version
(`1.2.0`, `1.2`, `1`) and `latest`:

```sh
docker run -d --name deco-mcp \
  -e DECO_HOST=192.168.68.1 \
  -e DECO_PASSWORD=your-password \
  -p 8000:8000 \
  ghcr.io/roquerodrigo/tplink-deco-mcp-server:latest
```

The container serves
[Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http)
at `http://localhost:8000/mcp`, with a health endpoint at `/healthz`:

```json
{
  "mcpServers": {
    "deco": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

The HTTP endpoint has no authentication of its own: keep it on a trusted
network or behind a reverse proxy that authenticates. To use stdio instead,
run the server binary as the container command:

```json
{
  "mcpServers": {
    "deco": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "DECO_HOST", "-e", "DECO_PASSWORD",
        "ghcr.io/roquerodrigo/tplink-deco-mcp-server:latest",
        "tplink-deco-mcp-server"
      ],
      "env": {
        "DECO_HOST": "192.168.68.1",
        "DECO_PASSWORD": "your-password"
      }
    }
  }
}
```

## Command-line options

```text
tplink-deco-mcp-server [--transport {stdio,streamable-http}] [--host HOST] [--port PORT]
                       [--log-level {DEBUG,INFO,WARNING,ERROR}]
```

`stdio` is the default transport. `--host` (default `127.0.0.1`) and `--port`
(default `8000`) apply to `streamable-http`.

## Run from source

```sh
git clone https://github.com/roquerodrigo/tplink-deco-mcp-server.git
cd tplink-deco-mcp-server
uv sync
DECO_HOST=… DECO_PASSWORD=… uv run tplink-deco-mcp-server
```

## Support

This MCP server is built and maintained on personal time, on hardware bought for the purpose. If it is useful to you, consider [sponsoring the work](https://github.com/sponsors/roquerodrigo) — it keeps the devices, the testing and the releases coming.

## License

[MIT](./LICENSE)
