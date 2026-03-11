# JCLi User Manual

## Commands

JCLi now uses a non-interactive command-line interface:

```bash
jcli start
jcli stop
jcli submit path/to/job.jcli
jcli status
jcli show-job 1
jcli show-logs 1
jcli show-logs 1 --step STEP1 --stream stdout
jcli hold 1
jcli release 1
jcli cancel 1
```

The state directory defaults to `.jcli/` under the current working directory. Override it with `--state-dir` or `JCLI_HOME`.

## Script Format

Supported constructs:

```jcl
//JOBNAME JOB CLASS=A,PRTY=2,USER=batch
//STEP1   EXEC PGM=/usr/bin/echo,ARGS='hello'
//OUTPUT  DD SYSOUT=A
```

Rules:

- Exactly one `JOB` statement is required
- At least one `EXEC` statement is required
- `CLASS` supports `A`, `B`, `C`, `D`, `E`, and `H`
- `PRTY` must be an integer from `1` to `10`
- `CLASS=H` submits the job in `HELD`

## Job States

- `SUBMITTED`
- `QUEUED`
- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `CANCELLED`
- `HELD`

## Scheduling Semantics

- Jobs are ordered by class rank, then by numeric priority, then FIFO
- Lower class rank and lower `PRTY` value run first
- The daemon enforces `--max-concurrent-jobs`
- Interrupted `RUNNING` jobs are moved back to `QUEUED` when the daemon restarts

## Logs

- System log: `.jcli/logs/system/system.log`
- Error log: `.jcli/logs/system/errors.log`
- Job log: `.jcli/logs/jobs/*.log`
- Step logs: `.jcli/logs/steps/*_stdout.log` and `*_stderr.log`

## Notes

- JCLi is designed for Linux execution targets even if the CLI can run elsewhere
- `DD SYSOUT=` is currently preserved as metadata and logging intent, not a full spool-routing system
- Dependency management, retries, schedules, a REST API, and remote workers are planned next
