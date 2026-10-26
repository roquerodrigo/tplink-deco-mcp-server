"""One page of the gateway's system log, as shown to the model."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from tplink_deco_api import LogType

# Some firmware leaves time/level/type empty and puts the whole syslog line in
# `content`, e.g. "Mon Oct 26 13:57:02 2026 daemon.notice pppd[18932]: len < 0".
_SYSLOG_LINE = re.compile(
    r"^(?P<time>\w{3} \w{3} +\d{1,2} \d{2}:\d{2}:\d{2} \d{4}) "
    r"(?P<facility>\w+)\.(?P<level>\w+) (?P<source>[^:]*): ?(?P<message>.*)$",
    re.DOTALL,
)


class SeveritySummary(BaseModel):
    """A severity the router can filter the log on."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Router's label, e.g. `ERROR` or `ALL`.")
    value: int = Field(description="Pass as `severity` to read this level and everything worse.")


class SystemLogEntrySummary(BaseModel):
    """A single line of the system log."""

    model_config = ConfigDict(frozen=True)

    time: str = Field(description="Timestamp in the router's local time.")
    facility: str = Field(description="Syslog facility such as `daemon` or `kern`, if known.")
    level: str = Field(description="Syslog level such as `err` or `notice`.")
    source: str = Field(description="Process that wrote the line, e.g. `pppd[18932]`.")
    message: str

    @classmethod
    def from_api(cls, item: Mapping[str, object]) -> SystemLogEntrySummary:
        """Build an entry from one ``logList`` item, splitting a raw syslog line if needed."""
        content = _text(item, "content")
        time, level, source = _text(item, "time"), _text(item, "level"), _text(item, "type")
        match = None if time else _SYSLOG_LINE.match(content)
        if match is None:
            return cls(time=time, facility="", level=level, source=source, message=content)
        return cls(
            time=match["time"],
            facility=match["facility"],
            level=match["level"],
            source=match["source"],
            message=match["message"],
        )


class SystemLogSummary(BaseModel):
    """One page of up to 100 system-log lines, plus the severities that can be read."""

    model_config = ConfigDict(frozen=True)

    severity: int = Field(description="Minimum severity this page was filtered on.")
    page: int = Field(description="Zero-based page index; 0 is the oldest page.")
    total_pages: int = Field(description="Number of pages; the last one holds the newest lines.")
    entries: list[SystemLogEntrySummary] = Field(description="Lines from oldest to newest.")
    available_severities: list[SeveritySummary]

    @classmethod
    def from_page(
        cls,
        severity: int,
        page: int,
        result: Mapping[str, object],
        severities: Sequence[LogType],
    ) -> SystemLogSummary:
        """Build the summary from a ``feedback_log`` read result."""
        raw_entries = result.get("logList")
        return cls(
            severity=severity,
            page=page,
            total_pages=total_pages(result),
            entries=[
                SystemLogEntrySummary.from_api(item)
                for item in (raw_entries if isinstance(raw_entries, list) else [])
                if isinstance(item, dict)
            ],
            available_severities=[
                SeveritySummary(name=item.name, value=item.value) for item in severities
            ],
        )


def total_pages(result: Mapping[str, object]) -> int:
    """Return the page count a ``feedback_log`` read reports, or 0 when it is missing."""
    total = result.get("totalNum")
    return total if isinstance(total, int) else 0


def _text(item: Mapping[str, object], key: str) -> str:
    value = item.get(key)
    return "" if value is None else str(value)
