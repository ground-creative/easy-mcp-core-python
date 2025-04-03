import importlib, os, ast
from typing import List, Dict, Any
from core.utils.logger import logger
from core.utils.env import EnvConfig


# Dynamically discover and register tools
def register_tools(mcp):
    tools_directory = os.path.join(
        os.path.dirname(__file__), "..", "..", "app", "tools"
    )

    if os.path.exists(tools_directory) and os.path.isdir(tools_directory):
        for filename in os.listdir(tools_directory):

            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"app.tools.{filename[:-3]}"  # Remove '.py' extension
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # Check if the attribute is a callable function and not a class
                        if (
                            callable(attr)
                            and hasattr(attr, "__name__")
                            and "tool" in attr.__name__.lower()
                            and not isinstance(attr, type)  # Ensure it's not a class
                        ):
                            mcp.tool()(attr)  # Register the tool dynamically
                            logger.info(f"🛠️  Registered tool: {attr.__name__}")

                except Exception as e:
                    logger.error(
                        f"❌ Failed to register tool from {filename}: {e}",
                        exc_info=EnvConfig.DEBUG_MCP,
                    )

    return mcp


def extract_tool_functions(directory: str) -> List[Dict[str, Any]]:
    tool_functions = []

    # Check if the directory exists
    if not os.path.exists(directory):
        logger.warning(f"The directory '{directory}' does not exist.")
        return tool_functions  # Return empty list if directory does not exist

    # Flag to check if any tool functions are found
    found_tool_function = False

    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as file:
                file_content = file.read()
                # Parse the file content into an AST
                tree = ast.parse(file_content)

                # Iterate over all functions in the AST
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.endswith(
                        "_tool"
                    ):
                        found_tool_function = True  # Mark that we found a tool function
                        function_info = {
                            "name": node.name,
                            "params": [],
                            "description": ast.get_docstring(node)
                            or "No description available",
                        }

                        # Preprocess the description to replace newlines with <br>
                        function_info["description"] = function_info[
                            "description"
                        ].replace("\n", "<br>")

                        # Extract parameter details
                        for arg in node.args.args:
                            param_info = {
                                "name": arg.arg,
                                "type": (
                                    ast.unparse(arg.annotation)
                                    if arg.annotation
                                    else "No type"
                                ),
                                "description": None,  # Placeholder for description
                            }
                            # Check for parameter description in the docstring
                            if function_info["description"]:
                                docstring_lines = function_info[
                                    "description"
                                ].splitlines()
                                for line in docstring_lines:
                                    if line.startswith(f"- {param_info['name']}"):
                                        param_info["description"] = line.split(": ", 1)[
                                            -1
                                        ].strip()
                                        break
                            function_info["params"].append(param_info)

                        tool_functions.append(function_info)

    # If no tool functions were found, log a warning
    if not found_tool_function:
        logger.warning(
            f"No '_tool' prefixed functions found in directory '{directory}'."
        )

    return tool_functions


def format_function_name(func_name: str) -> str:
    # Remove the '_tool' suffix
    if func_name.endswith("_tool"):
        func_name = func_name[:-5]  # Remove the last 5 characters
    # Replace underscores with spaces and capitalize each word
    return " ".join(word.capitalize() for word in func_name.split("_"))
