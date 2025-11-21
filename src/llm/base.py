import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4o")
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    def generate(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        response = completion(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_key
        )
        return response.choices[0].message.content
    
    # ✅ The invoke method you need
    def invoke(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.generate(messages, temperature=temperature, max_tokens=max_tokens)
