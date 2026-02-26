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

def save_jobs(jobs: List[Dict]) -> None:
    """Save pending jobs to the job queue file."""
    try:
        with open(JOB_QUEUE_FILE, "w", encoding="utf-8") as f:
            for job in jobs:
                f.write(
                    f"{job['student_id']}|{job['job_name']}|"
                    f"{job['exec_time']}|{job['priority']}\n"
                )
    except Exception as e:
        print(f"Error saving jobs: {e}")


def append_completed_job(job: Dict, algorithm: str) -> None:
    """Append a completed job to the completed jobs file."""
    try:
        with open(COMPLETED_JOBS_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"{timestamp}|{job['student_id']}|{job['job_name']}|"
                f"{job['exec_time']}|{job['priority']}|{algorithm}\n"
            )
    except Exception as e:
        print(f"Error recording completed job: {e}")


def view_pending_jobs() -> None:
    """Display all pending jobs in the queue."""
    jobs = load_jobs()
    
    if not jobs:
        print("\nNo pending jobs in the queue.\n")
        return
    
    print("\n" + "=" * 70)
    print("                         PENDING JOBS")
    print("=" * 70)
    print(f"{'#':<4} {'Student ID':<12} {'Job Name':<20} {'Time(s)':<8} {'Priority':<8}")
    print("-" * 70)
    
    for idx, job in enumerate(jobs, start=1):
        print(
            f"{idx:<4} {job['student_id']:<12} {job['job_name']:<20} "
            f"{job['exec_time']:<8} {job['priority']:<8}"
        )
    
    print("=" * 70 + "\n")
    log_event(f"Viewed {len(jobs)} pending job(s)")


def submit_job() -> None:
    """Submit a new job request to the queue."""
    print("\n" + "=" * 70)
    print("                       SUBMIT NEW JOB")
    print("=" * 70)
    
    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("Error: Student ID cannot be empty.")
        return
    
    job_name = input("Enter job name: ").strip()
    if not job_name:
        print("Error: Job name cannot be empty.")
        return
    
    # Validate execution time
    try:
        exec_time_input = input("Enter estimated execution time (seconds): ").strip()
        exec_time = int(exec_time_input)
        
        if exec_time <= 0:
            print("Error: Execution time must be a positive integer.")
            return
    except ValueError:
        print("Error: Invalid execution time. Please enter a whole number.")
        return
    
    # Validate priority
    try:
        priority_input = input("Enter priority (1-10, where 10 is highest): ").strip()
        priority = int(priority_input)
        
        if priority < 1 or priority > 10:
            print("Error: Priority must be between 1 and 10.")
            return
    except ValueError:
        print("Error: Invalid priority. Please enter a number between 1 and 10.")
        return
    
    # Append job to queue file
    try:
        with open(JOB_QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{student_id}|{job_name}|{exec_time}|{priority}\n")
        
        print("\n✓ Job submitted successfully!")
        print(f"  Student ID: {student_id}")
        print(f"  Job Name: {job_name}")
        print(f"  Execution Time: {exec_time} seconds")
        print(f"  Priority: {priority}\n")
        
        log_event(
            f"JOB_SUBMISSION | Student={student_id} | Job={job_name} | "
            f"ExecTime={exec_time}s | Priority={priority}"
        )
    
    except Exception as e:
        print(f"Error: Failed to submit job: {e}")