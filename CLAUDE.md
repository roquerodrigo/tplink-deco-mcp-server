# tplink-deco-mcp-server

MCP ([Model Context Protocol](https://modelcontextprotocol.io)) server that
exposes a TP-Link Deco mesh as tools an LLM client can call, built on the
sibling SDK [`tplink-deco-api`](https://github.com/roquerodrigo/tplink-deco-api)
and on the official `mcp` Python SDK (2.x, `MCPServer`). It talks to the router
on the LAN; there is no cloud API and no cache — every tool call is a live
router request.

Published to PyPI as `tplink-deco-mcp-server` (`uvx tplink-deco-mcp-server`)
and as a Docker image at `ghcr.io/roquerodrigo/tplink-deco-mcp-server`.

**Read `CODE_STYLE.md` before adding or restructuring code** — naming, typing,
docstrings, logging, error format, commit conventions and releasing live there.

## Structure

- `router/` — `RouterSettings` (env → settings), `RouterSession` (the single
  authenticated `DecoClient`, behind a lock) and `router_failure.py` (which SDK
  errors mean "session dropped", and how failures are phrased).
- `summaries/` — pydantic models the tools return; they decide what the model
  sees (field names, units, descriptions) and keep SDK shapes out of the
  contract.
- `tools/` — one class per router feature (`MeshTools`, `InternetTools`,
  `WifiTools`, `ClientTools`, `BlocklistTools`, `AddressReservationTools`,
  `SystemLogTools`). Each
  method is a tool; `register()` publishes them through `register_tool`.
- `server.py` builds the `MCPServer` (instructions, tool groups, `/healthz`);
  `cli.py` is the `tplink-deco-mcp-server` entry point.

## Run / verify

```sh
uv sync
uv run ruff format . && uv run ruff check . --fix && uv run mypy
uv run pytest
DECO_HOST=… DECO_PASSWORD=… uv run tplink-deco-mcp-server                       # stdio
DECO_HOST=… DECO_PASSWORD=… uv run tplink-deco-mcp-server --transport streamable-http
```

Tests are network-free: they mock `DecoClient` behind a real `RouterSession`
and drive the tools through an in-process `mcp.Client`, so the JSON schemas,
structured output and error results are exercised end to end. Coverage is
gated at 90%.

## Docker image

Two stages: the first builds the wheel and exports `uv.lock` to a hashed
requirements file; the second `pip install --require-hashes` those, then the
wheel with `--no-deps`. The default command serves Streamable HTTP on
`0.0.0.0:8000` (`/mcp`, health at `/healthz`); passing
`tplink-deco-mcp-server` as the command gives stdio.

```sh
docker build -t tplink-deco-mcp-server:dev .
docker run --rm -e DECO_HOST=… -e DECO_PASSWORD=… -p 8000:8000 tplink-deco-mcp-server:dev
```

## CI and releasing

`ci.yml` runs the shared `python-lint`/`python-test` reusables from
`roquerodrigo/workflows` plus a single-platform `docker` build, so a broken
`Dockerfile` fails the PR instead of the release. `release-please` owns the
version in `pyproject.toml` and `uv.lock` and the `CHANGELOG.md`; merging its PR
publishes to PyPI (`PYPI_API_TOKEN` secret) and pushes the multi-arch image to
ghcr tagged `<version>`, `<major>.<minor>`, `<major>` and `latest`.

## Gotchas

- **One router session per account.** Every login — this server, the Deco app,
  the `ha-tplink-deco` Home Assistant integration — evicts the previous holder.
  `RouterSession` keeps its session open and logs in again only when a request
  is rejected (`ApiError`, `AuthenticationError`, HTTP 401/403); a call can
  therefore cost one extra login when something else took the session in
  between. Don't "fix" this by logging in per call: that evicts everyone else
  on every request.
- **Never write to stdout.** Over stdio, stdout is the JSON-RPC stream. Logging
  is configured to stderr in `cli.py`.
- **Tool descriptions are the method docstrings** (`inspect.cleandoc`), and
  argument descriptions are the `Field(description=…)` in each `Annotated`
  parameter. Both are model-facing: write them for the LLM choosing the tool.
- **Tool signatures are read at runtime** to build the input schema, so types
  used in them (`MacAddress`, summaries) must be imported at module level —
  hence the `TC001` per-file ignore under `tools/`.
- **`ValueError` from the SDK is input validation** (malformed MAC/IP); it
  becomes a `ToolError` without dropping the session. `DecoError`/`OSError`
  drop the session so the next call logs in fresh.
- **Passwords stay out by default.** `get_wifi_configuration` returns Wi-Fi
  passwords only with `include_passwords: true`.
- The MCP server version comes from the installed package metadata, so it
  always matches the release.
- Repo is **public with branch protection** on `main` (reconciled weekly by the
  repository policy in `roquerodrigo/workflows`): land changes through a PR with
  green CI, merged with **rebase merge only**.
