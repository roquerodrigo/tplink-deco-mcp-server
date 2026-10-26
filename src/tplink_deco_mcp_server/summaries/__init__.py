"""Response shapes the tools hand to the model, built from the SDK records."""

from __future__ import annotations

from .address_reservation_summary import AddressReservationSummary, AddressReservationTableSummary
from .blocked_client_summary import BlockedClientSummary
from .client_summary import ClientSummary
from .internet_status_summary import (
    InternetStatusSummary,
    IpConnectionSummary,
    LanAddressSummary,
    WanAddressSummary,
)
from .node_summary import NodeSummary
from .performance_summary import PerformanceSummary
from .system_log_summary import (
    SeveritySummary,
    SystemLogEntrySummary,
    SystemLogSummary,
    total_pages,
)
from .wifi_configuration_summary import (
    WifiConfigurationSummary,
    WifiNetworkSummary,
    WifiRadioSummary,
)

__all__ = [
    "AddressReservationSummary",
    "AddressReservationTableSummary",
    "BlockedClientSummary",
    "ClientSummary",
    "InternetStatusSummary",
    "IpConnectionSummary",
    "LanAddressSummary",
    "NodeSummary",
    "PerformanceSummary",
    "SeveritySummary",
    "SystemLogEntrySummary",
    "SystemLogSummary",
    "WanAddressSummary",
    "WifiConfigurationSummary",
    "WifiNetworkSummary",
    "WifiRadioSummary",
    "total_pages",
]
