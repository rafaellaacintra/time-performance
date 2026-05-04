from .meta_ads_api import META_ADS_TOOLS, execute_meta_ads_tool
from .ga4_api import GA4_TOOLS, execute_ga4_tool
from .tray_api import TRAY_TOOLS, execute_tray_tool
from .web_search import WEB_SEARCH_TOOLS, execute_web_search_tool
from .notion_reporter import send_report as notion_send_report

ALL_TOOLS = META_ADS_TOOLS + GA4_TOOLS + TRAY_TOOLS + WEB_SEARCH_TOOLS

_TOOL_REGISTRY: dict = {}
for _tool in META_ADS_TOOLS:
    _TOOL_REGISTRY[_tool["name"]] = execute_meta_ads_tool
for _tool in GA4_TOOLS:
    _TOOL_REGISTRY[_tool["name"]] = execute_ga4_tool
for _tool in TRAY_TOOLS:
    _TOOL_REGISTRY[_tool["name"]] = execute_tray_tool
for _tool in WEB_SEARCH_TOOLS:
    _TOOL_REGISTRY[_tool["name"]] = execute_web_search_tool


def execute_tool(tool_name: str, tool_input: dict) -> str:
    executor = _TOOL_REGISTRY.get(tool_name)
    if not executor:
        return f"[ERRO] Ferramenta '{tool_name}' não encontrada no registro."
    return executor(tool_name, tool_input)
