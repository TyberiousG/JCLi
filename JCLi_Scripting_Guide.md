
# 📜 JCLi Scripting Guide

Welcome to the **JCLi Scripting Guide**! This guide will help you understand how to create, submit, and manage JCLi scripts to control jobs on your Linux system.

---

## 🚀 Introduction to JCLi

**JCLi** (Job Control for Linux) is a job scheduling system inspired by IBM's Job Control Language (JCL). It allows you to define jobs, specify execution steps, set priorities, and manage output.

---

## 📝 Basic Script Structure

A JCLi script consists of three main sections:

1. **JOB Statement** - Defines job details like priority, user, and class.
2. **EXEC Statement** - Specifies the program to execute with optional arguments.
3. **DD Statement** - Defines output handling (similar to SYSOUT in z/OS).

### ✅ Example Script

```jcl
//MYJOB   JOB CLASS=A,PRTY=5,USER=admin
//STEP1   EXEC PGM=/usr/bin/echo,ARGS='Hello, JCLi!'
//OUTPUT  DD SYSOUT=A
```

---

## 🔍 Script Breakdown

### 1️⃣ **JOB Statement**

```jcl
//MYJOB   JOB CLASS=A,PRTY=5,USER=admin
```

- `//MYJOB` → **Job Name** (max 8 characters recommended).
- `JOB` → Identifies the job declaration.
- `CLASS=A` → **Priority Class** (A, B, C, H).
- `PRTY=5` → **Priority Value** (1 = highest, 10 = lowest).
- `USER=admin` → User responsible for the job.

### 2️⃣ **EXEC Statement**

```jcl
//STEP1   EXEC PGM=/usr/bin/python3,ARGS='script.py --arg value'
```

- `//STEP1` → **Step Name** (each job can have multiple steps).
- `EXEC` → Command to execute a program.
- `PGM=` → Program path to execute.
- `ARGS=` → Arguments for the program.

### 3️⃣ **DD Statement (Output Handling)**

```jcl
//OUTPUT  DD SYSOUT=A
```

- `//OUTPUT` → Output Definition.
- `DD` → Data Definition.
- `SYSOUT=A` → Sends output to logs associated with Class A.

---

## 🚦 Priority Classes

| **Class** | **Description**                      |
|-----------|------------------------------------|
| A         | High Priority                      |
| B         | Medium Priority                    |
| C         | Low Priority                       |
| H         | **Hold** (Job remains on hold until manually released) |

---

## 📂 Example Scripts

### 1️⃣ **Simple Echo Job**

```jcl
//ECHOJOB  JOB CLASS=B,PRTY=4,USER=admin
//STEP1    EXEC PGM=/usr/bin/echo,ARGS='Hello from JCLi!'
//OUTPUT   DD SYSOUT=B
```

### 2️⃣ **Multiple Steps**

```jcl
//MULTISTEP JOB CLASS=A,PRTY=3,USER=root
//STEP1    EXEC PGM=/usr/bin/echo,ARGS='Step 1: Init'
//STEP2    EXEC PGM=/usr/bin/echo,ARGS='Step 2: Processing'
//STEP3    EXEC PGM=/usr/bin/echo,ARGS='Step 3: Complete'
//OUTPUT   DD SYSOUT=A
```

### 3️⃣ **Held Job (Class H)**

```jcl
//HOLDJOB  JOB CLASS=H,PRTY=5,USER=admin
//STEP1    EXEC PGM=/usr/bin/echo,ARGS='This job is held until released.'
//OUTPUT   DD SYSOUT=A
```

To release:
```bash
JCLi> QUEUE
Queue> RELEASE HOLDJOB
```

---

## 🚀 Submitting a JCLi Script

1. **Save the script:**
   ```bash
   nano my_job.jcli
   ```

2. **Submit the job:**
   ```bash
   JCLi> SUBMIT my_job.jcli
   ```

3. **Check job status:**
   ```bash
   JCLi> STATUS
   ```

4. **View logs:**
   ```bash
   cat logs/jobs/MYJOB_output.log
   ```

---

## ⚙️ Queue Commands

Within the **Queue Menu:**

- `R JOBNAME` → Restart a job
- `C JOBNAME` → Cancel a job
- `F JOBNAME` → Force a job to run immediately
- `RELEASE JOBNAME` → Release a held job
- `EXIT` → Return to the main menu

---

## 🚩 Troubleshooting

| **Error**                      | **Cause**                       | **Solution**                       |
|:-------------------------------|:--------------------------------|:-----------------------------------|
| `Validation Error: Missing JOB` | Missing `JOB` statement        | Add a proper `JOB` declaration.    |
| `Unknown command`              | Typo in the command            | Check for spelling mistakes.       |
| `Job not found`                | Invalid job name               | Verify job name exists in the queue. |
| `Job is held`                  | Class H job not released       | Use `RELEASE JOBNAME` to continue. |

---

## 🙌 Thanks for Using JCLi!

For more help, check out the full documentation or open an issue on GitHub if you're facing problems.

