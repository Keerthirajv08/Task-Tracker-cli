#!/usr/bin/env python3
"""
Task Tracker CLI - Improved

Features added (high level):
- Encapsulated TaskManager class with clear API
- Dataclass-based Task with type hints and JSON (de)serialization
- Finite State Machine (FSM) enforcing allowed status transitions
- Defensive programming: input validation, careful error handling
- Atomic writes and simple file locking to reduce corruption risk
- CLI built with argparse and subcommands
- Logging (console + file) and a --dry-run and --verbose flags
- Minimal migration/versioning support for the JSON store
- A lightweight self-test command for quick verification

Design goals: robust, explicit, testable, and easy to extend.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
#import shutil
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Configuration
TASKS_FILE = os.getenv("TASKS_FILE", "tasks.json")
LOCK_FILE = TASKS_FILE + ".lock"
STORE_VERSION = 1
LOG_FILE = os.getenv("TASK_TRACKER_LOG", "task_tracker.log")
LOCK_WAIT_SECONDS = 5
LOCK_SLEEP_INTERVAL = 0.08

# Setup basic logging
logger = logging.getLogger("task_tracker")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
# file handler
fh = logging.FileHandler(LOG_FILE)
fh.setFormatter(formatter)
logger.addHandler(fh)


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Finite state machine for allowed transitions.
ALLOWED_TRANSITIONS = {
    Status.TODO: {Status.IN_PROGRESS, Status.DONE},
    Status.IN_PROGRESS: {Status.DONE, Status.TODO},  # allow revert to TODO
    Status.DONE: {Status.TODO},  # reopen
}

@dataclass
class Task:
    id: int
    description: str
    status: Status = Status.TODO
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Task":
        # Defensive parsing with defaults
        try:
            status = Status(data.get("status", Status.TODO.value))
        except ValueError:
            status = Status.TODO

        created_at = data.get("created_at") or datetime.now(timezone.utc).isoformat()
        updated_at = data.get("updated_at") or created_at

        return Task(
            id=int(data["id"]),
            description=str(data.get("description", "")).strip(),
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )

class StoreError(RuntimeError):
    pass

class TaskManager:
    def __init__(self, path: str = TASKS_FILE):
        self.path = path
        self.lock_path = path + ".lock"
        self._ensure_store_exists()

    # ------------------ File / Locking utilities ------------------
    def _acquire_lock(self, timeout: float = LOCK_WAIT_SECONDS) -> None:
        start = time.time()
        while True:
            try:
                # Use O_CREAT | O_EXCL to ensure we create-only (atomic on POSIX)
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                # write pid for debugging
                with open(self.lock_path, "w") as f:
                    f.write(str(os.getpid()))
                return
            except FileExistsError:
                if time.time() - start > timeout:
                    raise StoreError("Timeout acquiring store lock")
                time.sleep(LOCK_SLEEP_INTERVAL)

    def _release_lock(self) -> None:
        try:
            if os.path.exists(self.lock_path):
                os.remove(self.lock_path)
        except OSError as e:
            logger.warning("Failed to remove lock file: %s", e)

    def _atomic_write(self, data: str) -> None:
        # write to a temp file on same filesystem then replace
        dirpath = os.path.dirname(os.path.abspath(self.path)) or "."
        fd, tmp = tempfile.mkstemp(prefix=".tasks_", dir=dirpath)
        try:
            with os.fdopen(fd, "w") as tmpf:
                tmpf.write(data)
                tmpf.flush()
                os.fsync(tmpf.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    def _ensure_store_exists(self) -> None:
        if not os.path.exists(self.path):
            logger.debug("Store not found, creating new store: %s", self.path)
            initial = {"version": STORE_VERSION, "tasks": []}
            self._atomic_write(json.dumps(initial, indent=2))

    # ------------------ Load / Save ------------------
    def load(self) -> List[Task]:
        try:
            with open(self.path, "r") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("Error loading store: %s -- resetting to empty store", e)
            return []

        # handle versioning
        version = payload.get("version", 0)
        tasks_data = payload.get("tasks", [])

        # TODO: implement migrations if needed
        if version != STORE_VERSION:
            logger.info("Store version mismatch (found=%s, expected=%s). Running migration stub.", version, STORE_VERSION)
            # naive migration: ignore version and parse tasks

        tasks: List[Task] = []
        for t in tasks_data:
            try:
                tasks.append(Task.from_dict(t))
            except Exception as e:
                logger.warning("Skipping invalid task in store: %s -- %s", t, e)
        return tasks

    def save(self, tasks: List[Task]) -> None:
        payload = {"version": STORE_VERSION, "tasks": [t.to_dict() for t in tasks]}
        data = json.dumps(payload, indent=2)
        # Acquire lock for write
        try:
            self._acquire_lock()
            self._atomic_write(data)
        finally:
            self._release_lock()

    # ------------------ Business operations ------------------
    def _next_id(self, tasks: List[Task]) -> int:
        return max((t.id for t in tasks), default=0) + 1

    def list_tasks(self, status: Optional[Status] = None) -> List[Task]:
        tasks = self.load()
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: (t.status.value, t.id))

    def add_task(self, description: str) -> Task:
        description = (description or "").strip()
        if not description:
            raise ValueError("Task description cannot be empty")
        if len(description) > 1000:
            raise ValueError("Task description too long")

        tasks = self.load()
        new_id = self._next_id(tasks)
        task = Task(id=new_id, description=description)
        tasks.append(task)
        self.save(tasks)
        logger.info("Added task %s", new_id)
        return task

    def update_task(self, task_id: int, new_description: str) -> Task:
        new_description = (new_description or "").strip()
        if not new_description:
            raise ValueError("New description cannot be empty")

        tasks = self.load()
        found = False
        for t in tasks:
            if t.id == task_id:
                t.description = new_description
                t.updated_at = datetime.now(timezone.utc).isoformat()
                found = True
                break
        if not found:
            raise KeyError(f"Task with ID {task_id} not found")
        self.save(tasks)
        logger.info("Updated task %s", task_id)
        return t

    def delete_task(self, task_id: int) -> None:
        tasks = self.load()
        original_len = len(tasks)
        tasks = [t for t in tasks if t.id != task_id]
        if len(tasks) == original_len:
            raise KeyError(f"Task with ID {task_id} not found")
        self.save(tasks)
        logger.info("Deleted task %s", task_id)

    def change_status(self, task_id: int, new_status: Status) -> Task:
        tasks = self.load()
        for t in tasks:
            if t.id == task_id:
                if t.status == new_status:
                    logger.info("Task %s already %s", task_id, new_status.value)
                    return t
                allowed = ALLOWED_TRANSITIONS.get(t.status, set())
                if new_status not in allowed:
                    raise ValueError(f"Invalid state transition: {t.status.value} -> {new_status.value}")
                t.status = new_status
                t.updated_at = datetime.now(timezone.utc).isoformat()
                self.save(tasks)
                logger.info("Task %s status changed to %s", task_id, new_status.value)
                return t
        raise KeyError(f"Task with ID {task_id} not found")


# ------------------ CLI / Presentation helpers ------------------

def human_dt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


def print_tasks(tasks: List[Task]) -> None:
    if not tasks:
        print("No tasks found")
        return

    print(f"\n{'ID':<6}{'Status':<15}{'Created':<20}{'Updated':<20} Description")
    print("-" * 90)
    for t in tasks:
        print(f"{t.id:<6}{t.status.value:<15}{human_dt(t.created_at):<20}{human_dt(t.updated_at):<20} {t.description}")
    print(f"\nTotal: {len(tasks)} task(s)\n")


def run_self_test(manager: TaskManager) -> None:
    print("Running a minimal self-test (no destructive actions are performed)...")
    ok = True
    try:
        # load and save roundtrip
        tasks = manager.load()
        manager.save(tasks)
        print("Store load/save OK")

        # create ephemeral task and delete it
        t = manager.add_task("__self_test_task__")
        if not isinstance(t.id, int):
            raise AssertionError("Invalid id type")
        manager.delete_task(t.id)
        print("Add/delete cycle OK")

        # transitions
        t2 = manager.add_task("__self_test_transitions__")
        manager.change_status(t2.id, Status.IN_PROGRESS)
        manager.change_status(t2.id, Status.DONE)
        manager.change_status(t2.id, Status.TODO)  # reopen
        manager.delete_task(t2.id)
        print("FSM transitions OK")
    except Exception as e:
        ok = False
        print("Self-test failed:", e)
    finally:
        if ok:
            print("SELF-TEST: PASSED")
        else:
            print("SELF-TEST: FAILED")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Task Tracker CLI - Improved")
    p.add_argument("--store", default=TASKS_FILE, help="Path to tasks JSON store")
    p.add_argument("--dry-run", action="store_true", help="Do not persist changes")
    p.add_argument("--verbose", action="store_true", help="Enable debug logging")

    sub = p.add_subparsers(dest="command")

    sub.add_parser("list", help="List all tasks")
    sub.add_parser("list-done", help="List done tasks")
    sub.add_parser("list-todo", help="List todo tasks")
    sub.add_parser("list-progress", help="List in-progress tasks")

    a = sub.add_parser("add", help="Add a new task")
    a.add_argument("description", nargs="+", help="Task description")

    u = sub.add_parser("update", help="Update a task's description")
    u.add_argument("id", type=int, help="Task ID")
    u.add_argument("description", nargs="+", help="New description")

    d = sub.add_parser("delete", help="Delete a task")
    d.add_argument("id", type=int, help="Task ID")

    s = sub.add_parser("start", help="Mark task in progress")
    s.add_argument("id", type=int, help="Task ID")

    done = sub.add_parser("done", help="Mark task done")
    done.add_argument("id", type=int, help="Task ID")

    todo = sub.add_parser("todo", help="Mark task todo")
    todo.add_argument("id", type=int, help="Task ID")

    sub.add_parser("self-test", help="Run a minimal self test of the store and FSM")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    manager = TaskManager(path=args.store)

    try:
        if args.command in (None, "list"):
            tasks = manager.list_tasks()
            print_tasks(tasks)
            return 0

        if args.command == "list-done":
            print_tasks(manager.list_tasks(Status.DONE))
            return 0
        if args.command == "list-todo":
            print_tasks(manager.list_tasks(Status.TODO))
            return 0
        if args.command == "list-progress":
            print_tasks(manager.list_tasks(Status.IN_PROGRESS))
            return 0

        if args.command == "add":
            desc = " ".join(args.description)
            if args.dry_run:
                print(f"[dry-run] would add: {desc}")
            else:
                t = manager.add_task(desc)
                print(f"Added task (ID: {t.id})")
            return 0

        if args.command == "update":
            desc = " ".join(args.description)
            if args.dry_run:
                print(f"[dry-run] would update {args.id} -> {desc}")
            else:
                manager.update_task(args.id, desc)
                print(f"Updated task {args.id}")
            return 0

        if args.command == "delete":
            if args.dry_run:
                print(f"[dry-run] would delete {args.id}")
            else:
                manager.delete_task(args.id)
                print(f"Deleted task {args.id}")
            return 0

        if args.command == "start":
            if args.dry_run:
                print(f"[dry-run] would mark {args.id} in progress")
            else:
                manager.change_status(args.id, Status.IN_PROGRESS)
                print(f"Task {args.id} marked in progress")
            return 0

        if args.command == "done":
            if args.dry_run:
                print(f"[dry-run] would mark {args.id} done")
            else:
                manager.change_status(args.id, Status.DONE)
                print(f"Task {args.id} marked done")
            return 0

        if args.command == "todo":
            if args.dry_run:
                print(f"[dry-run] would mark {args.id} todo")
            else:
                manager.change_status(args.id, Status.TODO)
                print(f"Task {args.id} marked todo")
            return 0

        if args.command == "self-test":
            run_self_test(manager)
            return 0

        parser.print_help()
        return 1

    except StoreError as se:
        logger.error("Store error: %s", se)
        return 2
    except KeyError as ke:
        logger.error("%s", ke)
        return 3
    except ValueError as ve:
        logger.error("%s", ve)
        return 4
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return 99


if __name__ == "__main__":
    raise SystemExit(main())
