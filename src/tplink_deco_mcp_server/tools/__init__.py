"""Tool groups, one per router feature, each registering its tools on the server."""

from __future__ import annotations

from .address_reservation_tools import AddressReservationTools
from .blocklist_tools import BlocklistTools
from .client_tools import ClientTools
from .internet_tools import InternetTools
from .mesh_tools import MeshTools
from .system_log_tools import SystemLogTools
from .tool_registration import ToolGroup
from .wifi_tools import WifiTools

__all__ = [
    "AddressReservationTools",
    "BlocklistTools",
    "ClientTools",
    "InternetTools",
    "MeshTools",
    "SystemLogTools",
    "ToolGroup",
    "WifiTools",
]
