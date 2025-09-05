# === CONFIGURATION ===
QDRANT_ENDPOINT = "https://d9edf050-e175-4cf1-8c4d-c3ee8c7cf9e2.us-east-1-1.aws.cloud.qdrant.io:6333"
QDRANT_COLLECTION_NAME = "challenge_templates" # Qdrant collection name for challenge templates
RAG_EMBEDDING_MODEL = "text-embedding-3-small" # OpenAI embedding model for RAG
RAG_NUM_RETRIEVED_CHALLENGES = 2 # Number of challenges to retrieve from Qdran for RAG
MAX_SPEC_CHANGES_ALLOWED = "unlimited" # or set to a specific number like 5