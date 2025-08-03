"""
MAC Assistant - Custom Commands & Workflow System
Allows users to create custom commands, workflows, and automation.
"""

import json
import os
import subprocess
import datetime
import asyncio
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import re


class CustomCommand:
    """Represents a custom user-defined command."""
    
    def __init__(self, name: str, command_type: str, definition: Dict[str, Any]):
        self.name = name
        self.command_type = command_type
        self.definition = definition
        self.created = definition.get("created", datetime.datetime.now().isoformat())
        self.usage_count = definition.get("usage_count", 0)
        self.last_used = definition.get("last_used")
        
    def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the custom command."""
        self.usage_count += 1
        self.last_used = datetime.datetime.now().isoformat()
        
        if self.command_type == "shortcut":
            return self._execute_shortcut(context)
        elif self.command_type == "workflow":
            return self._execute_workflow(context)
        elif self.command_type == "alias":
            return self._execute_alias(context)
        elif self.command_type == "macro":
            return self._execute_macro(context)
        else:
            return {"status": "error", "message": f"Unknown command type: {self.command_type}"}
    
    def _execute_shortcut(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a shortcut command."""
        action = self.definition.get("action", "")
        parameters = self.definition.get("parameters", {})
        
        # Replace parameters in action
        if context:
            for key, value in context.items():
                action = action.replace(f"{{{key}}}", str(value))
        
        # Execute based on action type
        action_type = self.definition.get("action_type", "system")
        
        if action_type == "system":
            return self._execute_system_command(action)
        elif action_type == "web":
            return self._execute_web_action(action)
        elif action_type == "file":
            return self._execute_file_action(action)
        elif action_type == "text":
            return self._execute_text_action(action)
        else:
            return {"status": "error", "message": f"Unknown action type: {action_type}"}
    
    def _execute_workflow(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow (sequence of commands)."""
        steps = self.definition.get("steps", [])
        results = []
        
        for i, step in enumerate(steps):
            try:
                step_result = self._execute_workflow_step(step, context)
                results.append(step_result)
                
                # If step failed and workflow is not set to continue on error
                if (step_result.get("status") == "error" and 
                    not self.definition.get("continue_on_error", False)):
                    return {
                        "status": "error",
                        "message": f"Workflow failed at step {i+1}: {step_result.get('message', 'Unknown error')}",
                        "completed_steps": results
                    }
                
                # Add delay between steps if specified
                delay = step.get("delay", 0)
                if delay > 0:
                    import time
                    time.sleep(delay)
                    
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error executing step {i+1}: {str(e)}",
                    "completed_steps": results
                }
        
        return {
            "status": "success",
            "message": f"Workflow '{self.name}' completed successfully",
            "results": results
        }
    
    def _execute_alias(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an alias command."""
        target_command = self.definition.get("target_command", "")
        
        if context:
            # Replace parameters in target command
            for key, value in context.items():
                target_command = target_command.replace(f"{{{key}}}", str(value))
        
        return {
            "status": "success",
            "message": f"Executing alias '{self.name}' -> '{target_command}'",
            "target_command": target_command
        }
    
    def _execute_macro(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a recorded macro."""
        commands = self.definition.get("commands", [])
        results = []
        
        for command in commands:
            try:
                # Execute each recorded command
                result = self._execute_system_command(command)
                results.append(result)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Macro failed at command '{command}': {str(e)}",
                    "completed_commands": results
                }
        
        return {
            "status": "success",
            "message": f"Macro '{self.name}' executed successfully",
            "results": results
        }
    
    def _execute_workflow_step(self, step: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_type = step.get("type", "command")
        
        if step_type == "command":
            command = step.get("command", "")
            if context:
                for key, value in context.items():
                    command = command.replace(f"{{{key}}}", str(value))
            return self._execute_system_command(command)
        
        elif step_type == "condition":
            return self._execute_condition_step(step, context)
        
        elif step_type == "loop":
            return self._execute_loop_step(step, context)
        
        elif step_type == "api_call":
            return self._execute_api_call_step(step, context)
        
        elif step_type == "user_input":
            return self._execute_user_input_step(step, context)
        
        else:
            return {"status": "error", "message": f"Unknown step type: {step_type}"}
    
    def _execute_system_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Command executed successfully",
                    "output": result.stdout.strip()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Command failed with return code {result.returncode}",
                    "error": result.stderr.strip()
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute command: {str(e)}"}
    
    def _execute_web_action(self, action: str) -> Dict[str, Any]:
        """Execute a web-based action."""
        import webbrowser
        
        try:
            webbrowser.open(action)
            return {
                "status": "success",
                "message": f"Opened URL: {action}"
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to open URL: {str(e)}"}
    
    def _execute_file_action(self, action: str) -> Dict[str, Any]:
        """Execute a file-based action."""
        try:
            # Parse file action (e.g., "open:file.txt", "create:newfile.txt", "delete:oldfile.txt")
            if ":" in action:
                operation, filepath = action.split(":", 1)
                
                if operation == "open":
                    os.startfile(filepath)  # Windows
                    return {"status": "success", "message": f"Opened file: {filepath}"}
                
                elif operation == "create":
                    Path(filepath).touch()
                    return {"status": "success", "message": f"Created file: {filepath}"}
                
                elif operation == "delete":
                    if Path(filepath).exists():
                        Path(filepath).unlink()
                        return {"status": "success", "message": f"Deleted file: {filepath}"}
                    else:
                        return {"status": "error", "message": f"File not found: {filepath}"}
                
                else:
                    return {"status": "error", "message": f"Unknown file operation: {operation}"}
            else:
                # Just open the file
                os.startfile(action)
                return {"status": "success", "message": f"Opened: {action}"}
                
        except Exception as e:
            return {"status": "error", "message": f"File action failed: {str(e)}"}
    
    def _execute_text_action(self, action: str) -> Dict[str, Any]:
        """Execute a text-based action."""
        return {
            "status": "success",
            "message": action,
            "type": "text_response"
        }
    
    def _execute_condition_step(self, step: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a conditional step."""
        condition = step.get("condition", "")
        true_action = step.get("true_action", {})
        false_action = step.get("false_action", {})
        
        # Simple condition evaluation (could be enhanced)
        condition_result = self._evaluate_condition(condition, context)
        
        if condition_result:
            return self._execute_workflow_step(true_action, context)
        else:
            return self._execute_workflow_step(false_action, context)
    
    def _execute_loop_step(self, step: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a loop step."""
        loop_type = step.get("loop_type", "count")
        loop_action = step.get("action", {})
        
        if loop_type == "count":
            count = step.get("count", 1)
            results = []
            
            for i in range(count):
                loop_context = {**(context or {}), "loop_index": i}
                result = self._execute_workflow_step(loop_action, loop_context)
                results.append(result)
            
            return {
                "status": "success",
                "message": f"Loop executed {count} times",
                "results": results
            }
        
        else:
            return {"status": "error", "message": f"Unknown loop type: {loop_type}"}
    
    def _execute_api_call_step(self, step: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an API call step."""
        # Placeholder for API call functionality
        return {
            "status": "success",
            "message": "API call step not fully implemented yet"
        }
    
    def _execute_user_input_step(self, step: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a user input step."""
        prompt = step.get("prompt", "Please provide input:")
        input_type = step.get("input_type", "text")
        
        # This would need integration with the main interface
        return {
            "status": "pending_input",
            "message": prompt,
            "input_type": input_type
        }
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any] = None) -> bool:
        """Evaluate a simple condition."""
        # Very basic condition evaluation
        # In a real implementation, you'd want a more robust expression evaluator
        
        if context:
            for key, value in context.items():
                condition = condition.replace(f"{{{key}}}", str(value))
        
        # Simple conditions like "5 > 3", "true", "false"
        try:
            return eval(condition)
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary."""
        return {
            "name": self.name,
            "command_type": self.command_type,
            "definition": self.definition,
            "created": self.created,
            "usage_count": self.usage_count,
            "last_used": self.last_used
        }


class CustomCommandManager:
    """Manages custom commands and workflows."""
    
    def __init__(self, commands_dir: str = "user_data"):
        self.commands_dir = Path(commands_dir)
        self.commands_dir.mkdir(exist_ok=True)
        
        self.commands_file = self.commands_dir / "custom_commands.json"
        self.templates_file = self.commands_dir / "command_templates.json"
        
        self.commands: Dict[str, CustomCommand] = {}
        self.templates = self._load_templates()
        
        self._load_commands()
    
    def _load_commands(self):
        """Load custom commands from file."""
        if self.commands_file.exists():
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    command = CustomCommand(
                        cmd_data["name"],
                        cmd_data["command_type"],
                        cmd_data["definition"]
                    )
                    command.usage_count = cmd_data.get("usage_count", 0)
                    command.last_used = cmd_data.get("last_used")
                    
                    self.commands[command.name] = command
                    
            except Exception as e:
                print(f"Error loading custom commands: {e}")
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load command templates."""
        default_templates = {
            "shortcut": {
                "name": "My Shortcut",
                "description": "A simple shortcut command",
                "action_type": "system",
                "action": "echo Hello World",
                "parameters": {}
            },
            "workflow": {
                "name": "My Workflow",
                "description": "A multi-step workflow",
                "steps": [
                    {
                        "type": "command",
                        "command": "echo Step 1",
                        "delay": 1
                    },
                    {
                        "type": "command", 
                        "command": "echo Step 2"
                    }
                ],
                "continue_on_error": False
            },
            "alias": {
                "name": "My Alias",
                "description": "An alias for another command",
                "target_command": "echo {message}"
            },
            "web_shortcut": {
                "name": "Quick Search",
                "description": "Quick web search",
                "action_type": "web",
                "action": "https://www.google.com/search?q={query}"
            },
            "file_manager": {
                "name": "Quick File Action",
                "description": "File management shortcut",
                "action_type": "file",
                "action": "open:{filepath}"
            }
        }
        
        if self.templates_file.exists():
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    return {**default_templates, **templates}
            except Exception:
                return default_templates
        else:
            self._save_templates(default_templates)
            return default_templates
    
    def _save_commands(self):
        """Save commands to file."""
        commands_data = [cmd.to_dict() for cmd in self.commands.values()]
        
        with open(self.commands_file, 'w', encoding='utf-8') as f:
            json.dump(commands_data, f, indent=2, ensure_ascii=False)
    
    def _save_templates(self, templates: Dict[str, Any]):
        """Save templates to file."""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
    
    def create_command(self, name: str, command_type: str, definition: Dict[str, Any]) -> bool:
        """Create a new custom command."""
        if name in self.commands:
            return False  # Command already exists
        
        # Validate definition based on type
        if not self._validate_command_definition(command_type, definition):
            return False
        
        command = CustomCommand(name, command_type, definition)
        self.commands[name] = command
        self._save_commands()
        
        return True
    
    def _validate_command_definition(self, command_type: str, definition: Dict[str, Any]) -> bool:
        """Validate command definition."""
        required_fields = {
            "shortcut": ["action_type", "action"],
            "workflow": ["steps"],
            "alias": ["target_command"],
            "macro": ["commands"]
        }
        
        if command_type not in required_fields:
            return False
        
        for field in required_fields[command_type]:
            if field not in definition:
                return False
        
        return True
    
    def execute_command(self, name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a custom command."""
        if name not in self.commands:
            return {"status": "error", "message": f"Command '{name}' not found"}
        
        command = self.commands[name]
        result = command.execute(context)
        
        # Save updated usage stats
        self._save_commands()
        
        return result
    
    def list_commands(self, command_type: str = None) -> List[Dict[str, Any]]:
        """List available custom commands."""
        commands = []
        
        for command in self.commands.values():
            if command_type is None or command.command_type == command_type:
                commands.append({
                    "name": command.name,
                    "type": command.command_type,
                    "description": command.definition.get("description", "No description"),
                    "usage_count": command.usage_count,
                    "last_used": command.last_used
                })
        
        return sorted(commands, key=lambda x: x["usage_count"], reverse=True)
    
    def delete_command(self, name: str) -> bool:
        """Delete a custom command."""
        if name in self.commands:
            del self.commands[name]
            self._save_commands()
            return True
        return False
    
    def get_command_details(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a command."""
        if name in self.commands:
            return self.commands[name].to_dict()
        return None
    
    def create_from_template(self, template_name: str, name: str, customizations: Dict[str, Any] = None) -> bool:
        """Create a command from a template."""
        if template_name not in self.templates:
            return False
        
        template = self.templates[template_name].copy()
        
        # Apply customizations
        if customizations:
            template.update(customizations)
        
        # Determine command type from template
        command_type = template.get("command_type", template_name)
        
        return self.create_command(name, command_type, template)
    
    def get_templates(self) -> Dict[str, Any]:
        """Get available command templates."""
        return self.templates.copy()
    
    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search commands by name or description."""
        query_lower = query.lower()
        results = []
        
        for command in self.commands.values():
            name_match = query_lower in command.name.lower()
            desc_match = query_lower in command.definition.get("description", "").lower()
            
            if name_match or desc_match:
                results.append({
                    "name": command.name,
                    "type": command.command_type,
                    "description": command.definition.get("description", "No description"),
                    "match_type": "name" if name_match else "description"
                })
        
        return results
    
    def export_commands(self, filepath: str) -> bool:
        """Export commands to a file."""
        try:
            commands_data = [cmd.to_dict() for cmd in self.commands.values()]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "commands": commands_data,
                    "templates": self.templates,
                    "exported": datetime.datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_commands(self, filepath: str) -> Dict[str, Any]:
        """Import commands from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            skipped_count = 0
            
            for cmd_data in data.get("commands", []):
                if cmd_data["name"] not in self.commands:
                    command = CustomCommand(
                        cmd_data["name"],
                        cmd_data["command_type"],
                        cmd_data["definition"]
                    )
                    self.commands[command.name] = command
                    imported_count += 1
                else:
                    skipped_count += 1
            
            # Import templates
            if "templates" in data:
                self.templates.update(data["templates"])
                self._save_templates(self.templates)
            
            self._save_commands()
            
            return {
                "status": "success",
                "imported": imported_count,
                "skipped": skipped_count,
                "message": f"Imported {imported_count} commands, skipped {skipped_count} existing commands"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to import commands: {str(e)}"
            }
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for custom commands."""
        if not self.commands:
            return {"total_commands": 0, "total_usage": 0}
        
        total_usage = sum(cmd.usage_count for cmd in self.commands.values())
        most_used = max(self.commands.values(), key=lambda x: x.usage_count)
        
        # Group by type
        type_stats = {}
        for command in self.commands.values():
            cmd_type = command.command_type
            if cmd_type not in type_stats:
                type_stats[cmd_type] = {"count": 0, "usage": 0}
            type_stats[cmd_type]["count"] += 1
            type_stats[cmd_type]["usage"] += command.usage_count
        
        return {
            "total_commands": len(self.commands),
            "total_usage": total_usage,
            "most_used_command": {
                "name": most_used.name,
                "usage_count": most_used.usage_count
            } if most_used.usage_count > 0 else None,
            "commands_by_type": type_stats
        }


class WorkflowBuilder:
    """Helper class for building complex workflows."""
    
    def __init__(self):
        self.steps = []
        self.name = ""
        self.description = ""
    
    def set_info(self, name: str, description: str = ""):
        """Set workflow name and description."""
        self.name = name
        self.description = description
        return self
    
    def add_command_step(self, command: str, delay: int = 0):
        """Add a command step to the workflow."""
        self.steps.append({
            "type": "command",
            "command": command,
            "delay": delay
        })
        return self
    
    def add_condition_step(self, condition: str, true_action: Dict, false_action: Dict = None):
        """Add a conditional step."""
        step = {
            "type": "condition",
            "condition": condition,
            "true_action": true_action
        }
        
        if false_action:
            step["false_action"] = false_action
        
        self.steps.append(step)
        return self
    
    def add_loop_step(self, action: Dict, count: int = 1):
        """Add a loop step."""
        self.steps.append({
            "type": "loop",
            "loop_type": "count",
            "count": count,
            "action": action
        })
        return self
    
    def add_user_input_step(self, prompt: str, input_type: str = "text"):
        """Add a user input step."""
        self.steps.append({
            "type": "user_input",
            "prompt": prompt,
            "input_type": input_type
        })
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the workflow definition."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "continue_on_error": False
        }
