"""CLI entrypoint for the Self-Correcting Computer-Use Agent."""

import argparse
import sys
from pathlib import Path

from sca import __version__


def cmd_doctor(args: argparse.Namespace) -> int:
    """Run environment diagnostics."""
    from sca.envs.doctor import run_doctor

    return run_doctor(check=args.check)


def cmd_run(args: argparse.Namespace) -> int:
    """Run agent on a single task."""
    print(f"Would run task: {args.task_id}")
    print(f"Output dir: {args.output_dir}")
    print(f"Max steps: {args.max_steps}")
    print("(Environment not connected - use with OSWorld)")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    """Run batch evaluation."""
    print(f"Would run batch eval on {len(args.tasks)} tasks")
    print(f"Output dir: {args.output_dir}")
    print("(Environment not connected - use with OSWorld)")
    return 0


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="sca",
        description="Self-Correcting Computer-Use Agent CLI",
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run agent on a task")
    run_parser.add_argument("task_id", help="Task ID to run")
    run_parser.add_argument(
        "-o", "--output-dir", type=Path, default=Path("outputs"), help="Output dir"
    )
    run_parser.add_argument(
        "--max-steps", type=int, default=100, help="Max steps per task"
    )
    run_parser.add_argument("--seed", type=int, default=42, help="Random seed")

    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Evaluate agent on benchmark")
    eval_parser.add_argument("tasks", nargs="+", help="Task IDs to evaluate")
    eval_parser.add_argument(
        "-o", "--output-dir", type=Path, default=Path("outputs"), help="Output dir"
    )
    eval_parser.add_argument(
        "--max-steps", type=int, default=100, help="Max steps per task"
    )
    eval_parser.add_argument("--seed", type=int, default=42, help="Random seed")

    # Replay command (placeholder)
    subparsers.add_parser("replay", help="Replay a trajectory")

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check environment setup")
    doctor_parser.add_argument(
        "--check", choices=["osworld", "docker", "all"], default="all"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "doctor":
        return cmd_doctor(args)

    if args.command == "run":
        return cmd_run(args)

    if args.command == "eval":
        return cmd_eval(args)

    # Commands will be implemented in future tasks
    print(f"Command '{args.command}' not yet implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
