from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import call

import pytest
from tplink_deco_api import LogType

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .conftest import ToolCaller

pytestmark = pytest.mark.anyio

_RAW_LINE = "Mon Oct 26 13:57:02 2026 daemon.notice pppd[18932]: len < 0"


def _severities() -> list[LogType]:
    return [LogType(name="ALL", value=8), LogType(name="NOTICE", value=5)]


def _page(*lines: object, total: object = 3) -> dict[str, object]:
    return {"logList": list(lines), "totalNum": total, "currentIndex": 0}


def _read(index: int) -> object:
    return call(
        "admin/log_export",
        "feedback_log",
        {"operation": "read", "params": {"index": index, "limit": 100}},
    )


async def test_reads_the_newest_page_by_default(call_tool: ToolCaller, deco: MagicMock) -> None:
    deco.get_log_types.return_value = _severities()
    deco.request.side_effect = [{}, _page({"content": "old"}), _page({"content": _RAW_LINE})]

    result = await call_tool("get_system_log")

    assert deco.request.call_args_list == [
        call("admin/log_export", "feedback_log", {"operation": "build", "params": {"level": 5}}),
        _read(0),
        _read(2),
    ]
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


async def test_keeps_structured_fields_and_skips_junk(
    call_tool: ToolCaller, deco: MagicMock
) -> None:
    deco.get_log_types.return_value = _severities()
    structured = {"time": "12:38:31", "level": "INFO", "type": "PPP", "content": "PPPoE up"}
    sourceless = {"content": "Mon Oct 26 15:47:19 2026 user.emerg : tp215,22[2338]:"}
    deco.request.side_effect = [
        {},
        _page(structured, sourceless, {"content": None}, "junk", total=1),
    ]

    result = await call_tool("get_system_log", severity=8)

    assert deco.request.call_count == 2
    assert result.structured_content["severity"] == 8
    assert result.structured_content["entries"] == [
        {
            "time": "12:38:31",
            "facility": "",
            "level": "INFO",
            "source": "PPP",
            "message": "PPPoE up",
        },
        {
            "time": "Mon Oct 26 15:47:19 2026",
            "facility": "user",
            "level": "emerg",
            "source": "",
            "message": "tp215,22[2338]:",
        },
        {"time": "", "facility": "", "level": "", "source": "", "message": ""},
    ]


async def test_reads_a_chosen_page(call_tool: ToolCaller, deco: MagicMock) -> None:
    deco.get_log_types.return_value = _severities()
    deco.request.side_effect = [{}, {"logList": "unexpected"}]

    result = await call_tool("get_system_log", page=1)

    assert deco.request.call_args_list[1:] == [_read(1)]
    assert result.structured_content["page"] == 1
    assert result.structured_content["entries"] == []
    assert result.structured_content["total_pages"] == 0


async def test_rejects_a_negative_page(call_tool: ToolCaller, deco: MagicMock) -> None:
    result = await call_tool("get_system_log", page=-1)

    assert result.is_error
    deco.request.assert_not_called()


async def test_surfaces_router_failures(call_tool: ToolCaller, deco: MagicMock) -> None:
    deco.get_log_types.side_effect = TimeoutError()

    result = await call_tool("get_system_log")

    assert result.is_error
    assert "Failed to read the system log" in result.content[0].text
