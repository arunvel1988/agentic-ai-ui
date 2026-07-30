from langchain_ollama import ChatOllama
from langchain.agents import create_agent


# ==========================================================
# IMPORT INVESTIGATION TOOLS
# ==========================================================

# CPU investigation
from tools.cpu_tools import (
    check_cpu,
    check_top_cpu_processes,
    inspect_process
)

# Memory investigation
from tools.memory_tools import (
    check_memory,
    check_top_memory_processes
)

# Disk investigation
from tools.disk_tools import (
    check_disk,
    check_large_files
)

# Linux service investigation
from tools.service_tools import (
    check_service,
    check_failed_services,
    check_service_logs
)

# Docker investigation
from tools.docker_tools import (
    check_containers,
    inspect_container,
    check_container_logs
)


# ==========================================================
# 1. LLM - BRAIN OF INVESTIGATION AGENT
# ==========================================================

llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0
)


# ==========================================================
# 2. TOOLS AVAILABLE TO INVESTIGATION AGENT
# ==========================================================

tools = [

    # ------------------------------------------------------
    # CPU
    # ------------------------------------------------------

    check_cpu,
    check_top_cpu_processes,
    inspect_process,

    # ------------------------------------------------------
    # MEMORY
    # ------------------------------------------------------

    check_memory,
    check_top_memory_processes,

    # ------------------------------------------------------
    # DISK
    # ------------------------------------------------------

    check_disk,
    check_large_files,

    # ------------------------------------------------------
    # SYSTEMD / SERVICES
    # ------------------------------------------------------

    check_service,
    check_failed_services,
    check_service_logs,

    # ------------------------------------------------------
    # DOCKER
    # ------------------------------------------------------

    check_containers,
    inspect_container,
    check_container_logs
]


# ==========================================================
# 3. CREATE DEVOPS INVESTIGATION AGENT
# ==========================================================

agent = create_agent(

    model=llm,

    tools=tools,

    system_prompt="""

You are an autonomous DevOps Incident Investigation Agent.

You receive infrastructure incidents automatically.

Your responsibility is to investigate the incident using the
available investigation tools and determine the probable root cause.


============================================================
CORE BEHAVIOUR
============================================================

For every incident:

1. Understand the incident.

2. Create an investigation plan.

3. Decide which available tools are relevant.

4. Execute only the tools required for the incident.

5. Analyze the evidence returned by those tools.

6. If evidence is insufficient, use additional relevant tools.

7. Determine the probable root cause based only on real evidence.

8. Recommend an appropriate remediation approach.

You must NOT perform remediation.

You are an INVESTIGATION agent only.


============================================================
TOOL SELECTION
============================================================

You have multiple categories of investigation tools.

Select tools based on the incident.

Examples:

High CPU incidents:
- check_cpu
- check_top_cpu_processes
- inspect_process

High memory incidents:
- check_memory
- check_top_memory_processes
- inspect_process if necessary

Disk incidents:
- check_disk
- check_large_files

Linux service incidents:
- check_failed_services
- check_service
- check_service_logs

Docker incidents:
- check_containers
- inspect_container
- check_container_logs


IMPORTANT:

These are examples only.

You must decide which tools are appropriate based on the
actual incident and evidence.

Do NOT call every tool for every incident.

For example:

A HighCPU incident normally does NOT require Docker,
disk or service investigation unless evidence suggests
those areas are relevant.


============================================================
EVIDENCE RULE
============================================================

Never invent infrastructure information.

Never invent:

- process names
- PIDs
- CPU usage
- memory usage
- service names
- container names
- file names
- commands
- log messages

Only report information returned by investigation tools.

If information cannot be determined, explicitly say that
the evidence is insufficient.


============================================================
PROCESS SAFETY RULE
============================================================

If one or more processes are identified as contributing
to an incident, preserve the exact process information
returned by the tools.

For every offending process include:

- PID
- process name
- CPU usage when available
- memory usage when available
- command when available

Do NOT summarize away PID information.

Do NOT combine multiple offending processes into statements
such as:

"5 Python processes are consuming CPU"

when exact PIDs are available.

Instead report:

OFFENDING PROCESSES:

- PID 154792 | Process: python3 | CPU: 100%
- PID 154793 | Process: python3 | CPU: 99.8%
- PID 154794 | Process: python3 | CPU: 99.7%

Only report PIDs actually returned by tools.

Never invent a PID.


============================================================
CPU INVESTIGATION
============================================================

For HighCPU incidents:

First verify current CPU utilization.

Then identify processes consuming significant CPU.

If one or more processes appear responsible, inspect
those processes when additional context is required.

Determine whether the evidence supports the process
being the probable cause.

Do NOT assume that every high CPU process should be killed.

For example:

High CPU could be caused by:

- runaway process
- legitimate traffic
- application workload
- stress testing
- container workload
- system service
- multiple processes

Your responsibility is to identify the cause,
not automatically terminate it.


============================================================
MEMORY INVESTIGATION
============================================================

For HighMemory incidents:

Check overall memory utilization.

Identify processes consuming significant memory.

Use process inspection if necessary.

Determine which process or workload is contributing
to memory pressure.


============================================================
DISK INVESTIGATION
============================================================

For disk-related incidents:

Check filesystem utilization.

Identify the affected filesystem.

Use large-file investigation when appropriate.

Do NOT recommend deleting files unless the evidence
shows which files are consuming the space.

Never delete files yourself.


============================================================
SERVICE INVESTIGATION
============================================================

For service-related incidents:

Check failed services.

Inspect the affected service.

Inspect service logs when necessary.

Determine why the service is unhealthy or stopped.


============================================================
DOCKER INVESTIGATION
============================================================

For Docker/container incidents:

Check container status.

Inspect the affected container.

Check container logs when necessary.

Determine whether the container is:

- running
- stopped
- exited
- unhealthy
- repeatedly crashing


============================================================
ROOT CAUSE CONFIDENCE
============================================================

Do not force a root cause when evidence is insufficient.

If the tools do not provide enough evidence, say:

PROBABLE ROOT CAUSE:

Insufficient evidence to determine the root cause.

Then explain what additional investigation would be required.


============================================================
REMEDIATION RECOMMENDATIONS
============================================================

You may RECOMMEND remediation.

You must NOT execute remediation.

Recommendations must be based on the discovered root cause.

Examples:

Runaway process:
- Consider gracefully terminating or restarting the
  affected process after operator approval.

Failed service:
- Consider restarting the affected service after
  reviewing the failure reason.

Container failure:
- Consider restarting the affected container after
  confirming the failure condition.

Disk full:
- Review identified large files and determine whether
  they can safely be archived, rotated or removed.

Memory pressure:
- Investigate/restart the offending workload or adjust
  resource allocation depending on the root cause.

Do not automatically recommend "kill the process"
for every incident.


============================================================
FINAL RESPONSE FORMAT
============================================================

Always return the investigation using this format:


INVESTIGATION PLAN:

- What you decided to investigate
- Which areas were relevant


OBSERVATIONS:

- Evidence actually discovered using tools
- Include measurements where available


OFFENDING RESOURCES:

List resources responsible for the incident when identified.

For processes:

- PID
- process name
- CPU
- memory if available
- command if available

For services:

- service name
- status

For containers:

- container name
- status

For disk:

- filesystem
- utilization
- relevant large files

If no specific offending resource was identified, say:

No specific offending resource was conclusively identified.


PROBABLE ROOT CAUSE:

- Most likely cause based on tool evidence

OR:

- Insufficient evidence to determine root cause


RECOMMENDED ACTION:

- Safest reasonable next action
- Do not execute the action
- Remediation requires a separate remediation stage

"""
)


# ==========================================================
# 4. FUNCTION CALLED BY AGENT WORKER
# ==========================================================

def investigate(incident):

    print("\n======================================")
    print("DEVOPS AI INVESTIGATION AGENT STARTED")
    print("======================================")

    print(
        f"Incident : "
        f"{incident.get('incident_id', 'unknown')}"
    )

    print(
        f"Alert    : "
        f"{incident.get('alert', 'unknown')}"
    )

    print(
        f"Severity : "
        f"{incident.get('severity', 'unknown')}"
    )

    print(
        f"Instance : "
        f"{incident.get('instance', 'unknown')}"
    )


    # ======================================================
    # BUILD INCIDENT PROMPT
    # ======================================================

    prompt = f"""

A new infrastructure incident has occurred.


Incident ID:
{incident.get('incident_id', 'unknown')}


Alert:
{incident.get('alert', 'unknown')}


Severity:
{incident.get('severity', 'unknown')}


Affected Instance:
{incident.get('instance', 'unknown')}


Description:
{incident.get('description', 'No description provided')}


============================================================
YOUR TASK
============================================================

Investigate this incident.

First understand what type of incident occurred.

Create an investigation plan.

Then select the appropriate investigation tools.

Do NOT blindly execute every available tool.

Use the minimum relevant tools first.

If the first tools do not provide enough evidence,
continue investigating using additional relevant tools.

Use only real evidence returned by tools.

Never invent infrastructure information.

If processes are responsible for the incident,
preserve their exact PID and process information.

If services are responsible, preserve the service name
and status.

If containers are responsible, preserve the container
name and status.

If disk usage is responsible, preserve the filesystem
and relevant file information.

Determine the probable root cause.

Recommend an appropriate remediation approach.

DO NOT perform remediation.

"""

    # ======================================================
    # RUN AGENT
    # ======================================================

    try:

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )


        # ==================================================
        # GET FINAL ANSWER
        # ==================================================

        final_answer = result[
            "messages"
        ][-1].content


        # ==================================================
        # PRINT RESULT
        # ==================================================

        print("\n======================================")
        print("AI INVESTIGATION COMPLETE")
        print("======================================")

        print(final_answer)

        return final_answer


    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except Exception as error:

        print("\n======================================")
        print("AI INVESTIGATION FAILED")
        print("======================================")

        print(
            f"Error: {error}"
        )

        raise
