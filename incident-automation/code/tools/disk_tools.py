import os
import psutil

from langchain_core.tools import tool


@tool
def check_disk() -> str:
    """
    Check filesystem disk utilization.
    """

    output = []

    for partition in psutil.disk_partitions():

        try:

            usage = psutil.disk_usage(
                partition.mountpoint
            )

            output.append(
                f"Mount: {partition.mountpoint} | "
                f"Used: {usage.percent:.1f}% | "
                f"Free: {usage.free / (1024**3):.2f} GB"
            )

        except (
            PermissionError,
            FileNotFoundError
        ):
            continue

    return "\n".join(output)


@tool
def check_large_files(path: str = "/tmp") -> str:
    """
    Find the largest files under a directory.
    Useful when investigating disk-full incidents.
    """

    if not os.path.isdir(path):
        return f"Directory does not exist: {path}"

    files = []

    for root, dirs, filenames in os.walk(path):

        for filename in filenames:

            full_path = os.path.join(
                root,
                filename
            )

            try:

                size = os.path.getsize(
                    full_path
                )

                files.append(
                    (size, full_path)
                )

            except (
                PermissionError,
                FileNotFoundError
            ):
                continue

    files.sort(
        reverse=True
    )

    if not files:
        return f"No files found under {path}."

    output = []

    for size, filename in files[:10]:

        output.append(
            f"{filename} | "
            f"{size / (1024**2):.2f} MB"
        )

    return "\n".join(output)
