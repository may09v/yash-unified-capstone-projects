import json
from typing import Dict, Optional, List
from src.llm.base import LLMClient
from src.prompt_engineering.templates import PromptBuilder
from src.utils.config_loader import load_model_config

class TicketHandler:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()
        self.config = load_model_config()
        self.teams = self.config["teams"]
    
    def detect_intent(self, user_input: str, recent_context: List[str], ticket_id: Optional[str], ticket_data: Optional[Dict]) -> str:
        messages = self.prompt_builder.build_intent_detection_prompt(
            user_input, recent_context, ticket_id, ticket_data
        )
        response = self.llm_client.generate(messages, temperature=0.3)
        
        action = response.strip().lower()
        if "confirm" in action or "yes" in action or "correct" in action:
            return "confirm"
        elif "modify" in action or "change" in action or "update" in action or "actually" in action:
            return "modify"
        elif "cancel" in action or "no" in action or "stop" in action:
            return "cancel"
        else:
            return "create"
    

    def extract_ticket_info(self, user_input: str) -> Dict:
        messages = self.prompt_builder.build_ticket_extraction_prompt(user_input)
        response = self.llm_client.generate(messages, temperature=0.7)
        
        try:
            ticket_data = json.loads(response)
        except json.JSONDecodeError:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                ticket_data = json.loads(response[start:end])
            else:
                raise ValueError("Failed to parse ticket information")
        
        return ticket_data
    
    def assign_team(self, category: str, description: str) -> str:
        description_lower = description.lower()
        category_lower = category.lower()
        
        best_match = None
        max_matches = 0
        
        for team in self.teams:
            matches = sum(1 for keyword in team["specialization"] 
                         if keyword in description_lower or keyword in category_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = team["name"]
        
        return best_match or "Software & Applications Team"
    
    def process_ticket(self, user_input: str) -> Dict:
        ticket_info = self.extract_ticket_info(user_input)
        
        assigned_team = self.assign_team(
            ticket_info.get("category", ""),
            ticket_info.get("description", "")
        )
        
        ticket_info["assigned_team"] = assigned_team
        ticket_info["status"] = "pending_confirmation"
        
        return ticket_info
