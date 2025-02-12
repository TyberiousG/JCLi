
# 🏗️ JCLi Architecture Documentation

Welcome to the **JCLi Architecture Guide**. This document outlines the design, core components, and data flow of JCLi, a job control subsystem for Linux inspired by IBM’s Job Control Language (JCL).

---

## 🚀 Overview

JCLi is a modular job control system that allows users to define, schedule, and manage jobs using JCL-like scripts. The system consists of key components:

- **Control Interface (CLI)**: User-facing command-line interface for managing jobs.
- **Daemon**: Background process that handles job scheduling, lifecycle management, and execution.
- **Interpreter**: Parses and validates JCLi scripts.
- **Scheduler**: Manages job priorities and execution order.
- **Executor**: Executes jobs as shell commands or scripts.
- **Queue Interface**: Interactive menu for managing queued jobs.
- **Logging**: Handles job output, event logs, and error tracking.

---

## 📦 High-Level Architecture

```
+---------------------------+
|      Control Interface    |
|  (JCLi Command-Line Tool) |
+-------------+-------------+
              |
              v
+-------------+-------------+
|          Daemon           |
|  - Job Lifecycle Manager  |
|  - Scheduler              |
|  - Held Job Handling      |
+-------------+-------------+
              |
      +-------+--------+
      |                |
+-----+-----+    +-----+-----+
| Interpreter |  |  Executor  |
|  (Parses    |  |  (Runs     |
|  JCLi Files)|  |  Jobs)     |
+-------------+  +-----------+
              |
      +-------+--------+
      |    Logging     |
      +----------------+
```

---

## 🔍 Core Components

### 1️⃣ **Control Interface (CLI)**

- **Files:** `ControlInterface/cli.py`, `command_handler.py`
- Provides the user-facing command-line interface.
- Accepts commands like `SUBMIT`, `STATUS`, `QUEUE`, `EXIT`.
- Delegates commands to the Daemon.

---

### 2️⃣ **Daemon**

- **Files:** `Daemon/daemon.py`, `scheduler.py`, `job_lifecycle.py`
- The heart of JCLi—manages job queues, scheduling, and execution.
- **Key Responsibilities:**
  - Manages running and queued jobs.
  - Handles job lifecycle states: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `HELD`.
  - Supports Class H (held) jobs that require manual release.

---

### 3️⃣ **Interpreter**

- **Files:** `Interpreter/parser.py`, `validator.py`
- Parses JCLi scripts and validates their syntax.
- Extracts job details like name, priority, user, and execution steps.

---

### 4️⃣ **Scheduler**

- **Files:** `Daemon/scheduler.py`, `priority_manager.py`
- Uses a priority queue to schedule jobs based on class (`A`, `B`, `C`, `H`) and priority (`1-10`).
- Held jobs (`CLASS=H`) are managed separately and only executed after manual release.

---

### 5️⃣ **Executor**

- **Files:** `Executor/executor.py`, `shell_executor.py`, `binary_executor.py`
- Executes jobs as shell commands, scripts, or binaries.
- Captures standard output and error logs.

---

### 6️⃣ **Queue Interface**

- **Files:** `QueueInterface/queue_menu.py`, `queue_commands.py`
- Interactive interface for managing queued jobs.
- Supports commands:
  - `R <JOBNAME>`: Restart
  - `C <JOBNAME>`: Cancel
  - `F <JOBNAME>`: Force execution
  - `RELEASE <JOBNAME>`: Release held jobs

---

### 7️⃣ **Logging**

- **Files:** `Logging/logger.py`, `job_logger.py`, `event_logger.py`
- Logs job outputs (`SYSOUT` equivalent), statuses, and system events.
- Error handling and audit trails are stored in log files.

---

## 🔄 Job Lifecycle

1. **Job Submission** (`SUBMIT my_job.jcli`)
   - CLI sends the script to the Interpreter.
   - Interpreter parses and validates the job.

2. **Job Queuing**
   - Daemon receives the job.
   - Class H jobs are marked as `HELD` until released.
   - Other jobs are queued based on priority.

3. **Job Execution**
   - Scheduler picks the next job based on priority.
   - Executor runs the job.

4. **Job Completion**
   - Job output and status are logged.
   - Final status: `COMPLETED`, `FAILED`, or `CANCELLED`.

---

## 🗂️ Folder Structure

```
JCLi/
├── ControlInterface/
│   ├── cli.py
│   └── command_handler.py
├── Daemon/
│   ├── daemon.py
│   ├── scheduler.py
│   ├── job_lifecycle.py
│   └── priority_manager.py
├── Interpreter/
│   ├── parser.py
│   └── validator.py
├── Executor/
│   ├── executor.py
│   └── shell_executor.py
├── QueueInterface/
│   ├── queue_menu.py
│   └── queue_commands.py
├── Logging/
│   ├── logger.py
│   └── event_logger.py
└── logs/
    ├── jobs/
    └── system/
```

---

## 🔗 Future Enhancements

- **Recurring Job Scheduling** (like cron jobs).
- **Job Dependencies** (e.g., Job B starts after Job A completes).
- **Resource Management** (CPU, memory constraints).
- **Web Interface** for job management.

---

## 🙌 Contributing

See `CONTRIBUTING.md` for guidelines on how to contribute to JCLi.
