[![PyPI](https://img.shields.io/pypi/v/dss-ai-tools.svg)](https://pypi.org/project/dss-ai-tools/)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/LUMII-Syslab/dss-ai-tools/blob/main/LICENSE)
# dss-ai-tools

Tools for exploring [Data Shape Server (DSS)](https://github.com/LUMII-Syslab/data-shape-server) knowledge graph schemas — classes, properties, their relations, and namespaces — over the DSS HTTP API. There are three ways to use it, all sharing one small client:

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

DSS refers to data schemas as *ontologies* and uses that term throughout its API; the CLI follows the same naming.

| Command | Description |
| --- | --- |
| `ontologies [--variant ...] [--tag TAG]` | List the ontologies (schemas) loaded in DSS; `--variant` selects an alternate info view, `--tag` filters (with variant `3`). |
| `schema-tags` | List the tags used to group ontologies. |
| `public-ns` | List the globally known namespace prefixes shared across ontologies. |
| `namespaces <ont>` | List the namespace prefixes declared in one ontology. |
| `classes <ont> [--limit N] [--filter STR]` | List classes in an ontology; narrow with a name filter. |
| `properties <ont> [--limit N] [--filter REGEX] [--kind ...]` | List properties in an ontology, optionally by kind; narrow with a name filter. |
| `resolve-class <ont> <name>` | Look up a class by its prefixed name; returns its metadata, including its id. |
| `resolve-property <ont> <name>` | Look up a property by its prefixed name; returns its metadata, including its id. |
| `class-out-properties <ont> <class_id> [--limit N]` | List the properties that originate from a class (outgoing). |
| `class-in-properties <ont> <class_id> [--limit N]` | List the properties that point to a class (incoming). |
| `class-pairs <ont> <p_list>` | List the (source, target) class pairs that a property connects. |
| `call <ont> <fn> [--body JSON\|-] [--param k=v ...]` | Generic API call: invoke any DSS function not covered by the commands above. |

The `class-*` commands use numeric ids: get a class id from `resolve-class` and a property id from `resolve-property`.

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
