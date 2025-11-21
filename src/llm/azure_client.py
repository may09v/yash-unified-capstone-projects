from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings


from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'azure_config.yaml'

def load_azure_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

azure_config = load_azure_config()

AZURE_OPENAI_ENDPOINT = azure_config['AZURE_OPENAI_ENDPOINT']
DEPLOYMENT_NAME = azure_config['DEPLOYMENT_NAME']
AZURE_OPENAI_KEY = azure_config['AZURE_OPENAI_KEY']
AZURE_TEXT_OPENAI_VERSION= azure_config['AZURE_TEXT_OPENAI_VERSION']
###################################

def ConnectAzure():
    try:
        print(DEPLOYMENT_NAME)
        model = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment=DEPLOYMENT_NAME,
            api_version=AZURE_TEXT_OPENAI_VERSION,
            api_key=AZURE_OPENAI_KEY  
        )
        return {"status":True,"model":model}
    except Exception as e:
        return {"status":False,"model":''}

def connect_azure_embedding():
    try:
        embeddings = AzureOpenAIEmbeddings(
            deployment="text-embedding-3-small",
            model="text-embedding-3-small",
            openai_api_type="azure",
            openai_api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            openai_api_version="2023-05-15",
            chunk_size=2048)
        return {"status":True,"model":embeddings}
    except Exception as e:
        return {"status":False,"model":''}