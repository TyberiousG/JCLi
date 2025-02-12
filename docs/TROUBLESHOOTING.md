
# 🛠️ JCLi Troubleshooting Guide

Welcome to the **JCLi Troubleshooting Guide**. This document helps diagnose and resolve common issues encountered while using JCLi, including job submission errors, daemon issues, and queue management problems.

---

## 🚀 Quick Checklist

Before diving into specific issues:

- ✅ Is the JCLi Daemon running? (`START` command)  
- ✅ Are the scripts properly formatted?  
- ✅ Check logs: `logs/system/errors.log` and `logs/jobs/<job>_output.log`  

---

## ❗ Common Issues & Fixes

### 1️⃣ **Daemon Not Starting**

**Error:**
```
[CommandHandler] Daemon is not running.
```

**Cause:** The daemon hasn’t been started.

**Solution:**
```bash
JCLi> START
```

If the issue persists, check `logs/system/errors.log` for detailed errors.

---

### 2️⃣ **Job Submission Fails**

**Error:**
```
Validation Error: Missing JOB statement.
```

**Cause:** The JCLi script is missing the `JOB` declaration.

**Solution:**
Ensure your script starts with:
```jcl
//JOBNAME  JOB CLASS=A,PRTY=5,USER=admin
```

---

### 3️⃣ **Unknown Command Error**

**Error:**
```
[CommandHandler] Unknown command: 'XYZ'. Type 'HELP' for a list of commands.
```

**Cause:** Typo or unsupported command.

**Solution:**
```bash
JCLi> HELP
```
Review the command list and correct any typos.

---

### 4️⃣ **Job Stuck in HELD Status**

**Issue:**  
Jobs with `CLASS=H` remain in the queue indefinitely.

**Solution:**  
Manually release the job:
```bash
JCLi> QUEUE
Queue> RELEASE JOBNAME
```

---

### 5️⃣ **Cannot Re-enter Queue Menu**

**Issue:**  
After exiting the Queue menu, it won’t reopen.

**Cause:** The `running` flag in `queue_menu.py` isn’t reset.

**Fix:**  
Ensure this line exists at the start of the `run()` method:
```python
self.running = True
```

---

### 6️⃣ **Job Not Found in Queue**

**Error:**
```
Job 'JOBNAME' not found in the queue.
```

**Cause:**  
- Job was completed or canceled.  
- Typo in job name.  
- Held jobs not listed properly.

**Solution:**  
1. Verify job status:
   ```bash
   JCLi> STATUS
   ```
2. Check both regular and held jobs in the Queue menu:
   ```bash
   JCLi> QUEUE
   ```

---

### 7️⃣ **Job Execution Fails**

**Error:**
```
[Executor] Error: File not found.
```

**Cause:** Invalid program path or missing executable.

**Solution:**  
- Verify the `PGM` path in the script:
  ```jcl
  //STEP1 EXEC PGM=/usr/bin/python3,ARGS='script.py'
  ```
- Check file permissions:
  ```bash
  ls -l /usr/bin/python3
  ```

---

## 📊 Log Files for Debugging

- **System Errors:** `logs/system/errors.log`
- **Job Output:** `logs/jobs/<job>_output.log`
- **Daemon Events:** `logs/system/events.log`

---

## 🚦 Job Status Codes

| **Status**   | **Meaning**                      |
|--------------|---------------------------------|
| `QUEUED`     | Job is waiting to be executed.  |
| `RUNNING`    | Job is currently executing.     |
| `COMPLETED`  | Job finished successfully.      |
| `FAILED`     | Job encountered an error.       |
| `CANCELLED`  | Job was manually canceled.      |
| `HELD`       | Job is on hold, pending release.|

---

## 🚀 Advanced Debugging

### Enable Debug Logging (Optional)

In `Logging/logger.py`, add debug logs:
```python
print(f"[DEBUG] Job '{job.name}' status: {status}")
```

---

## 🙋 Need More Help?

- **Check Documentation:** `README.md`, `JCLi_Scripting_Guide.md`  
- **Open an Issue:** [GitHub Issues](https://github.com/your-repo/issues)  
- **Contribute Fixes:** See `CONTRIBUTING.md` for details.

