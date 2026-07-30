import subprocess

from langchain_core.tools import tool


@tool
def check_service(service_name: str) -> str:
    """
    Check the current status of a systemd service.
    """

    try:

        result = subprocess.run(
            [
                "systemctl",
                "status",
                service_name,
                "--no-pager"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        return output[-6000:]

    except Exception as error:

        return (
            f"Unable to check service "
            f"{service_name}: {error}"
        )


@tool
def check_failed_services() -> str:
    """
    List currently failed systemd services.
    """

    try:

        result = subprocess.run(
            [
                "systemctl",
                "--failed",
                "--no-pager",
                "--plain"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.stdout

    except Exception as error:

        return (
            f"Unable to check failed services: "
            f"{error}"
        )


@tool
def check_service_logs(
    service_name: str,
    lines: int = 50
) -> str:
    """
    Read recent journal logs for a systemd service.
    """

    lines = max(
        1,
        min(lines, 200)
    )

    try:

        result = subprocess.run(
            [
                "journalctl",
                "-u",
                service_name,
                "-n",
                str(lines),
                "--no-pager"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.stdout[-8000:]

    except Exception as error:

        return (
            f"Unable to read logs for "
            f"{service_name}: {error}"
        )
