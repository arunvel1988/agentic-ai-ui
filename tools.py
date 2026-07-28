"""
tools.py
---------
All tools available to the AI Agent.
"""

from datetime import datetime
import os
import math
import subprocess
import psutil


# ==========================================================
# Time Tools
# ==========================================================

def get_current_time():
    """Return current system time."""
    return datetime.now().strftime("%I:%M:%S %p")


def get_current_date():
    """Return current date."""
    return datetime.now().strftime("%Y-%m-%d")


# ==========================================================
# Calculator
# ==========================================================

def calculate(expression: str):
    """
    Safely evaluate simple mathematical expressions.

    Example:
        calculate("23 * (45 + 2)")
    """

    allowed = {
        "__builtins__": {},
        "abs": abs,
        "round": round,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
    }

    try:
        result = eval(expression, allowed)
        return str(result)
    except Exception as ex:
        return f"Calculation Error: {ex}"


# ==========================================================
# File Tools
# ==========================================================

def read_file(filename: str):
    """Read a text file."""

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as ex:
        return str(ex)


def write_file(filename: str, content: str):
    """Write text into a file."""

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return "File written successfully."

    except Exception as ex:
        return str(ex)


def list_directory(path="."):
    """List files inside a directory."""

    try:
        return "\n".join(os.listdir(path))

    except Exception as ex:
        return str(ex)


# ==========================================================
# System Tools
# ==========================================================

def cpu_usage():
    """CPU utilization percentage."""
    return f"{psutil.cpu_percent(interval=1)} %"


def memory_usage():
    """RAM usage."""

    mem = psutil.virtual_memory()

    return (
        f"Used : {round(mem.used/1024**3,2)} GB\n"
        f"Total: {round(mem.total/1024**3,2)} GB\n"
        f"Usage: {mem.percent}%"
    )


def disk_usage():
    """Disk usage."""

    disk = psutil.disk_usage("/")

    return (
        f"Used : {round(disk.used/1024**3,2)} GB\n"
        f"Free : {round(disk.free/1024**3,2)} GB\n"
        f"Usage: {disk.percent}%"
    )


def running_processes(limit=15):
    """Top running processes."""

    processes = []

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            processes.append(
                f"{proc.info['pid']}    {proc.info['name']}"
            )
        except Exception:
            pass

    return "\n".join(processes[:limit])


# ==========================================================
# Linux Command
# ==========================================================

SAFE_COMMANDS = [
    "ls",
    "pwd",
    "whoami",
    "df",
    "free",
    "uptime",
    "hostname",
    "date",
]


def execute_command(command: str):
    """
    Execute only safe Linux commands.
    """

    first = command.split()[0]

    if first not in SAFE_COMMANDS:
        return f"Command '{first}' is not allowed."

    try:

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return result.stdout

        return result.stderr

    except Exception as ex:
        return str(ex)


# ==========================================================
# Tool Registry
# ==========================================================

TOOLS = {
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "calculate": calculate,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "cpu_usage": cpu_usage,
    "memory_usage": memory_usage,
    "disk_usage": disk_usage,
    "running_processes": running_processes,
    "execute_command": execute_command,
}
