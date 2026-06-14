#!/usr/bin/env python3
"""MCP server exposing the Data Shape Server (DSS) API as tools.

Wraps the same HTTP endpoints as the bundled ``dss.py`` and serves them over
the Model Context Protocol so MCP-aware clients (Claude Desktop, Claude Code,
etc.) can explore a DSS schema directly.

Run (stdio transport):

    DSS_BASE_URL=https://dss.semtech.lv python3 dss_mcp.py

Requires the ``mcp`` package (see requirements.txt); ``dss.py`` itself stays
standard-library only.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

# Reuse dss.py's request helpers (bundled alongside this file) so the CLI and
# the MCP server can never drift apart.
import dss


def _base_url(override: str | None) -> str:
    return override or os.environ.get("DSS_BASE_URL", dss.DEFAULT_BASE_URL)


def _timeout() -> float:
    return float(os.environ.get("DSS_TIMEOUT", dss.DEFAULT_TIMEOUT))


mcp = FastMCP(
    "dss",
    instructions=(
        "Explore a Data Shape Server (DSS) knowledge-graph schema: list "
        "ontologies (PostgreSQL schema names like 'dbpedia', 'wikidata'), "
        "browse classes and properties, resolve prefixed names, and inspect "
        "namespaces. Start with list_ontologies to learn valid ontology "
        "names; they are case-sensitive and must match a db_schema_name. "
        "Narrow large results with a filter (POSIX regex; plain substrings "
        "work) and a small limit before pulling more."
    ),
)


@mcp.tool()
def list_ontologies(
    variant: str = "default",
    tag: str | None = None,
    base_url: str | None = None,
) -> Any:
    """List the ontologies / schemata loaded in DSS.

    variant: one of "default", "2", "3", "4", "5", "tags" — selects the
        server-side /api/info variant (each returns differently-shaped
        metadata). tag: filter by a schema tag; only valid with variant "3".
    """
    if tag is not None and variant != "3":
        raise ValueError('tag is only supported with variant "3"')
    url = _base_url(base_url)
    if variant == "default":
        return dss.get(url, "/api/info", timeout=_timeout())
    if variant == "tags":
        return dss.get(url, "/api/infoOntTags", timeout=_timeout())
    if variant == "3" and tag is not None:
        return dss.get(url, f"/api/info3/{dss._enc(tag)}", timeout=_timeout())
    if variant in {"2", "3", "4", "5"}:
        return dss.get(url, f"/api/info{variant}", timeout=_timeout())
    raise ValueError(f"unknown variant: {variant}")


@mcp.tool()
def schema_tags(base_url: str | None = None) -> Any:
    """List the schema tags used to group ontologies."""
    return dss.get(_base_url(base_url), "/api/schema_tags", timeout=_timeout())


@mcp.tool()
def public_ns(base_url: str | None = None) -> Any:
    """List globally-known namespace prefixes (across all ontologies)."""
    return dss.get(_base_url(base_url), "/api/public_ns", timeout=_timeout())


@mcp.tool()
def namespaces(ontology: str, base_url: str | None = None) -> Any:
    """List the namespace prefixes declared in one ontology."""
    return dss.get(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/ns",
        timeout=_timeout(),
    )


@mcp.tool()
def list_classes(
    ontology: str,
    limit: int = 100,
    filter: str | None = None,
    base_url: str | None = None,
) -> Any:
    """List classes in an ontology.

    filter: POSIX regex matched against the class name (plain substrings
        work). Start with a small limit and narrow with filter.
    """
    body = dss._build_main(limit=limit, filter=filter)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/getClasses",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def list_properties(
    ontology: str,
    kind: str = "All",
    limit: int = 100,
    filter: str | None = None,
    base_url: str | None = None,
) -> Any:
    """List properties in an ontology.

    kind (propertyKind): All | Data | Object | ObjectExt | Connect.
    filter: POSIX regex matched against the property name.
    """
    body = dss._build_main(propertyKind=kind, limit=limit, filter=filter)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/getProperties",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def resolve_class(ontology: str, name: str, base_url: str | None = None) -> Any:
    """Resolve a class by prefixed name (e.g. dbo:Person) to its metadata."""
    body = dss._build_main(name=name)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/resolveClassByName",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def resolve_property(ontology: str, name: str, base_url: str | None = None) -> Any:
    """Resolve a property by prefixed name (e.g. dbo:birthPlace)."""
    body = dss._build_main(name=name)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/resolvePropertyByName",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def class_out_properties(
    ontology: str,
    class_id: int,
    limit: int = 200,
    base_url: str | None = None,
) -> Any:
    """List the properties used outgoing from a class.

    class_id is the numeric class id (c_id) — get it from resolve_class.
    """
    body = dss._build_main(c_id=class_id, limit=limit)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/xx_getClassOutProperties",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def class_in_properties(
    ontology: str,
    class_id: int,
    limit: int = 200,
    base_url: str | None = None,
) -> Any:
    """List the properties pointing into a class.

    class_id is the numeric class id (c_id) — get it from resolve_class.
    """
    body = dss._build_main(c_id=class_id, limit=limit)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/xx_getClassInProperties",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def class_pairs(
    ontology: str,
    p_list: str,
    base_url: str | None = None,
) -> Any:
    """List the (source class, target class) pairs a property connects.

    p_list is a numeric property id (e.g. "116") — get it from
    resolve_property. Rows come in pairs sharing a cp_rel_id; type_id 2 is
    the source (subject) class and type_id 1 the target (object) class, with
    cnt the usage count.
    """
    body = dss._build_main(p_list=p_list)
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/xx_getCPCInfoNew",
        body,
        timeout=_timeout(),
    )


@mcp.tool()
def call(
    ontology: str,
    fn: str,
    params: dict | None = None,
    base_url: str | None = None,
) -> Any:
    """Escape hatch: POST /api/ontologies/<ontology>/<fn>.

    Use for DSS functions not wrapped above (e.g. the xx_* family used by
    ViziQuer, or getTreeClasses). params is wrapped as {"main": params};
    pass {} or omit for an empty body. The full handler list lives in
    server/routes/api/index.js of the DSS repo.
    """
    body = {"main": params or {}}
    return dss.post(
        _base_url(base_url),
        f"/api/ontologies/{dss._enc(ontology)}/{dss._enc(fn)}",
        body,
        timeout=_timeout(),
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
