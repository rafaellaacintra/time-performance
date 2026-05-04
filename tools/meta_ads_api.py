import requests
from config import META_ACCESS_TOKEN, META_AD_ACCOUNT_ID

_GRAPH_VERSION = "v21.0"
_BASE_URL = f"https://graph.facebook.com/{_GRAPH_VERSION}"

_INSIGHT_FIELDS = ",".join([
    "campaign_id", "campaign_name",
    "adset_id", "adset_name",
    "ad_id", "ad_name",
    "impressions", "clicks", "spend",
    "ctr", "cpc", "cpm", "frequency", "reach",
    "actions", "action_values",
])

_LEVEL_MAP = {
    "campaign": "campaign",
    "adset": "adset",
    "ad": "ad",
    "age": "campaign",
    "gender": "campaign",
    "placement": "campaign",
}

_BREAKDOWN_MAP = {
    "age": "age",
    "gender": "gender",
    "placement": "publisher_platform",
}

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
        return _get_campaign_metrics(tool_input)
    if tool_name == "meta_ads_update_campaign":
        return _update_campaign(tool_input)
    return f"[ERRO] Ferramenta Meta Ads '{tool_name}' não reconhecida."


def _get_campaign_metrics(tool_input: dict) -> str:
    if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
        return "[ERRO] META_ACCESS_TOKEN e META_AD_ACCOUNT_ID não configurados no .env"

    date_range = tool_input.get("date_range", "last_7d")
    breakdown = tool_input.get("breakdown", "campaign")
    campaign_ids = tool_input.get("campaign_ids", [])

    level = _LEVEL_MAP.get(breakdown, "campaign")
    params: dict = {
        "fields": _INSIGHT_FIELDS,
        "date_preset": date_range,
        "level": level,
        "access_token": META_ACCESS_TOKEN,
        "limit": 100,
    }
    if breakdown in _BREAKDOWN_MAP:
        params["breakdowns"] = _BREAKDOWN_MAP[breakdown]

    account = f"act_{META_AD_ACCOUNT_ID}"

    if campaign_ids:
        # fetch each campaign individually and merge
        rows = []
        for cid in campaign_ids:
            url = f"{_BASE_URL}/{cid}/insights"
            r = requests.get(url, params=params, timeout=30)
            data = r.json()
            if "error" in data:
                return f"[ERRO Meta API] {data['error'].get('message', data['error'])}"
            rows.extend(data.get("data", []))
    else:
        url = f"{_BASE_URL}/{account}/insights"
        r = requests.get(url, params=params, timeout=30)
        data = r.json()
        if "error" in data:
            return f"[ERRO Meta API] {data['error'].get('message', data['error'])}"
        rows = data.get("data", [])

    if not rows:
        return f"Nenhum dado encontrado para o período '{date_range}'."

    return _format_insights(rows, date_range, breakdown)


def _format_insights(rows: list, date_range: str, breakdown: str) -> str:
    lines = [
        f"MÉTRICAS META ADS — {date_range} (breakdown: {breakdown})",
        "═" * 50,
        "",
    ]

    total_spend = 0.0
    total_conversions = 0
    total_revenue = 0.0

    for row in rows:
        spend = float(row.get("spend", 0))
        impressions = int(row.get("impressions", 0))
        clicks = int(row.get("clicks", 0))
        ctr = float(row.get("ctr", 0))
        cpc = float(row.get("cpc", 0))
        cpm = float(row.get("cpm", 0))
        frequency = float(row.get("frequency", 0))
        reach = int(row.get("reach", 0))

        conversions = _sum_action(row.get("actions", []))
        revenue = _sum_action(row.get("action_values", []))
        roas = revenue / spend if spend > 0 else 0.0
        cpa = spend / conversions if conversions > 0 else 0.0

        total_spend += spend
        total_conversions += conversions
        total_revenue += revenue

        name = _row_name(row, breakdown)
        lines += [
            f"{'Campanha' if breakdown == 'campaign' else breakdown.capitalize()}: \"{name}\"",
            f"  ID: {_row_id(row, breakdown)}",
            f"  Investimento: R$ {spend:,.2f}  |  Impressões: {impressions:,}  |  Cliques: {clicks:,}",
            f"  CTR: {ctr:.2f}%  |  CPC: R$ {cpc:.2f}  |  CPM: R$ {cpm:.2f}",
            f"  Alcance: {reach:,}  |  Frequência: {frequency:.1f}x",
            f"  Conversões: {conversions}  |  CPA: R$ {cpa:.2f}  |  ROAS: {roas:.1f}x",
            f"  Receita atribuída: R$ {revenue:,.2f}",
            "",
        ]

    total_roas = total_revenue / total_spend if total_spend > 0 else 0.0
    total_cpa = total_spend / total_conversions if total_conversions > 0 else 0.0
    lines += [
        "TOTAL DO PERÍODO",
        f"  Investimento: R$ {total_spend:,.2f}  |  Conversões: {total_conversions}",
        f"  CPA médio: R$ {total_cpa:.2f}  |  ROAS consolidado: {total_roas:.1f}x",
        f"  Receita atribuída: R$ {total_revenue:,.2f}",
    ]

    return "\n".join(lines)


def _sum_action(action_list: list) -> float:
    purchase_types = {
        "purchase",
        "offsite_conversion.fb_pixel_purchase",
        "omni_purchase",
    }
    return sum(
        float(a.get("value", 0))
        for a in action_list
        if a.get("action_type") in purchase_types
    )


def _row_name(row: dict, breakdown: str) -> str:
    if breakdown in ("campaign", "age", "gender", "placement"):
        return row.get("campaign_name", row.get("campaign_id", "—"))
    if breakdown == "adset":
        return row.get("adset_name", row.get("adset_id", "—"))
    if breakdown == "ad":
        return row.get("ad_name", row.get("ad_id", "—"))
    return "—"


def _row_id(row: dict, breakdown: str) -> str:
    if breakdown in ("campaign", "age", "gender", "placement"):
        return row.get("campaign_id", "—")
    if breakdown == "adset":
        return row.get("adset_id", "—")
    if breakdown == "ad":
        return row.get("ad_id", "—")
    return "—"


def _update_campaign(tool_input: dict) -> str:
    if not META_ACCESS_TOKEN:
        return "[ERRO] META_ACCESS_TOKEN não configurado no .env"

    campaign_id = tool_input.get("campaign_id")
    if not campaign_id:
        return "[ERRO] campaign_id é obrigatório."

    payload: dict = {"access_token": META_ACCESS_TOKEN}

    changes = []
    if "status" in tool_input:
        payload["status"] = tool_input["status"]
        changes.append(f"status → {tool_input['status']}")

    if "daily_budget" in tool_input:
        # Meta API expects budget in cents
        payload["daily_budget"] = int(tool_input["daily_budget"] * 100)
        changes.append(f"orçamento diário → R$ {tool_input['daily_budget']:.2f}")

    if "bid_amount" in tool_input:
        payload["bid_amount"] = int(tool_input["bid_amount"] * 100)
        changes.append(f"lance → R$ {tool_input['bid_amount']:.2f}")

    if len(payload) == 1:
        return "[ERRO] Nenhuma alteração especificada além do access_token."

    url = f"{_BASE_URL}/{campaign_id}"
    r = requests.post(url, data=payload, timeout=30)
    data = r.json()

    if "error" in data:
        return f"[ERRO Meta API] {data['error'].get('message', data['error'])}"

    success = data.get("success", False)
    if success:
        return f"Campanha {campaign_id} atualizada com sucesso: {', '.join(changes)}"
    return f"[AVISO] Resposta inesperada da API: {data}"
