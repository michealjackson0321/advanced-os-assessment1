#!/usr/bin/env python3
"""
University High Performance Computing Job Scheduler
This script manages computational job requests and processes them using
Round Robin or Priority Scheduling algorithms.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# File paths for persistent storage
JOB_QUEUE_FILE = "job_queue.txt"
COMPLETED_JOBS_FILE = "completed_jobs.txt"
SCHEDULER_LOG_FILE = "scheduler_log.txt"

def log_event(message: str) -> None:
    """Log scheduling events with timestamp to the scheduler log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SCHEDULER_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")


def load_jobs() -> List[Dict]:
    """Load pending jobs from the job queue file."""
    jobs = []
    
    if not os.path.exists(JOB_QUEUE_FILE):
        return jobs
    
    try:
        with open(JOB_QUEUE_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split("|")
                if len(parts) != 4:
                    print(f"Warning: Skipping malformed entry on line {line_num}")
                    continue
                
                student_id, job_name, exec_time_str, priority_str = parts
                
                try:
                    exec_time = int(exec_time_str)
                    priority = int(priority_str)
                    
                    jobs.append({
                        "student_id": student_id,
                        "job_name": job_name,
                        "exec_time": exec_time,
                        "priority": priority
                    })
                except ValueError:
                    print(f"Warning: Invalid numeric values on line {line_num}")
                    continue
    
    except Exception as e:
        print(f"Error loading jobs: {e}")
    
    return jobs
