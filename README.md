# AI-Powered Challenge Onboarding Wizard - Backend

This repository contains the backend server for the AI-Powered Challenge Onboarding Wizard. It is a robust Python application built with FastAPI that serves as the "brain" for the entire challenge creation process, providing both the Phase 1 conversational agent and the Phase 2 AI-powered recommendation engine.

## Architecture Overview

The backend is designed as a modular, service-oriented application that communicates with a Next.js frontend. It leverages a multi-agent system built with LangGraph to manage the complex, stateful conversation for problem scoping and integrates with various AI services for recommendations.

A simple overview of the request flow:

```
+------------------+      +-------------------------+      +---------------------+
|                  |      |                         |      |                     |
|  Next.js Frontend|----->|   FastAPI Backend       |----->|  OpenAI & LangGraph |
| (React UI)       |      | (WebSocket & REST APIs) |      |  (LLM & Agent Logic)|
|                  |      |                         |      |                     |
+------------------+      +-----------+-------------+      +----------+----------+
                                      |                       ^
                                      |                       |
                                      v                       |
                               +------+-----------------------+
                               |      Qdrant Vector Database  |
                               |      (RAG for Similar      |
                               |      Challenges)             |
                               +-----------------------------+
```

## Agents in the Workflow

The system is built on a modular, agent-based architecture. Each agent is responsible for a specific stage:

- **Scope Discussion Agent**: Interactively clarifies and refines the initial challenge description with the user.
- **Schema Selection Agent**: Selects the most appropriate schema template based on the clarified scope.
- **RAG Integration Agent**: Searches for similar challenges to provide relevant context.
- **Specification Generation Agent**: Drafts a structured challenge specification from the gathered information.
- **Specification Discussion Agent**: Iteratively reviews and refines the generated specification with the user.

## Core Features

- **Phase 1 Conversational Agent**: A stateful, LangGraph-powered agent that interactively refines a user's problem statement via a persistent WebSocket connection.
- **Phase 2 Recommendation Engine**: A suite of REST APIs that provide intelligent, context-aware suggestions for every step of the challenge wizard.
- **Retrieval-Augmented Generation (RAG)**: Integrates with a Qdrant vector database to retrieve similar past challenges, grounding the AI's suggestions in real-world examples.
- **Dynamic Schema Support**: Uses a configurable JSON file (`platform_schema.json`) to define the structure of the final challenge specification, making the wizard adaptable to different platforms.

## 🚀 Getting Started

Follow these steps to set up and run the backend server locally.

### 1. Environment Configuration

This project requires API keys for OpenAI and Qdrant. Never commit API keys directly to your repository.

First, create a `.env` file in the root of the `/backend` directory. You can copy the example file if one is provided:

```bash
cp .env.example .env
```

Next, open the `.env` file and add your secret keys:

```
OPENAI_API_KEY="sk-..."
QDRANT_API_KEY="..."
```

The application uses the `python-dotenv` library to automatically load these variables when it starts.

### 2. Installation

It is highly recommended to use a Python virtual environment to manage dependencies.

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Running the Server

Once your environment is configured and dependencies are installed, you can start the FastAPI server:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading, which is useful for development. The API will now be live and accessible at `http://localhost:8000`.

## ⚙️ Configuration Deep Dive

While API keys are managed in `.env`, other operational parameters are configured in Python and JSON files.

### Core Configuration (`config/config.py`)

This file stores key parameters for the application's behavior. You can adjust these values as needed:

- `QDRANT_ENDPOINT`: The URL for your Qdrant instance.
- `QDRANT_COLLECTION_NAME`: The name of the collection holding challenge templates.
- `RAG_EMBEDDING_MODEL`: The OpenAI embedding model used for RAG.
- `RAG_NUM_RETRIEVED_CHALLENGES`: The number of similar challenges to retrieve.
- `MAX_SPEC_CHANGES_ALLOWED`: The number of times a user can adjust a generated spec.

### Platform Schemas (`config/platform_schema.json`)

This file defines the structure for different challenge types. You can modify this file to add, remove, or change the required fields for any challenge, and the schema-driven parts of the application will adapt accordingly.

### RAG Integration

The service is integrated with a Qdrant vector database to find similar challenges for Retrieval-Augmented Generation. For development, the endpoint in `config.py` points to a pre-populated database. If you wish to import your own data, a helper script is provided in the `qdrant-challenges-importer` directory.

## Project Structure

A brief overview of the key directories and files:

- `/agent`: Contains the core logic for the LangGraph agent and the various recommender modules.
- `/agent/nodes`: Individual, modular functions that represent the steps in the LangGraph workflow.
- `/config`: Holds all project configuration, including prompts and the platform schema.
- `/utils`: Helper modules for tasks like input handling and RAG integration.
- `server.py`: The main FastAPI application file that defines all API endpoints and manages WebSocket connections.
- `main.py`: The entry point for running the agent in a command-line interface (CLI) mode for testing.

## API Endpoints

The server exposes the following endpoints for the frontend application:

### WebSocket Endpoint
- `ws:///ws?session={sessionId}`: Establishes a real-time, stateful connection for the Step 1 conversational agent.

### REST Endpoints
- `POST /api/recommendations`: Gets AI-powered challenge type recommendations.
- `POST /api/impact-preview`: Gets an AI-generated preview of how a challenge type affects later steps.
- `POST /api/audience-recommendations`: Gets suggestions for target audience and registration settings.
- `POST /api/submission-recommendations`: Gets suggestions for submission formats and guidelines.
- `POST /api/prize-recommendations`: Gets suggestions for prize structures and recognition plans.
- `POST /api/timeline-recommendations`: Gets suggestions for timelines and key milestones.
- `POST /api/evaluation-recommendations`: Gets suggestions for evaluation criteria and scoring models.
- `POST /api/communications-recommendations`: Gets suggestions for communication and monitoring plans.
- `POST /api/validate-challenge`: Analyzes the complete challenge configuration for potential conflicts or inconsistencies.
- `POST /api/get-schema-for-step`: Retrieves the dynamic form fields for a specific step from `platform_schema.json`.