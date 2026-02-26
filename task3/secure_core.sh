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

#############################################################################
# LOGGING FUNCTION
#############################################################################
log_event() {
    local student_id="$1"
    local filename="$2"
    local status="$3"
    local details="$4"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "${timestamp} | STUDENT=${student_id} | FILE=${filename} | STATUS=${status} | ${details}" >> "$SUBMISSION_LOG"
}

#############################################################################
# INITIALIZE SYSTEM
#############################################################################
initialize_system() {
    # Create necessary directories and files if they don't exist
    if [ ! -d "$SUBMISSION_DIR" ]; then
        mkdir -p "$SUBMISSION_DIR"
    fi
    
    if [ ! -f "$SUBMISSION_LOG" ]; then
        touch "$SUBMISSION_LOG"
        log_event "SYSTEM" "INIT" "INITIALIZED" "Exam submission system started"
    fi
    
    if [ ! -f "$SUBMISSIONS_INDEX" ]; then
        touch "$SUBMISSIONS_INDEX"
    fi
}

############################################################################
# VALIDATE FILE EXTENSION
#############################################################################
validate_file_extension() {
    local filename="$1"
    local extension="${filename##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    if [ "$extension" = "pdf" ] || [ "$extension" = "docx" ]; then
        return 0
    else
        return 1
    fi
}

#############################################################################
# VALIDATE FILE SIZE
#############################################################################
validate_file_size() {
    local filepath="$1"
    
    # Use stat if available, otherwise fallback to wc
    if command -v stat &> /dev/null; then
        # Try GNU stat format first
        local filesize=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null)
    else
        # Fallback to wc -c
        local filesize=$(wc -c < "$filepath")
    fi
    
    if [ "$filesize" -le "$MAX_FILE_SIZE" ]; then
        echo "$filesize"
        return 0
    else
        echo "$filesize"
        return 1
    fi
}
