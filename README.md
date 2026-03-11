# JCLi

JCLi is a Linux batch/job-control system inspired by IBM JCL. Jobs are submitted as `JOB` / `EXEC` / `DD` scripts, persisted in SQLite, dispatched by a restart-safe daemon, and executed with per-step logs and status tracking.

## What Changed

The original repository had a promising modular layout but most runtime behavior lived in thin in-memory classes. This refactor keeps the mainframe-inspired surface area while moving the real control plane into a clean Python package:

- `jcli.cli`: non-interactive control plane commands
- `jcli.parser`: lexical parsing plus structured validation errors
- `jcli.store`: SQLite-backed job, step, event, and daemon state
- `jcli.scheduler`: priority plus FIFO scheduling with concurrency limits
- `jcli.executor`: per-step subprocess execution and log capture
- `jcli.daemon`: PID-safe daemon loop with restart recovery

The legacy `main.py` and `ControlInterface/cli.py` entry points now route into the new package.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick Start

1. Start the daemon:

```bash
jcli start
```

2. Submit a job:

```bash
jcli submit JCLi_Samples/simple_echo.jcli
```

3. Inspect queue state:

```bash
jcli status
jcli show-job 1
```

4. Inspect logs:

```bash
jcli show-logs 1
jcli show-logs 1 --step STEP1 --stream stdout
```

5. Control jobs:

```bash
jcli hold 1
jcli release 1
jcli cancel 1
jcli stop
```

## Example Script

```jcl
//PAYROLL JOB CLASS=A,PRTY=2,USER=batch
//EXTRACT EXEC PGM=/usr/bin/python3,ARGS='/opt/jcli/jobs/extract.py'
//REPORT  EXEC PGM=/usr/bin/python3,ARGS='/opt/jcli/jobs/report.py --format pdf'
//OUTPUT  DD SYSOUT=A
```

Scheduling rules:

- Lower class rank runs first: `A` before `B` before `C`
- Lower numeric `PRTY` runs first within a class
- Jobs with equal class and priority run FIFO
- `CLASS=H` submits the job in `HELD`

## State and Logs

By default JCLi stores runtime state under `.jcli/` in the current working directory:

- `.jcli/jcli.db`: persistent SQLite store
- `.jcli/daemon.pid`: daemon PID lock
- `.jcli/logs/system/system.log`: operator/system log
- `.jcli/logs/system/errors.log`: error log
- `.jcli/logs/jobs/<job>.log`: job lifecycle log
- `.jcli/logs/steps/<step>_stdout.log`: step stdout
- `.jcli/logs/steps/<step>_stderr.log`: step stderr

Set `JCLI_HOME` or pass `--state-dir` to relocate the state directory.

## Development

Run the built-in test suite:

```bash
python -m unittest discover -s tests -v
```

Linting is configured in [`pyproject.toml`](/Users/ty/Documents/GitHub/JCLi/pyproject.toml).

## Docs

- Architecture assessment and target design: [`docs/ARCHITECTURE.MD`](/Users/ty/Documents/GitHub/JCLi/docs/ARCHITECTURE.MD)
- User manual: [`docs/USER_MANUAL.md`](/Users/ty/Documents/GitHub/JCLi/docs/USER_MANUAL.md)
- Roadmap: [`docs/ROADMAP.md`](/Users/ty/Documents/GitHub/JCLi/docs/ROADMAP.md)
