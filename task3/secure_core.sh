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

#############################################################################
# CHECK FOR DUPLICATE FILENAME
#############################################################################
check_duplicate_filename() {
    local student_id="$1"
    local filename="$2"
    
    # Check if this student has already submitted a file with this name
    if grep -q "^${student_id}|${filename}|" "$SUBMISSIONS_INDEX" 2>/dev/null; then
        return 0  # Duplicate found
    else
        return 1  # Not a duplicate
    fi
}

#############################################################################
# CHECK FOR DUPLICATE CONTENT (SHA-256 HASH)
#############################################################################
check_duplicate_content() {
    local filepath="$1"
    
    # Calculate SHA-256 hash
    local hash=$(sha256sum "$filepath" | awk '{print $1}')
    
    # Check if this hash already exists in the index
    if grep -q "|${hash}|" "$SUBMISSIONS_INDEX" 2>/dev/null; then
        echo "$hash"
        return 0  # Duplicate content found
    else
        echo "$hash"
        return 1  # Not a duplicate
    fi
}

#############################################################################
# SUBMIT ASSIGNMENT
#############################################################################
submit_assignment() {
    echo ""
    echo "============================================================"
    echo "           EXAMINATION ASSIGNMENT SUBMISSION"
    echo "============================================================"
    echo ""
    
    # Get student ID
    read -p "Enter your Student ID: " student_id
    student_id=$(echo "$student_id" | xargs)  # Trim whitespace
    
    if [ -z "$student_id" ]; then
        echo -e "${RED}Error: Student ID cannot be empty.${NC}"
        log_event "" "NONE" "REJECTED" "Empty student ID"
        return
    fi
    
    # Get filename/path
    read -p "Enter the full path to your assignment file: " filepath
    filepath=$(echo "$filepath" | xargs)  # Trim whitespace
    
    if [ -z "$filepath" ]; then
        echo -e "${RED}Error: File path cannot be empty.${NC}"
        log_event "$student_id" "NONE" "REJECTED" "Empty file path"
        return
    fi
    
    # Check if file exists
    if [ ! -f "$filepath" ]; then
        echo -e "${RED}Error: File does not exist: $filepath${NC}"
        log_event "$student_id" "$filepath" "REJECTED" "File not found"
        return
    fi
    
    # Extract filename from path
    local filename=$(basename "$filepath")
    
    echo ""
    echo "Validating file: $filename"
    echo "------------------------------------------------------------"
    
    # Step 1: Validate file extension
    echo -n "Checking file format... "
    if ! validate_file_extension "$filename"; then
        echo -e "${RED}FAILED${NC}"
        echo -e "${RED}Error: Invalid file format. Only PDF and DOCX files are accepted.${NC}"
        log_event "$student_id" "$filename" "REJECTED" "Invalid format (only .pdf and .docx allowed)"
        return
    fi
    echo -e "${GREEN}OK${NC}"
    
    # Step 2: Validate file size
    echo -n "Checking file size... "
    local filesize=$(validate_file_size "$filepath")
    local validate_result=$?
    
    if [ $validate_result -ne 0 ]; then
        local size_mb=$(echo "scale=2; $filesize / 1048576" | bc)
        echo -e "${RED}FAILED${NC}"
        echo -e "${RED}Error: File size exceeds 5MB limit (${size_mb}MB).${NC}"
        log_event "$student_id" "$filename" "REJECTED" "File too large (${size_mb}MB, max 5MB)"
        return
    fi
    
    local size_kb=$(echo "scale=2; $filesize / 1024" | bc)
    echo -e "${GREEN}OK (${size_kb}KB)${NC}"
    
    # Step 3: Check for duplicate filename
    echo -n "Checking for duplicate filename... "
    if check_duplicate_filename "$student_id" "$filename"; then
        echo -e "${RED}FAILED${NC}"
        echo -e "${RED}Error: You have already submitted a file with this name.${NC}"
        log_event "$student_id" "$filename" "REJECTED" "Duplicate filename"
        return
    fi
    echo -e "${GREEN}OK${NC}"
    
    # Step 4: Check for duplicate content
    echo -n "Checking for duplicate content... "
    local hash=$(check_duplicate_content "$filepath")
    local duplicate_result=$?
    
    if [ $duplicate_result -eq 0 ]; then
        echo -e "${RED}FAILED${NC}"
        echo -e "${RED}Error: This file content has already been submitted (possibly with a different name).${NC}"
        log_event "$student_id" "$filename" "REJECTED" "Duplicate content (SHA-256: ${hash})"
        return
    fi
    echo -e "${GREEN}OK${NC}"
    
    # All validations passed - copy file to submissions directory
    local dest_path="${SUBMISSION_DIR}/${student_id}_${filename}"
    
    if cp "$filepath" "$dest_path"; then
        # Add entry to submissions index
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "${student_id}|${filename}|${hash}|${timestamp}" >> "$SUBMISSIONS_INDEX"
        
        echo ""
        echo "============================================================"
        echo -e "${GREEN}✓ SUBMISSION SUCCESSFUL${NC}"
        echo "============================================================"
        echo "Student ID:  $student_id"
        echo "File:        $filename"
        echo "Size:        ${size_kb}KB"
        echo "Hash:        ${hash:0:16}..."
        echo "Timestamp:   $timestamp"
        echo "============================================================"
        
        log_event "$student_id" "$filename" "ACCEPTED" "File stored successfully (${size_kb}KB)"
    else
        echo -e "${RED}Error: Failed to copy file to submission directory.${NC}"
        log_event "$student_id" "$filename" "REJECTED" "File copy failed"
    fi
    
    echo ""
}