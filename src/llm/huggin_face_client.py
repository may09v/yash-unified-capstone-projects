

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'hugging_config.yaml'
def load_hugging_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
    
### Varinables 
hugging_config = load_hugging_config()
HUGGIN_FACE=hugging_config['HUGGIN_FACE']
HUGGIN_FACE_REPO_ID=hugging_config['HUGGIN_FACE_REPO_ID']


def ConnectHugginface():
    try:
        hf_endpoint = HuggingFaceEndpoint(
            repo_id=HUGGIN_FACE_REPO_ID,
            huggingfacehub_api_token=HUGGIN_FACE,
        )
        llm = ChatHuggingFace(llm=hf_endpoint)
        return {"status":True,"model":llm}
    except Exception as e:
        return {"status":False,"model":''}