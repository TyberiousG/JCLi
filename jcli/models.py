from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobState(StrEnum):
    SUBMITTED = "SUBMITTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    HELD = "HELD"


@dataclass(slots=True)
class ValidationError:
    line: int
    code: str
    message: str


@dataclass(slots=True)
class DDStatement:
    name: str
    sysout: str


@dataclass(slots=True)
class StepDefinition:
    name: str
    program: str
    arguments: str = ""
    dd_statements: list[DDStatement] = field(default_factory=list)


@dataclass(slots=True)
class JobDefinition:
    name: str
    job_class: str
    priority: int
    user: str
    steps: list[StepDefinition]
    dd_statements: list[DDStatement] = field(default_factory=list)
    source_path: str | None = None
    raw_script: str | None = None


@dataclass(slots=True)
class StepResult:
    step_name: str
    state: JobState
    return_code: int
    started_at: datetime
    finished_at: datetime
    stdout: str
    stderr: str

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()


@dataclass(slots=True)
class JobRecord:
    id: int
    name: str
    job_class: str
    priority: int
    user: str
    state: JobState
    source_path: str | None
    submitted_at: datetime
    updated_at: datetime
    held_reason: str | None = None
    current_step: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None
    dependencies: str | None = None
    retry_limit: int = 0


@dataclass(slots=True)
class StepRecord:
    id: int
    job_id: int
    name: str
    program: str
    arguments: str
    ordinal: int
    state: JobState
    started_at: datetime | None = None
    finished_at: datetime | None = None
    return_code: int | None = None
    stdout_path: str | None = None
    stderr_path: str | None = None


def row_to_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def row_to_job(row: Any) -> JobRecord:
    return JobRecord(
        id=row["id"],
        name=row["name"],
        job_class=row["job_class"],
        priority=row["priority"],
        user=row["user_name"],
        state=JobState(row["state"]),
        source_path=row["source_path"],
        submitted_at=row_to_datetime(row["submitted_at"]) or utc_now(),
        updated_at=row_to_datetime(row["updated_at"]) or utc_now(),
        held_reason=row["held_reason"],
        current_step=row["current_step"],
        started_at=row_to_datetime(row["started_at"]),
        finished_at=row_to_datetime(row["finished_at"]),
        exit_code=row["exit_code"],
        dependencies=row["dependencies"],
        retry_limit=row["retry_limit"],
    )


def row_to_step(row: Any) -> StepRecord:
    return StepRecord(
        id=row["id"],
        job_id=row["job_id"],
        name=row["name"],
        program=row["program"],
        arguments=row["arguments"],
        ordinal=row["ordinal"],
        state=JobState(row["state"]),
        started_at=row_to_datetime(row["started_at"]),
        finished_at=row_to_datetime(row["finished_at"]),
        return_code=row["return_code"],
        stdout_path=row["stdout_path"],
        stderr_path=row["stderr_path"],
    )
