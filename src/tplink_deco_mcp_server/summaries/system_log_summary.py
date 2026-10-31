"""One page of the gateway's system log, as shown to the model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tplink_deco_api import LogType, SystemLogEntry, SystemLogPage


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
    def from_entry(cls, entry: SystemLogEntry) -> SystemLogEntrySummary:
        """Build the summary from an SDK ``SystemLogEntry``."""
        return cls(
            time=entry.time,
            facility=entry.facility,
            level=entry.level,
            source=entry.source,
            message=entry.message,
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
        log_page: SystemLogPage,
        severities: Sequence[LogType],
    ) -> SystemLogSummary:
        """Build the summary from an SDK ``SystemLogPage`` and the router's severities."""
        return cls(
            severity=severity,
            page=log_page.page,
            total_pages=log_page.total_pages,
            entries=[SystemLogEntrySummary.from_entry(entry) for entry in log_page.entries],
            available_severities=[
                SeveritySummary(name=item.name, value=item.value) for item in severities
            ],
        )
