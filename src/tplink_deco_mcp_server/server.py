"""Assemble the MCP server and its tool groups."""

from __future__ import annotations

from importlib.metadata import version
from typing import TYPE_CHECKING

from mcp.server.mcpserver import MCPServer
from starlette.responses import PlainTextResponse

from .tools import (
    AddressReservationTools,
    BlocklistTools,
    ClientTools,
    InternetTools,
    MeshTools,
    SystemLogTools,
    WifiTools,
)

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

    from .router import RouterSession
    from .tools import ToolGroup

SERVER_NAME = "tplink-deco-mcp-server"

_INSTRUCTIONS = """\
This MCP provides access to a TP-Link Deco mesh Wi-Fi network on the local network.

Use it when the user asks about their home network, Wi-Fi, router, internet connection, or the \
devices connected to it: who is online, which device uses bandwidth, which IP a device has, \
renaming devices, blocking a device from the internet, reserving a fixed IP, reading the \
router's system log, or diagnosing an outage.

Devices are identified by MAC address. When the user names a device, call `list_clients` first \
to resolve its MAC. Tools that change settings apply immediately on the router.\
"""


def build_server(router: RouterSession) -> MCPServer[None]:
    """Return an MCP server whose tools act on the mesh through ``router``."""
    server: MCPServer[None] = MCPServer(
        name=SERVER_NAME, version=version(SERVER_NAME), instructions=_INSTRUCTIONS
    )
    tool_groups: tuple[ToolGroup, ...] = (
        MeshTools(router),
        InternetTools(router),
        WifiTools(router),
        ClientTools(router),
        BlocklistTools(router),
        AddressReservationTools(router),
        SystemLogTools(router),
    )
    for tool_group in tool_groups:
        tool_group.register(server)
    server.custom_route("/healthz", methods=["GET"])(_report_health)
    return server


async def _report_health(_request: Request) -> Response:
    return PlainTextResponse("ok")
