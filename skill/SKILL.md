---
name: dss
description: Explore a Data Shape Server (DSS) knowledge-graph schema — list ontologies, browse classes and properties, resolve names, inspect namespaces. Use when the user wants to understand what's in a DSS-hosted RDF schema or build SPARQL queries against one.
allowed-tools: Bash(python3 *)
---

# DSS — Data Shape Server explorer

This skill talks to a running Data Shape Server over HTTP. DSS stores RDF-endpoint schema metadata (classes, properties, namespaces, relations) per *ontology* (a PostgreSQL schema name like `dbpedia`, `wikidata`, `nobel_prizes`).

## Setup

Point the CLI at a DSS server:

```bash
export DSS_BASE_URL=https://dss.semtech.lv   # or wherever DSS is running
```

The CLI is a single-file Python script using only the standard library — no `pip install` needed. Python ≥ 3.9.

## When to use this skill

- The user asks what schemas / ontologies / endpoints are loaded in DSS.
- The user wants to look up classes or properties in a schema, with or without a name filter.
- The user wants to resolve a prefixed name (e.g. `dbo:Person`) to its full IRI / metadata.
- The user wants to know which properties a class uses, or which classes a property connects.
- The user is drafting a SPARQL query and needs to know what prefixes, classes, or properties are available.

## How to use

Always invoke the bundled CLI by its absolute path so it resolves no matter the working directory:

```bash
python3 ${CLAUDE_SKILL_DIR}/dss.py <command>
```

`${CLAUDE_SKILL_DIR}` expands to this skill's folder. Output is JSON on stdout.

### Discovery

```bash
python3 ${CLAUDE_SKILL_DIR}/dss.py ontologies           # list all loaded schemata
python3 ${CLAUDE_SKILL_DIR}/dss.py schema-tags          # tags used to group schemata
python3 ${CLAUDE_SKILL_DIR}/dss.py ontologies --variant 3 --tag che   # only schemata with a given tag
python3 ${CLAUDE_SKILL_DIR}/dss.py public-ns            # globally-known namespace prefixes
```

### Browse one ontology

```bash
python3 ${CLAUDE_SKILL_DIR}/dss.py namespaces dbpedia
python3 ${CLAUDE_SKILL_DIR}/dss.py classes dbpedia --limit 50
python3 ${CLAUDE_SKILL_DIR}/dss.py classes dbpedia --filter Person --limit 20
python3 ${CLAUDE_SKILL_DIR}/dss.py properties dbpedia --filter birth --kind Object
```

`--kind` accepts `All`, `Data`, `Object`, `ObjectExt`, or `Connect`. `--filter` is a POSIX regex (plain substrings work).

### Resolve a name

```bash
python3 ${CLAUDE_SKILL_DIR}/dss.py resolve-class dbpedia dbo:Person
python3 ${CLAUDE_SKILL_DIR}/dss.py resolve-property dbpedia dbo:birthPlace
```

### Relations between classes and properties

```bash
# properties used outgoing from / incoming to a class (by class id, the `c_id` from resolve-class)
python3 ${CLAUDE_SKILL_DIR}/dss.py class-out-properties war_sampo 61 --limit 200
python3 ${CLAUDE_SKILL_DIR}/dss.py class-in-properties  war_sampo 61 --limit 200

# (source class, target class) pairs a property connects (by property id, the `p_id` from resolve-property)
python3 ${CLAUDE_SKILL_DIR}/dss.py class-pairs war_sampo 116
```

These key on numeric **ids**, not names: get a class id from `resolve-class` and a property id from `resolve-property` first. In `class-pairs` output, rows come in pairs sharing a `cp_rel_id`; `type_id:2` is the source (subject) class and `type_id:1` the target (object) class, and `cnt` is the usage count.

### Escape hatch — any DSS function

For functions not wrapped above (e.g. the `xx_*` family used by ViziQuer):

```bash
# pass arbitrary params as key=value (values JSON-parsed when possible)
python3 ${CLAUDE_SKILL_DIR}/dss.py call dbpedia xx_getClassList --param limit=10 --param filter=Person

# or feed a full body
python3 ${CLAUDE_SKILL_DIR}/dss.py call dbpedia getTreeClasses --body '{"main":{"limit":100,"treeMode":"Top"}}'
echo '{"main":{"limit":100,"treeMode":"Top"}}' | python3 ${CLAUDE_SKILL_DIR}/dss.py call dbpedia getTreeClasses --body -
```

The full handler list lives in `server/routes/api/index.js` of the DSS repo.

## Common flags

- `--base-url URL` — override `DSS_BASE_URL` for one call.
- `--timeout SECONDS` — default 30.
- `--compact` — single-line JSON, easier to pipe through `jq`.

## Tips for the agent

- If `ontologies` returns an empty list, the DSS database has no schemata imported — say so rather than guessing names.
- Ontology names are case-sensitive and must match `db_schema_name` from `ontologies` output. The server returns 404 for unknown names.
- Large result sets are paged by `--limit`; start with a small limit and narrow with `--filter` before pulling more.
- Errors print to stderr with exit code 2; success returns the API JSON on stdout, exit 0.
