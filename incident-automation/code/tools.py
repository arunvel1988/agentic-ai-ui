import psutil
import time

from langchain_core.tools import tool


@tool
def check_cpu() -> str:
    """Check the current CPU utilization of the server."""

    cpu = psutil.cpu_percent(interval=1)

    return f"Current CPU utilization is {cpu}%"


@tool
def check_top_processes() -> str:
    """Find the processes consuming the most CPU."""

    processes = []

    # Start CPU sampling
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except Exception:
            pass

    time.sleep(1)

    # Read CPU utilization
    for proc in psutil.process_iter(["pid", "name"]):

        try:

            cpu = proc.cpu_percent(None)

            processes.append({
                "pid": proc.pid,
                "name": proc.info["name"],
                "cpu": cpu
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            continue

    processes.sort(
        key=lambda x: x["cpu"],
        reverse=True
    )

    output = ["Top CPU consuming processes:"]

    for proc in processes[:5]:

        output.append(
            f"PID={proc['pid']} "
            f"PROCESS={proc['name']} "
            f"CPU={proc['cpu']}%"
        )

    return "\n".join(output)
