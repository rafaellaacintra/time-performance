TRAY_TOOLS = [
    {
        "name": "tray_get_store_metrics",
        "description": (
            "Busca métricas de performance da loja no Tray: pedidos, receita, ticket médio, "
            "carrinhos abandonados e principais produtos. Use para monitorar a saúde do e-commerce "
            "e identificar oportunidades de recuperação de receita."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "enum": ["today", "yesterday", "last_7d", "last_30d"],
                    "description": "Período das métricas.",
                },
            },
            "required": ["date_range"],
        },
    },
    {
        "name": "tray_get_products",
        "description": (
            "Busca dados do catálogo de produtos no Tray: preço, estoque, vendas e taxa de conversão. "
            "Use para identificar produtos com alto potencial, baixo estoque crítico ou "
            "oportunidades de vitrine e cross-sell."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filtro por categoria de produto (opcional).",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["sales", "revenue", "views", "conversion_rate", "stock"],
                    "description": "Ordenar produtos por esta métrica.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Número de produtos a retornar (padrão: 10).",
                },
                "in_stock_only": {
                    "type": "boolean",
                    "description": "Retornar apenas produtos com estoque disponível.",
                },
            },
            "required": [],
        },
    },
]


def execute_tray_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "tray_get_store_metrics":
        date_range = tool_input.get("date_range", "last_7d")
        return f"""
MÉTRICAS TRAY — {date_range}
══════════════════════════════════════════════════

PEDIDOS E RECEITA
  Pedidos finalizados: 542  |  Receita bruta: R$ 54.230,90
  Ticket médio: R$ 100,06  |  Itens por pedido: 2,3

CARRINHOS ABANDONADOS
  Carrinhos criados: 2.790  |  Abandonados: 2.248 (80,6% taxa de abandono)
  Receita recuperável estimada: R$ 22.480,00
  E-mails de recuperação enviados: 1.124  |  Recuperados: 89 (7,9%)

NOVOS vs RECORRENTES
  Clientes novos: 71%  |  Clientes recorrentes: 29%
  LTV médio clientes recorrentes: R$ 420,00

TOP 3 PRODUTOS DO PERÍODO
  1. Produto A — 89 unidades — R$ 8.900,00
  2. Produto B — 73 unidades — R$ 5.110,00
  3. Produto C — 61 unidades — R$ 4.880,00
"""

    if tool_name == "tray_get_products":
        sort_by = tool_input.get("sort_by", "sales")
        limit = tool_input.get("limit", 10)
        category = tool_input.get("category", "todos")
        return f"""
CATÁLOGO TRAY — top {limit} por {sort_by} (categoria: {category})
══════════════════════════════════════════════════

  # | Produto    | Preço    | Estoque | Vendas 30d | Conv.  | Margem
  ──┼────────────┼──────────┼─────────┼────────────┼────────┼───────
  1 | Produto A  | R$100,00 |     145 |         89 |  4,2%  |  62%
  2 | Produto B  | R$ 70,00 |      89 |         73 |  3,8%  |  55%
  3 | Produto C  | R$ 80,00 |     234 |         61 |  2,9%  |  58%
  4 | Produto D  | R$150,00 |      12 |         45 |  5,1%  |  70%  ← estoque crítico
  5 | Produto E  | R$ 45,00 |     567 |         38 |  1,4%  |  48%
  6 | Produto F  | R$200,00 |      67 |         32 |  3,3%  |  75%
  7 | Produto G  | R$ 35,00 |     890 |         28 |  0,9%  |  40%
  8 | Produto H  | R$120,00 |      34 |         25 |  4,8%  |  68%
  9 | Produto I  | R$ 55,00 |     123 |         21 |  2,1%  |  52%
 10 | Produto J  | R$ 90,00 |      78 |         18 |  2,6%  |  60%

ALERTAS
  Produto D com estoque crítico (12 un.) e alta conversão (5,1%) — repor urgente
  Produto E com conversão baixa (1,4%) — revisar página, fotos e descrição
"""

    return f"[ERRO] Ferramenta Tray '{tool_name}' não reconhecida."
