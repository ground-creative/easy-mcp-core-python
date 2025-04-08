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
    seen_functions = set()  # Set to track unique function names

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
            # Use exec to import the module and access its functions
            with open(file_path, "r") as file:
                file_content = file.read()
                exec(
                    file_content, globals()
                )  # Execute the file content in the global context

                # Now, iterate over all functions in the globals()
                for name, func in globals().items():
                    if (
                        callable(func)
                        and name.endswith("_tool")
                        and name not in seen_functions
                        and not getattr(func, "_exclude", False)  # Check for exclusion
                    ):
                        found_tool_function = True  # Mark that we found a tool function
                        function_info = {
                            "name": name,
                            "params": [],
                            "description": func.__doc__ or "No description available",
                            "tags": getattr(func, "_tags", ["General"])[
                                0
                            ],  # Get the single tag or default to "General"
                        }

                        # Preprocess the description to replace newlines with <br>
                        function_info["description"] = function_info[
                            "description"
                        ].replace("\n", "<br>")

                        # Remove the first newline if the description starts with a newline
                        if function_info["description"].startswith("<br>"):
                            function_info["description"] = function_info["description"][
                                4:
                            ]  # Remove the first <br>

                        # Extract parameter details
                        for arg in func.__annotations__:
                            param_info = {
                                "name": arg,
                                "type": str(func.__annotations__[arg]),
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
                        seen_functions.add(name)  # Add the function name to the set

    # If no tool functions were found, log a warning
    if not found_tool_function:
        logger.warning(
            f"No '_tool' prefixed functions found in directory '{directory}'."
        )

    return tool_functions


def group_tools_by_tag(
    tool_functions: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    grouped_tools = {}

    # Group tools by their tags
    for tool in tool_functions:
        tag = tool["tags"]  # Assuming tags are stored as a string
        if tag not in grouped_tools:
            grouped_tools[tag] = []  # Initialize the list for the tag
        grouped_tools[tag].append(tool)  # Add the tool to the corresponding tag list

    # Sort the dictionary by tag (keys) alphabetically
    sorted_grouped_tools = dict(sorted(grouped_tools.items()))

    # Sort functions within each tag alphabetically by their names
    for tag in sorted_grouped_tools:
        sorted_grouped_tools[tag].sort(
            key=lambda x: x["name"].lower()
        )  # Sort alphabetically, case insensitive

    return sorted_grouped_tools


def doc_tag(tag: str):
    """Add a single tag to the tool function for service info page"""

    def decorator(func):
        func._tags = (tag,)  # Store the tag as a tuple
        return func

    return decorator


def doc_exclude(func):
    """Decorator to exclude a function from the tool functions list."""
    func._exclude = True  # Set an attribute to indicate exclusion
    return func


def format_function_name(func_name: str) -> str:
    # Remove the '_tool' suffix
    if func_name.endswith("_tool"):
        func_name = func_name[:-5]  # Remove the last 5 characters
    # Replace underscores with spaces and capitalize each word
    return " ".join(word.capitalize() for word in func_name.split("_"))
