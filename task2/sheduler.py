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


def round_robin_scheduling() -> None:
    """Process jobs using Round Robin scheduling with 5-second time quantum."""
    jobs = load_jobs()
    
    if not jobs:
        print("\nNo jobs to schedule.\n")
        return
    
    TIME_QUANTUM = 5
    print(f"\n{'=' * 70}")
    print(f"       ROUND ROBIN SCHEDULING (Time Quantum = {TIME_QUANTUM} seconds)")
    print("=" * 70 + "\n")
    
    # Initialize remaining time for each job
    for job in jobs:
        job["remaining"] = job["exec_time"]
    
    execution_log = []
    cycle = 1
    
    # Process jobs in round-robin fashion
    while any(job["remaining"] > 0 for job in jobs):
        print(f"--- Cycle {cycle} ---")
        
        for job in jobs:
            if job["remaining"] <= 0:
                continue
            
            # Determine how much time this job gets in this cycle
            run_time = min(TIME_QUANTUM, job["remaining"])
            job["remaining"] -= run_time
            
            print(
                f"  Running: {job['job_name']} (Student: {job['student_id']}) "
                f"for {run_time}s | Remaining: {job['remaining']}s"
            )
            
            execution_log.append({
                "student_id": job["student_id"],
                "job_name": job["job_name"],
                "run_time": run_time,
                "remaining": job["remaining"]
            })
            
            log_event(
                f"RR_EXECUTION | Student={job['student_id']} | Job={job['job_name']} | "
                f"RunTime={run_time}s | Remaining={job['remaining']}s"
            )
            
            # If job completed, record it
            if job["remaining"] == 0:
                append_completed_job(job, "RoundRobin")
                print(f"    ✓ Job '{job['job_name']}' COMPLETED")
        
        cycle += 1
        print()
    
    # Clear the job queue
    save_jobs([])
    
    print("=" * 70)
    print("All jobs completed using Round Robin scheduling.")
    print("=" * 70 + "\n")
    
    log_event(f"Round Robin scheduling completed: {len(jobs)} job(s) processed")

def priority_scheduling() -> None:
    """Process jobs using Priority scheduling (highest priority first)."""
    jobs = load_jobs()
    
    if not jobs:
        print("\nNo jobs to schedule.\n")
        return
    
    print(f"\n{'=' * 70}")
    print("          PRIORITY SCHEDULING (Highest Priority First)")
    print("=" * 70 + "\n")
    
    # Sort jobs by priority in descending order (10 is highest priority)
    sorted_jobs = sorted(jobs, key=lambda j: j["priority"], reverse=True)
    
    print(f"{'#':<4} {'Student ID':<12} {'Job Name':<20} {'Time(s)':<8} {'Priority':<8}")
    print("-" * 70)
    
    for idx, job in enumerate(sorted_jobs, start=1):
        print(
            f"{idx:<4} {job['student_id']:<12} {job['job_name']:<20} "
            f"{job['exec_time']:<8} {job['priority']:<8}"
        )
        
        log_event(
            f"PRIORITY_EXECUTION | Student={job['student_id']} | Job={job['job_name']} | "
            f"ExecTime={job['exec_time']}s | Priority={job['priority']}"
        )
        
        # Record completed job
        append_completed_job(job, "Priority")
    
    # Clear the job queue
    save_jobs([])
    
    print("\n" + "=" * 70)
    print("All jobs completed using Priority scheduling.")
    print("=" * 70 + "\n")
    
    log_event(f"Priority scheduling completed: {len(sorted_jobs)} job(s) processed")

def view_completed_jobs() -> None:
    """Display all completed jobs."""
    if not os.path.exists(COMPLETED_JOBS_FILE):
        print("\nNo completed jobs recorded yet.\n")
        return
    
    try:
        with open(COMPLETED_JOBS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            print("\nNo completed jobs recorded yet.\n")
            return
        
        print("\n" + "=" * 90)
        print("                              COMPLETED JOBS")
        print("=" * 90)
        print(
            f"{'Timestamp':<20} {'Student ID':<12} {'Job Name':<20} "
            f"{'Time(s)':<8} {'Priority':<8} {'Algorithm':<12}"
        )
        print("-" * 90)
        
        for line in lines:
            parts = line.split("|")
            if len(parts) == 6:
                timestamp, student_id, job_name, exec_time, priority, algorithm = parts
                print(
                    f"{timestamp:<20} {student_id:<12} {job_name:<20} "
                    f"{exec_time:<8} {priority:<8} {algorithm:<12}"
                )
        
        print("=" * 90 + "\n")
        log_event(f"Viewed {len(lines)} completed job(s)")
    
    except Exception as e:
        print(f"Error reading completed jobs: {e}")

def process_job_queue() -> None:
    """Prompt user to select scheduling algorithm and process the queue."""
    jobs = load_jobs()
    
    if not jobs:
        print("\nNo jobs in queue to process.\n")
        return
    
    print("\n" + "=" * 70)
    print("                    SELECT SCHEDULING ALGORITHM")
    print("=" * 70)
    print("1) Round Robin (Time Quantum = 5 seconds)")
    print("2) Priority Scheduling (Highest priority first)")
    print("")
    
    choice = input("Enter your choice [1-2]: ").strip()
    
    if choice == "1":
        round_robin_scheduling()
    elif choice == "2":
        priority_scheduling()
    else:
        print("\nInvalid choice. Returning to main menu.\n")


def bye_exit() -> None:
    """Handle graceful exit with confirmation."""
    print("")
    confirm = input("Are you sure you want to exit? (Y/N): ").strip().upper()
    
    if confirm in ["Y", "YES"]:
        print("\nBye")
        log_event("Job scheduler exited by user")
        sys.exit(0)
    elif confirm in ["N", "NO"]:
        print("Exit cancelled. Returning to main menu.\n")
    else:
        print("Invalid input. Exit cancelled.\n")

def main_menu() -> None:
    """Display main menu and handle user interaction."""
    while True:
        print("=" * 70)
        print("    University High Performance Computing Job Scheduler")
        print("=" * 70)
        print("")
        print("1) View pending jobs")
        print("2) Submit a job request")
        print("3) Process job queue (Round Robin or Priority)")
        print("4) View completed jobs")
        print("5) Bye (exit)")
        print("")
        
        choice = input("Enter your choice [1-5]: ").strip()
        
        if choice == "1":
            view_pending_jobs()
        elif choice == "2":
            submit_job()
        elif choice == "3":
            process_job_queue()
        elif choice == "4":
            view_completed_jobs()
        elif choice == "5":
            bye_exit()
        else:
            print("\nInvalid option. Please choose a number between 1 and 5.\n")


if __name__ == "__main__":
    # Initialize log file if it doesn't exist
    if not os.path.exists(SCHEDULER_LOG_FILE):
        log_event("Job scheduler initialized")
    
    # Start the main menu
    main_menu()
