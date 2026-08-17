from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from .detect import detect, load_manifest
from .models import cache_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("detect", "manifest"))
    parser.add_argument("--manifest", default="config/local-toolchains.yaml")
    parser.add_argument("--tool")
    parser.add_argument("--repository", default=".")
    args = parser.parse_args()
    raw, tools = load_manifest(Path(args.manifest))
    selected = [t for t in tools if not args.tool or t.id == args.tool]
    if args.tool and not selected:
        parser.error(f"unknown tool: {args.tool}")
    if args.command == "manifest":
        print(json.dumps([asdict(t) for t in selected], indent=2))
        return 0
    root = cache_root(os.getenv(raw["cacheRootVariable"]))
    observations = [detect(t, root, Path(args.repository).resolve()) for t in selected]
    print(json.dumps([asdict(o) for o in observations], indent=2))
    return 1 if any(o.status == "FAIL" for o in observations) else 0


if __name__ == "__main__":
    raise SystemExit(main())
