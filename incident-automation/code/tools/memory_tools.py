import psutil

from langchain_core.tools import tool


@tool
def check_memory() -> str:
    """
    Check current system memory utilization.
    """

    memory = psutil.virtual_memory()

    return (
        f"Memory utilization: {memory.percent:.1f}%\n"
        f"Total: {memory.total / (1024**3):.2f} GB\n"
        f"Used: {memory.used / (1024**3):.2f} GB\n"
        f"Available: {memory.available / (1024**3):.2f} GB"
    )


@tool
def check_top_memory_processes() -> str:
    """
    Find processes consuming the most memory.
    """

    processes = []

    for proc in psutil.process_iter(
        [
            "pid",
            "name",
            "memory_percent",
            "cmdline"
        ]
    ):

        try:

            processes.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "memory": proc.info["memory_percent"],
                "command": " ".join(
                    proc.info["cmdline"] or []
                )
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    processes.sort(
        key=lambda x: x["memory"],
        reverse=True
    )

    output = []

    for process in processes[:10]:

        output.append(
            f"PID {process['pid']} | "
            f"Process: {process['name']} | "
            f"Memory: {process['memory']:.2f}% | "
            f"Command: {process['command']}"
        )

    return "\n".join(output)
