# JCLi Architecture

## Current Assessment

The original codebase established the right conceptual modules, but several important boundaries were only nominal:

- The control interface, daemon, scheduler, and executor communicated through in-memory objects only, so job state vanished on process exit.
- Parsing and validation were split into files, but parsing was largely string matching without structured error reporting or a normalized step model.
- Queueing was heap-based but tied to process memory, with no recovery path after daemon restart.
- Job lifecycle and execution logic overlapped, and execution was mostly direct `subprocess.run` calls without durable step telemetry.
- Logging existed, but each layer wrote ad hoc text files instead of using a consistent system/job/step logging strategy.

Useful pieces that were preserved in spirit:

- The JCL-like script surface: `JOB`, `EXEC`, and `DD`
- Class-based queue semantics, especially hold behavior via `CLASS=H`
- The modular intent of control plane, interpreter, daemon, executor, and logging

## Target Architecture

JCLi now centers on a single package with explicit boundaries:

```text
CLI / Control Plane
  -> Parser / Validator
  -> Persistence Store (SQLite)
  -> Scheduler
  -> Daemon
  -> Executor
  -> Logging / Observability
```

### Control Plane

- `jcli.cli`
- Owns operator commands such as `start`, `stop`, `submit`, `status`, `show-job`, `show-logs`, `cancel`, `hold`, and `release`
- Talks to the daemon indirectly through SQLite state and the PID/stop-request files

### Parser / Interpreter

- `jcli.parser`
- Converts `.jcli` text into normalized `JobDefinition`, `StepDefinition`, and `DDStatement` models
- Returns structured `ValidationError` instances instead of loose strings
- Validates supported `JOB`, `EXEC`, and `DD` constructs while leaving room for future dependency and retry extensions

### Persistence / State

- `jcli.store`
- SQLite is the system of record for jobs, steps, daemon state, and operator events
- Job states are canonicalized to:
  - `SUBMITTED`
  - `QUEUED`
  - `RUNNING`
  - `SUCCEEDED`
  - `FAILED`
  - `CANCELLED`
  - `HELD`
- Restart recovery moves interrupted `RUNNING` work back to `QUEUED`

### Scheduler / Daemon

- `jcli.scheduler` and `jcli.daemon`
- Scheduler chooses dispatch order by class rank, numeric priority, then FIFO submission order
- Daemon enforces a concurrency ceiling, maintains a PID lock, handles stop requests, and rehydrates the queue from SQLite on startup
- The database schema already includes hooks for future dependency and retry semantics

### Executor / Runtime

- `jcli.executor`
- Executes each step independently, captures stdout/stderr, return codes, and timing metadata
- Updates step and job state in the persistent store as work progresses
- Stops job execution on the first failing step, which matches classic batch behavior

### Logging / Observability

- `jcli.logging`
- Separates:
  - system log
  - error log
  - job log
  - step stdout/stderr logs
- Adds JSONL sidecars for machine-readable event consumption where useful

## Architectural Decisions

- SQLite was chosen over JSON files because it gives durable state, transactional updates, and straightforward query semantics without adding infrastructure.
- The daemon and CLI are intentionally decoupled through the store so the control plane can remain simple and scriptable.
- The parser supports a focused subset of JCL rather than pretending to be full JCL; this keeps the internals clean while preserving the mainframe flavor.
- Step-level state is persisted separately from job state so future features like retries, dependencies, and remote workers have a stable foundation.
