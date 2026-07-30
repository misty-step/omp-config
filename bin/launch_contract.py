from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from config_contract import ContractError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile, verify, or run an OMP launch bundle")
    commands = parser.add_subparsers(dest="command", required=True)

    compile_command = commands.add_parser("compile", help="compile a launch contract into a bundle")
    compile_command.add_argument("contract", type=Path)
    compile_command.add_argument("--out", required=True, type=Path)
    compile_command.add_argument("--config-root", type=Path, default=Path(__file__).resolve().parents[1])
    compile_command.add_argument("--force", action="store_true")

    verify_command = commands.add_parser("verify", help="verify a compiled launch bundle")
    verify_command.add_argument("bundle", type=Path)

    run_command = commands.add_parser("run", help="run a verified launch bundle")
    run_command.add_argument("bundle", type=Path)
    run_command.add_argument("--prompt", required=True)
    run_command.add_argument("--mode", choices=("text", "json"), default="text")
    run_command.add_argument("--omp", default="omp")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "compile":
            from launch_compile import compile_bundle

            manifest = compile_bundle(args.config_root, args.contract, args.out, force=args.force)
            print(json.dumps(manifest, indent=2, sort_keys=True))
            return 0
        if args.command == "verify":
            from launch_verify import verify_bundle

            print(json.dumps(verify_bundle(args.bundle), indent=2, sort_keys=True))
            return 0
        if args.command == "run":
            from launch_run import run_bundle

            return run_bundle(args.bundle, args.prompt, mode=args.mode, omp=args.omp)
    except ContractError as error:
        _parser().error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
