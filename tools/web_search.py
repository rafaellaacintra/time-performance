from openai import OpenAI
from config import OPENAI_API_KEY

_SEARCH_MODEL = "gpt-4o-mini"

WEB_SEARCH_TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Pesquisa na web por inteligência de mercado: análise de concorrentes, tendências, "
            "sazonalidade, referências criativas e benchmarks do setor de e-commerce e tráfego pago. "
            "Use para embasar recomendações com dados externos atuais."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Consulta de busca específica e detalhada, ex: "
                        "'estratégia tráfego pago concorrentes moda feminina brasil julho 2024'"
                    ),
                },
                "search_type": {
                    "type": "string",
                    "enum": ["competitors", "trends", "seasonality", "creative_references", "benchmarks"],
                    "description": "Tipo de pesquisa para contextualizar os resultados.",
                },
            },
            "required": ["query", "search_type"],
        },
    },
]


def execute_web_search_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name != "web_search":
        return f"[ERRO] Ferramenta de busca '{tool_name}' não reconhecida."

    if not OPENAI_API_KEY:
        return "[ERRO] OPENAI_API_KEY não configurada no .env"

    query = tool_input.get("query", "")
    search_type = tool_input.get("search_type", "general")

    prompt = (
        f"Você é um especialista em marketing digital e e-commerce brasileiro. "
        f"Pesquise na web sobre: {query}\n\n"
        f"Tipo de pesquisa: {search_type}\n\n"
        f"Retorne um resumo estruturado com os achados mais relevantes, "
        f"incluindo dados concretos, tendências identificadas e implicações práticas "
        f"para campanhas de tráfego pago no Brasil."
    )

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=_SEARCH_MODEL,
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
        return _extract_text(response, query, search_type)
    except Exception as exc:
        return f"[ERRO na busca web] {exc}"


def _extract_text(response, query: str, search_type: str) -> str:
    texts = []
    for item in response.output:
        if item.type == "message":
            for content in item.content:
                if content.type == "output_text":
                    texts.append(content.text)

    if not texts:
        return f"[Busca] Nenhum resultado retornado para: {query}"

    header = f'RESULTADOS DA BUSCA — "{query}" (tipo: {search_type})\n{"═" * 50}\n\n'
    return header + "\n\n".join(texts)
