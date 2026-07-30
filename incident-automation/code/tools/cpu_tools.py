import time
import psutil

from langchain_core.tools import tool


@tool
def check_cpu() -> str:
    """
    Check current overall CPU utilization.
    Use this when investigating HighCPU incidents.
    """

    cpu = psutil.cpu_percent(interval=1)

    return f"Current CPU utilization: {cpu:.1f}%"


@tool
def check_top_cpu_processes() -> str:
    """
    Find processes currently consuming high CPU.
    Returns PID, process name, CPU and command.
    """

    processes = []

    # Initialize CPU counters
    procs = list(psutil.process_iter())

    for proc in procs:
        try:
            proc.cpu_percent(interval=None)
        except Exception:
            pass

    time.sleep(1)

    for proc in procs:

        try:

            cpu = proc.cpu_percent(interval=None)

            if cpu < 1:
                continue

            name = proc.name()

            try:
                command = " ".join(proc.cmdline())
            except Exception:
                command = "unknown"

            processes.append({
                "pid": proc.pid,
                "name": name,
                "cpu": cpu,
                "command": command
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    processes.sort(
        key=lambda x: x["cpu"],
        reverse=True
    )

    if not processes:
        return "No significant CPU-consuming processes found."

    output = []

    for process in processes[:10]:

        output.append(
            f"PID {process['pid']} | "
            f"Process: {process['name']} | "
            f"CPU: {process['cpu']:.1f}% | "
            f"Command: {process['command']}"
        )

    return "\n".join(output)


@tool
def inspect_process(pid: int) -> str:
    """
    Inspect a specific process by PID.
    """

    try:

        process = psutil.Process(pid)

        return (
            f"PID: {pid}\n"
            f"Process: {process.name()}\n"
            f"Status: {process.status()}\n"
            f"User: {process.username()}\n"
            f"CPU: {process.cpu_percent(interval=1):.1f}%\n"
            f"Memory: {process.memory_percent():.2f}%\n"
            f"Command: {' '.join(process.cmdline())}"
        )

    except psutil.NoSuchProcess:
        return f"PID {pid} does not exist."

    except psutil.AccessDenied:
        return f"Access denied for PID {pid}."
