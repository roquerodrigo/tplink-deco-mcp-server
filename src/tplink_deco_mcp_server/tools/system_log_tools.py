"""Tools that read the gateway's system log."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..summaries import SystemLogSummary
from .tool_registration import READ_ONLY, register_tool

if TYPE_CHECKING:
    from mcp.server.mcpserver import MCPServer
    from tplink_deco_api import DecoClient

    from ..router import RouterSession

# NOTICE, the level the router's own System Log page opens with.
_DEFAULT_SEVERITY = 5


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
                    "Minimum severity, a `value` from `available_severities` of an earlier "
                    "result. Omit for NOTICE and worse."
                ),
            ),
        ] = None,
        page: Annotated[
            int | None,
            Field(
                ge=0,
                description=(
                    "Zero-based page of 100 lines; 0 is the oldest. "
                    "Omit for the newest page; lower numbers go back in time."
                ),
            ),
        ] = None,
    ) -> SystemLogSummary:
        """Read one page of the router's system log, newest page by default.

        Returns up to 100 lines from oldest to newest (time, syslog facility
        and level, the process that wrote it, message), the page count, and
        the severities that can be passed as `severity`. Use it to explain
        outages, PPPoE reconnects, reboots, DHCP or Wi-Fi events. The newest
        page can hold only a few lines, so read the page before it when more
        context is needed. The router keeps a limited buffer, so older history
        may already be gone.
        """

        def read(deco: DecoClient) -> SystemLogSummary:
            severities = deco.get_log_types()
            # The session layer takes any ApiError for a dropped session and logs in
            # again, evicting the account's other holder, so never send an unknown level.
            if severity is not None and severity not in {item.value for item in severities}:
                message = f"Failed to read the system log: unknown severity {severity}"
                raise ValueError(message)
            chosen_severity = _DEFAULT_SEVERITY if severity is None else severity
            log_page = deco.get_system_log(chosen_severity, page)
            return SystemLogSummary.from_page(chosen_severity, log_page, severities)

        return self._router.run("read the system log", read)
