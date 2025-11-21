import os
from dotenv import load_dotenv
from pathlib import Path
import yaml

import litellm
litellm.drop_params=True
import os
os.environ["LITELLM_DROP_PARAMS"] = "True"
from langchain_litellm import ChatLiteLLM

HUGGINGFACE_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'hugging_config.yaml'
def load_hugging_config():
    with HUGGINGFACE_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

AZURE_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'azure_config.yaml'
def load_azure_config():
    with AZURE_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
azure_config = load_azure_config()

GEMINI_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'gemini_config.yaml'
def load_gemini_config():
    with GEMINI_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
gemin_config = load_gemini_config()

PROVIDER=gemin_config["PROVIDE"]
DEPLOYMENT_NAME=gemin_config["GEMINI_MODEL"]

# PROVIDER=azure_config["PROVIDE"]
# DEPLOYMENT_NAME=azure_config["DEPLOYMENT_NAME"]

load_dotenv()
 
def create_chat_model(provider: str=PROVIDER, model_name: str=DEPLOYMENT_NAME, temperature: float = 0.7):
    try:
        """
        Creates and returns a ChatLiteLLM instance.
        Supported providers: 'huggingface', 'azure', 'openai'
        """
        if provider=='azure':
            os.environ["AZURE_API_KEY"] = azure_config["AZURE_OPENAI_KEY"]
            os.environ["AZURE_API_BASE"] = azure_config["AZURE_OPENAI_ENDPOINT"]
            os.environ["AZURE_API_VERSION"] =azure_config["AZURE_TEXT_OPENAI_VERSION"]

        elif provider=='huggingface':
            hugging_config = load_hugging_config()
            os.environ["HUGGINGFACE_API_KEY"]=hugging_config['HUGGIN_FACE']
            os.environ["HUGGIN_FACE_REPO_ID"]=hugging_config['HUGGIN_FACE_REPO_ID']

        elif provider=='gemini':
            os.environ["GEMINI_API_KEY"]=gemin_config['GEMINI_API_KEY']
            
        else:
            return {"status":False,"model":''} 
        litellm.modify_params = {
            "drop_params": True,
            "supported_params": ["temperature", "max_tokens", "top_p", "stream"]  # specify only supported params
        }
        
        chat_model = ChatLiteLLM(
            model=f"{provider}/{model_name}",
            temperature=temperature
        )
        return {"status":True,"model":chat_model}
    except Exception as e:
        return {"status":False,"model":'','error':e}