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

