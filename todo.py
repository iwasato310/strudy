#!/usr/bin/env python3
"""Simple CLI TODO app with JSON persistence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DATA_FILE = Path("todos.json")


def load_todos() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise SystemExit("Error: todos.json is invalid JSON.")


def save_todos(todos: list[dict[str, Any]]) -> None:
    DATA_FILE.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id(todos: list[dict[str, Any]]) -> int:
    if not todos:
        return 1
    return max(item["id"] for item in todos) + 1


def cmd_add(args: argparse.Namespace) -> None:
    todos = load_todos()
    item = {
        "id": next_id(todos),
        "task": args.task.strip(),
        "done": False,
    }
    if not item["task"]:
        raise SystemExit("Error: task cannot be empty.")
    todos.append(item)
    save_todos(todos)
    print(f"Added TODO #{item['id']}: {item['task']}")


def cmd_list(args: argparse.Namespace) -> None:
    todos = load_todos()
    if args.all:
        filtered = todos
    elif args.done:
        filtered = [item for item in todos if item["done"]]
    else:
        filtered = [item for item in todos if not item["done"]]

    if not filtered:
        print("No TODOs found.")
        return

    for item in filtered:
        mark = "x" if item["done"] else " "
        print(f"[{mark}] #{item['id']} {item['task']}")


def find_todo(todos: list[dict[str, Any]], todo_id: int) -> dict[str, Any]:
    for item in todos:
        if item["id"] == todo_id:
            return item
    raise SystemExit(f"Error: TODO #{todo_id} not found.")


def cmd_done(args: argparse.Namespace) -> None:
    todos = load_todos()
    item = find_todo(todos, args.id)
    item["done"] = True
    save_todos(todos)
    print(f"Marked TODO #{args.id} as done.")


def cmd_undone(args: argparse.Namespace) -> None:
    todos = load_todos()
    item = find_todo(todos, args.id)
    item["done"] = False
    save_todos(todos)
    print(f"Marked TODO #{args.id} as not done.")


def cmd_delete(args: argparse.Namespace) -> None:
    todos = load_todos()
    _ = find_todo(todos, args.id)
    todos = [item for item in todos if item["id"] != args.id]
    save_todos(todos)
    print(f"Deleted TODO #{args.id}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO CLI app")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a TODO")
    p_add.add_argument("task", help="task text")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list TODOs")
    p_list.add_argument("--all", action="store_true", help="show all TODOs")
    p_list.add_argument("--done", action="store_true", help="show only done TODOs")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="mark TODO as done")
    p_done.add_argument("id", type=int, help="TODO id")
    p_done.set_defaults(func=cmd_done)

    p_undone = sub.add_parser("undone", help="mark TODO as not done")
    p_undone.add_argument("id", type=int, help="TODO id")
    p_undone.set_defaults(func=cmd_undone)

    p_delete = sub.add_parser("delete", help="delete a TODO")
    p_delete.add_argument("id", type=int, help="TODO id")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
