"""
Notion reporter: creates a page in the configured database for each agent report.
Requires NOTION_TOKEN and NOTION_DATABASE_ID in .env.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

import requests

from config import NOTION_TOKEN, NOTION_DATABASE_ID

_BASE_URL = "https://api.notion.com/v1"
_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# Valid values must match the select options in the Notion database exactly.
REPORT_TYPES = {
    "daily": "Relatório Diário",
    "environmental": "Análise Ambiental",
    "media": "Análise de Mídia",
    "creative": "Análise Criativa",
    "revops": "RevOps",
    "ecommerce": "E-commerce",
    "validation": "Validação Head",
    "execution": "Execução",
}

STATUS_OPTIONS = {
    "generated": "Gerado",
    "pending_approval": "Aguardando Aprovação",
    "approved": "Aprovado",
    "executed": "Executado",
    "rejected": "Reprovado",
}


def send_report(
    report_type: str,
    content: str,
    status: str = "generated",
    period: Optional[str] = None,
    extra_title: str = "",
) -> str:
    """
    Create a Notion page in the configured database.

    Returns the URL of the created page, or an error message.
    """
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        return "[Notion] NOTION_TOKEN ou NOTION_DATABASE_ID não configurados — pulando envio."

    today = date.today().strftime("%d/%m/%Y")
    type_label = REPORT_TYPES.get(report_type, report_type)
    period_label = f" — {period}" if period else ""
    extra = f" — {extra_title}" if extra_title else ""
    title = f"{type_label}{period_label}{extra} | Vista Biio | {today}"

    properties = _build_properties(title, report_type, status, period)
    blocks = _text_to_blocks(content)

    # Notion allows max 100 children on create; append the rest afterwards.
    first_batch = blocks[:100]
    remaining = blocks[100:]

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties,
        "children": first_batch,
    }

    resp = requests.post(f"{_BASE_URL}/pages", json=payload, headers=_headers(), timeout=30)
    data = resp.json()

    if resp.status_code != 200:
        msg = data.get("message", str(data))
        return f"[Notion ERRO] {resp.status_code}: {msg}"

    page_id = data["id"]
    page_url = data.get("url", f"https://notion.so/{page_id.replace('-', '')}")

    if remaining:
        _append_blocks(page_id, remaining)

    return page_url


def _headers() -> dict:
    # Rebuild each call so token changes in tests take effect.
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def _append_blocks(page_id: str, blocks: list) -> None:
    for i in range(0, len(blocks), 100):
        batch = blocks[i : i + 100]
        requests.patch(
            f"{_BASE_URL}/blocks/{page_id}/children",
            json={"children": batch},
            headers=_headers(),
            timeout=30,
        )


def _build_properties(title: str, report_type: str, status: str, period: Optional[str]) -> dict:
    props: dict = {
        "Nome": {"title": [{"text": {"content": title}}]},
        "Data": {"date": {"start": date.today().isoformat()}},
        "Tipo": {"select": {"name": REPORT_TYPES.get(report_type, report_type)}},
        "Status": {"select": {"name": STATUS_OPTIONS.get(status, status)}},
    }
    if period:
        props["Período"] = {"select": {"name": "Manhã" if period == "morning" else "Tarde"}}
    return props


def _text_to_blocks(text: str) -> list:
    blocks = []
    for line in text.splitlines():
        line = line.rstrip()

        if not line:
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": []}})
            continue

        # Separator lines (═══ ─── ===)
        if re.fullmatch(r"[═─=\-\s]+", line):
            blocks.append({"type": "divider", "divider": {}})
            continue

        # Section headings: all-caps line, or "1. TÍTULO" pattern
        is_heading = line.isupper() or bool(re.match(r"^\d+\.\s+[A-ZÁÉÍÓÚÃÕÂÊÎÔÛÇ]", line))

        for chunk in _split_2000(line):
            if is_heading:
                blocks.append({
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": chunk}}]},
                })
            else:
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]},
                })

    return blocks


def _split_2000(text: str) -> list[str]:
    return [text[i : i + 2000] for i in range(0, max(len(text), 1), 2000)]
