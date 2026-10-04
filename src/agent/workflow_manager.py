import os
import re

class WorkflowManager:
    """
    Manages the state and transition logic for workflows.
    """
    def __init__(self):
        self.workflow_tasks = []
        self.current_task_index = -1

    def load_workflow(self, filepath: str) -> dict:
        """
        Loads a workflow from a markdown file.
        Returns a dict containing either 'error' message or 'success' with initial prompt.
        """
        if not os.path.exists(filepath):
            return {"success": False, "error": f"Workflow file not found: {filepath}"}

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
        
        intro = parts[0].strip() if parts else ""
        tasks = ["## " + part.strip() for part in parts[1:]]

        if not tasks:
            return {"success": False, "error": "No tasks (## headers) found in workflow file."}

        self.workflow_tasks = tasks
        self.current_task_index = 0

        first_prompt = (
            f"You are starting a new automated workflow. Execute the tasks sequentially. "
            f"When you finish the current task, you MUST call the mark_task_completed tool.\n\n"
            f"Workflow Context:\n{intro}\n\n"
            f"Current Task (1/{len(tasks)}):\n{tasks[0]}"
        )
        return {"success": True, "prompt": first_prompt}

    def advance_workflow(self) -> dict:
        """
        Advances the workflow to the next task.
        Returns a dict with 'is_complete' and either 'prompt' for next task or completion message.
        """
        self.current_task_index += 1
        
        if self.workflow_tasks and self.current_task_index < len(self.workflow_tasks):
            next_task = self.workflow_tasks[self.current_task_index]
            prompt = (
                f"Previous task marked complete. Moving to next task "
                f"({self.current_task_index + 1}/{len(self.workflow_tasks)}):\n\n{next_task}"
            )
            return {"is_complete": False, "prompt": prompt}
        else:
            self.workflow_tasks = []
            self.current_task_index = -1
            return {"is_complete": True, "prompt": "All workflow tasks have been completed."}

    def clear(self):
        """Clears the current workflow state."""
        self.workflow_tasks = []
        self.current_task_index = -1
