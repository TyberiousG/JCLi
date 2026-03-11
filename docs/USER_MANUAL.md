# JCLi User Manual

This manual covers the current behavior of JCLi as implemented in this repository: how to start it, how to submit work, how the interactive CLI behaves, and which JCL-like script forms the interpreter accepts.

## 1. What JCLi Is

JCLi is a lightweight batch job controller inspired by IBM JCL. A user writes a `.jcli` script, submits it through the control interface, and the daemon queues and executes the job. Jobs can contain one or more `EXEC` steps, can be prioritized by class and numeric priority, and write status/output logs under the `logs/` directory.

Main components:

- `ControlInterface`: interactive command shell.
- `Interpreter`: parser and validator for `.jcli` scripts.
- `Daemon`: queue management and job dispatch loop.
- `QueueInterface`: interactive queue management menu.
- `Logging`: per-job output/status logs and system error logs.

## 2. Requirements

Current repository expectations:

- Python 3.x
- No third-party Python dependencies
- Programs referenced by `PGM=` must exist on the machine where JCLi is running

The project is written with Linux-style paths in mind, but the CLI itself can be launched anywhere Python runs. Job execution only succeeds when the paths and commands in the submitted script are valid for that host.

## 3. Starting JCLi

From the repository root:

```bash
python main.py
```

You can also start the control interface module directly:

```bash
python -m ControlInterface.cli
```

On startup, JCLi opens an interactive shell:

```text
$JCLC Welcome to JCLi!
Enter 'HELP' to see available commands.
$JCLC
```

Important: launching the shell does not automatically start the job daemon. You should run `START` before expecting queued jobs to dispatch.

## 4. Interactive CLI Usage

JCLi currently uses an interactive shell only. There are no command-line flags such as `--submit` or `--status` in this codebase. All control operations happen after the shell starts.

### 4.1 Main Commands

The following commands are available at the `$JCLC` prompt:

| Command | Purpose |
| --- | --- |
| `START` | Starts the background daemon thread that dispatches queued jobs |
| `STOP` | Stops the daemon loop |
| `SUBMIT <path>` | Loads, parses, validates, and queues a `.jcli` script |
| `STATUS` | Prints known status values for submitted jobs |
| `QUEUE` | Opens the queue management menu |
| `HELP` | Prints the command list |
| `EXIT` | Leaves the control interface |

Commands are case-insensitive because the shell normalizes the command word to uppercase.

### 4.2 Typical CLI Session

```text
$JCLC START
$JCLD Starting daemon...
$JCLH Daemon started.

$JCLC SUBMIT JCLi_Samples/simple_echo.jcli
$JCLD Submitting job: ECHOJOB
[Scheduler] Job 'ECHOJOB' added to queue with priority 105.
$JCLL Job 'ECHOJOB' status updated to: QUEUED
$JCLH Job 'ECHOJOB' submitted successfully.

$JCLC STATUS
$JCLS Job 'ECHOJOB': QUEUED
```

Because execution is asynchronous, a job may still show `QUEUED` if you check status immediately after submission.

### 4.3 Command Details

#### `START`

Starts the daemon thread if it is not already running.

Behavior:

- Prints a message if the daemon starts successfully.
- Prints a different message if the daemon is already running.
- Once started, the daemon checks the scheduler roughly once per second.

#### `STOP`

Stops the daemon dispatch loop.

Behavior:

- Prevents new queued jobs from being dispatched.
- Does not delete jobs already in the queue.
- Does not undo a job that has already started running.

#### `SUBMIT <path_to_script>`

Reads a `.jcli` file from disk, parses it, validates it, and submits it to the daemon.

Behavior:

- If the file path is missing, JCLi prints `Usage: SUBMIT <path_to_jcli_script>`.
- If the file does not exist, JCLi prints an error.
- If validation fails, JCLi prints one or more `Validation Error:` lines and does not submit the job.
- If the job class is `H`, the job is placed in the held queue instead of the active scheduler queue.

Important operational note:

- You can submit jobs before running `START`, but they will remain queued or held until the daemon is started or a queue action forces them to run.

#### `STATUS`

Prints all job names and their latest known status values.

Observed statuses in the current code:

- `HELD`
- `QUEUED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

`STATUS` only prints jobs that have been seen by the daemon lifecycle manager during the current process. It is not a historical report loaded from disk.

#### `QUEUE`

Opens a second interactive prompt, `$JCLQ`, for queue management.

The queue display shows:

- Active scheduled jobs
- Held jobs
- Class
- Numeric priority
- Current status
- User

#### `HELP`

Prints the built-in command reference from the control interface.

#### `EXIT`

Exits the interactive shell.

If you press `Ctrl+C` or send EOF, the shell also exits.

## 5. Queue Menu Usage

The queue menu is entered with `QUEUE` from the main shell.

Example:

```text
$JCLC QUEUE
$JCLQ
```

### 5.1 Queue Commands

The queue menu accepts one of these forms:

| Command | Meaning |
| --- | --- |
| `R <job>` | Restart a job |
| `C <job>` | Cancel a queued or held job |
| `F <job>` | Force a job to run immediately |
| `RL <job>` | Release a held job back into the scheduler |
| `EXIT` | Return to the main shell |

The queue input is uppercased before parsing, so uppercase job names are the safest choice when authoring scripts.

### 5.2 Queue Command Behavior

#### `R <job>`

Restart does two things:

1. Cancels the matching queued or held job.
2. Resubmits the same job object to the daemon.

If the daemon is not running, the restarted job will be resubmitted but not dispatched until the daemon is started.

#### `C <job>`

Cancel removes the job from the scheduler queue or from the held list and marks it `CANCELLED`.

This command is intended for jobs that have not started yet. It does not terminate an already running operating-system process.

#### `F <job>`

Force removes the job from the queue and executes it immediately through the job lifecycle executor.

Notes:

- `F` works even if the daemon is not running, because it invokes execution directly.
- If the job had been held, it is removed from the held list first.

#### `RL <job>`

Release only works for jobs currently marked `HELD`.

Behavior:

- Removes the job from the held list
- Re-queues it in the scheduler
- Changes its status from `HELD` to `QUEUED`

### 5.3 Queue Command Errors

Common queue errors:

- If the syntax is not exactly two tokens for `R`, `C`, `F`, or `RL`, JCLi prints `SYNTAX ERROR. R,C,F,RL - ENTER JOB. READY.`
- If the named job is not found, JCLi prints `JOB '<job>' NOT FOUND. REENTER. READY.`
- If you try `RL` on a job that is not held, JCLi reports that it is not currently held.

## 6. JCLi Scripting Syntax

JCLi scripts are plain text files, usually with a `.jcli` extension. The parser scans the file line by line and recognizes lines containing:

- `JOB`
- `EXEC`
- `DD`

The intended structure is:

```jcl
//JOBNAME  JOB CLASS=A,PRTY=5,USER=admin
//STEP1    EXEC PGM=/usr/bin/echo,ARGS='Hello from JCLi'
//OUTPUT   DD SYSOUT=A
```

### 6.1 General Rules

- Statement lines should begin with `//`.
- A script should contain exactly one logical `JOB` definition.
- A job can contain one or more `EXEC` statements.
- A script may contain one `DD` line for output class metadata.
- Blank lines are harmless because unrecognized lines are ignored.
- There is no formal comment syntax in the parser.

### 6.2 `JOB` Statement

Format:

```jcl
//JOBNAME  JOB CLASS=A,PRTY=5,USER=admin
```

Fields supported by the parser:

| Field | Required | Meaning |
| --- | --- | --- |
| Job name after `//` | Yes | Logical job identifier |
| `CLASS=` | No, but strongly recommended | Priority class |
| `PRTY=` | Yes in practice | Numeric priority from 1 to 10 |
| `USER=` | No | User label stored with the job |

Details:

- The job name is taken from the token immediately after `//`.
- If `CLASS=` is omitted, the parser defaults to `C`.
- If `USER=` is omitted, the parser defaults to `default`.
- If `PRTY=` is omitted, the parser defaults to `0`, which then fails validation because valid priorities are `1` through `10`.

Valid classes in the current validator:

- `A`
- `B`
- `C`
- `D`
- `E`
- `H`

Class meanings:

- `A` through `E`: schedulable classes, highest to lowest
- `H`: hold class; the job is submitted in held state until released manually

### 6.3 Priority Semantics

Priority is calculated from both class and `PRTY`.

Internal scheduling formula:

```text
(class_base * 100) + priority
```

Class ordering:

| Class | Base |
| --- | --- |
| `A` | 1 |
| `B` | 2 |
| `C` | 3 |
| `D` | 4 |
| `E` | 5 |

Lower computed values run first.

Examples:

- `CLASS=A,PRTY=1` outranks `CLASS=A,PRTY=9`
- `CLASS=A,PRTY=10` still outranks `CLASS=B,PRTY=1`
- `CLASS=H` is not scheduled; it is held

### 6.4 `EXEC` Statement

Format:

```jcl
//STEP1  EXEC PGM=/usr/bin/echo,ARGS='Hello world'
```

Supported fields:

| Field | Required | Meaning |
| --- | --- | --- |
| Step name after `//` | No, but recommended | Label written into output logs |
| `PGM=` | Yes | Program or executable path |
| `ARGS='...'` | No | Argument string split at runtime |

Details:

- Each `EXEC` line becomes one execution step.
- Steps run in the order they appear in the script.
- If any step exits with a non-zero return code, the job is marked `FAILED` and remaining steps are not run.
- If all steps succeed, the job is marked `COMPLETED`.

Program handling:

- `PGM=` is parsed as a non-space, non-comma token.
- Use a fully qualified executable path whenever possible.
- Relative paths may work if valid from the current working directory, but absolute paths are more reliable.

Argument handling:

- The parser expects the argument string in single quotes: `ARGS='...'`
- At execution time, arguments are split with shell-like parsing (`shlex.split`)
- Quoting inside `ARGS` should therefore be kept simple and deliberate

Examples:

```jcl
//STEP1  EXEC PGM=/usr/bin/python3,ARGS='script.py --mode full'
//STEP2  EXEC PGM=/usr/bin/echo,ARGS='Processing complete'
```

### 6.5 Multi-Step Jobs

A job may contain more than one `EXEC` statement:

```jcl
//MULTISTEP JOB CLASS=B,PRTY=4,USER=admin
//STEP1     EXEC PGM=/usr/bin/echo,ARGS='Step 1'
//STEP2     EXEC PGM=/usr/bin/echo,ARGS='Step 2'
//STEP3     EXEC PGM=/usr/bin/echo,ARGS='Step 3'
//OUTPUT    DD SYSOUT=B
```

Execution behavior:

1. `STEP1` runs first
2. `STEP2` runs next if `STEP1` succeeds
3. `STEP3` runs next if `STEP2` succeeds
4. Output is appended to the same job log, with step headers such as `[STEP1]`

### 6.6 `DD` Statement

Format:

```jcl
//OUTPUT  DD SYSOUT=A
```

Supported field:

| Field | Required | Meaning |
| --- | --- | --- |
| `SYSOUT=` | No | Output class label stored in the job definition |

Important limitation:

- In the current code, `SYSOUT` is metadata only.
- It does not route output to separate destinations.
- Job output always goes to files under `logs/jobs/`.

### 6.7 Minimal Valid Script

```jcl
//MYJOB   JOB CLASS=C,PRTY=5,USER=admin
//STEP1   EXEC PGM=/usr/bin/echo,ARGS='Hello'
//OUTPUT  DD SYSOUT=C
```

### 6.8 Held Job Example

```jcl
//HOLDJOB JOB CLASS=H,PRTY=5,USER=admin
//STEP1   EXEC PGM=/usr/bin/echo,ARGS='Run me later'
//OUTPUT  DD SYSOUT=A
```

Lifecycle:

1. Submit with `SUBMIT`
2. See it as `HELD` in `STATUS` or `QUEUE`
3. Open `QUEUE`
4. Run `RL HOLDJOB`
5. The job becomes `QUEUED`
6. The daemon dispatches it when its turn arrives

## 7. Validation Rules

Before a script is accepted, the validator checks:

- Job name must be present
- Job class must be one of `A`, `B`, `C`, `D`, `E`, or `H`
- Priority must be an integer from `1` to `10`
- Every `EXEC` step must include a `PGM=`
- If there are no parsed steps, the job-level program field must be present

Typical validation failures:

- Missing `PRTY=`
- Invalid class such as `Z`
- Missing `PGM=`
- Priority outside `1..10`

Example messages:

```text
Validation Error: Priority '0' is invalid. Must be between 1 and 10.
Validation Error: Step 'STEP1' is missing a program (PGM).
```

## 8. Logging and Output Files

JCLi writes logs under `logs/`.

### 8.1 Job Logs

Per-job files are created in `logs/jobs/`:

- `<JOBNAME>_output.log`
- `<JOBNAME>_status.log`

`_output.log` contains:

- timestamped log sections
- `[STDOUT]` output
- `[STDERR]` output
- step labels like `[STEP1]` when available

`_status.log` contains:

- timestamped status transitions such as `QUEUED`, `RUNNING`, `COMPLETED`, and `FAILED`

### 8.2 System Logs

System logs are created in `logs/system/`:

- `events.log`
- `errors.log`

`errors.log` is especially useful when a job fails because the executable does not exist or raises an execution exception.

## 9. Execution Model

Understanding the runtime model helps explain what you see in `STATUS` and `QUEUE`.

### 9.1 Submission

When you submit a script:

1. The file is read
2. The parser extracts job metadata and steps
3. The validator checks the result
4. The daemon either:
   - stores the job in the held list if `CLASS=H`, or
   - adds it to the scheduler queue otherwise

### 9.2 Dispatch

When the daemon is running:

1. It checks the queue about once per second
2. It pops the highest-priority job
3. It marks the job `RUNNING`
4. It executes each `EXEC` step in order with `subprocess.run`

### 9.3 Completion

- If every step returns exit code `0`, the job becomes `COMPLETED`
- If any step returns a non-zero exit code, the job becomes `FAILED`
- If execution raises an exception, the job also becomes `FAILED`

## 10. Examples

### 10.1 Simple Echo Job

```jcl
//ECHOJOB  JOB CLASS=A,PRTY=5,USER=admin
//STEP1    EXEC PGM=/usr/bin/echo,ARGS='Hello, JCLi World!'
//OUTPUT   DD SYSOUT=A
```

### 10.2 Backup Job

```jcl
//BACKUP   JOB CLASS=A,PRTY=3,USER=root
//STEP1    EXEC PGM=/bin/tar,ARGS='-czf /tmp/backup.tar.gz /etc'
//OUTPUT   DD SYSOUT=A
```

### 10.3 Failing Job

```jcl
//FAILJOB  JOB CLASS=B,PRTY=5,USER=admin
//STEP1    EXEC PGM=/bin/false,ARGS=''
//OUTPUT   DD SYSOUT=B
```

This is useful for testing `FAILED` status handling and error logging.

## 11. Troubleshooting

### 11.1 Job Never Runs

Possible causes:

- The daemon was never started
- The job was submitted with `CLASS=H`
- The program path in `PGM=` is invalid

Checks:

- Run `STATUS`
- Open `QUEUE`
- Verify you already issued `START`
- Inspect `logs/jobs/<JOBNAME>_status.log`
- Inspect `logs/system/errors.log`

### 11.2 Validation Error on Submit

Most common causes:

- Missing `PRTY=`
- Invalid priority value
- Missing `PGM=`
- Invalid class

Fix the script and submit again.

### 11.3 Queue Command Cannot Find Job

The queue menu compares names directly. Use the exact script job name, and prefer uppercase names in scripts to match the queue menu's uppercased input behavior.

### 11.4 `STATUS` Only Shows `QUEUED`

This usually means you checked too quickly or the daemon is not running. The daemon dispatches on a loop, not immediately inside the `SUBMIT` command.

### 11.5 Running on Windows

The control shell can launch, but sample jobs reference Linux binaries such as `/usr/bin/echo`, `/bin/tar`, and `/bin/false`. Replace those with commands valid on the host operating system if you want the jobs to execute successfully there.

## 12. Current Limitations

This manual describes the implementation as it exists now. A few practical limits are worth calling out directly:

- No non-interactive CLI flags are implemented
- No persistent job database is loaded on startup
- `SYSOUT=` does not change file destinations
- The parser is intentionally simple and does not support full JCL syntax
- There is no built-in comment syntax
- Queue cancellation does not terminate already running OS processes
- Held jobs must be released manually with `RL <job>`

## 13. Recommended Workflow

For day-to-day use, this is the safest sequence:

1. Write a `.jcli` file with a valid `JOB`, at least one `EXEC`, and a `DD`
2. Start JCLi with `python main.py`
3. Run `START`
4. Run `SUBMIT <file>`
5. Run `STATUS`
6. Use `QUEUE` if you need to restart, cancel, force, or release held work
7. Inspect `logs/jobs/` and `logs/system/` for output and errors

## 14. Reference Summary

### Main Shell

```text
START
STOP
SUBMIT <path>
STATUS
QUEUE
HELP
EXIT
```

### Queue Shell

```text
R <job>
C <job>
F <job>
RL <job>
EXIT
```

### Script Skeleton

```jcl
//JOBNAME  JOB CLASS=A,PRTY=5,USER=admin
//STEP1    EXEC PGM=/path/to/program,ARGS='arg1 arg2'
//OUTPUT   DD SYSOUT=A
```
