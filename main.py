#!/usr/bin/env python3
"""
CLI for the multi-agent paid traffic management system.
Run with: python main.py
"""
import sys
from orchestrator import Orchestrator


def print_header():
    print("\n" + "=" * 60)
    print("  TIME DE PERFORMANCE DIGITAL — TRÁFEGO PAGO")
    print("=" * 60)


def print_menu():
    print("\nEscolha uma opção:")
    print("  1. Relatório diário completo (todos os agentes)")
    print("  2. Análise ambiental de mercado")
    print("  3. Análise de mídia (Meta Ads)")
    print("  4. Análise criativa")
    print("  5. Análise RevOps (funil completo)")
    print("  6. Análise de e-commerce (Tray + GA4)")
    print("  7. Validar plano com Head de Marketing")
    print("  0. Sair")
    print()


def get_input(prompt: str, default: str = "") -> str:
    value = input(prompt).strip()
    return value if value else default


def run_full_report(orchestrator: Orchestrator):
    category = get_input("Categoria/nicho (deixe em branco para genérico): ")
    period_input = get_input("Período [morning/afternoon] (padrão: morning): ", "morning")
    period = period_input if period_input in ("morning", "afternoon") else "morning"
    orchestrator.daily_report(category=category, period=period)


def run_environmental(orchestrator: Orchestrator):
    category = get_input("Categoria/nicho (deixe em branco para genérico): ")
    focus = get_input("Foco específico (deixe em branco para análise completa): ")
    result = orchestrator.environmental.analyze(category=category, focus=focus)
    print("\n" + result)


def run_media(orchestrator: Orchestrator):
    period_input = get_input("Período [morning/afternoon] (padrão: morning): ", "morning")
    period = period_input if period_input in ("morning", "afternoon") else "morning"
    result = orchestrator.media.analyze(period=period)
    print("\n" + result)


def run_creative(orchestrator: Orchestrator):
    focus = get_input("Foco específico (deixe em branco para análise completa): ")
    result = orchestrator.creative.analyze(focus=focus)
    print("\n" + result)


def run_revops(orchestrator: Orchestrator):
    focus = get_input("Foco específico (deixe em branco para análise completa): ")
    result = orchestrator.revops.analyze(focus=focus)
    print("\n" + result)


def run_ecommerce(orchestrator: Orchestrator):
    focus = get_input("Foco específico (deixe em branco para análise completa): ")
    result = orchestrator.ecommerce.analyze(focus=focus)
    print("\n" + result)


def run_validate(orchestrator: Orchestrator):
    print("Cole o plano de ajustes a ser validado (finalize com uma linha contendo apenas 'FIM'):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "FIM":
            break
        lines.append(line)
    plan = "\n".join(lines)
    if not plan.strip():
        print("Nenhum plano fornecido.")
        return
    context = get_input("Contexto adicional (deixe em branco se não houver): ")
    result = orchestrator.head.validate(plan=plan, context=context)
    print("\n" + result)


def main():
    print_header()

    try:
        orchestrator = Orchestrator()
    except Exception as exc:
        print(f"\n[ERRO] Falha ao inicializar o orquestrador: {exc}")
        print("Verifique se ANTHROPIC_API_KEY está configurada no arquivo .env")
        sys.exit(1)

    actions = {
        "1": run_full_report,
        "2": run_environmental,
        "3": run_media,
        "4": run_creative,
        "5": run_revops,
        "6": run_ecommerce,
        "7": run_validate,
    }

    while True:
        print_menu()
        choice = get_input("Opção: ")

        if choice == "0":
            print("\nAté logo!\n")
            break

        action = actions.get(choice)
        if action:
            try:
                action(orchestrator)
            except KeyboardInterrupt:
                print("\n\n[Interrompido pelo usuário]")
            except Exception as exc:
                print(f"\n[ERRO] {exc}")
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
