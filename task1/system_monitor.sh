#!/bin/bash

# University Data Centre Process and Resource Management System
# This script provides system administration tools for process monitoring,
# disk management, and log control.

LOG_FILE="system_monitor_log.txt"

# Function to log actions with timestamps
log_action() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $message" >> "$LOG_FILE"
}

# Function to display current CPU and memory usage
show_cpu_memory() {
    echo ""
    echo "==== Current CPU and Memory Usage ===="
    echo ""
    
    # Display CPU information using top
    echo "CPU Usage:"
    top -b -n1 | head -5
    echo ""
    
    # Display memory information using free
    echo "Memory Usage:"
    free -h
    echo ""
    
    log_action "Viewed CPU and memory usage statistics"
}

# Function to list top 10 memory consuming processes
list_top_memory_processes() {
    echo ""
    echo "==== Top 10 Memory Consuming Processes ===="
    echo ""
    printf "%-8s %-10s %-6s %-6s %s\n" "PID" "USER" "CPU%" "MEM%" "COMMAND"
    echo "------------------------------------------------------------"
    ps aux --sort=-%mem | awk 'NR>1 {printf "%-8s %-10s %-6s %-6s %s\n", $2, $1, $3, $4, $11}' | head -10
    echo ""
    
    log_action "Listed top 10 memory consuming processes"
}

# Function to terminate a selected process with safeguards
terminate_process() {
    echo ""
    read -p "Enter PID of process to terminate: " pid
    
    # Validate PID is a number
    if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid PID. Please enter a numeric process ID."
        log_action "Invalid PID entered: $pid"
        return
    fi
    
    # Check if process exists
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "Error: No process found with PID $pid."
        log_action "Process termination failed: PID $pid does not exist"
        return
    fi
    
    # Get process information
    proc_name=$(ps -p "$pid" -o comm= 2>/dev/null)
    proc_user=$(ps -p "$pid" -o user= 2>/dev/null)
    
    # List of critical PIDs that should never be terminated
    critical_pids=(1)
    for cp in "${critical_pids[@]}"; do
        if [ "$pid" -eq "$cp" ]; then
            echo "Error: Cannot terminate critical system process (PID $pid)."
            echo "This is a protected process essential for system operation."
            log_action "BLOCKED: Attempted to terminate critical process PID $pid ($proc_name)"
            return
        fi
    done
    
    # List of critical process names that should never be terminated
    case "$proc_name" in
        init|systemd|kthreadd|rcu_sched|ksoftirqd|migration|watchdog|kworker)
            echo "Error: Cannot terminate critical system process '$proc_name'."
            echo "This process is essential for system operation."
            log_action "BLOCKED: Attempted to terminate critical process $proc_name (PID $pid)"
            return
            ;;
    esac
    
    # Display process details and request confirmation
    echo ""
    echo "Process Details:"
    echo "  PID: $pid"
    echo "  Name: $proc_name"
    echo "  User: $proc_user"
    echo ""
    
    read -p "Are you sure you want to terminate this process? (Y/N): " confirm
    
    case "$confirm" in
        [Yy]|[Yy][Ee][Ss])
            if kill "$pid" 2>/dev/null; then
                echo "Success: Process $pid ($proc_name) has been terminated."
                log_action "TERMINATED: Process PID $pid ($proc_name) by user"
            else
                echo "Error: Failed to terminate process $pid."
                echo "This may be due to insufficient permissions or the process already exited."
                log_action "FAILED: Could not terminate process PID $pid ($proc_name)"
            fi
            ;;
        [Nn]|[Nn][Oo])
            echo "Termination cancelled."
            log_action "CANCELLED: Termination of process PID $pid ($proc_name) cancelled by user"
            ;;
        *)
            echo "Invalid input. Termination cancelled."
            log_action "CANCELLED: Invalid confirmation input for PID $pid termination"
            ;;
    esac
    echo ""
}

# Function to inspect disk usage and archive large log files
inspect_disk_and_logs() {
    echo ""
    read -p "Enter directory path to inspect: " target_dir
    
    # Validate directory exists
    if [ ! -d "$target_dir" ]; then
        echo "Error: Directory '$target_dir' does not exist."
        log_action "Disk inspection failed: Directory $target_dir not found"
        return
    fi
    
    echo ""
    echo "==== Disk Usage for: $target_dir ===="
    du -sh "$target_dir" 2>/dev/null
    echo ""
    
    # Search for log files larger than 50MB
    echo "Searching for log files larger than 50MB..."
    mapfile -t large_logs < <(find "$target_dir" -type f -name "*.log" -size +50M 2>/dev/null)
    
    if [ "${#large_logs[@]}" -eq 0 ]; then
        echo "No log files larger than 50MB found in this directory."
        log_action "Disk inspection complete: No large log files in $target_dir"
        return
    fi
    
    echo ""
    echo "Found ${#large_logs[@]} large log file(s):"
    for logfile in "${large_logs[@]}"; do
        size=$(ls -lh "$logfile" | awk '{print $5}')
        echo "  - $logfile ($size)"
    done
    echo ""
    
    # Create ArchiveLogs directory if it doesn't exist
    archive_dir="$target_dir/ArchiveLogs"
    if [ ! -d "$archive_dir" ]; then
        mkdir -p "$archive_dir"
        echo "Created archive directory: $archive_dir"
        log_action "Created ArchiveLogs directory at $archive_dir"
    fi
    
    # Compress and archive large log files with timestamps
    timestamp=$(date '+%Y%m%d_%H%M%S')
    echo "Archiving large log files..."
    
    for logfile in "${large_logs[@]}"; do
        base_name=$(basename "$logfile")
        archive_name="${base_name%.log}_${timestamp}.log.gz"
        
        if gzip -c "$logfile" > "$archive_dir/$archive_name" 2>/dev/null; then
            echo "  Archived: $logfile -> $archive_dir/$archive_name"
            log_action "Archived log file: $logfile to $archive_dir/$archive_name"
        else
            echo "  Failed to archive: $logfile"
            log_action "Failed to archive log file: $logfile"
        fi
    done
    
    echo ""
    
    # Check if ArchiveLogs exceeds 1GB and display warning
    archive_size_bytes=$(du -sb "$archive_dir" 2>/dev/null | awk '{print $1}')
    
    if [ -n "$archive_size_bytes" ]; then
        one_gb=$((1024*1024*1024))
        
        if [ "$archive_size_bytes" -gt "$one_gb" ]; then
            archive_size_gb=$(echo "scale=2; $archive_size_bytes / $one_gb" | bc)
            echo "WARNING: ArchiveLogs directory exceeds 1GB!"
            echo "Current size: ${archive_size_gb}GB"
            echo "Consider cleaning up old archived logs to free disk space."
            log_action "WARNING: ArchiveLogs at $archive_dir exceeds 1GB (${archive_size_gb}GB)"
        else
            archive_size_mb=$(echo "scale=2; $archive_size_bytes / 1024 / 1024" | bc)
            echo "Archive directory size: ${archive_size_mb}MB"
        fi
    fi
    
    echo ""
}

# Function to handle graceful exit with confirmation
bye_exit() {
    echo ""
    read -p "Are you sure you want to exit? (Y/N): " confirm
    
    case "$confirm" in
        [Yy]|[Yy][Ee][Ss])
            echo ""
            echo "Bye"
            log_action "System monitor exited by user"
            exit 0
            ;;
        [Nn]|[Nn][Oo])
            echo "Exit cancelled. Returning to main menu."
            ;;
        *)
            echo "Invalid input. Exit cancelled."
            ;;
    esac
}

# Main menu loop
main_menu() {
    while true; do
        echo ""
        echo "========================================================="
        echo "  University Data Centre Process and Resource Management"
        echo "========================================================="
        echo ""
        echo "1) Display current CPU and memory usage"
        echo "2) List top ten memory consuming processes"
        echo "3) Terminate a process"
        echo "4) Disk inspection and log archiving"
        echo "5) Bye (exit)"
        echo ""
        read -p "Enter your choice [1-5]: " choice
        
        case "$choice" in
            1)
                show_cpu_memory
                ;;
            2)
                list_top_memory_processes
                ;;
            3)
                terminate_process
                ;;
            4)
                inspect_disk_and_logs
                ;;
            5)
                bye_exit
                ;;
            *)
                echo ""
                echo "Invalid option. Please select a number between 1 and 5."
                ;;
        esac
    done
}

# Initialize log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    log_action "System monitor initialized"
fi

# Start the main menu
main_menu
