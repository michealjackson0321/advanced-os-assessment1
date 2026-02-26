#!/usr/bin/env python3
"""
University Secure Examination System - Login Monitor
Handles student/admin login, failed attempt tracking, and account lockout.
Called by secure_core.sh with the submission log file path as argument.
"""

import sys
import os
import json
import hashlib
from datetime import datetime

# File paths
ACCOUNTS_FILE = "accounts.json"
LOGIN_LOG_FILE = "login_attempts.txt"
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 30


def log_login_event(username: str, status: str, details: str) -> None:
    """Log login events with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGIN_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | USER={username} | STATUS={status} | {details}\n")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_accounts() -> dict:
    """Load accounts from the accounts file."""
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_accounts(accounts: dict) -> None:
    """Save accounts to the accounts file."""
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)


def is_account_locked(account: dict) -> bool:
    """Check if an account is currently locked out."""
    if account.get("failed_attempts", 0) >= MAX_FAILED_ATTEMPTS:
        lockout_time_str = account.get("lockout_time")
        if lockout_time_str:
            lockout_time = datetime.strptime(lockout_time_str, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - lockout_time).total_seconds() / 60
            if elapsed < LOCKOUT_DURATION_MINUTES:
                remaining = int(LOCKOUT_DURATION_MINUTES - elapsed)
                return True, remaining
            else:
                # Lockout expired, reset
                return False, 0
    return False, 0


def get_lockout_status(account: dict):
    """Return (is_locked: bool, minutes_remaining: int)."""
    if account.get("failed_attempts", 0) >= MAX_FAILED_ATTEMPTS:
        lockout_time_str = account.get("lockout_time")
        if lockout_time_str:
            lockout_time = datetime.strptime(lockout_time_str, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - lockout_time).total_seconds() / 60
            if elapsed < LOCKOUT_DURATION_MINUTES:
                remaining = int(LOCKOUT_DURATION_MINUTES - elapsed)
                return True, remaining
            else:
                return False, 0
    return False, 0


def create_account(accounts: dict) -> None:
    """Create a new student or admin account."""
    print("\n  --- Create New Account ---")
    username = input("  Enter username (Student ID or admin name): ").strip()

    if not username:
        print("  Error: Username cannot be empty.")
        return

    if username in accounts:
        print(f"  Error: Account '{username}' already exists.")
        return

    role = input("  Role (student/admin) [default: student]: ").strip().lower()
    if role not in ("student", "admin"):
        role = "student"

    password = input("  Set password: ").strip()
    if not password:
        print("  Error: Password cannot be empty.")
        return

    confirm = input("  Confirm password: ").strip()
    if password != confirm:
        print("  Error: Passwords do not match.")
        return

    accounts[username] = {
        "role": role,
        "password_hash": hash_password(password),
        "failed_attempts": 0,
        "lockout_time": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }

    save_accounts(accounts)
    print(f"\n  Account '{username}' ({role}) created successfully.")
    log_login_event(username, "ACCOUNT_CREATED", f"New {role} account registered")


def login(accounts: dict) -> None:
    """Authenticate a user and handle lockout logic."""
    print("\n  --- Login ---")
    username = input("  Username: ").strip()

    if not username:
        print("  Error: Username cannot be empty.")
        return

    if username not in accounts:
        print("  Error: Account not found.")
        log_login_event(username, "FAILED", "Account not found")
        return

    account = accounts[username]

    # Check lockout
    locked, remaining = get_lockout_status(account)
    if locked:
        print(f"\n  Account is LOCKED due to too many failed attempts.")
        print(f"  Try again in {remaining} minute(s).")
        log_login_event(username, "BLOCKED", f"Account locked, {remaining} min remaining")
        return

    # Reset expired lockout
    if not locked and account.get("failed_attempts", 0) >= MAX_FAILED_ATTEMPTS:
        account["failed_attempts"] = 0
        account["lockout_time"] = None

    password = input("  Password: ").strip()
    entered_hash = hash_password(password)

    if entered_hash == account["password_hash"]:
        account["failed_attempts"] = 0
        account["lockout_time"] = None
        account["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_accounts(accounts)

        print(f"\n  Login successful! Welcome, {username} ({account['role']}).")
        print(f"  Last login: {account.get('last_login', 'First login')}")
        log_login_event(username, "SUCCESS", f"Successful login as {account['role']}")
    else:
        account["failed_attempts"] = account.get("failed_attempts", 0) + 1
        attempts_left = MAX_FAILED_ATTEMPTS - account["failed_attempts"]

        if account["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            account["lockout_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_accounts(accounts)
            print(f"\n  Incorrect password. Account is now LOCKED for {LOCKOUT_DURATION_MINUTES} minutes.")
            log_login_event(username, "LOCKED", f"Account locked after {MAX_FAILED_ATTEMPTS} failed attempts")
        else:
            save_accounts(accounts)
            print(f"\n  Incorrect password. {attempts_left} attempt(s) remaining before lockout.")
            log_login_event(username, "FAILED", f"Wrong password, {attempts_left} attempts left")


def view_login_history(log_file: str) -> None:
    """Display recent login attempts from the login log."""
    print("\n  --- Login Attempt History ---")

    if not os.path.exists(LOGIN_LOG_FILE):
        print("  No login history found.")
        return

    try:
        with open(LOGIN_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print("  No login history found.")
            return

        print(f"\n  {'TIMESTAMP':<22} {'USER':<15} {'STATUS':<15} DETAILS")
        print("  " + "-" * 70)

        for line in lines[-20:]:  # Show last 20 entries
            parts = line.strip().split(" | ")
            if len(parts) >= 3:
                timestamp = parts[0] if len(parts) > 0 else "N/A"
                user = parts[1].replace("USER=", "") if len(parts) > 1 else "N/A"
                status = parts[2].replace("STATUS=", "") if len(parts) > 2 else "N/A"
                details = parts[3] if len(parts) > 3 else ""
                print(f"  {timestamp:<22} {user:<15} {status:<15} {details}")
    except IOError:
        print("  Error reading login history.")


def view_all_accounts(accounts: dict) -> None:
    """Display all registered accounts and their status."""
    print("\n  --- Registered Accounts ---")

    if not accounts:
        print("  No accounts registered yet.")
        return

    print(f"\n  {'USERNAME':<20} {'ROLE':<10} {'STATUS':<12} {'FAILED':<8} LAST LOGIN")
    print("  " + "-" * 75)

    for username, info in accounts.items():
        locked, _ = get_lockout_status(info)
        status = "LOCKED" if locked else "ACTIVE"
        failed = info.get("failed_attempts", 0)
        last_login = info.get("last_login") or "Never"
        role = info.get("role", "student")
        print(f"  {username:<20} {role:<10} {status:<12} {failed:<8} {last_login}")


def unlock_account(accounts: dict) -> None:
    """Manually unlock a locked account."""
    print("\n  --- Unlock Account ---")
    username = input("  Enter username to unlock: ").strip()

    if username not in accounts:
        print(f"  Error: Account '{username}' not found.")
        return

    accounts[username]["failed_attempts"] = 0
    accounts[username]["lockout_time"] = None
    save_accounts(accounts)
    print(f"  Account '{username}' has been unlocked successfully.")
    log_login_event(username, "UNLOCKED", "Account manually unlocked by admin")


def view_submission_log(log_file: str) -> None:
    """Display recent entries from the submission log."""
    print("\n  --- Submission Activity Log ---")

    if not os.path.exists(log_file):
        print(f"  Log file not found: {log_file}")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print("  No activity recorded yet.")
            return

        print(f"\n  Showing last 15 entries from: {log_file}")
        print("  " + "-" * 80)
        for line in lines[-15:]:
            print(f"  {line.strip()}")
    except IOError:
        print("  Error reading submission log.")


def main_menu(log_file: str) -> None:
    """Display the login monitor main menu."""
    accounts = load_accounts()

    while True:
        print("\n  ============================================================")
        print("         LOGIN MONITOR & ACCOUNT MANAGEMENT")
        print("  ============================================================")
        print("  1. Login")
        print("  2. Create Account")
        print("  3. View Login History")
        print("  4. View All Accounts")
        print("  5. Unlock an Account")
        print("  6. View Submission Activity Log")
        print("  7. Back to Main Menu")
        print("  ============================================================")

        choice = input("  Enter your choice [1-7]: ").strip()

        if choice == "1":
            accounts = load_accounts()
            login(accounts)
        elif choice == "2":
            accounts = load_accounts()
            create_account(accounts)
        elif choice == "3":
            view_login_history(log_file)
        elif choice == "4":
            accounts = load_accounts()
            view_all_accounts(accounts)
        elif choice == "5":
            accounts = load_accounts()
            unlock_account(accounts)
        elif choice == "6":
            view_submission_log(log_file)
        elif choice == "7":
            print("\n  Returning to main menu...")
            break
        else:
            print("\n  Invalid choice. Please select a number between 1 and 7.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    # Receive submission log file path from secure_core.sh
    log_file = sys.argv[1] if len(sys.argv) > 1 else "submission_log.txt"
    main_menu(log_file)
