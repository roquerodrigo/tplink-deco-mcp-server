from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .factories import log_types, system_log_page

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .conftest import ToolCaller

pytestmark = pytest.mark.anyio


async def test_reads_the_newest_page_at_the_default_severity(
    call_tool: ToolCaller, deco: MagicMock
) -> None:
    deco.get_log_types.return_value = log_types()
    deco.get_system_log.return_value = system_log_page()

    result = await call_tool("get_system_log")

    deco.get_system_log.assert_called_once_with(5, None)
    assert result.structured_content == {
        "severity": 5,
        "page": 2,
        "total_pages": 3,
        "entries": [
            {
                "time": "Mon Oct 26 13:57:02 2026",
                "facility": "daemon",
                "level": "notice",
                "source": "pppd[18932]",
                "message": "len < 0",
            }
        ],
        "available_severities": [{"name": "ALL", "value": 8}, {"name": "NOTICE", "value": 5}],
    }


async def test_reads_a_chosen_severity_and_page(call_tool: ToolCaller, deco: MagicMock) -> None:
    deco.get_log_types.return_value = log_types()
    deco.get_system_log.return_value = system_log_page(page=1)

    result = await call_tool("get_system_log", severity=8, page=1)

    deco.get_system_log.assert_called_once_with(8, 1)
    assert result.structured_content["severity"] == 8
    assert result.structured_content["page"] == 1


async def test_rejects_a_severity_the_router_does_not_offer(
    call_tool: ToolCaller, deco: MagicMock
) -> None:
    deco.get_log_types.return_value = log_types()

    result = await call_tool("get_system_log", severity=99)

    assert result.is_error
    assert "unknown severity 99" in result.content[0].text
    deco.get_system_log.assert_not_called()
    deco.login.assert_called_once()


async def test_rejects_a_negative_page(call_tool: ToolCaller, deco: MagicMock) -> None:
    result = await call_tool("get_system_log", page=-1)

    assert result.is_error
    deco.get_system_log.assert_not_called()


async def test_surfaces_router_failures(call_tool: ToolCaller, deco: MagicMock) -> None:
    deco.get_log_types.side_effect = TimeoutError()

    result = await call_tool("get_system_log")

    assert result.is_error
    assert "Failed to read the system log" in result.content[0].text
