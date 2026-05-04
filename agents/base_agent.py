from typing import Optional
import anthropic
from config import MODEL, MAX_TOKENS, MAX_TOOL_ITERATIONS
from tools import execute_tool


class BaseAgent:
    """
    Base class for all agents. Handles the tool-use loop and prompt caching.

    The system prompt is cached with cache_control "ephemeral" to avoid
    re-sending large prompts on every turn. Each agent subclass defines
    its own system_prompt and tools list.
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        name: str,
        system_prompt: str,
        tools: list,
    ):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools

    def run(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Run the agent on a user message, optionally with additional context
        (e.g., metrics already fetched, reports from other agents).

        Executes the tool-use loop until Claude returns end_turn or the
        iteration limit is reached.
        """
        if context:
            full_message = f"{user_message}\n\nContexto adicional disponível:\n{context}"
        else:
            full_message = user_message

        messages = [{"role": "user", "content": full_message}]
        last_response = None

        for _ in range(MAX_TOOL_ITERATIONS):
            create_kwargs: dict = {
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "system": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                "messages": messages,
            }
            if self.tools:
                create_kwargs["tools"] = self.tools

            last_response = self.client.messages.create(**create_kwargs)

            if last_response.stop_reason == "end_turn":
                return self._extract_text(last_response)

            if last_response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": last_response.content})
                tool_results = []
                for block in last_response.content:
                    if block.type == "tool_use":
                        result = execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            # pause_turn or unexpected stop reason — append and continue
            messages.append({"role": "assistant", "content": last_response.content})

        return self._extract_text(last_response) if last_response else ""

    def _extract_text(self, response: anthropic.types.Message) -> str:
        return "\n".join(
            block.text for block in response.content if block.type == "text"
        )
