from src.utils.config_loader import load_prompt_templates
from typing import List, Optional, Dict

class PromptBuilder:
    def __init__(self):
        self.templates = load_prompt_templates()
    
    def build_intent_detection_prompt(self, user_input: str, recent_context: List[str], ticket_id: Optional[str], ticket_data: Optional[Dict]) -> list:
        context_str = "\n".join([f"- {msg}" for msg in recent_context[:-1]]) if len(recent_context) > 1 else "No previous context"
        ticket_str = f"\nCurrent pending ticket: {ticket_data}" if ticket_data else "\nNo pending ticket"
        
        return [
            {"role": "system", "content": self.templates["intent_detection"]["system"]},
            {"role": "user", "content": self.templates["intent_detection"]["user"].format(
                context=context_str,
                ticket_info=ticket_str,
                user_input=user_input
            )}
        ]
    
    def build_ticket_extraction_prompt(self, user_input: str) -> list:
        return [
            {"role": "system", "content": self.templates["ticket_extraction"]["system"]},
            {"role": "user", "content": self.templates["ticket_extraction"]["user"].format(user_input=user_input)}
        ]
    
    def build_confirmation_prompt(self, title: str, description: str, category: str, priority: str, team: str) -> list:
        return [
            {"role": "system", "content": self.templates["confirmation"]["system"]},
            {"role": "user", "content": self.templates["confirmation"]["user"].format(
                title=title,
                description=description,
                category=category,
                priority=priority,
                team=team
            )}
        ]
