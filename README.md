[![License](http://img.shields.io/:license-mit-blue.svg)](https://raw.githubusercontent.com/LUMII-Syslab/viziquer/master/LICENSE)
# dss-ai-tools

Tools for exploring a [Data Shape Server (DSS)](https://github.com/LUMII-Syslab/data-shape-server) knowledge-graph schemas — classes, properties, their relations, and namespaces — over the DSS HTTP API. Three ways to use it, all sharing one small client:

| Component | What it is | Where |
| --- | --- | --- |
| **CLI** | A single-file Python client (`dss`), standard library only, Python ≥ 3.9. | [`dss.py`](dss.py) |
| **Claude skill** | A self-contained Claude Code skill that drives the CLI. | [`skill/`](skill/) |
| **MCP server** | An [MCP](https://modelcontextprotocol.io) server exposing the same endpoints as tools. | [`mcp-server/`](mcp-server/) |

The CLI is the source of truth; the skill and MCP server bundle a copy of `dss.py` so each is self-contained. Run [`scripts/sync.sh`](scripts/sync.sh) after editing the canonical `dss.py` to refresh the copies.

## Configure

All three read the same environment variables:

```bash
export DSS_BASE_URL=https://dss.semtech.lv   # default
export DSS_TIMEOUT=30                        # optional, seconds
```

The CLI and MCP tools also accept a per-call override (`--base-url` / `base_url`).

## CLI

```bash
python3 dss.py --help
```

Install on your PATH (optional):

```bash
pipx install .          # provides the `dss` command (see pyproject.toml)
# or, no packaging:
ln -s "$(pwd)/dss.py" ~/.local/bin/dss && chmod +x dss.py
```

### Commands

| Command | DSS endpoint |
| --- | --- |
| `ontologies [--variant ...] [--tag TAG]` | `GET /api/info` (variants `2`–`5`, `tags`; `--tag` with variant `3`) |
| `schema-tags` | `GET /api/schema_tags` |
| `public-ns` | `GET /api/public_ns` |
| `namespaces <ont>` | `GET /api/ontologies/<ont>/ns` |
| `classes <ont> [--limit N] [--filter STR]` | `POST .../getClasses` |
| `properties <ont> [--limit N] [--filter REGEX] [--kind ...]` | `POST .../getProperties` |
| `resolve-class <ont> <name>` | `POST .../resolveClassByName` |
| `resolve-property <ont> <name>` | `POST .../resolvePropertyByName` |
| `class-out-properties <ont> <class_id> [--limit N]` | `POST .../xx_getClassOutProperties` (by `c_id`) |
| `class-in-properties <ont> <class_id> [--limit N]` | `POST .../xx_getClassInProperties` (by `c_id`) |
| `class-pairs <ont> <p_list>` | `POST .../xx_getCPCInfoNew` — (source, target) class pairs for a property |
| `call <ont> <fn> [--body JSON\|-] [--param k=v ...]` | `POST .../<fn>` (escape hatch) |

The `class-*` commands key on numeric ids: get a class id from `resolve-class` and a property id from `resolve-property`.

Output is indented human-readable JSON by default; pass `--compact` for single-line (pipe-friendly).

```bash
dss ontologies | jq '.[].db_schema_name'
dss classes dbpedia --filter Person --limit 20
dss resolve-property dbpedia dbo:birthPlace
dss class-pairs war_sampo 116
```

## Claude skill

`skill/` is a self-contained Claude Code skill. Install it user-level:

```bash
mkdir -p ~/.claude/skills
cp -R skill ~/.claude/skills/dss
```

See [`docs/USAGE.md`](docs/USAGE.md) for setup, pointing it at a server, and example prompts.

## MCP server

See [`mcp-server/README.md`](mcp-server/README.md). In short:

```bash
cd mcp-server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DSS_BASE_URL=https://dss.semtech.lv python3 dss_mcp.py
```

## Exit codes (CLI)

- `0` — success, JSON on stdout
- `2` — HTTP / transport / argument error, message on stderr
- `130` — interrupted (Ctrl-C)

## License

MIT
