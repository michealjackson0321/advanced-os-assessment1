#!/bin/bash

#############################################################################
# TASK 3: SECURE EXAMINATION SUBMISSION AND ACCESS CONTROL SYSTEM
# This script implements a secure file submission system with:
# - File validation (PDF/DOCX only, 5MB limit)
# - Duplicate detection (filename and content hash)
# - Menu-driven interface with input validation
# - Integration with login monitoring and account lockout
# - Comprehensive logging system
#############################################################################

# Configuration
SUBMISSION_DIR="Submissions"
SUBMISSION_LOG="submission_log.txt"
SUBMISSIONS_INDEX="submissions_index.txt"
LOGIN_MONITOR_SCRIPT="login_monitor.py"
MAX_FILE_SIZE=$((5 * 1024 * 1024))  # 5MB in bytes

# Colors for better visibility (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

