"""
agent.py
---------

Simple AI Agent Runtime
"""

from models import llm
from tools import TOOLS


SYSTEM_PROMPT = """
You are an AI Assistant.

You have access to these tools:

1. get_current_time
2. get_current_date
3. calculate
4. cpu_usage
5. memory_usage
6. disk_usage
7. running_processes
8. list_directory

If a tool is needed, reply EXACTLY in this format:

TOOL:<tool_name>
INPUT:<tool_input>

Examples:

User:
What time is it?

Assistant:
TOOL:get_current_time
INPUT:

-------------------------

User:
Calculate 56 * 78

Assistant:
TOOL:calculate
INPUT:56 * 78

-------------------------

If no tool is needed,
answer normally.
"""


class Agent:

    def __init__(self):
        pass

    def ask(self, user_message):

        prompt = f"""
{SYSTEM_PROMPT}

User:
{user_message}

Assistant:
"""

        response = llm.generate(prompt)

        print("LLM RESPONSE")
        print(response)
        print("-" * 50)

        # ------------------------------------------------
        # Did the LLM request a tool?
        # ------------------------------------------------

        if response.startswith("TOOL:"):

            lines = response.splitlines()

            tool_name = lines[0].replace("TOOL:", "").strip()

            tool_input = ""

            if len(lines) > 1 and lines[1].startswith("INPUT:"):
                tool_input = lines[1].replace("INPUT:", "").strip()

            if tool_name not in TOOLS:
                return f"Unknown Tool: {tool_name}"

            tool = TOOLS[tool_name]

            try:

                if tool_input == "":
                    result = tool()
                else:
                    result = tool(tool_input)

            except Exception as ex:
                return str(ex)

            # ---------------------------------------------
            # Ask LLM to create final answer
            # ---------------------------------------------

            final_prompt = f"""
User asked:

{user_message}

Tool Used:

{tool_name}

Tool Result:

{result}

Give a friendly answer.
"""

            return llm.generate(final_prompt)

        # ------------------------------------------------

        return response


agent = Agent()
