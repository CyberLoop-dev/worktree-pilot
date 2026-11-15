import argparse
import json
import subprocess
import sys


def run_git(arguments):
    result = subprocess.run(["git", *arguments], text=True, capture_output=True)
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise RuntimeError(message)
    return result.stdout


def parse_worktrees(output):
    entries = []
    current = {}
    for line in output.splitlines() + [""]:
        if not line:
            if current:
                entries.append(current)
                current = {}
        elif line.startswith("worktree "):
            current["path"] = line[len("worktree "):]
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):]
        elif line.startswith("branch refs/heads/"):
            current["branch"] = line[len("branch refs/heads/"):]
        elif line == "detached":
            current["branch"] = "(detached)"
        elif line == "bare":
            current["bare"] = True
        elif line == "locked":
            current["locked"] = True
        elif line.startswith("prunable"):
            current["prunable"] = True
    return entries


def list_worktrees():
    return parse_worktrees(run_git(["worktree", "list", "--porcelain"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage Git worktrees with safe defaults.")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List linked worktrees")
    listing.add_argument("--json", action="store_true")
    add = commands.add_parser("add", help="Create a worktree")
    add.add_argument("branch")
    add.add_argument("path")
    add.add_argument("--create", action="store_true", help="Create the branch before adding the worktree")
    remove = commands.add_parser("remove", help="Remove a worktree but keep its branch")
    remove.add_argument("path")
    prune = commands.add_parser("prune", help="Preview stale metadata; use --apply to prune")
    prune.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            entries = list_worktrees()
            if args.json:
                print(json.dumps(entries, indent=2))
            else:
                for entry in entries:
                    print(f"{entry.get('branch', '(unknown)'):24} {entry.get('path', '')}")
                print(f"{len(entries)} worktree(s)")
        elif args.command == "add":
            command = ["worktree", "add"]
            if args.create:
                command += ["-b", args.branch]
            else:
                command += [args.path, args.branch]
            if args.create:
                command.append(args.path)
            print(run_git(command).strip() or "Worktree created.")
        elif args.command == "remove":
            print(run_git(["worktree", "remove", args.path]).strip() or f"Removed {args.path}; branch was kept.")
        else:
            command = ["worktree", "prune", "--verbose"]
            if not args.apply:
                command.append("--dry-run")
                print("Preview only. Pass --apply to perform pruning.")
            print(run_git(command).strip() or "No stale worktree metadata found.")
        return 0
    except (OSError, RuntimeError) as error:
        print(f"worktree-pilot: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
