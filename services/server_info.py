from fastapi import APIRouter, Request
from core.utils.env import EnvConfig
from core.utils.config import config
from core.version import version
from core.utils.tools import (
    extract_tool_functions,
    format_function_name,
    group_tools_by_tag,
)
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os


templates_directory = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=templates_directory)

# Create a router with a general tag for API documentation organization
router = APIRouter()

server_info_config = config.get("INFO_SERVICE_CONFIG", {})
main_url = server_info_config.get("service_url", "/")
privacy_policy_url = server_info_config.get("privacy_policy_url", "")
terms_of_service_url = server_info_config.get("terms_of_service_url", "")


@router.get(main_url)
async def status(request: Request):
    """Status endpoint that returns the current server status"""

    login_url = server_info_config.get("login_url", "")
    site_url = server_info_config.get("site_url", "")
    site_name = server_info_config.get("site_name", site_url)
    header_params = server_info_config.get("header_params", {})  # Get header parameters
    notes = server_info_config.get("notes", [])
    current_directory = os.getcwd()
    tools_directory = os.path.join(current_directory, "app/tools")
    functions_info = []

    if server_info_config.get("show_tools_specs", False):
        functions_info = extract_tool_functions(tools_directory)
        functions_info = group_tools_by_tag(functions_info)

    return templates.TemplateResponse(
        "server_info.html",
        {
            "request": request,
            "version": version,
            "logo_url": EnvConfig.get("SERVICES_LOGO_URL", ""),
            "favicon_url": EnvConfig.get("SERVICES_FAVICON_URL", ""),
            "login_url": login_url,
            "site_url": site_url,
            "site_name": site_name,
            "mcp_server_url": f"{EnvConfig.get('MCP_SERVER_URL')}",
            "mcp_server_name": EnvConfig.get("SERVER_NAME"),
            "functions_info": functions_info,  # Pass the functions_info to the template
            "format_function_name": format_function_name,  # Pass the formatting function to the template
            "header_params": header_params,  # Pass the header parameters to the template
            "notes": notes,
            "privacy_policy_url": privacy_policy_url,
            "terms_of_service_url": terms_of_service_url,
        },
    )
