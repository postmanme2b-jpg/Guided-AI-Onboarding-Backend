# === CONFIGURATION ===
QDRANT_ENDPOINT = "https://1ffe4e9a-9602-4fd7-a0a1-d2b045f45c96.us-west-1-0.aws.cloud.qdrant.io" # Qdrant endpoint for challenge templates
QDRANT_COLLECTION_NAME = "challenge_templates" # Qdrant collection name for challenge templates
RAG_EMBEDDING_MODEL = "text-embedding-3-small" # OpenAI embedding model for RAG
RAG_NUM_RETRIEVED_CHALLENGES = 2 # Number of challenges to retrieve from Qdran for RAG
MAX_SPEC_CHANGES_ALLOWED = "unlimited" # or set to a specific number like 5