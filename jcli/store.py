from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .models import JobDefinition, JobRecord, JobState, StepRecord, row_to_job, row_to_step, utc_now


CLASS_RANK = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "H": 9}


class JobStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    job_class TEXT NOT NULL,
                    class_rank INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    source_path TEXT,
                    raw_script TEXT,
                    submitted_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    current_step TEXT,
                    held_reason TEXT,
                    exit_code INTEGER,
                    dependencies TEXT,
                    retry_limit INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    program TEXT NOT NULL,
                    arguments TEXT NOT NULL,
                    state TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    return_code INTEGER,
                    stdout_path TEXT,
                    stderr_path TEXT,
                    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS daemon_state (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    stop_requested INTEGER NOT NULL DEFAULT 0,
                    pid INTEGER,
                    updated_at TEXT NOT NULL
                );
                INSERT OR IGNORE INTO daemon_state(singleton, stop_requested, pid, updated_at)
                VALUES (1, 0, NULL, '1970-01-01T00:00:00+00:00');
                CREATE TABLE IF NOT EXISTS job_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    created_at TEXT NOT NULL,
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT
                );
                """
            )

    def submit_job(self, job: JobDefinition, held: bool = False) -> int:
        state = JobState.HELD if held else JobState.SUBMITTED
        now = utc_now().isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO jobs (
                    name, job_class, class_rank, priority, user_name, state, source_path, raw_script,
                    submitted_at, updated_at, held_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.name,
                    job.job_class,
                    CLASS_RANK.get(job.job_class, 5),
                    job.priority,
                    job.user,
                    state.value,
                    job.source_path,
                    job.raw_script,
                    now,
                    now,
                    "Submitted in hold class H." if held else None,
                ),
            )
            job_id = int(cursor.lastrowid)
            for ordinal, step in enumerate(job.steps, start=1):
                conn.execute(
                    """
                    INSERT INTO steps (job_id, name, ordinal, program, arguments, state)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (job_id, step.name, ordinal, step.program, step.arguments, JobState.QUEUED.value if not held else JobState.HELD.value),
                )
            if not held:
                conn.execute(
                    "UPDATE jobs SET state = ?, updated_at = ? WHERE id = ?",
                    (JobState.QUEUED.value, now, job_id),
                )
            conn.execute(
                "INSERT INTO job_events (job_id, created_at, level, event_type, message, payload) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, now, "INFO", "job.submitted", f"Job {job.name} submitted.", json.dumps({})),
            )
            return job_id

    def add_event(self, job_id: int | None, level: str, event_type: str, message: str, payload: dict | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO job_events (job_id, created_at, level, event_type, message, payload) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, utc_now().isoformat(), level, event_type, message, json.dumps(payload or {})),
            )

    def transition_job(self, job_id: int, state: JobState, *, current_step: str | None = None, exit_code: int | None = None, held_reason: str | None = None) -> None:
        now = utc_now().isoformat()
        with self.connect() as conn:
            started_at = now if state == JobState.RUNNING else None
            finished_at = now if state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED} else None
            existing = conn.execute("SELECT started_at FROM jobs WHERE id = ?", (job_id,)).fetchone()
            conn.execute(
                """
                UPDATE jobs
                SET state = ?, updated_at = ?, current_step = ?, exit_code = ?,
                    held_reason = ?,
                    started_at = COALESCE(started_at, ?),
                    finished_at = COALESCE(?, finished_at)
                WHERE id = ?
                """,
                (state.value, now, current_step, exit_code, held_reason, started_at if existing and existing["started_at"] is None else None, finished_at, job_id),
            )

    def transition_step(self, step_id: int, state: JobState, *, return_code: int | None = None, stdout_path: str | None = None, stderr_path: str | None = None) -> None:
        now = utc_now().isoformat()
        with self.connect() as conn:
            existing = conn.execute("SELECT started_at FROM steps WHERE id = ?", (step_id,)).fetchone()
            conn.execute(
                """
                UPDATE steps
                SET state = ?, return_code = ?, stdout_path = COALESCE(?, stdout_path),
                    stderr_path = COALESCE(?, stderr_path),
                    started_at = COALESCE(started_at, ?),
                    finished_at = CASE WHEN ? IN ('SUCCEEDED', 'FAILED', 'CANCELLED') THEN ? ELSE finished_at END
                WHERE id = ?
                """,
                (
                    state.value,
                    return_code,
                    stdout_path,
                    stderr_path,
                    now if existing and existing["started_at"] is None and state == JobState.RUNNING else None,
                    state.value,
                    now,
                    step_id,
                ),
            )

    def list_jobs(self) -> list[JobRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM jobs ORDER BY submitted_at DESC, id DESC").fetchall()
        return [row_to_job(row) for row in rows]

    def get_job(self, job_id: int) -> JobRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return row_to_job(row) if row else None

    def get_job_by_name(self, name: str) -> JobRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1", (name,)).fetchone()
        return row_to_job(row) if row else None

    def get_steps(self, job_id: int) -> list[StepRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM steps WHERE job_id = ? ORDER BY ordinal", (job_id,)).fetchall()
        return [row_to_step(row) for row in rows]

    def get_next_queued_jobs(self, limit: int) -> list[JobRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM jobs
                WHERE state = ?
                ORDER BY class_rank ASC, priority ASC, submitted_at ASC, id ASC
                LIMIT ?
                """,
                (JobState.QUEUED.value, limit),
            ).fetchall()
        return [row_to_job(row) for row in rows]

    def count_running_jobs(self) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM jobs WHERE state = ?", (JobState.RUNNING.value,)).fetchone()
        return int(row["count"])

    def recover_interrupted_jobs(self) -> int:
        now = utc_now().isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE jobs SET state = ?, updated_at = ?, current_step = NULL WHERE state = ?",
                (JobState.QUEUED.value, now, JobState.RUNNING.value),
            )
            conn.execute(
                "UPDATE steps SET state = ? WHERE state = ?",
                (JobState.QUEUED.value, JobState.RUNNING.value),
            )
            recovered = cursor.rowcount
        return recovered

    def request_stop(self, pid: int | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE daemon_state SET stop_requested = 1, pid = COALESCE(?, pid), updated_at = ? WHERE singleton = 1",
                (pid, utc_now().isoformat()),
            )

    def clear_stop_request(self, pid: int | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE daemon_state SET stop_requested = 0, pid = ?, updated_at = ? WHERE singleton = 1",
                (pid, utc_now().isoformat()),
            )

    def stop_requested(self) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT stop_requested FROM daemon_state WHERE singleton = 1").fetchone()
        return bool(row["stop_requested"])

    def hold_job(self, job_id: int, reason: str = "Held by operator.") -> None:
        self.transition_job(job_id, JobState.HELD, held_reason=reason)
        with self.connect() as conn:
            conn.execute("UPDATE steps SET state = ? WHERE job_id = ? AND state IN (?, ?)", (JobState.HELD.value, job_id, JobState.QUEUED.value, JobState.SUBMITTED.value))

    def release_job(self, job_id: int) -> None:
        self.transition_job(job_id, JobState.QUEUED, held_reason=None)
        with self.connect() as conn:
            conn.execute("UPDATE steps SET state = ? WHERE job_id = ? AND state = ?", (JobState.QUEUED.value, job_id, JobState.HELD.value))

    def cancel_job(self, job_id: int) -> None:
        self.transition_job(job_id, JobState.CANCELLED)
        with self.connect() as conn:
            conn.execute(
                "UPDATE steps SET state = ?, finished_at = ? WHERE job_id = ? AND state IN (?, ?, ?)",
                (JobState.CANCELLED.value, utc_now().isoformat(), job_id, JobState.QUEUED.value, JobState.HELD.value, JobState.RUNNING.value),
            )
