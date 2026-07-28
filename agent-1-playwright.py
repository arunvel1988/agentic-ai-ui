"""
agent.py
---------

Simple AI Agent Runtime with Memory
"""

from models import llm
from tools import TOOLS
from memory import memory


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
9. read_file
10. write_file
11. execute_command
12. browse_url
13. get_page_links

-------------------------------------------------------

If a tool is needed, reply ONLY in this format.

TOOL:<tool_name>
INPUT:<tool_input>

Examples

User:
What time is it?

Assistant:
TOOL:get_current_time
INPUT:

----------------------------

User:
Calculate 45 * 89

Assistant:
TOOL:calculate
INPUT:45 * 89

----------------------------

If no tool is required,
answer the question normally.

Do NOT explain why you selected a tool.
"""


class Agent:

    def __init__(self):
        pass

    def ask(self, user_message):

        # -----------------------------------------
        # Load previous conversation
        # -----------------------------------------

        history = memory.history()

        prompt = f"""
{SYSTEM_PROMPT}

Previous Conversation

{history}

User:
{user_message}

Assistant:
"""

        # -----------------------------------------
        # Ask LLM
        # -----------------------------------------

        response = llm.generate(prompt)

        print("\n========== LLM ==========")
        print(response)
        print("=========================\n")

        # -----------------------------------------
        # Tool Calling
        # -----------------------------------------

        if response.startswith("TOOL:"):

            lines = response.splitlines()

            tool_name = lines[0].replace("TOOL:", "").strip()

            tool_input = ""

            if len(lines) > 1 and lines[1].startswith("INPUT:"):
                tool_input = lines[1].replace("INPUT:", "").strip()

            print(f"Executing Tool : {tool_name}")
            print(f"Tool Input     : {tool_input}")

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

            print("\n========== TOOL RESULT ==========")
            print(result)
            print("=================================\n")

            # -----------------------------------------
            # Ask LLM to generate final response
            # -----------------------------------------

            final_prompt = f"""
You are an AI Assistant.

Previous Conversation

{history}

User Question

{user_message}

Tool Used

{tool_name}

Tool Output

{result}

Generate a helpful final response for the user.
"""

            final_answer = llm.generate(final_prompt)

            # Save conversation

            memory.add_user(user_message)
            memory.add_assistant(final_answer)

            return final_answer

        # -----------------------------------------
        # Normal Response
        # -----------------------------------------

        memory.add_user(user_message)
        memory.add_assistant(response)

        return response


agent = Agent()
