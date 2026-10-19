import os
import re
import logging

logger = logging.getLogger(__name__)

WORKFLOWS_DIR = os.path.join(os.getcwd(), "workflows")

def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extracts simple key-value YAML frontmatter and body."""
    metadata = {}
    body = content
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            for line in fm_text.splitlines():
                line = line.strip()
                if line and ":" in line and not line.startswith("#"):
                    k, v = line.split(":", 1)
                    metadata[k.strip().lower()] = v.strip().strip("'\"")
    return metadata, body

def scan_workflows() -> dict[str, dict]:
    """
    Scans the workflows/ directory and returns metadata for all .md files.
    Tolerates formatting errors without raising exceptions.
    """
    workflows = {}
    if not os.path.exists(WORKFLOWS_DIR):
        try:
            os.makedirs(WORKFLOWS_DIR, exist_ok=True)
        except OSError as e:
            logger.warning(f"Could not create workflows directory: {e}")
            return workflows

    for filename in os.listdir(WORKFLOWS_DIR):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(WORKFLOWS_DIR, filename)
        stem = os.path.splitext(filename)[0]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata, body = _parse_frontmatter(content)
            name = metadata.get("name", stem).strip()
            description = metadata.get("description", "").strip()

            if not description:
                # Fallback: grab the first non-header sentence from body
                for line in body.splitlines():
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#") and not cleaned.startswith("-"):
                        description = cleaned
                        break
                if not description:
                    description = f"Workflow for {name}"

            workflows[name.lower()] = {
                "name": name,
                "file_path": file_path,
                "description": description,
                "content": content
            }
        except Exception as e:
            logger.warning(f"Failed to parse workflow file {filename}: {e}")

    return workflows

def get_workflow_catalog_prompt() -> str:
    """Generates the Available Workflows block for the LLM system prompt."""
    workflows = scan_workflows()
    if not workflows:
        return (
            "## Available Workflows\n"
            "Currently no workflows are defined in the workflows/ directory. "
            "You cannot perform desktop automation actions until a workflow is created.\n\n"
        )

    catalog = [
        "## Available Workflows\n",
        "You are strictly allowed to execute desktop automation ONLY if the user request matches one of these workflows:\n"
    ]
    for wf in workflows.values():
        catalog.append(f"- **{wf['name']}**: {wf['description']}\n")

    catalog.append(
        "\nSTRICT RULE: If the user asks you to perform a task that does NOT match any workflow above, "
        "politely explain that you do not have a workflow for that yet, list the workflows you can do, "
        "and DO NOT call any tools.\n\n"
    )
    return "".join(catalog)

def read_workflow(workflow_name: str) -> dict:
    """Reads and returns the workflow markdown content."""
    workflows = scan_workflows()
    key = workflow_name.strip().lower()

    # Exact match or match by stem
    matched = workflows.get(key)
    if not matched:
        # Check if user passed filename or partial name
        for k, v in workflows.items():
            if k in key or key in k:
                matched = v
                break

    if not matched:
        available = ", ".join(workflows.keys()) if workflows else "None"
        return {
            "success": False,
            "error": f"Workflow '{workflow_name}' not found. Available workflows: {available}"
        }

    return {
        "success": True,
        "workflow_name": matched["name"],
        "content": matched["content"]
    }
