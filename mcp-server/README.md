# DSS MCP Server

This is an [MCP](https://modelcontextprotocol.io) server that exposes the Data Shape
Server (DSS) API as tools for LLM applications.

It wraps the same HTTP endpoints as the bundled
`dss.py` CLI — the CLI stays standard-library only and this MCP server just reuses its
request functionality.

This MCP server can be run without installation (thanks to the tool being available on PyPI) — just
register it with an LLM application (see [Register with a client](#register-with-a-client)).

*Compatibility: This MCP server has been verified to work with Claude Code and the Claude Desktop app.
It should work with other MCP-capable LLM clients, but we have not tested those.*

> Note: `dss.py` in this folder is a copy of the top-level CLI; keep the two in sync
> if you change one.

## Install

*In most cases, you will not need to install this tool – it is enough to just register
it with the LLM client application.*

The easiest way is the published package, which provides the `dss-mcp` command.
The `mcp` extra pulls in the `mcp` runtime (the CLI does not need it):

```bash
pipx install "dss-ai-tools[mcp]"     # provides the `dss-mcp` command
# or run without installing:
uvx --from "dss-ai-tools[mcp]" dss-mcp
```

The `uvx` (no-install) path requires [`uv`](https://docs.astral.sh/uv/) to be
installed — `uvx` is part of `uv`. Install it with `pipx install uv`,
`brew install uv`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Requires Python >= 3.10.

### From a checkout

To run from a clone of this repo instead:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

Point it at a DSS instance via the same environment variables the CLI uses:

```bash
export DSS_BASE_URL=https://dss.semtech.lv   # default
export DSS_TIMEOUT=30                        # optional, seconds
```

Each tool also accepts an optional `base_url` argument to override per call.

## Run

```bash
DSS_BASE_URL=https://dss.semtech.lv dss-mcp                  # if installed (stdio transport)
DSS_BASE_URL=https://dss.semtech.lv .venv/bin/python3 dss_mcp.py   # from a checkout
```

From a checkout, use the venv's interpreter (`.venv/bin/python3`) as shown, or
activate the venv first (`source .venv/bin/activate`) and run `python3 dss_mcp.py`.
Plain `python3` without the venv won't find the `mcp` package.

Or with the MCP CLI for local inspection:

```bash
mcp dev dss_mcp.py
```

## Tools

| Tool | DSS endpoint |
| --- | --- |
| `list_ontologies(variant="default", tag=None)` | `GET /api/info[2-5\|OntTags]`, `GET /api/info3/<tag>` |
| `schema_tags()` | `GET /api/schema_tags` |
| `public_ns()` | `GET /api/public_ns` |
| `namespaces(ontology)` | `GET /api/ontologies/<ont>/ns` |
| `list_classes(ontology, limit=100, filter=None)` | `POST .../getClasses` |
| `list_properties(ontology, kind="All", limit=100, filter=None)` | `POST .../getProperties` |
| `resolve_class(ontology, name)` | `POST .../resolveClassByName` |
| `resolve_property(ontology, name)` | `POST .../resolvePropertyByName` |
| `class_out_properties(ontology, class_id, limit=200)` | `POST .../xx_getClassOutProperties` (by `c_id`) |
| `class_in_properties(ontology, class_id, limit=200)` | `POST .../xx_getClassInProperties` (by `c_id`) |
| `class_pairs(ontology, p_list)` | `POST .../xx_getCPCInfoNew` — (source, target) class pairs for a property |
| `call(ontology, fn, params=None)` | `POST .../<fn>` (escape hatch) |

The `class_*` tools key on numeric ids: get a `class_id` from `resolve_class` and a property id (`p_list`) from `resolve_property`.

## Register with a client

The examples below use `uvx` to fetch and run the server on demand, which
requires [`uv`](https://docs.astral.sh/uv/) to be installed (see [Install](#install)).

### Claude Code

```bash
# from the published package, no checkout needed
claude mcp add dss -e DSS_BASE_URL=https://dss.semtech.lv -- uvx --from "dss-ai-tools[mcp]" dss-mcp

# or from a checkout (use the venv's interpreter so the mcp package is found)
claude mcp add dss -e DSS_BASE_URL=https://dss.semtech.lv -- /path/to/dss-ai-tools/mcp-server/.venv/bin/python3 /path/to/dss-ai-tools/mcp-server/dss_mcp.py
```

### Claude Desktop

1. **Open the config file.** In Claude Desktop go to **Settings → Developer →
   Edit Config**. That opens `claude_desktop_config.json`, located at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the `dss` server** under `mcpServers` (merge this in if the file
   already has other servers):

   ```json
   {
     "mcpServers": {
       "dss": {
         "command": "uvx",
         "args": ["--from", "dss-ai-tools[mcp]", "dss-mcp"],
         "env": { "DSS_BASE_URL": "https://dss.semtech.lv" }
       }
     }
   }
   ```

3. **Restart Claude Desktop** (quit completely, not just close the window).
   Then open a chat and click the tools icon — `dss` and its tools should
   appear.

To run the MCP server from a checkout instead, set `"command"` to the venv's
`.venv/bin/python3` and `"args"` to `["/path/to/dss-ai-tools/mcp-server/dss_mcp.py"]`.

### Troubleshooting

> **If `uvx` isn't found**, Claude Desktop launches with a minimal `PATH` and
> may not see tools installed in your shell. Use the absolute path instead —
> run `which uvx` (macOS/Linux) or `where uvx` (Windows) and put that full path
> in `"command"`, e.g. `"/Users/you/.local/bin/uvx"`.

> **`ModuleNotFoundError: No module named 'mcp'`** means you're running the
> checkout copy with a Python that lacks the `mcp` package. Use the venv's
> `.venv/bin/python3` (after `pip install -r requirements.txt`), not a bare
> `python3`.

