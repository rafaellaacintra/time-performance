GA4_TOOLS = [
    {
        "name": "ga4_get_traffic_metrics",
        "description": (
            "Busca métricas de tráfego e conversão do Google Analytics 4. "
            "Retorna sessões, usuários, taxa de rejeição, taxa de conversão, receita "
            "e transações. Pode segmentar por origem, mídia, campanha ou dispositivo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "enum": ["today", "yesterday", "last_7d", "last_14d", "last_30d"],
                    "description": "Período das métricas.",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Dimensões para segmentação, ex: ['source', 'medium', 'campaign', "
                        "'device_category', 'landing_page']."
                    ),
                },
                "segment": {
                    "type": "string",
                    "description": "Segmento de usuários para filtrar, ex: 'paid_traffic', 'organic'.",
                },
            },
            "required": ["date_range"],
        },
    },
    {
        "name": "ga4_get_funnel_data",
        "description": (
            "Busca dados do funil de conversão no GA4, mostrando o volume e a taxa de abandono "
            "em cada etapa: sessão → produto → carrinho → checkout → compra. "
            "Use para identificar gargalos e oportunidades de CRO."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "enum": ["last_7d", "last_14d", "last_30d"],
                    "description": "Período dos dados do funil.",
                },
                "segment": {
                    "type": "string",
                    "description": "Segmento para filtrar o funil, ex: 'paid_traffic', 'mobile'.",
                },
            },
            "required": ["date_range"],
        },
    },
]


def execute_ga4_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "ga4_get_traffic_metrics":
        date_range = tool_input.get("date_range", "last_7d")
        dimensions = tool_input.get("dimensions", [])

        result = f"""
MÉTRICAS GA4 — {date_range}
══════════════════════════════════════════════════

VISÃO GERAL
  Sessões: 24.891  |  Usuários: 18.234  |  Novos: 14.102 (77,3%)
  Taxa de rejeição: 42,3%  |  Duração média: 3min 47s
  Taxa de conversão: 2,18%  |  Transações: 542
  Receita: R$ 54.230,90  |  Ticket médio: R$ 100,06
"""
        if any(d in dimensions for d in ["source", "medium", "campaign"]):
            result += """
POR ORIGEM / MÍDIA
  google / cpc         →  8.234 sessões  |  2,9% conv  |  R$ 22.100,00
  facebook / cpc       →  6.891 sessões  |  2,1% conv  |  R$ 14.320,00
  instagram / cpc      →  2.340 sessões  |  1,8% conv  |  R$  4.890,00
  google / organic     →  5.102 sessões  |  1,8% conv  |  R$ 10.890,00
  direct / none        →  1.213 sessões  |  2,4% conv  |  R$  6.890,00
  email / newsletter   →    891 sessões  |  3,1% conv  |  R$  4.030,00
"""
        if "device_category" in dimensions:
            result += """
POR DISPOSITIVO
  mobile   →  14.934 sessões (60%)  |  1,7% conv  |  R$ 24.104,00
  desktop  →   8.711 sessões (35%)  |  3,1% conv  |  R$ 27.115,00
  tablet   →   1.246 sessões  (5%)  |  2,0% conv  |  R$  3.011,00
"""
        return result

    if tool_name == "ga4_get_funnel_data":
        date_range = tool_input.get("date_range", "last_30d")
        segment = tool_input.get("segment", "todos os usuários")
        return f"""
FUNIL DE CONVERSÃO — {date_range} ({segment})
══════════════════════════════════════════════════

  1. Sessões no site          24.891   100,0%
  2. Visualizaram produto     14.234    57,2%   ↓ abandono: 42,8%
  3. Adicionaram ao carrinho   5.891    23,7%   ↓ abandono: 58,6%  ← MAIOR GARGALO
  4. Iniciaram checkout        3.102    12,5%   ↓ abandono: 47,4%
  5. Inseriram dados           2.234     9,0%   ↓ abandono: 28,0%
  6. Concluíram pagamento      1.643     6,6%   ↓ abandono: 26,4%
  7. Pedido confirmado         1.601     6,4%   ↓ abandono:  2,6%

OBSERVAÇÕES
  Maior gargalo: Produto → Carrinho (58,6% de abandono)
  2º maior gargalo: Sessão → Produto (42,8% não visualiza produto)
  Receita perdida estimada no carrinho: R$ 22.480,00/mês
"""

    return f"[ERRO] Ferramenta GA4 '{tool_name}' não reconhecida."
