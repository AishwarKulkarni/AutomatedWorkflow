AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_workflow",
            "description": (
                "Read the full instructions and steps of a specific workflow from the workflow catalog. "
                "Call this tool when the user's request matches an available workflow so you can see "
                "the exact sequence of steps to execute."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {
                        "type": "string",
                        "description": "The name of the workflow to read (e.g. 'write_letter').",
                    },
                },
                "required": ["workflow_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_actions",
            "description": (
                "Execute an array of desktop automation actions sequentially in a single batch. "
                "Actions will run in order, and execution halts immediately if any action fails. "
                "Use this tool to execute the compiled workflow steps."
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
                                    "description": "Name of the AHK action to execute (e.g. 'FocusApp', 'SendShortcut', 'Paste', 'TypeText', 'CopyToClipboard').",
                                },
                                "args": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Positional arguments for the action.",
                                },
                                "target_app": {
                                    "type": "string",
                                    "description": "Optional app variable name (e.g. 'App_Notepad', 'App_Brave').",
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
