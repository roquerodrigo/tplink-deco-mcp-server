# Code Style Guide

Style conventions for `tplink-deco-mcp-server`, an MCP server exposing TP-Link
Deco mesh routers as tools for LLM clients. Run
`uv run ruff format . && uv run ruff check . --fix && uv run mypy` before
committing — all three must exit cleanly. `uv run pytest` follows.

**Always read this file before adding or restructuring code.**

## Language

- Code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, tool names and descriptions.
- The conversation language with the user can be Portuguese or anything else;
  what is committed to disk stays English.

## File organization

- **Source layout is `src/tplink_deco_mcp_server/`**, tests in `tests/`,
  packaging in `pyproject.toml`. Hatchling is the build backend.
- **Split by context.** `router/` owns the connection to the router,
  `summaries/` the response shapes, `tools/` the tool groups. A new router
  feature gets its own tool group class (`<feature>_tools.py`) and, when it
  returns data, its own summary module.
- **One top-level class per file.** Leaf models parsed from a single payload
  may share the module named after the top-level model
  (`internet_status_summary.py` holds `IpConnectionSummary`,
  `WanAddressSummary`, …).
- **Public surface goes through each package's `__init__.py`.** Module-level
  private helpers are prefixed `_`.

## Naming

- Classes are `CapWords`, describing what they are: `RouterSession`,
  `ClientSummary`, `BlocklistTools`.
- Functions, methods and variables are `snake_case`. **No abbreviations**:
  `download_kilobytes_per_second`, not `down_kbps`.
- **Tool names are the method names**, `snake_case` verbs: `list_clients`,
  `block_client`, `get_internet_status`.
- Summary fields are named for the model reading them, not after the router's
  wire keys (`network` instead of `interface`, `firmware_version` instead of
  `software_ver`).

## Typing

**Strict typing. No `Any`, no bare collection generics.** Mypy enforces this
with `disallow_any_explicit`.

- Response shapes are frozen pydantic models (`model_config =
  ConfigDict(frozen=True)`); their `Field(description=…)` ends up in the
  tool's output schema.
- Tool arguments are `Annotated[<type>, Field(description=…)]`; shared ones live
  in `tools/tool_parameters.py` (`MacAddress`).
- `MCPServer` is always parametrized: `MCPServer[None]`.
- Always type return values explicitly.

## Imports

- Every module starts with `from __future__ import annotations`.
- Same-package relative imports (`from .module import …`) are the default.
- Type-only imports go into a `TYPE_CHECKING` block — **except** what tool
  signatures and pydantic fields reference: the MCP server and pydantic resolve
  those annotations at runtime.
- `noqa` comments require a written justification inline.

## Docstrings

- Every public class, function and method has a docstring; a module docstring
  opens every file.
- **A tool method's docstring is its model-facing description.** Lead with
  what the tool does and when to use it, then what it returns. Mention
  related tools by name when the model should call one first or instead.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious: a
  hidden constraint, a router quirk, an MCP-protocol detail.
- **No section dividers.** Split into files instead.

## Logging

- Module-level logger with an explicit dotted name:
  `log: logging.Logger = logging.getLogger("tplink_deco_mcp_server.<area>")`.
- Lazy `%`-formatting, never f-strings.
- **Never write to stdout** — it is the JSON-RPC stream over stdio. Logging is
  configured to stderr in `cli.py`; no `print`.
- Never log the router password, session tokens or Wi-Fi passwords.

## Error messages

- Format: `"Failed to <verb> <object>: <cause>"`. Keep them short and
  grep-able — the model reads them to decide what to do next.
- Tool code raises `ValueError` for bad input and lets SDK errors propagate;
  `RouterSession.run` turns both into a `ToolError`, which the server returns
  as `isError: true` content. Don't raise anything else across the tool
  boundary: the server hides other exceptions behind a generic message.
- Bind the message to a local before raising: `message = "…"` then
  `raise ValueError(message)`.

## Public API surface

- **The MCP tool list is the public contract.** Adding a tool is `feat`;
  removing or renaming a tool, an argument or a summary field is a
  `BREAKING CHANGE:` — clients and prompts hard-code them.
- Read-only tools carry `READ_ONLY` annotations; tools that change settings
  carry `CHANGES_SETTINGS` or, when they discard something, `DISCARDS_SETTINGS`.

## Pre-commit hooks

The repository ships `.pre-commit-config.yaml` mirroring the lint commands;
install once per clone with `pre-commit install`.

## Conventional commits

All commits follow [Conventional Commits](https://www.conventionalcommits.org/),
in **English**, which Release Autopilot parses to bump the version and write
`CHANGELOG.md`:

| Type | Meaning | Bump |
|---|---|---|
| `feat` | New feature (e.g. new tool) | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `deps` | Dependency bump | patch |
| `docs` | Documentation only | none |
| `refactor` | Refactor without behavior change | none |
| `test` | Test-only change | none |
| `ci` | CI / tooling change | none |
| `chore` | Anything else (rarely) | none |

- Subject line: imperative mood, lowercase, no trailing period.
- Use scopes when useful: `feat(tools): add guest network toggle`.
- A `BREAKING CHANGE:` footer (or `!` after type) bumps the major version.

## Packaging

- `requires-python = ">=3.14"`, matching `tplink-deco-api`.
- Runtime dependencies use `>=` lower bounds; `uv.lock` pins what CI and the
  Docker image install.
- `[project.scripts]` exposes `tplink-deco-mcp-server`.

## Releasing

- Release Autopilot keeps a release PR up to date with the next version and
  `CHANGELOG.md`. Merging it publishes to PyPI and pushes the Docker image to
  ghcr.
- Don't manually edit the version in `pyproject.toml` — Release Autopilot
  owns it.

## Testing

- `uv run pytest` runs the suite, gated at **90%** coverage.
- The suite is **network-free**: mock `DecoClient` (see `tests/conftest.py`)
  and drive tools through the in-process `mcp.Client` fixture `call_tool`, so
  schemas, structured output and error results are covered as clients see them.
- Build SDK records through `tests/factories.py`, overriding only the fields a
  test cares about.
