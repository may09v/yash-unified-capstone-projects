import yaml
from pathlib import Path

def load_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def get_config_path(filename: str) -> str:
    return str(Path(__file__).parent.parent.parent / "config" / filename)

def load_model_config() -> dict:
    return load_yaml(get_config_path("model_config.yaml"))

def load_prompt_templates() -> dict:
    return load_yaml(get_config_path("prompt_templates.yaml"))
