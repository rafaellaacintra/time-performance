import anthropic
from agents import (
    EnvironmentalAnalyst,
    MediaAnalyst,
    CreativeAnalyst,
    RevOpsAnalyst,
    MarketingHead,
    EcommerceAnalyst,
)


class Orchestrator:
    """
    Coordinates the multi-agent workflow for a daily performance review.

    daily_report() runs a structured pipeline:
      1. Environmental + Media + RevOps analyses (independent, can be read sequentially)
      2. Creative analysis (uses media context)
      3. E-commerce analysis (independent)
      4. Marketing Head validation of the combined media plan
      5. Execution of approved actions by Media Analyst
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.environmental = EnvironmentalAnalyst(self.client)
        self.media = MediaAnalyst(self.client)
        self.creative = CreativeAnalyst(self.client)
        self.revops = RevOpsAnalyst(self.client)
        self.head = MarketingHead(self.client)
        self.ecommerce = EcommerceAnalyst(self.client)

    def daily_report(self, category: str = "", period: str = "morning") -> dict:
        """
        Run the full daily performance workflow.

        Returns a dict with each agent's output and the final execution result.
        """
        print("\n" + "=" * 60)
        print("RELATÓRIO DIÁRIO — TIME DE PERFORMANCE")
        print("=" * 60)

        # Phase 1: Independent analyses
        print("\n[1/5] Análise Ambiental...")
        env_report = self.environmental.analyze(category=category)
        _print_section("ANÁLISE AMBIENTAL", env_report)

        print("\n[2/5] Análise de Mídia...")
        media_plan = self.media.analyze(period=period)
        _print_section("ANÁLISE DE MÍDIA", media_plan)

        print("\n[3/5] Análise RevOps...")
        revops_report = self.revops.analyze()
        _print_section("ANÁLISE REVOPS", revops_report)

        # Phase 2: Creative analysis with media context
        print("\n[3/5] Análise Criativa...")
        creative_report = self.creative.analyze()
        _print_section("ANÁLISE CRIATIVA", creative_report)

        # Phase 3: E-commerce analysis
        print("\n[4/5] Análise de E-commerce...")
        ecommerce_report = self.ecommerce.analyze()
        _print_section("ANÁLISE DE E-COMMERCE", ecommerce_report)

        # Phase 4: Marketing Head validates the media plan
        print("\n[5/5] Validação pelo Head de Marketing...")
        combined_context = (
            f"ANÁLISE AMBIENTAL:\n{env_report}\n\n"
            f"ANÁLISE REVOPS:\n{revops_report}\n\n"
            f"ANÁLISE DE E-COMMERCE:\n{ecommerce_report}"
        )
        validation = self.head.validate(plan=media_plan, context=combined_context)
        _print_section("VALIDAÇÃO DO HEAD DE MARKETING", validation)

        # Phase 5: Execute approved actions
        execution_result = ""
        if _plan_approved(validation):
            print("\n[EXECUÇÃO] Executando ajustes aprovados...")
            execution_result = self.media.execute_approved_actions(
                approved_plan=_extract_approved_actions(validation)
            )
            _print_section("RESULTADO DA EXECUÇÃO", execution_result)
        else:
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
        """Run a single agent by name. Useful for on-demand analysis."""
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
        return agents[agent_name]()


def _print_section(title: str, content: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print("─" * 60)
    print(content)


def _plan_approved(validation: str) -> bool:
    """Heuristic: check if the validation text signals at least partial approval."""
    upper = validation.upper()
    return "APROVADO" in upper and "REPROVADO" not in upper.split("APROVADO")[0]


def _extract_approved_actions(validation: str) -> str:
    """
    Return the approved actions section from the validation text.
    Falls back to the full validation if the section isn't clearly delimited.
    """
    markers = ["AÇÕES APROVADAS", "ACOES APROVADAS", "APROVADO"]
    for marker in markers:
        idx = validation.upper().find(marker)
        if idx != -1:
            return validation[idx:]
    return validation
