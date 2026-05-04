from openai import OpenAI
from config import OPENAI_API_KEY
from agents import (
    EnvironmentalAnalyst,
    MediaAnalyst,
    CreativeAnalyst,
    RevOpsAnalyst,
    MarketingHead,
    EcommerceAnalyst,
)
from tools import notion_send_report


class Orchestrator:
    """
    Coordinates the multi-agent workflow for a daily performance review.

    daily_report() pipeline:
      1. Environmental, Media, RevOps analyses
      2. Creative analysis
      3. E-commerce analysis
      4. Marketing Head validates the media plan
      5. Execute approved actions (if plan is approved)

    Each step's output is sent to Notion automatically if configured.
    """

    def __init__(self):
        client = OpenAI(api_key=OPENAI_API_KEY)
        self.environmental = EnvironmentalAnalyst(client)
        self.media = MediaAnalyst(client)
        self.creative = CreativeAnalyst(client)
        self.revops = RevOpsAnalyst(client)
        self.head = MarketingHead(client)
        self.ecommerce = EcommerceAnalyst(client)

    def daily_report(self, category: str = "", period: str = "morning") -> dict:
        """Run the full daily performance workflow."""
        print("\n" + "=" * 60)
        print("RELATÓRIO DIÁRIO — TIME DE PERFORMANCE")
        print("=" * 60)

        print("\n[1/6] Análise Ambiental...")
        env_report = self.environmental.analyze(category=category)
        _print_section("ANÁLISE AMBIENTAL", env_report)
        _notion("environmental", env_report, "generated", period)

        print("\n[2/6] Análise de Mídia...")
        media_plan = self.media.analyze(period=period)
        _print_section("ANÁLISE DE MÍDIA", media_plan)
        _notion("media", media_plan, "pending_approval", period)

        print("\n[3/6] Análise RevOps...")
        revops_report = self.revops.analyze()
        _print_section("ANÁLISE REVOPS", revops_report)
        _notion("revops", revops_report, "generated", period)

        print("\n[4/6] Análise Criativa...")
        creative_report = self.creative.analyze()
        _print_section("ANÁLISE CRIATIVA", creative_report)
        _notion("creative", creative_report, "pending_approval", period)

        print("\n[5/6] Análise de E-commerce...")
        ecommerce_report = self.ecommerce.analyze()
        _print_section("ANÁLISE DE E-COMMERCE", ecommerce_report)
        _notion("ecommerce", ecommerce_report, "generated", period)

        print("\n[6/6] Validação pelo Head de Marketing...")
        combined_context = (
            f"ANÁLISE AMBIENTAL:\n{env_report}\n\n"
            f"ANÁLISE REVOPS:\n{revops_report}\n\n"
            f"ANÁLISE DE E-COMMERCE:\n{ecommerce_report}"
        )
        validation = self.head.validate(plan=media_plan, context=combined_context)
        _print_section("VALIDAÇÃO DO HEAD DE MARKETING", validation)

        execution_result = ""
        if _plan_approved(validation):
            _notion("validation", validation, "approved", period)
            print("\n[EXECUÇÃO] Executando ajustes aprovados...")
            execution_result = self.media.execute_approved_actions(
                approved_plan=_extract_approved_actions(validation)
            )
            _print_section("RESULTADO DA EXECUÇÃO", execution_result)
            _notion("execution", execution_result, "executed", period)
        else:
            _notion("validation", validation, "rejected", period)
            print("\n[EXECUÇÃO] Plano não aprovado para execução automática.")
            print("Revise as recomendações do Head de Marketing e submeta novo plano.")

        print("\n" + "=" * 60)
        print("FIM DO RELATÓRIO DIÁRIO")
        print("=" * 60 + "\n")

        return {
            "environmental": env_report,
            "media_plan": media_plan,
            "revops": revops_report,
            "creative": creative_report,
            "ecommerce": ecommerce_report,
            "validation": validation,
            "execution": execution_result,
        }

    def run_agent(self, agent_name: str, **kwargs) -> str:
        """Run a single agent by name with optional Notion publishing."""
        agents = {
            "environmental": lambda: self.environmental.analyze(**kwargs),
            "media": lambda: self.media.analyze(**kwargs),
            "creative": lambda: self.creative.analyze(**kwargs),
            "revops": lambda: self.revops.analyze(**kwargs),
            "ecommerce": lambda: self.ecommerce.analyze(**kwargs),
        }
        if agent_name not in agents:
            raise ValueError(
                f"Agente '{agent_name}' não encontrado. "
                f"Disponíveis: {list(agents.keys())}"
            )
        result = agents[agent_name]()
        period = kwargs.get("period", None)
        _notion(agent_name, result, "generated", period)
        return result


def _notion(report_type: str, content: str, status: str, period=None) -> None:
    url = notion_send_report(report_type=report_type, content=content, status=status, period=period)
    if url.startswith("http"):
        print(f"  [Notion] Página criada: {url}")
    elif "[Notion]" in url:
        print(f"  {url}")


def _print_section(title: str, content: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print("─" * 60)
    print(content)


def _plan_approved(validation: str) -> bool:
    upper = validation.upper()
    return "APROVADO" in upper and "REPROVADO" not in upper.split("APROVADO")[0]


def _extract_approved_actions(validation: str) -> str:
    markers = ["AÇÕES APROVADAS", "ACOES APROVADAS", "APROVADO"]
    for marker in markers:
        idx = validation.upper().find(marker)
        if idx != -1:
            return validation[idx:]
    return validation
