#!/usr/bin/env python3
"""Command-line client for the Data Shape Server (DSS) API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "https://dss.semtech.lv"
DEFAULT_TIMEOUT = 30.0


class DSSError(Exception):
    pass


def _request(
    base_url: str,
    method: str,
    path: str,
    *,
    body: dict | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    url = base_url.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise DSSError(f"HTTP {e.code} {e.reason} on {method} {url}\n{detail}") from e
    except urllib.error.URLError as e:
        raise DSSError(f"Cannot reach {url}: {e.reason}") from e
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.decode("utf-8", errors="replace")


def get(base_url: str, path: str, **kw) -> Any:
    return _request(base_url, "GET", path, **kw)


def post(base_url: str, path: str, body: dict, **kw) -> Any:
    return _request(base_url, "POST", path, body=body, **kw)


def _enc(segment: str) -> str:
    return urllib.parse.quote(segment, safe="")


def _emit(data: Any, compact: bool) -> None:
    if compact:
        print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def _build_main(**kwargs) -> dict:
    main = {k: v for k, v in kwargs.items() if v is not None}
    return {"main": main}


def _parse_kv(items: list[str]) -> dict:
    out: dict[str, Any] = {}
    for it in items:
        if "=" not in it:
            raise DSSError(f"--param expects key=value, got: {it}")
        k, v = it.split("=", 1)
        try:
            out[k] = json.loads(v)
        except json.JSONDecodeError:
            out[k] = v
    return out


# ---------- commands ----------

def cmd_ontologies(args: argparse.Namespace) -> Any:
    variant = args.variant
    if args.tag is not None and variant != "3":
        raise DSSError("--tag is only supported with --variant 3")
    if variant == "default":
        return get(args.base_url, "/api/info", timeout=args.timeout)
    if variant == "tags":
        return get(args.base_url, "/api/infoOntTags", timeout=args.timeout)
    if variant == "3" and args.tag is not None:
        return get(args.base_url, f"/api/info3/{_enc(args.tag)}", timeout=args.timeout)
    if variant in {"2", "3", "4", "5"}:
        return get(args.base_url, f"/api/info{variant}", timeout=args.timeout)
    raise DSSError(f"unknown --variant: {variant}")


def cmd_schema_tags(args: argparse.Namespace) -> Any:
    return get(args.base_url, "/api/schema_tags", timeout=args.timeout)


def cmd_public_ns(args: argparse.Namespace) -> Any:
    return get(args.base_url, "/api/public_ns", timeout=args.timeout)


def cmd_namespaces(args: argparse.Namespace) -> Any:
    return get(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/ns",
        timeout=args.timeout,
    )


def cmd_classes(args: argparse.Namespace) -> Any:
    body = _build_main(limit=args.limit, filter=args.filter)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/getClasses",
        body,
        timeout=args.timeout,
    )


def cmd_properties(args: argparse.Namespace) -> Any:
    body = _build_main(
        propertyKind=args.kind,
        limit=args.limit,
        filter=args.filter,
    )
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/getProperties",
        body,
        timeout=args.timeout,
    )


def cmd_resolve_class(args: argparse.Namespace) -> Any:
    body = _build_main(name=args.name)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/resolveClassByName",
        body,
        timeout=args.timeout,
    )


def cmd_resolve_property(args: argparse.Namespace) -> Any:
    body = _build_main(name=args.name)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/resolvePropertyByName",
        body,
        timeout=args.timeout,
    )


def cmd_class_out_properties(args: argparse.Namespace) -> Any:
    body = _build_main(c_id=args.class_id, limit=args.limit)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/xx_getClassOutProperties",
        body,
        timeout=args.timeout,
    )


def cmd_class_in_properties(args: argparse.Namespace) -> Any:
    body = _build_main(c_id=args.class_id, limit=args.limit)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/xx_getClassInProperties",
        body,
        timeout=args.timeout,
    )


def cmd_class_pairs(args: argparse.Namespace) -> Any:
    body = _build_main(p_list=args.p_list)
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/xx_getCPCInfoNew",
        body,
        timeout=args.timeout,
    )


def cmd_call(args: argparse.Namespace) -> Any:
    if args.body and args.param:
        raise DSSError("--body and --param are mutually exclusive")
    if args.body:
        raw = sys.stdin.read() if args.body == "-" else args.body
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as e:
            raise DSSError(f"--body is not valid JSON: {e}") from e
    elif args.param:
        body = {"main": _parse_kv(args.param)}
    else:
        body = {"main": {}}
    return post(
        args.base_url,
        f"/api/ontologies/{_enc(args.ontology)}/{_enc(args.fn)}",
        body,
        timeout=args.timeout,
    )


# ---------- arg parsing ----------

def _add_common(parser: argparse.ArgumentParser, *, is_root: bool = False) -> None:
    # On subparsers, suppress defaults so a value set on the root parser
    # isn't overwritten by the subparser's default when the user only
    # supplied the flag at the root.
    if is_root:
        url_default = os.environ.get("DSS_BASE_URL", DEFAULT_BASE_URL)
        timeout_default: float = float(os.environ.get("DSS_TIMEOUT", DEFAULT_TIMEOUT))
        compact_default: Any = False
    else:
        url_default = argparse.SUPPRESS
        timeout_default = argparse.SUPPRESS
        compact_default = argparse.SUPPRESS

    parser.add_argument(
        "--base-url",
        default=url_default,
        help="DSS base URL (env: DSS_BASE_URL, default: %s)"
        % os.environ.get("DSS_BASE_URL", DEFAULT_BASE_URL),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=timeout_default,
        help="Request timeout in seconds (default: %s)"
        % os.environ.get("DSS_TIMEOUT", DEFAULT_TIMEOUT),
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        default=compact_default,
        help="Single-line JSON output (default: indented)",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dss",
        description="Talk to a Data Shape Server (DSS) HTTP API. "
        "Outputs JSON to stdout.",
    )
    _add_common(p, is_root=True)

    sub = p.add_subparsers(dest="command", required=True, metavar="COMMAND")

    def add(name: str, **kw) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, **kw)
        _add_common(sp)
        return sp

    s = add("ontologies", help="List known ontologies / schemata")
    s.add_argument(
        "--variant",
        choices=["default", "2", "3", "4", "5", "tags"],
        default="default",
        help="Server-side variant of /api/info (default: default = /api/info)",
    )
    s.add_argument(
        "--tag",
        help="Filter by schema tag (only with --variant 3: /api/info3/<tag>)",
    )
    s.set_defaults(func=cmd_ontologies)

    s = add("schema-tags", help="List known schema tags")
    s.set_defaults(func=cmd_schema_tags)

    s = add("public-ns", help="List public namespaces")
    s.set_defaults(func=cmd_public_ns)

    s = add("namespaces", help="List namespaces for an ontology")
    s.add_argument("ontology")
    s.set_defaults(func=cmd_namespaces)

    s = add("classes", help="List classes in an ontology")
    s.add_argument("ontology")
    s.add_argument("--limit", type=int, default=100)
    s.add_argument(
        "--filter",
        help="POSIX regex matched against the name (plain substrings work)",
    )
    s.set_defaults(func=cmd_classes)

    s = add("properties", help="List properties in an ontology")
    s.add_argument("ontology")
    s.add_argument("--limit", type=int, default=100)
    s.add_argument(
        "--filter",
        help="POSIX regex matched against the name (plain substrings work)",
    )
    s.add_argument(
        "--kind",
        default="All",
        help="propertyKind: All | Data | Object | ObjectExt | Connect (default: All)",
    )
    s.set_defaults(func=cmd_properties)

    s = add("resolve-class", help="Look up a class by name (prefix:local)")
    s.add_argument("ontology")
    s.add_argument("name")
    s.set_defaults(func=cmd_resolve_class)

    s = add("resolve-property", help="Look up a property by name")
    s.add_argument("ontology")
    s.add_argument("name")
    s.set_defaults(func=cmd_resolve_property)

    s = add(
        "class-out-properties",
        help="List properties used outgoing from a class (by class id)",
    )
    s.add_argument("ontology")
    s.add_argument("class_id", type=int, help="Class id (c_id)")
    s.add_argument("--limit", type=int, default=200)
    s.set_defaults(func=cmd_class_out_properties)

    s = add(
        "class-in-properties",
        help="List properties pointing into a class (by class id)",
    )
    s.add_argument("ontology")
    s.add_argument("class_id", type=int, help="Class id (c_id)")
    s.add_argument("--limit", type=int, default=200)
    s.set_defaults(func=cmd_class_in_properties)

    s = add(
        "class-pairs",
        help="List (source class, target class) pairs for a property",
    )
    s.add_argument("ontology")
    s.add_argument(
        "p_list",
        help="Property id, sent as the p_list param (e.g. 116)",
    )
    s.set_defaults(func=cmd_class_pairs)

    s = add(
        "call",
        help="Generic POST /api/ontologies/<ont>/<fn> escape hatch",
    )
    s.add_argument("ontology")
    s.add_argument("fn", help="Function name (e.g. getClasses, xx_getClassInfo)")
    s.add_argument(
        "--body",
        help="Full JSON body. Use '-' to read from stdin.",
    )
    s.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Build {main: {...}} from KEY=VALUE pairs (value parsed as JSON if possible). Repeatable.",
    )
    s.set_defaults(func=cmd_call)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except DSSError as e:
        print(f"dss: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    try:
        _emit(result, args.compact)
    except BrokenPipeError:
        # Downstream consumer (e.g. `head`) closed the pipe; not an error.
        # Detach stdout so interpreter shutdown doesn't try to flush it.
        sys.stdout = None
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
