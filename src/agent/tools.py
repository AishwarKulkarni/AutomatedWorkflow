AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_actions",
            "description": (
                "Execute an array of desktop automation actions sequentially. "
                "They will be executed in order, and you will receive a structured result "
                "containing the outcomes. Call this tool to batch your actions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "actions": {
                        "type": "array",
                        "description": "An array of actions to execute sequentially.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action_name": {
                                    "type": "string",
                                    "description": "Name of the action to execute.",
                                },
                                "args": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Positional arguments for the action.",
                                },
                                "target_app": {
                                    "type": "string",
                                    "description": "Optional app variable name (e.g. 'App_Notepad').",
                                },
                            },
                            "required": ["action_name", "args"],
                        },
                    },
                },
                "required": ["actions"],
            },
        },
    },
]
