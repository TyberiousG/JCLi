# JCLi

📜 Overview
JCLi is an open-source job control system designed to manage batch jobs on Linux systems. Inspired by IBM's Job Control Language (JCL), JCLi provides a flexible, file-driven approach to job submission, execution, and monitoring. It’s ideal for automation enthusiasts, sysadmins, and developers looking to experiment with lightweight job scheduling.

🚀 Features
✅ File-Based Job Submission (JCL-style scripts)
✅ Priority-Based Job Scheduling (like z/OS priority classes)
✅ Modular Architecture (Interpreter, Daemon, Executor)
✅ Job Status Tracking & Logging (output and event logs)
✅ Simple Command-Line Interface (CLI)
✅ Customizable & Extensible for Advanced Use Cases

📂 Project Structure
JCLi/
├── ControlInterface/   # CLI and command handling
├── Daemon/             # Job scheduler and lifecycle manager
├── Executor/           # Executes shell scripts, binaries, and containers
├── Interpreter/        # Parses and validates JCLi scripts
├── Logging/            # Job and system event logging
└── logs/               # Output logs and job status tracking
⚡ Getting Started
1️⃣ Prerequisites
OS: Linux
Python: 3.6+
Dependencies: None (pure Python)
2️⃣ Installation
git clone https://github.com/yourusername/JCLi.git
cd JCLi
python -m ControlInterface.cli
📝 JCLi Script Example

//MYJOB   JOB CLASS=A,PRTY=5,USER=admin
//STEP1   EXEC PGM=/usr/bin/echo,ARGS='Hello from JCLi!'
//OUTPUT  DD SYSOUT=A

JOB - Defines the job, user, and priority.
EXEC - Executes the specified program with arguments.
DD - Handles output logging.

🚀 How to Submit a Job

Save your script:
nano my_first_job.jcli

Run the JCLi CLI:
python -m ControlInterface.cli

Submit the job:
JCLi> SUBMIT my_first_job.jcli

Check job status:
JCLi> STATUS

View logs:
cat logs/jobs/MYJOB_output.log

⚙️ Command Reference

START  -	Starts the JCLi Daemon
STOP   -	Stops the JCLi Daemon
SUBMIT - <file>	Submits a JCLi script for execution
STATUS -	Shows the status of all submitted jobs
HELP   -	Displays help information
EXIT   -	Exits the JCLi CLI

📊 Logging
Job Output: logs/jobs/<job_name>_output.log
Job Status: logs/jobs/<job_name>_status.log
System Events: logs/system/events.log
Error Logs: logs/system/errors.log


🧩 Contributing
We welcome contributions! Whether it's fixing bugs, adding new features, or improving documentation, your help is appreciated.

Fork the repo
Create a new branch: git checkout -b feature/new-feature
Commit your changes: git commit -m 'Add new feature'
Push to the branch: git push origin feature/new-feature
Open a Pull Request

📜 License
JCLi is licensed under the GNU General Public License (GPL).
Feel free to use, modify, and distribute under the terms of the GPL.

🙌 Acknowledgments
Inspired by IBM’s Job Control Language (JCL)
Built with Python, Linux, and a lot of 💡
