import os
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists (for local testing)
load_dotenv()

class Config:
    # --- Application Settings ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local") # 'local', 'staging', 'production'
    PORT = int(os.getenv("PORT", 8080))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # --- Google Cloud & Vertex AI Settings ---
    # In Cloud Run, PROJECT_ID is often available by default, but it's best to be explicit
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro")

    # --- Memory / Checkpointer Settings ---
    # For local: "sqlite". For production: "firestore" or "postgres"
    CHECKPOINT_BACKEND = os.getenv("CHECKPOINT_BACKEND", "sqlite")
    LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "short_term_memory.db")
    
    # --- MCP Tool Settings ---
    # 'stdio' for local npx execution, 'sse' for remote secure execution
    MCP_TRANSPORT_MODE = os.getenv("MCP_TRANSPORT_MODE", "stdio")
    INTERNAL_MCP_SERVER_URL = os.getenv("INTERNAL_MCP_SERVER_URL", "")

# --- Logging Setup ---
def setup_logging():
    """Configures JSON-friendly logging for Google Cloud Operations (Stackdriver)."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # If in production, you might want to use python-json-logger here
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format=log_format
    )
    return logging.getLogger("stateless-agent")

logger = setup_logging()
