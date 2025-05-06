from typing import Callable, Any, Dict

def add_template_globals(env: Any, globals_dict: Dict[str, Callable]) -> None:
    """Add global functions to Jinja environment.
    
    Args:
        env: The Jinja2 environment
        globals_dict: Dictionary mapping names to functions
    """
    for name, func in globals_dict.items():
        env.globals[name] = func