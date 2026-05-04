META_ADS_TOOLS = [
    {
        "name": "meta_ads_get_campaign_metrics",
        "description": (
            "Busca métricas de performance das campanhas no Meta Ads (Facebook/Instagram). "
            "Retorna impressões, cliques, CTR, CPC, CPM, ROAS, conversões e investimento "
            "para um intervalo de datas. Use para análise de performance e identificação "
            "de oportunidades de otimização."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "description": "Período das métricas.",
                    "enum": ["today", "yesterday", "last_7d", "last_14d", "last_30d"],
                },
                "campaign_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs de campanhas específicas. Se vazio, retorna todas.",
                },
                "breakdown": {
                    "type": "string",
                    "description": "Quebra dos dados por dimensão.",
                    "enum": ["campaign", "adset", "ad", "age", "gender", "placement"],
                },
            },
            "required": ["date_range"],
        },
    },
    {
        "name": "meta_ads_update_campaign",
        "description": (
            "Atualiza configurações de uma campanha no Meta Ads (orçamento, lance, status). "
            "REQUER aprovação prévia do Head de Marketing antes da execução. "
            "Use apenas após validação do plano de ajustes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "ID da campanha a ser atualizada.",
                },
                "daily_budget": {
                    "type": "number",
                    "description": "Novo orçamento diário em BRL.",
                },
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED"],
                    "description": "Status da campanha.",
                },
                "bid_amount": {
                    "type": "number",
                    "description": "Novo valor de lance em BRL.",
                },
            },
            "required": ["campaign_id"],
        },
    },
]


def execute_meta_ads_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "meta_ads_get_campaign_metrics":
        date_range = tool_input.get("date_range", "last_7d")
        breakdown = tool_input.get("breakdown", "campaign")
        return f"""
MÉTRICAS META ADS — {date_range} (breakdown: {breakdown})
══════════════════════════════════════════════════

Campanha: "Conversão — Produtos Destaque"
  Investimento: R$ 7.001,54  |  Impressões: 145.230  |  Cliques: 3.847
  CTR: 2,65%  |  CPC: R$ 1,82  |  CPM: R$ 48,21
  Conversões: 187  |  CPA: R$ 37,44  |  ROAS: 4,2x

Campanha: "Remarketing — Abandono de Carrinho"
  Investimento: R$ 2.112,88  |  Impressões: 48.920  |  Cliques: 2.156
  CTR: 4,41%  |  CPC: R$ 0,98  |  CPM: R$ 43,19
  Conversões: 143  |  CPA: R$ 14,77  |  ROAS: 7,8x

Campanha: "Awareness — Topo de Funil"
  Investimento: R$ 9.413,82  |  Impressões: 289.450  |  Cliques: 4.023
  CTR: 1,39%  |  CPC: R$ 2,34  |  CPM: R$ 32,52
  Conversões: 89  |  CPA: R$ 105,77  |  ROAS: 1,9x

TOTAL DO PERÍODO
  Investimento: R$ 18.528,24  |  Conversões: 419  |  CPA médio: R$ 44,22
  ROAS consolidado: 3,8x  |  Receita atribuída: R$ 70.407,31
"""

    if tool_name == "meta_ads_update_campaign":
        campaign_id = tool_input.get("campaign_id")
        changes = []
        if "daily_budget" in tool_input:
            changes.append(f"orçamento diário → R$ {tool_input['daily_budget']:.2f}")
        if "status" in tool_input:
            changes.append(f"status → {tool_input['status']}")
        if "bid_amount" in tool_input:
            changes.append(f"lance → R$ {tool_input['bid_amount']:.2f}")
        return f"[STUB] Campanha {campaign_id} atualizada com sucesso: {', '.join(changes)}"

    return f"[ERRO] Ferramenta Meta Ads '{tool_name}' não reconhecida."
