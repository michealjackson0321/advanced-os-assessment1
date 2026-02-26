# Advanced Operating Systems – Assessment 1

A collection of three system administration and operating systems tools built for a university environment. Each task demonstrates core OS concepts including process management, CPU scheduling, file security, and access control.

---

## Project Structure

```
advanced-os-assessment1/
├── task1/
│   └── system_monitor.sh          # Process & resource monitor (Bash)
├── task2/
│   └── sheduler.py                # HPC Job Scheduler (Python)
├── task3/
│   ├── secure_core.sh             # Secure file submission system (Bash)
│   └── login_monitor.py           # Login & account management (Python)
├── docs/
└── README.md
```

---

## Requirements

### All Tasks
| Requirement | Version | Notes |
|---|---|---|
| Bash | Any | Git Bash (Windows) or native (Linux/macOS) |
| Python | 3.8+ | Required for Task 2 and Task 3 |

### Windows – Python Detection
The scripts automatically detect Python in this order:
1. `py` (Windows Python Launcher – recommended)
2. `python3`
3. `python`

Verify your installation:
```powershell
py --version
```

### Linux / macOS
All features work natively. Install dependencies if missing:
```bash
sudo apt install python3 coreutils procps   # Debian/Ubuntu
```

> **Note:** Task 1 uses Linux-specific commands (`top`, `free`, `ps --sort`). On Windows Git Bash, menu options 1 and 2 will report errors. Use WSL for full functionality on Windows.

---

## Task 1 – University Data Centre Process & Resource Monitor

**File:** `task1/system_monitor.sh`

A Bash-based interactive tool for monitoring system resources and managing processes.

### Features
- Display live CPU and memory usage
- List top 10 memory-consuming processes
- Safely terminate a process with PID validation and safeguards against critical system processes
- Inspect disk usage of a directory and archive log files larger than 50 MB into a compressed `ArchiveLogs/` folder
- Warns if the archive directory exceeds 1 GB

### How to Run

**Windows (Git Bash):**
```bash
bash task1/system_monitor.sh
```

**Linux / macOS:**
```bash
bash task1/system_monitor.sh
# or make it executable first:
chmod +x task1/system_monitor.sh
./task1/system_monitor.sh
```

### Menu Options
```
1) Display current CPU and memory usage
2) List top ten memory consuming processes
3) Terminate a process
4) Disk inspection and log archiving
5) Bye (exit)
```

### Log Files Created
| File | Location | Description |
|---|---|---|
| `system_monitor_log.txt` | Working directory | Timestamped record of all actions performed |

---

## Task 2 – University HPC Job Scheduler

**File:** `task2/sheduler.py`

A Python-based interactive job scheduler supporting two CPU scheduling algorithms.

### Features
- Submit computational jobs with student ID, name, execution time, and priority (1–10)
- View all pending jobs in the queue
- Process the queue using:
  - **Round Robin** – 5-second time quantum, cycles through all jobs fairly
  - **Priority Scheduling** – Executes jobs in descending priority order (10 = highest)
- View completed jobs with timestamps and algorithm used
- Persistent storage – queue survives between sessions

### How to Run

**Windows:**
```powershell
python task2\sheduler.py
# or
py task2\sheduler.py
```

**Linux / macOS:**
```bash
python3 task2/sheduler.py
```

### Menu Options
```
1) View pending jobs
2) Submit a job request
3) Process job queue (Round Robin or Priority)
4) View completed jobs
5) Bye (exit)
```

### Log Files Created
| File | Location | Description |
|---|---|---|
| `scheduler_log.txt` | Working directory | Event log of all submissions and scheduling runs |
| `job_queue.txt` | Working directory | Persistent queue of pending jobs |
| `completed_jobs.txt` | Working directory | Record of all completed jobs with algorithm used |

---

## Task 3 – Secure Examination Submission & Access Control System

**Files:** `task3/secure_core.sh` + `task3/login_monitor.py`

A Bash + Python system for securely submitting exam assignments with file validation, duplicate detection, and account-based access control.

### Features

**secure_core.sh**
- Submit assignment files (PDF and DOCX only, max 5 MB)
- Validates file extension, file size, duplicate filename per student, and duplicate file content (SHA-256 hash)
- View your own submissions by student ID
- Admin view of all submissions
- Integrates with `login_monitor.py` for login and account management

**login_monitor.py**
- Create student or admin accounts with hashed passwords (SHA-256)
- Login with failed attempt tracking
- **Account lockout** after 3 failed attempts for 30 minutes
- Manually unlock locked accounts
- View login attempt history
- View submission activity log

### How to Run

**Windows (Git Bash):**
```bash
bash task3/secure_core.sh
```

**Linux / macOS:**
```bash
bash task3/secure_core.sh
```

### Menu Options
```
1) Submit Assignment
2) View My Submissions
3) List All Submissions (Admin)
4) Login / Account Management
5) Exit (Bye)
```

### Accepted File Types
| Type | Extension | Max Size |
|---|---|---|
| PDF Document | `.pdf` | 5 MB |
| Word Document | `.docx` | 5 MB |

### Log Files Created
| File | Location | Description |
|---|---|---|
| `submission_log.txt` | Working directory | Timestamped record of all submission attempts (accepted and rejected) |
| `submissions_index.txt` | Working directory | Index of accepted submissions with SHA-256 hashes |
| `login_attempts.txt` | Working directory | Record of all login events and account changes |
| `accounts.json` | Working directory | Stored user accounts (hashed passwords, roles, lockout status) |
| `Submissions/` | Working directory | Directory where accepted assignment files are stored |

---

## Running from the Correct Directory

All scripts write log files to the **current working directory** when the script is executed. It is recommended to run all scripts from the project root:

```bash
# From: advanced-os-assessment1/
bash task1/system_monitor.sh
python task2/sheduler.py
bash task3/secure_core.sh
```

This keeps all generated files (logs, queues, submissions) together in one place.

---

## Summary of All Generated Files

| File | Created By | Purpose |
|---|---|---|
| `system_monitor_log.txt` | Task 1 | System monitor action log |
| `scheduler_log.txt` | Task 2 | Scheduler event log |
| `job_queue.txt` | Task 2 | Pending job queue (persistent) |
| `completed_jobs.txt` | Task 2 | Completed job history |
| `submission_log.txt` | Task 3 | Submission attempt log |
| `submissions_index.txt` | Task 3 | Accepted submissions index |
| `login_attempts.txt` | Task 3 | Login event log |
| `accounts.json` | Task 3 | User account store |
| `Submissions/` | Task 3 | Stored submitted files |