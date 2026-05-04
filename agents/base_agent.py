import json
from typing import Optional
from openai import OpenAI
from config import MODEL, MAX_TOKENS, MAX_TOOL_ITERATIONS
from tools import execute_tool


def _to_openai_tools(anthropic_tools: list) -> list:
    """Convert Anthropic tool schema format to OpenAI function calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in anthropic_tools
    ]


class BaseAgent:
    def __init__(self, client: OpenAI, name: str, system_prompt: str, tools: list):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self._oai_tools = _to_openai_tools(tools) if tools else []

    def run(self, user_message: str, context: Optional[str] = None) -> str:
        if context:
            full_message = f"{user_message}\n\nContexto adicional disponível:\n{context}"
        else:
            full_message = user_message

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": full_message},
        ]
        last_content = ""

        for _ in range(MAX_TOOL_ITERATIONS):
            kwargs: dict = {
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "messages": messages,
            }
            if self._oai_tools:
                kwargs["tools"] = self._oai_tools

            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            message = choice.message
            last_content = message.content or ""

            if choice.finish_reason == "stop":
                return last_content

            if choice.finish_reason == "tool_calls" and message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                for tc in message.tool_calls:
                    try:
                        tool_input = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}
                    result = execute_tool(tc.function.name, tool_input)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                continue

            return last_content

        return last_content
