# Using the `dss` skill in Claude Code

The `skill/` folder is a self-contained Claude Code skill. Once installed, Claude can use it to explore a Data Shape Server schema on your behalf. Run the commands below from the repository root.

## 1. Install the skill

Pick one of these.

**User-level** — available in every project:

```bash
mkdir -p ~/.claude/skills
cp -R skill ~/.claude/skills/dss
```

**Project-level** — only inside this repo:

```bash
mkdir -p .claude/skills
ln -s "$(pwd)/skill" .claude/skills/dss
```

A symlink lets edits to `skill/` take effect immediately, without recopying.

## 2. Point it at a DSS server

The CLI reads `DSS_BASE_URL` from its environment. For the live instance:

**Shell rc (easiest):** add to `~/.zshrc`, then open a new terminal.

```bash
export DSS_BASE_URL=http://viziquer.app:9005
```

**Project-scoped** — in `.claude/settings.json`:

```json
{ "env": { "DSS_BASE_URL": "http://viziquer.app:9005" } }
```

**One-off** — agent can prefix the command:

```bash
DSS_BASE_URL=http://viziquer.app:9005 python3 ~/.claude/skills/dss/dss.py ontologies
```

## 3. Sanity check

```bash
DSS_BASE_URL=http://viziquer.app:9005 \
  python3 ~/.claude/skills/dss/dss.py ontologies | head
```

You should see a JSON array of schemas (DBpedia, Wikidata, Europeana, ...). If you instead see `Cannot reach …`, the URL or network is wrong; if you see `HTTP 404`, the path prefix is wrong (the server expects `/api/...`).

## 4. Drive it from Claude Code

Restart Claude Code so it re-scans skills, then ask things like:

- "What ontologies are loaded in DSS?"
- "List 20 classes in `dbpedia` whose name contains `Person`."
- "Resolve `dbo:birthPlace` in the `dbpedia` schema."
- "What namespaces does `wikidata` use?"
- "Get object properties in `europeana` matching `creator`."

Claude will pick up the skill from `SKILL.md` and run `python3 dss.py …` for you. Output is JSON, which Claude can then read and summarize.

## 5. Calling the CLI directly

You can also use it as a plain command-line tool. See `README.md` for the full command reference. The most useful ones:

```bash
dss ontologies                                  # list schemas
dss namespaces dbpedia                          # prefixes
dss classes dbpedia --filter Person --limit 20
dss properties dbpedia --kind Object --filter birth
dss resolve-class dbpedia dbo:Person
dss resolve-property dbpedia dbo:birthPlace
dss call dbpedia getTreeClasses --param limit=200 --param treeMode=Top   # escape hatch
```

To get a short `dss` command on your PATH:

```bash
ln -s ~/.claude/skills/dss/dss.py ~/.local/bin/dss
chmod +x ~/.claude/skills/dss/dss.py
```

## Troubleshooting

- **`Cannot reach …`** — server unreachable or DNS fails. Check `DSS_BASE_URL` and that the host is online.
- **`HTTP 400 bad ontology name`** — ontology name has characters outside `[a-zA-Z0-9_-]`.
- **`HTTP 404 unknown ontology`** — name doesn't match any `db_schema_name` from `dss ontologies`.
- **Claude doesn't seem to know the skill exists** — make sure the folder is at `~/.claude/skills/dss/` (or `.claude/skills/dss/` in the project), contains `SKILL.md`, and that you restarted Claude Code after installing.
