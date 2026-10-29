import json
import os
import re
from typing import Any, Callable, Dict, Generator, List, Optional
from src.tools import DBMSToolKit

SYSTEM_PROMPT = """You are an expert DBMS (Database Management Systems) AI Teaching Assistant and Research Agent.

You have access to 3 powerful tools:
1. `search_dbms_notes(query, top_k)`: Searches the student's lecture slides/notes.
2. `fetch_page_context(page_number)`: Reads the entire text of a specific slide/page.
3. `execute_sql_sandbox(sql_query)`: Executes SQL in a sandbox database with tables: Students, Courses, Departments, Enrollments.

CRITICAL OPERATIONAL RULES:
- Ground your answers in the course material whenever possible. Cite exact page numbers (e.g., [Page 14]).
- If an initial search doesn't return adequate information, REFORMULATE your query using technical synonyms and search again.
- If a search result mentions a table or diagram on that page, use `fetch_page_context(page_number)` to read the surrounding text.
- If asked to write or debug SQL, run it in `execute_sql_sandbox` first to verify that it executes without errors and produces expected results.
- When you have gathered enough information, synthesize a clear, comprehensive, and well-structured final answer.

PROTOCOL FORMAT:
When thinking, output your reasoning first:
Thought: <what you understand, what information is missing, and what action you plan to take>
Action: <tool_name>
Action Input: <JSON formatted arguments>

When you are ready to conclude, output:
Final Answer: <your complete, authoritative answer with citations>
"""


class AgentStep:
    def __init__(self, step_type: str, content: str, tool_name: str = "", tool_args: Any = None):
        self.step_type = step_type  # 'thought', 'tool_call', 'observation', 'final_answer', 'error'
        self.content = content
        self.tool_name = tool_name
        self.tool_args = tool_args or {}


class DBMSAgent:
    """Autonomous ReAct agent for DBMS course Q&A and SQL problem solving."""

    def __init__(self, toolkit: DBMSToolKit, max_iterations: int = 6):
        self.toolkit = toolkit
        self.max_iterations = max_iterations
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash" if self.provider == "gemini" else "gpt-4o-mini")
        self._init_llm_client()

    def _init_llm_client(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if self.provider == "gemini" and gemini_key and gemini_key != "your_gemini_api_key_here":
            from google import genai
            self.client = genai.Client(api_key=gemini_key)
            self.active_backend = "gemini"
        elif openai_key and openai_key != "your_openai_api_key_here":
            from openai import OpenAI
            self.client = OpenAI(api_key=openai_key)
            self.active_backend = "openai"
        elif gemini_key and gemini_key != "your_gemini_api_key_here":
            from google import genai
            self.client = genai.Client(api_key=gemini_key)
            self.active_backend = "gemini"
        else:
            self.client = None
            self.active_backend = "mock"

    def _call_llm(self, prompt: str) -> str:
        if self.active_backend == "gemini":
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text or ""
        elif self.active_backend == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        else:
            # Fallback mock mode for testing without an API key
            return self._mock_llm_response(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        """Simulates intelligent agent behavior when running in demo/offline mode."""
        if "Action Input:" not in prompt:
            # First turn: execute search
            return (
                "Thought: The user is asking a DBMS question. I should search the course notes for relevant concepts.\n"
                'Action: search_dbms_notes\n'
                'Action Input: {"query": "database concepts and fundamentals", "top_k": 3}'
            )
        else:
            # Concluding turn
            return (
                "Thought: I have reviewed the retrieved course excerpts. I can now provide a synthesized answer.\n"
                "Final Answer: [Demo Mode] Here is the synthesis based on your course notes. (To enable full live reasoning, add your GEMINI_API_KEY to .env)."
            )

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        if tool_name == "search_dbms_notes":
            return self.toolkit.search_dbms_notes(**args)
        elif tool_name == "fetch_page_context":
            return self.toolkit.fetch_page_context(**args)
        elif tool_name == "execute_sql_sandbox":
            return self.toolkit.execute_sql_sandbox(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'. Available tools: search_dbms_notes, fetch_page_context, execute_sql_sandbox."

    def run(self, user_question: str) -> Generator[AgentStep, None, str]:
        """
        Executes the ReAct loop generator, yielding each step for live UI display.
        Returns the final answer string upon completion.
        """
        conversation_history = f"{SYSTEM_PROMPT}\n\nUser Question: {user_question}\n"
        final_answer = ""

        for iteration in range(1, self.max_iterations + 1):
            llm_output = self._call_llm(conversation_history)

            # Check for Final Answer
            if "Final Answer:" in llm_output:
                parts = llm_output.split("Final Answer:", 1)
                thought_part = parts[0].strip()
                if thought_part:
                    yield AgentStep("thought", thought_part)

                final_answer = parts[1].strip()
                yield AgentStep("final_answer", final_answer)
                return final_answer

            # Parse Thought and Action
            thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", llm_output, re.DOTALL)
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)", llm_output)
            action_input_match = re.search(r"Action Input:\s*(\{.*?\})", llm_output, re.DOTALL)

            thought_text = thought_match.group(1).strip() if thought_match else llm_output.strip()
            yield AgentStep("thought", thought_text)

            if not action_match:
                # Model did not format an action properly; prompt it to conclude or act
                conversation_history += f"\n{llm_output}\nObservation: Please specify a valid Action and Action Input, or provide 'Final Answer:'."
                continue

            tool_name = action_match.group(1).strip()
            raw_input = action_input_match.group(1).strip() if action_input_match else "{}"

            try:
                tool_args = json.loads(raw_input)
            except Exception:
                # Handle single unquoted string argument
                tool_args = {"query": raw_input.strip('"{}\' ')}

            yield AgentStep("tool_call", f"Calling `{tool_name}`", tool_name=tool_name, tool_args=tool_args)

            # Execute tool
            observation = self._execute_tool(tool_name, tool_args)
            yield AgentStep("observation", observation, tool_name=tool_name)

            # Append to prompt history for next iteration
            conversation_history += (
                f"\nThought: {thought_text}\n"
                f"Action: {tool_name}\n"
                f"Action Input: {json.dumps(tool_args)}\n"
                f"Observation: {observation}\n"
            )

        # Reached max steps
        fallback_prompt = conversation_history + "\nObservation: Maximum steps reached. Synthesize your Final Answer now based on everything gathered."
        concluding_output = self._call_llm(fallback_prompt)
        if "Final Answer:" in concluding_output:
            final_answer = concluding_output.split("Final Answer:", 1)[1].strip()
        else:
            final_answer = concluding_output.strip()

        yield AgentStep("final_answer", final_answer)
        return final_answer
