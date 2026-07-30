from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from tools import (
    check_cpu,
    check_top_processes
)


# -------------------------------------------------
# 1. LLM - Brain of our agent
# -------------------------------------------------

llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0
)


# -------------------------------------------------
# 2. Tools available to the agent
# -------------------------------------------------

tools = [
    check_cpu,
    check_top_processes
]


# -------------------------------------------------
# 3. Create DevOps investigation agent
# -------------------------------------------------

agent = create_agent(
    model=llm,

    tools=tools,

    system_prompt="""
You are an autonomous DevOps Incident Investigation Agent.

You receive infrastructure incidents automatically.

Your responsibility is to investigate the incident and determine
the probable root cause.

IMPORTANT:

First understand the incident.

Then create an investigation plan.

Decide which available tools are required.

Execute the appropriate tools.

Analyze the returned evidence.

If the evidence is insufficient, use additional available tools.

Never invent infrastructure information.

Do not perform remediation.


IMPORTANT PROCESS SAFETY RULE:

If one or more processes are identified as contributing to
the incident, you MUST include the exact PID of every offending
process that was returned by the investigation tools.

Do NOT summarize multiple offending processes without their PIDs.

Do NOT invent PIDs.

Only report PIDs that were actually returned by tools.

For every offending process, report:

- PID
- process name
- CPU usage

Example:

OFFENDING PROCESSES:
- PID 154792 | Process: stress-ng-cpu | CPU: 100%
- PID 154793 | Process: stress-ng-cpu | CPU: 99.8%
- PID 154794 | Process: stress-ng-cpu | CPU: 99.7%

If the tools do not provide PID information, explicitly say:

OFFENDING PROCESSES:
Exact PID information is unavailable.

This information may later be used by a separate remediation
system, so accuracy is critical.


At the end provide:

INVESTIGATION PLAN:
- What you decided to investigate

OBSERVATIONS:
- What you actually discovered from tools

OFFENDING PROCESSES:
- Exact PID, process name and CPU usage for processes
  contributing to the incident
- Only include processes supported by tool evidence

PROBABLE ROOT CAUSE:
- Most likely cause based on evidence

RECOMMENDED ACTION:
- What the DevOps engineer should do
"""
)


# -------------------------------------------------
# 4. Function called automatically by worker
# -------------------------------------------------

def investigate(incident):

    print("\n======================================")
    print("DEVOPS AI AGENT STARTED")
    print("======================================")

    print(f"Incident : {incident['incident_id']}")
    print(f"Alert    : {incident['alert']}")
    print(f"Severity : {incident['severity']}")
    print(f"Instance : {incident['instance']}")

    prompt = f"""
A new infrastructure incident has occurred.

Incident ID:
{incident['incident_id']}

Alert:
{incident['alert']}

Severity:
{incident['severity']}

Affected Instance:
{incident['instance']}

Description:
{incident['description']}

Investigate this incident.

First determine an appropriate investigation plan.

Then use the available tools to collect real evidence.

Continue investigating until you have enough evidence to determine
the probable root cause.

IMPORTANT:

If processes are responsible for the incident, include the exact
PID, process name, and CPU usage for every offending process
returned by the tools.

Do not summarize away the PID information.

Never invent PIDs.

Do not make up server information.
"""

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

    final_answer = result["messages"][-1].content

    print("\n======================================")
    print("AI INVESTIGATION COMPLETE")
    print("======================================")

    print(final_answer)

    return final_answer
