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
    if tool_name == "web_search":
        query = tool_input.get("query", "")
        search_type = tool_input.get("search_type", "general")
        return f"""
RESULTADOS DA BUSCA — "{query}" (tipo: {search_type})
══════════════════════════════════════════════════

[STUB] Resultado 1 — Tendência de mercado
  Sazonalidade alta identificada para o período: volume de buscas 38% acima da média.
  Pico previsto para os próximos 7 dias. Concorrentes aumentando investimento em ~25%.

[STUB] Resultado 2 — Inteligência competitiva
  Concorrente principal usando criativos de vídeo curto (15-30s) com CTR 2,3x maior
  que estáticos. Estratégia de lance focada em horário nobre (19h-22h).

[STUB] Resultado 3 — Oportunidade de CPC
  CPCs 15% abaixo da média nas manhãs de terça a quinta. Janela de eficiência
  identificada para alocação orçamentária.

[STUB] Resultado 4 — Referência criativa
  Formato "antes e depois" com prova social performando acima da média no setor.
  UGC (conteúdo gerado por usuário) com taxa de engajamento 40% superior a produções.

[STUB] Resultado 5 — Benchmark do setor
  ROAS médio do setor para tráfego pago: 3,5x a 5,0x. CPA médio: R$ 35-60.
  Taxa de conversão de referência e-commerce: 1,8% a 3,2%.
"""

    return f"[ERRO] Ferramenta de busca '{tool_name}' não reconhecida."
