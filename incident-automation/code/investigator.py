#######################################

cat investigator.py 

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from prometheus_tools import check_cpu_history
from app.agent.tools import (
    check_cpu,
    check_top_processes
)


# -------------------------------
# Ollama LLM
# -------------------------------

llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0
)


# -------------------------------
# Tools available to Agent
# -------------------------------

tools = [
    check_cpu,
    check_cpu_history,
    check_top_processes
]


# -------------------------------
# DevOps AI Agent
# -------------------------------

agent = create_agent(

    model=llm,

    tools=tools,

    system_prompt="""
You are an autonomous DevOps Incident Investigation Agent.

You receive infrastructure incidents automatically.

For every incident:

1. Understand the incident.

2. Create an investigation plan.

3. Decide which available tools are useful.

4. Execute the required tools.

5. Analyze the evidence returned by the tools.

6. If the evidence is insufficient, use another appropriate tool.

7. Determine the probable root cause.

Do not invent infrastructure information.

Do not perform remediation.

Return:

INVESTIGATION PLAN

OBSERVATIONS

PROBABLE ROOT CAUSE

RECOMMENDED ACTION
"""
)


def investigate(incident):

    print("\n================================")
    print("DEVOPS AI AGENT STARTED")
    print("================================")

    print(f"Incident : {incident['incident_id']}")
    print(f"Alert    : {incident['alert']}")
    print(f"Severity : {incident['severity']}")
    print(f"Instance : {incident['instance']}")

    prompt = f"""
A new infrastructure incident has occurred.

Incident ID: {incident['incident_id']}

Alert: {incident['alert']}

Severity: {incident['severity']}

Instance: {incident['instance']}

Description: {incident['description']}

Investigate this incident.

Create an investigation plan.

Select the appropriate tools yourself.

Use real evidence from those tools.

Determine the probable root cause.
"""

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    answer = result["messages"][-1].content

    return answer


#########################################################



