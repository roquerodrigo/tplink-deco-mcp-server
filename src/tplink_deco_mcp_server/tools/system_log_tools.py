"""Tools that read the gateway's system log."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..summaries import SystemLogSummary, total_pages
from .tool_registration import READ_ONLY, register_tool

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mcp.server.mcpserver import MCPServer
    from tplink_deco_api import DecoClient

    from ..router import RouterSession

DEFAULT_SEVERITY = 5
"""`NOTICE`: the level the router's own System Log page opens with."""

PAGE_SIZE = 100
"""Lines per page; the router's web UI uses the same size."""

_LOG_PATH = "admin/log_export"
_LOG_FORM = "feedback_log"


class SystemLogTools:
    """Reads the system log the router shows under Advanced > System > System Log."""

    def __init__(self, router: RouterSession) -> None:
        self._router = router

    def register(self, server: MCPServer[None]) -> None:
        """Add the system-log tools to ``server``."""
        register_tool(server, self.get_system_log, title="System log", annotations=READ_ONLY)

    def get_system_log(
        self,
        severity: Annotated[
            int | None,
            Field(
                description=(
                    "Minimum severity, a `value` from `available_severities`: 1 ALERT, "
                    "2 CRITICAL, 3 ERROR, 4 WARNING, 5 NOTICE, 6 INFO, 7 DEBUG, 8 ALL. "
                    f"Omit for {DEFAULT_SEVERITY} (NOTICE and worse)."
                ),
            ),
        ] = None,
        page: Annotated[
            int | None,
            Field(
                ge=0,
                description=(
                    f"Zero-based page of {PAGE_SIZE} lines; 0 is the oldest. "
                    "Omit for the newest page; lower numbers go back in time."
                ),
            ),
        ] = None,
    ) -> SystemLogSummary:
        """Read one page of the router's system log, newest page by default.

        Returns up to 100 lines from oldest to newest (time, syslog facility
        and level, the process that wrote it, message), the page count, and
        the severities that can be passed as `severity`. Use it to explain
        outages, PPPoE reconnects, reboots, DHCP or Wi-Fi events. The router
        keeps a limited buffer, so older history may already be gone.
        """
        chosen_severity = DEFAULT_SEVERITY if severity is None else severity

        def read(deco: DecoClient) -> SystemLogSummary:
            severities = deco.get_log_types()
            deco.request(
                _LOG_PATH,
                _LOG_FORM,
                {"operation": "build", "params": {"level": chosen_severity}},
            )
            chosen_page = 0 if page is None else page
            result = _read_page(deco, chosen_page)
            newest_page = max(total_pages(result) - 1, 0)
            if page is None and newest_page != chosen_page:
                chosen_page = newest_page
                result = _read_page(deco, chosen_page)
            return SystemLogSummary.from_page(chosen_severity, chosen_page, result, severities)

        return self._router.run("read the system log", read)


def _read_page(deco: DecoClient, page: int) -> Mapping[str, object]:
    return deco.request(
        _LOG_PATH,
        _LOG_FORM,
        {"operation": "read", "params": {"index": page, "limit": PAGE_SIZE}},
    )
