from dotenv import load_dotenv
import os

load_dotenv()

MODEL_CONFIG = {
    "llama": {
        "api_url": "http://localhost:1234/v1/chat/completions",
        "model_name": "llama-3.1-8b-instruct"
    },
    "vedas_agent": {
        "endpoint": "http://localhost:8001/ask-vedas",
        "headers": {"Content-Type": "application/json"},
        "api_key": os.getenv("GEMINI_API_KEY"),
        "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
    },
    "edumentor_agent": {
        "endpoint": "http://localhost:8001/edumentor",
        "headers": {"Content-Type": "application/json"},
        "api_key": os.getenv("GEMINI_API_KEY"),
        "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
    },
    "wellness_agent": {
        "endpoint": "http://localhost:8001/wellness",
        "headers": {"Content-Type": "application/json"},
        "api_key": os.getenv("GEMINI_API_KEY"),
        "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
    }
}

MONGO_CONFIG = {
    "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
    "database": "bhiv_core",
    "collection": "task_logs"
}

# Timeout Configuration
TIMEOUT_CONFIG = {
    "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", 120)),
    "image_processing_timeout": int(os.getenv("IMAGE_PROCESSING_TIMEOUT", 180)),
    "audio_processing_timeout": int(os.getenv("AUDIO_PROCESSING_TIMEOUT", 240)),
    "pdf_processing_timeout": int(os.getenv("PDF_PROCESSING_TIMEOUT", 150)),
    "llm_timeout": int(os.getenv("LLM_TIMEOUT", 120)),
    "file_upload_timeout": int(os.getenv("FILE_UPLOAD_TIMEOUT", 300))
}

RL_CONFIG = {
    "use_rl": os.getenv("USE_RL", "true").lower() == "true",
    "exploration_rate": float(os.getenv("RL_EXPLORATION_RATE", 0.2)),
    "buffer_file": "logs/learning_log.json",
    "model_log_file": "logs/model_logs.json",
    "agent_log_file": "logs/agent_logs.json",
    "memory_size": int(os.getenv("RL_MEMORY_SIZE", 1000)),
    "min_exploration_rate": float(os.getenv("RL_MIN_EXPLORATION", 0.05)),
    "exploration_decay": float(os.getenv("RL_EXPLORATION_DECAY", 0.995)),
    "confidence_threshold": float(os.getenv("RL_CONFIDENCE_THRESHOLD", 0.7)),
    "enable_ucb": os.getenv("RL_ENABLE_UCB", "true").lower() == "true",
    "enable_fallback_learning": os.getenv("RL_ENABLE_FALLBACK_LEARNING", "true").lower() == "true",
    "log_to_mongo": os.getenv("RL_LOG_TO_MONGO", "true").lower() == "true"
}


# from dotenv import load_dotenv
# import os

# load_dotenv()

# MODEL_CONFIG = {
#     "llama": {
#         "api_url": "http://localhost:1234/v1/chat/completions",
#         "model_name": "llama-3.1-8b-instruct"
#     },
#     "vedas_agent": {
#         "endpoint": "http://localhost:8001/ask-vedas",
#         "headers": {"Content-Type": "application/json"},
#         "api_key": os.getenv("GEMINI_API_KEY"),
#         "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
#     },
#     "edumentor_agent": {
#         "endpoint": "http://localhost:8001/edumentor",
#         "headers": {"Content-Type": "application/json"},
#         "api_key": os.getenv("GEMINI_API_KEY"),
#         "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
#     },
#     "wellness_agent": {
#         "endpoint": "http://localhost:8001/wellness",
#         "headers": {"Content-Type": "application/json"},
#         "api_key": os.getenv("GEMINI_API_KEY"),
#         "backup_api_key": os.getenv("GEMINI_API_KEY_BACKUP")
#     }
# }

# MONGO_CONFIG = {
#     "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
#     "database": "bhiv_core",
#     "collection": "task_logs"
# }