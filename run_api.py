"""Script to run the FastAPI application."""
import sys
import uvicorn
from src.utils.config_loader import get_config
from src.utils.logger import setup_logger
from src.utils.exception_handler import log_exception, ConfigurationError

# Initialize logger
logger = setup_logger(__name__)


def main():
    """Run the FastAPI application."""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()

        # Get server settings
        host = "localhost"
        port = config.get('fastapi.port', 8000)
        reload = True

        logger.info(f"Server configuration: host={host}, port={port}, reload={reload}")

        print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║   Sales Transcript Analysis API                              ║
    ║                                                              ║
    ║   Server starting at: http://{host}:{port}              ║
    ║   API Documentation: http://{host}:{port}/docs          ║
    ║                                                              ║
    ║   Press CTRL+C to stop the server                           ║
    ╚══════════════════════════════════════════════════════════════╝
        """)

        # Run the server
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e.message}")
        print(f"Details: {e.details}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        print("\n\n✅ Server stopped gracefully")
        sys.exit(0)

    except Exception as e:
        log_exception(e, context="run_api.main")
        logger.error(f"Fatal error starting server: {e}")
        print(f"\n❌ Fatal Error: {str(e)}")
        print("Check logs/exceptions.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()

