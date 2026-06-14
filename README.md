[![PyPI](https://img.shields.io/pypi/v/dss-ai-tools.svg)](https://pypi.org/project/dss-ai-tools/)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/LICENSE)
# dss-ai-tools

Tools for exploring a [Data Shape Server (DSS)](https://github.com/LUMII-Syslab/data-shape-server) knowledge graph schemas — classes, properties, their relations, and namespaces — over the DSS HTTP API. There are three ways to use it, all sharing one small client:

| Component | What it is | Where |
| --- | --- | --- |
| **CLI** | A single-file Python client (`dss`), standard library only. Requires Python >= 3.10. | [`dss.py`](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/dss.py) |
| **Claude skill** | A self-contained Claude Code skill that drives the CLI. | [`skill/`](https://github.com/LUMII-Syslab/dss-ai-tools/tree/main/skill) |
| **MCP server** | An MCP server exposing the same endpoints as tools. | [`mcp-server/`](https://github.com/LUMII-Syslab/dss-ai-tools/tree/main/mcp-server) |

The CLI implements the core functionality; the skill and MCP server bundle a copy of `dss.py` so each is self-contained. Run [`scripts/sync.sh`](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/scripts/sync.sh) after editing the canonical `dss.py` to refresh the copies.

## Configure

All three approaches use the same environment variables:

```bash
export DSS_BASE_URL=https://dss.semtech.lv   # default
export DSS_TIMEOUT=30                        # optional, seconds
```

The CLI and MCP tools also accept a per-call override (`--base-url` / `base_url`).

## CLI

```bash
python3 dss.py --help
```

Install from PyPI to get the `dss` command on your PATH:

```bash
pipx install dss-ai-tools     # provides the `dss` command
# or run without installing:
uvx --from dss-ai-tools dss --help
```

Or install from a checkout of this repo:

```bash
pipx install .          # provides the `dss` command (see pyproject.toml)
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

See [`docs/USAGE.md`](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/docs/USAGE.md) for setup, pointing it at a server, and example prompts.

## MCP server

See [`mcp-server/README.md`](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/mcp-server/README.md). 

You can register it from the published PyPI package (no checkout needed).

## Exit codes (CLI)

- `0` — success, JSON on stdout
- `2` — HTTP / transport / argument error, message on stderr
- `130` — interrupted (Ctrl-C)

## License

MIT
