"""Configuration loader utility."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from src.utils.exception_handler import ConfigurationError, log_exception
from src.utils.logger import setup_logger

# Initialize logger
config_logger = setup_logger(__name__)


class ConfigLoader:
    """Load and manage configuration from YAML files and environment variables."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        try:
            self.config_dir = Path(config_dir)
            self.config: Dict[str, Any] = {}
            self.prompts: Dict[str, Any] = {}

            # Validate config directory exists
            if not self.config_dir.exists():
                error_msg = f"Configuration directory not found: {config_dir}"
                config_logger.error(error_msg)
                raise ConfigurationError(error_msg, details={"config_dir": str(config_dir)})

            # Load environment variables
            env_file = self.config_dir / ".env"
            if env_file.exists():
                try:
                    load_dotenv(env_file)
                    config_logger.info(f"Loaded environment variables from {env_file}")
                except Exception as e:
                    config_logger.warning(f"Failed to load .env file: {e}")

            # Load configuration files
            self._load_config()
            self._load_prompts()
            self._override_with_env()

            config_logger.info("Configuration loaded successfully")

        except ConfigurationError:
            raise
        except Exception as e:
            log_exception(e, context="ConfigLoader.__init__")
            raise ConfigurationError(
                f"Failed to initialize configuration: {str(e)}",
                details={"config_dir": str(config_dir)}
            )
    
    def _load_config(self):
        """Load main configuration from YAML file."""
        config_file = self.config_dir / "config.yaml"

        try:
            if not config_file.exists():
                error_msg = f"Configuration file not found: {config_file}"
                config_logger.error(error_msg)
                raise ConfigurationError(error_msg, details={"file": str(config_file)})

            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            if not isinstance(self.config, dict):
                error_msg = "Configuration file must contain a valid YAML dictionary"
                config_logger.error(error_msg)
                raise ConfigurationError(error_msg, details={"file": str(config_file)})

            config_logger.info(f"Loaded configuration from {config_file}")

        except ConfigurationError:
            raise
        except yaml.YAMLError as e:
            log_exception(e, context="ConfigLoader._load_config")
            raise ConfigurationError(
                f"Invalid YAML in configuration file: {str(e)}",
                details={"file": str(config_file)}
            )
        except Exception as e:
            log_exception(e, context="ConfigLoader._load_config")
            raise ConfigurationError(
                f"Failed to load configuration file: {str(e)}",
                details={"file": str(config_file)}
            )
    
    def _load_prompts(self):
        """Load prompts configuration from YAML file."""
        prompts_file = self.config_dir / "prompts.yaml"

        try:
            if not prompts_file.exists():
                error_msg = f"Prompts file not found: {prompts_file}"
                config_logger.error(error_msg)
                raise ConfigurationError(error_msg, details={"file": str(prompts_file)})

            with open(prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)

            if not isinstance(self.prompts, dict):
                error_msg = "Prompts file must contain a valid YAML dictionary"
                config_logger.error(error_msg)
                raise ConfigurationError(error_msg, details={"file": str(prompts_file)})

            config_logger.info(f"Loaded prompts from {prompts_file}")

        except ConfigurationError:
            raise
        except yaml.YAMLError as e:
            log_exception(e, context="ConfigLoader._load_prompts")
            raise ConfigurationError(
                f"Invalid YAML in prompts file: {str(e)}",
                details={"file": str(prompts_file)}
            )
        except Exception as e:
            log_exception(e, context="ConfigLoader._load_prompts")
            raise ConfigurationError(
                f"Failed to load prompts file: {str(e)}",
                details={"file": str(prompts_file)}
            )
    
    def _override_with_env(self):
        """Override configuration with environment variables."""
        try:
            # Azure OpenAI
            if os.getenv("AZURE_OPENAI_ENDPOINT"):
                self.config.setdefault('azure_openai', {})['endpoint'] = os.getenv("AZURE_OPENAI_ENDPOINT")
            if os.getenv("AZURE_OPENAI_API_KEY"):
                self.config.setdefault('azure_openai', {})['api_key'] = os.getenv("AZURE_OPENAI_API_KEY")
            if os.getenv("AZURE_OPENAI_API_VERSION"):
                self.config.setdefault('azure_openai', {})['api_version'] = os.getenv("AZURE_OPENAI_API_VERSION")
            if os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"):
                self.config.setdefault('azure_openai', {})['deployment_name'] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            if os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"):
                self.config.setdefault('embeddings', {})['deployment_name'] = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

            # Milvus
            if os.getenv("MILVUS_HOST"):
                self.config.setdefault('milvus', {})['host'] = os.getenv("MILVUS_HOST")
            if os.getenv("MILVUS_PORT"):
                try:
                    self.config.setdefault('milvus', {})['port'] = int(os.getenv("MILVUS_PORT"))
                except ValueError as e:
                    config_logger.warning(f"Invalid MILVUS_PORT value: {os.getenv('MILVUS_PORT')}")
            if os.getenv("MILVUS_USER"):
                self.config.setdefault('milvus', {})['user'] = os.getenv("MILVUS_USER")
            if os.getenv("MILVUS_PASSWORD"):
                self.config.setdefault('milvus', {})['password'] = os.getenv("MILVUS_PASSWORD")
            if os.getenv("MILVUS_DATABASE"):
                self.config.setdefault('milvus', {})['database'] = os.getenv("MILVUS_DATABASE")
            if os.getenv("MILVUS_SECURE"):
                self.config.setdefault('milvus', {})['secure'] = os.getenv("MILVUS_SECURE").lower() == 'true'
            if os.getenv("MILVUS_COLLECTION_NAME"):
                self.config.setdefault('milvus', {})['collection_name'] = os.getenv("MILVUS_COLLECTION_NAME")

            config_logger.info("Environment variable overrides applied")

        except Exception as e:
            log_exception(e, context="ConfigLoader._override_with_env")
            config_logger.warning(f"Error applying environment overrides: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'azure_openai.endpoint')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_prompt(self, prompt_name: str) -> str:
        """Get prompt template by name.
        
        Args:
            prompt_name: Name of the prompt template
            
        Returns:
            Prompt template string
        """
        return self.prompts.get(prompt_name, "")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config


# Global configuration instance
_config_instance = None


def get_config() -> ConfigLoader:
    """Get global configuration instance.
    
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance

