from langchain_google_genai import GoogleGenerativeAIEmbeddings

from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'gemini_config.yaml'

def load_google_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

google_config = load_google_config()

GEMINI_API_KEY = google_config['GEMINI_API_KEY']
GEMINI_EMBEDDING_MODEL = google_config['GEMINI_EMBEDDING_MODEL']
PROVIDER = google_config['PROVIDE']

def connect_gemini_embedding():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
            chunk_size=2048
        )
        return {"status": True, "model": embeddings}
    except Exception as e:
        return {"status": False, "model": ''}
