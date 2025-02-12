
# ⚙️ JCLi Configuration Guide

Welcome to the **JCLi Configuration Guide**. This document outlines how to configure JCLi to suit your environment, including job scheduling behavior, logging settings, and system limits.

---

## 🚀 Overview

JCLi is designed to work out of the box with minimal configuration. However, advanced users can customize job priorities, logging paths, and other system behaviors.

---

## 📁 Configuration Files

Currently, JCLi uses hardcoded defaults, but future versions may include external config files. For now, configurations can be adjusted directly in the following modules:

- **Daemon Settings:** `Daemon/daemon.py`
- **Scheduler Settings:** `Daemon/scheduler.py`
- **Priority Settings:** `Daemon/priority_manager.py`
- **Logging Configuration:** `Logging/logger.py`

---

## 🔄 Job Scheduling Configuration

### 1️⃣ **Priority Classes & Values**

- **File:** `Daemon/priority_manager.py`

```python
self.priority_map = {
    "A": 1,    # High Priority
    "B": 2,    # Medium Priority
    "C": 3,    # Low Priority
    "H": 99    # Held Jobs (manually released)
}
```

- **Modify Priorities:**
  - Lower numbers = higher priority.
  - Adjust values to fine-tune job execution order.

---

### 2️⃣ **Job Hold Behavior (Class H)**

- **File:** `Daemon/daemon.py`

Jobs submitted with `CLASS=H` are held until manually released.

```python
if job.job_class == "H":
    self.held_jobs.append(job)
    self.job_lifecycle.update_status(job, "HELD")
```

- **Configuration:** You can modify the behavior to automatically release jobs after a timeout if needed (manual customization required).

---

## 📊 Logging Configuration

### 1️⃣ **Log Directory**

- **File:** `Logging/logger.py`

```python
self.log_dir = "logs/jobs"
```

- **Change Log Path:**
  - Update `self.log_dir` to redirect logs to another directory.

### 2️⃣ **Log Levels (Future Feature)**

Currently, JCLi logs all events. In future versions, log levels (INFO, WARNING, ERROR) will be configurable.

---

## 🚦 System Settings

### 1️⃣ **Concurrency Settings**

- **File:** `Daemon/scheduler.py`

```python
self.max_concurrent_jobs = 3
```

- **Adjust Max Concurrent Jobs:**
  - Increase or decrease based on system performance.

### 2️⃣ **Job Timeout (Optional)**

If you want to add a timeout for jobs:

```python
import threading

def execute_with_timeout(job, timeout=60):  # 60 seconds timeout
    thread = threading.Thread(target=self.execute_job, args=(job,))
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        print(f"Job '{job.name}' timed out!")
```

---

## 📂 Directory Structure

```
JCLi/
├── Daemon/
│   ├── daemon.py               # Job lifecycle & held jobs
│   ├── scheduler.py            # Job scheduling logic
│   └── priority_manager.py     # Priority configurations
├── Logging/
│   └── logger.py               # Log handling
└── logs/
    ├── jobs/                   # Job output logs
    └── system/                 # System event logs
```

---

## 🛠️ Advanced Customization

1. **Custom Job Classes:**
   - Add new classes in `priority_manager.py` and define behaviors in `daemon.py`.

2. **Dynamic Configuration (Planned Feature):**
   - Future updates may introduce `config.yaml` or `.ini` files for dynamic settings.

3. **Database Integration (Future):**
   - Potential support for tracking job statuses in a database instead of flat files.

---

## 🙌 Need Help?

For advanced configurations or issues, feel free to open an issue on GitHub or contribute to the project!

