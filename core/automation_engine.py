"""
MAC Assistant - Advanced Automation & Workflow System
Intelligent task automation, workflow creation, and smart triggers.
"""

import json
import os
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import re

@dataclass
class AutomationTrigger:
    """Represents an automation trigger."""
    id: str
    name: str
    trigger_type: str  # time, event, condition, voice, location
    conditions: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AutomationAction:
    """Represents an automation action."""
    id: str
    action_type: str  # command, notification, email, api_call, file_operation
    parameters: Dict[str, Any]
    delay_seconds: int = 0
    retry_count: int = 0

@dataclass
class Workflow:
    """Represents a complete workflow."""
    id: str
    name: str
    description: str
    trigger: AutomationTrigger
    actions: List[AutomationAction]
    enabled: bool = True
    run_count: int = 0
    last_run: datetime = None
    success_rate: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class AutomationEngine:
    """Advanced automation and workflow engine."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize automation engine."""
        self.data_dir = data_dir
        self.workflows_file = os.path.join(data_dir, "workflows.json")
        self.automation_log_file = os.path.join(data_dir, "automation_log.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load workflows
        self.workflows = self._load_workflows()
        self.automation_log = self._load_automation_log()
        
        # Runtime state
        self.is_running = False
        self.trigger_thread = None
        self.active_schedules = {}
        
        # Action handlers
        self.action_handlers = {
            'command': self._handle_command_action,
            'notification': self._handle_notification_action,
            'email': self._handle_email_action,
            'api_call': self._handle_api_call_action,
            'file_operation': self._handle_file_operation_action,
            'reminder': self._handle_reminder_action,
            'delay': self._handle_delay_action
        }
    
    def _load_workflows(self) -> List[Workflow]:
        """Load workflows from storage."""
        if not os.path.exists(self.workflows_file):
            return []
        
        try:
            with open(self.workflows_file, 'r', encoding='utf-8') as f:
                workflows_data = json.load(f)
            
            workflows = []
            for workflow_dict in workflows_data:
                # Convert datetime strings back to datetime objects
                if workflow_dict.get('created_at'):
                    workflow_dict['created_at'] = datetime.fromisoformat(workflow_dict['created_at'])
                if workflow_dict.get('last_run'):
                    workflow_dict['last_run'] = datetime.fromisoformat(workflow_dict['last_run'])
                
                # Reconstruct trigger
                trigger_data = workflow_dict['trigger']
                if trigger_data.get('created_at'):
                    trigger_data['created_at'] = datetime.fromisoformat(trigger_data['created_at'])
                trigger = AutomationTrigger(**trigger_data)
                
                # Reconstruct actions
                actions = []
                for action_data in workflow_dict['actions']:
                    actions.append(AutomationAction(**action_data))
                
                # Create workflow
                workflow_dict['trigger'] = trigger
                workflow_dict['actions'] = actions
                workflows.append(Workflow(**workflow_dict))
            
            return workflows
        except Exception as e:
            print(f"Error loading workflows: {e}")
            return []
    
    def _save_workflows(self):
        """Save workflows to storage."""
        try:
            workflows_data = []
            for workflow in self.workflows:
                workflow_dict = asdict(workflow)
                # Convert datetime objects to strings
                if workflow_dict.get('created_at'):
                    workflow_dict['created_at'] = workflow.created_at.isoformat()
                if workflow_dict.get('last_run'):
                    workflow_dict['last_run'] = workflow.last_run.isoformat()
                
                # Handle trigger datetime
                if workflow_dict['trigger'].get('created_at'):
                    workflow_dict['trigger']['created_at'] = workflow.trigger.created_at.isoformat()
                
                workflows_data.append(workflow_dict)
            
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving workflows: {e}")
    
    def _load_automation_log(self) -> List[Dict]:
        """Load automation execution log."""
        if not os.path.exists(self.automation_log_file):
            return []
        
        try:
            with open(self.automation_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading automation log: {e}")
            return []
    
    def _save_automation_log(self):
        """Save automation log."""
        try:
            # Keep only last 1000 entries
            if len(self.automation_log) > 1000:
                self.automation_log = self.automation_log[-1000:]
            
            with open(self.automation_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.automation_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving automation log: {e}")
    
    def create_workflow_from_command(self, command: str) -> Dict[str, Any]:
        """Create a workflow from natural language command."""
        try:
            # Parse the command to extract workflow components
            workflow_data = self._parse_workflow_command(command)
            
            if not workflow_data:
                return {
                    'success': False,
                    'message': "❌ Could not understand the workflow request. Try being more specific."
                }
            
            # Generate unique IDs
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trigger_id = f"trigger_{workflow_id}"
            
            # Create trigger
            trigger = AutomationTrigger(
                id=trigger_id,
                name=workflow_data['trigger_name'],
                trigger_type=workflow_data['trigger_type'],
                conditions=workflow_data['trigger_conditions']
            )
            
            # Create actions
            actions = []
            for i, action_data in enumerate(workflow_data['actions']):
                action_id = f"action_{workflow_id}_{i}"
                action = AutomationAction(
                    id=action_id,
                    action_type=action_data['type'],
                    parameters=action_data['parameters']
                )
                actions.append(action)
            
            # Create workflow
            workflow = Workflow(
                id=workflow_id,
                name=workflow_data['name'],
                description=workflow_data['description'],
                trigger=trigger,
                actions=actions
            )
            
            # Add to workflows
            self.workflows.append(workflow)
            self._save_workflows()
            
            return {
                'success': True,
                'message': f"✅ Workflow '{workflow.name}' created successfully!",
                'workflow': workflow,
                'details': {
                    'trigger': f"{trigger.trigger_type}: {trigger.name}",
                    'actions': f"{len(actions)} actions configured",
                    'id': workflow_id
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error creating workflow: {str(e)}"
            }
    
    def _parse_workflow_command(self, command: str) -> Optional[Dict]:
        """Parse natural language workflow command."""
        command_lower = command.lower().strip()
        
        # Common workflow patterns
        workflow_patterns = [
            # "Every morning at 8am, remind me to take vitamins"
            {
                'pattern': r'every (\w+) at (\d{1,2}(?::\d{2})?\s*(?:am|pm)?),?\s*(.+)',
                'trigger_type': 'time',
                'example': 'every morning at 8am, remind me to take vitamins'
            },
            # "When I say 'start work mode', turn on focus mode"
            {
                'pattern': r'when i say [\'\"](.*?)[\'\"],?\s*(.+)',
                'trigger_type': 'voice',
                'example': 'when I say "start work mode", turn on focus mode'
            },
            # "If it's Friday afternoon, suggest weekend plans"
            {
                'pattern': r'if it\'s (\w+) (\w+),?\s*(.+)',
                'trigger_type': 'condition',
                'example': 'if it\'s Friday afternoon, suggest weekend plans'
            }
        ]
        
        for pattern_info in workflow_patterns:
            match = re.search(pattern_info['pattern'], command_lower)
            if match:
                return self._extract_workflow_from_match(match, pattern_info, command)
        
        # Fallback: try to extract basic automation
        return self._extract_basic_automation(command)
    
    def _extract_workflow_from_match(self, match, pattern_info, original_command) -> Dict:
        """Extract workflow data from regex match."""
        trigger_type = pattern_info['trigger_type']
        
        if trigger_type == 'time':
            frequency = match.group(1)  # morning, evening, daily, etc.
            time_str = match.group(2)   # 8am, 2:30pm, etc.
            action_desc = match.group(3) # remind me to take vitamins
            
            return {
                'name': f"Scheduled {action_desc}",
                'description': f"Auto-generated workflow: {original_command}",
                'trigger_name': f"{frequency.title()} at {time_str}",
                'trigger_type': 'time',
                'trigger_conditions': {
                    'frequency': frequency,
                    'time': time_str,
                    'enabled_days': self._parse_frequency_to_days(frequency)
                },
                'actions': [
                    {
                        'type': 'reminder',
                        'parameters': {
                            'message': action_desc,
                            'priority': 'medium'
                        }
                    }
                ]
            }
        
        elif trigger_type == 'voice':
            trigger_phrase = match.group(1)
            action_desc = match.group(2)
            
            return {
                'name': f"Voice command: {trigger_phrase}",
                'description': f"Auto-generated workflow: {original_command}",
                'trigger_name': f"Voice: '{trigger_phrase}'",
                'trigger_type': 'voice',
                'trigger_conditions': {
                    'phrase': trigger_phrase,
                    'exact_match': False
                },
                'actions': [
                    {
                        'type': 'command',
                        'parameters': {
                            'command': action_desc,
                            'speak_response': True
                        }
                    }
                ]
            }
        
        elif trigger_type == 'condition':
            day = match.group(1)
            time_of_day = match.group(2)
            action_desc = match.group(3)
            
            return {
                'name': f"{day.title()} {time_of_day} automation",
                'description': f"Auto-generated workflow: {original_command}",
                'trigger_name': f"{day.title()} {time_of_day}",
                'trigger_type': 'condition',
                'trigger_conditions': {
                    'day_of_week': day,
                    'time_of_day': time_of_day
                },
                'actions': [
                    {
                        'type': 'notification',
                        'parameters': {
                            'title': f"{day.title()} {time_of_day}",
                            'message': action_desc,
                            'priority': 'medium'
                        }
                    }
                ]
            }
        
        return None
    
    def _extract_basic_automation(self, command: str) -> Optional[Dict]:
        """Extract basic automation from command."""
        # Simple fallback for basic automation
        return {
            'name': "Custom Automation",
            'description': f"Basic automation: {command}",
            'trigger_name': "Manual trigger",
            'trigger_type': 'manual',
            'trigger_conditions': {},
            'actions': [
                {
                    'type': 'command',
                    'parameters': {
                        'command': command,
                        'speak_response': False
                    }
                }
            ]
        }
    
    def _parse_frequency_to_days(self, frequency: str) -> List[str]:
        """Parse frequency to specific days."""
        frequency_lower = frequency.lower()
        
        if frequency_lower in ['daily', 'every day']:
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        elif frequency_lower in ['weekdays', 'workdays']:
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        elif frequency_lower in ['weekends']:
            return ['saturday', 'sunday']
        elif frequency_lower in ['morning']:
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        elif frequency_lower in ['evening']:
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        else:
            return [frequency_lower] if frequency_lower in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] else []
    
    def start_automation_engine(self):
        """Start the automation engine."""
        if self.is_running:
            return
        
        self.is_running = True
        self.trigger_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.trigger_thread.start()
        
        print("🤖 Automation engine started")
    
    def stop_automation_engine(self):
        """Stop the automation engine."""
        self.is_running = False
        if self.trigger_thread:
            self.trigger_thread.join(timeout=2)
        
        print("🤖 Automation engine stopped")
    
    def _automation_loop(self):
        """Main automation monitoring loop."""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for workflow in self.workflows:
                    if not workflow.enabled:
                        continue
                    
                    # Check if workflow should be triggered
                    if self._should_trigger_workflow(workflow, current_time):
                        self._execute_workflow(workflow)
                
                # Sleep for 30 seconds before checking again
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in automation loop: {e}")
                time.sleep(60)  # Wait longer if there's an error
    
    def _should_trigger_workflow(self, workflow: Workflow, current_time: datetime) -> bool:
        """Check if a workflow should be triggered."""
        trigger = workflow.trigger
        
        if trigger.trigger_type == 'time':
            return self._check_time_trigger(trigger, current_time)
        elif trigger.trigger_type == 'condition':
            return self._check_condition_trigger(trigger, current_time)
        # Note: voice and event triggers are handled elsewhere
        
        return False
    
    def _check_time_trigger(self, trigger: AutomationTrigger, current_time: datetime) -> bool:
        """Check if time-based trigger should fire."""
        conditions = trigger.conditions
        
        # Check if current day is enabled
        enabled_days = conditions.get('enabled_days', [])
        current_day = current_time.strftime('%A').lower()
        
        if enabled_days and current_day not in enabled_days:
            return False
        
        # Parse target time
        time_str = conditions.get('time', '')
        try:
            target_time = self._parse_time_string(time_str)
            current_time_only = current_time.time()
            
            # Check if we're within 1 minute of target time
            target_datetime = datetime.combine(current_time.date(), target_time)
            time_diff = abs((current_time - target_datetime).total_seconds())
            
            return time_diff <= 60  # Within 1 minute
            
        except Exception:
            return False
    
    def _parse_time_string(self, time_str: str) -> time:
        """Parse time string like '8am', '2:30pm', etc."""
        time_str = time_str.lower().strip()
        
        # Handle formats like '8am', '2:30pm'
        if 'am' in time_str or 'pm' in time_str:
            is_pm = 'pm' in time_str
            time_part = time_str.replace('am', '').replace('pm', '').strip()
            
            if ':' in time_part:
                hour, minute = map(int, time_part.split(':'))
            else:
                hour = int(time_part)
                minute = 0
            
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
            
            return time(hour, minute)
        
        # Handle 24-hour format
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        
        raise ValueError(f"Cannot parse time: {time_str}")
    
    def _check_condition_trigger(self, trigger: AutomationTrigger, current_time: datetime) -> bool:
        """Check if condition-based trigger should fire."""
        conditions = trigger.conditions
        
        # Check day of week
        day_of_week = conditions.get('day_of_week', '').lower()
        current_day = current_time.strftime('%A').lower()
        
        if day_of_week and day_of_week != current_day:
            return False
        
        # Check time of day
        time_of_day = conditions.get('time_of_day', '').lower()
        current_hour = current_time.hour
        
        time_ranges = {
            'morning': (6, 12),
            'afternoon': (12, 18),
            'evening': (18, 22),
            'night': (22, 24)
        }
        
        if time_of_day in time_ranges:
            start_hour, end_hour = time_ranges[time_of_day]
            if not (start_hour <= current_hour < end_hour):
                return False
        
        return True
    
    def _execute_workflow(self, workflow: Workflow):
        """Execute a workflow."""
        try:
            print(f"🤖 Executing workflow: {workflow.name}")
            
            workflow.run_count += 1
            workflow.last_run = datetime.now()
            
            success_count = 0
            total_actions = len(workflow.actions)
            
            for action in workflow.actions:
                try:
                    # Add delay if specified
                    if action.delay_seconds > 0:
                        time.sleep(action.delay_seconds)
                    
                    # Execute action
                    result = self._execute_action(action)
                    
                    if result.get('success', False):
                        success_count += 1
                    
                    # Log action result
                    self._log_action_result(workflow, action, result)
                    
                except Exception as e:
                    print(f"Error executing action {action.id}: {e}")
                    self._log_action_result(workflow, action, {'success': False, 'error': str(e)})
            
            # Update success rate
            workflow.success_rate = success_count / total_actions if total_actions > 0 else 0
            
            # Save updated workflows
            self._save_workflows()
            
            print(f"✅ Workflow '{workflow.name}' completed ({success_count}/{total_actions} actions successful)")
            
        except Exception as e:
            print(f"Error executing workflow {workflow.name}: {e}")
    
    def _execute_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute a single action."""
        handler = self.action_handlers.get(action.action_type)
        
        if not handler:
            return {
                'success': False,
                'message': f"Unknown action type: {action.action_type}"
            }
        
        return handler(action.parameters)
    
    def _handle_command_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle command execution action."""
        command = parameters.get('command', '')
        
        # This would integrate with the main brain to execute commands
        return {
            'success': True,
            'message': f"Command executed: {command}"
        }
    
    def _handle_notification_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle notification action."""
        title = parameters.get('title', 'MAC Assistant')
        message = parameters.get('message', '')
        priority = parameters.get('priority', 'medium')
        
        print(f"🔔 {title}: {message}")
        
        return {
            'success': True,
            'message': f"Notification sent: {title}"
        }
    
    def _handle_email_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle email sending action."""
        # Placeholder for email integration
        return {
            'success': True,
            'message': "Email action executed (placeholder)"
        }
    
    def _handle_api_call_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle API call action."""
        # Placeholder for API call integration
        return {
            'success': True,
            'message': "API call executed (placeholder)"
        }
    
    def _handle_file_operation_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle file operation action."""
        # Placeholder for file operations
        return {
            'success': True,
            'message': "File operation executed (placeholder)"
        }
    
    def _handle_reminder_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle reminder action."""
        message = parameters.get('message', '')
        priority = parameters.get('priority', 'medium')
        
        print(f"⏰ Reminder: {message}")
        
        return {
            'success': True,
            'message': f"Reminder set: {message}"
        }
    
    def _handle_delay_action(self, parameters: Dict) -> Dict[str, Any]:
        """Handle delay action."""
        delay_seconds = parameters.get('seconds', 1)
        time.sleep(delay_seconds)
        
        return {
            'success': True,
            'message': f"Delayed for {delay_seconds} seconds"
        }
    
    def _log_action_result(self, workflow: Workflow, action: AutomationAction, result: Dict):
        """Log action execution result."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'workflow_id': workflow.id,
            'workflow_name': workflow.name,
            'action_id': action.id,
            'action_type': action.action_type,
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error', '')
        }
        
        self.automation_log.append(log_entry)
        self._save_automation_log()
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get automation engine status."""
        active_workflows = [w for w in self.workflows if w.enabled]
        total_runs = sum(w.run_count for w in self.workflows)
        avg_success_rate = sum(w.success_rate for w in self.workflows) / len(self.workflows) if self.workflows else 0
        
        return {
            'engine_running': self.is_running,
            'total_workflows': len(self.workflows),
            'active_workflows': len(active_workflows),
            'total_runs': total_runs,
            'average_success_rate': avg_success_rate,
            'recent_executions': len([log for log in self.automation_log if 
                                    datetime.fromisoformat(log['timestamp']) > datetime.now() - timedelta(days=7)])
        }
