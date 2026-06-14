# dss-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes the Data Shape
Server (DSS) API as tools. It wraps the same HTTP endpoints as the bundled
`dss.py` CLI — the CLI stays standard-library only, this server just reuses its
request helpers. `dss.py` is a copy of the top-level CLI; keep them in sync if
you change one.

## Install

The MCP server runs from a checkout of this repo — it is not part of the `dss-ai-tools` PyPI package, which installs only the `dss` CLI.

The server needs the `mcp` package (the CLI does not):

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
DSS_BASE_URL=https://dss.semtech.lv python3 dss_mcp.py   # stdio transport
```

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

### Claude Code

```bash
claude mcp add dss -e DSS_BASE_URL=https://dss.semtech.lv -- python3 /path/to/dss-ai-tools/mcp-server/dss_mcp.py
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "dss": {
      "command": "python3",
      "args": ["/path/to/dss-ai-tools/mcp-server/dss_mcp.py"],
      "env": { "DSS_BASE_URL": "https://dss.semtech.lv" }
    }
  }
}
```

Use the venv's interpreter (`.venv/bin/python3`) if you installed `mcp` there.
