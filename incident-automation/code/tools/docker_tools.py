import docker

from langchain_core.tools import tool


def get_docker_client():

    return docker.from_env()


@tool
def check_containers() -> str:
    """
    List Docker containers and their current states.
    """

    try:

        client = get_docker_client()

        containers = client.containers.list(
            all=True
        )

        if not containers:
            return "No Docker containers found."

        output = []

        for container in containers:

            output.append(
                f"Container: {container.name} | "
                f"ID: {container.short_id} | "
                f"Status: {container.status} | "
                f"Image: {container.image.tags}"
            )

        return "\n".join(output)

    except Exception as error:

        return (
            f"Unable to inspect Docker: {error}"
        )


@tool
def inspect_container(
    container_name: str
) -> str:
    """
    Inspect a specific Docker container.
    """

    try:

        client = get_docker_client()

        container = client.containers.get(
            container_name
        )

        state = container.attrs.get(
            "State",
            {}
        )

        return (
            f"Container: {container.name}\n"
            f"ID: {container.short_id}\n"
            f"Status: {container.status}\n"
            f"Running: {state.get('Running')}\n"
            f"ExitCode: {state.get('ExitCode')}\n"
            f"Error: {state.get('Error')}\n"
            f"StartedAt: {state.get('StartedAt')}\n"
            f"FinishedAt: {state.get('FinishedAt')}"
        )

    except Exception as error:

        return (
            f"Unable to inspect container "
            f"{container_name}: {error}"
        )


@tool
def check_container_logs(
    container_name: str
) -> str:
    """
    Read recent logs from a Docker container.
    """

    try:

        client = get_docker_client()

        container = client.containers.get(
            container_name
        )

        logs = container.logs(
            tail=100
        )

        return logs.decode(
            "utf-8",
            errors="replace"
        )

    except Exception as error:

        return (
            f"Unable to read container logs: "
            f"{error}"
        )
