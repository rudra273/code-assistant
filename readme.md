# AI Code Assistant

This tool is designed to help you with code generation and modification using AI. It leverages Large Language Models (LLMs) to understand your coding goals and project context to provide relevant assistance.

## How to Use

1.  **Set Project Goal:** In the main panel, use the "Set Project Goal" text area to describe the overall objective or purpose of your coding project. Click "Update Goal" to save it. This goal will be used as part of the context for the AI assistant.
2.  **Select Project Folder:** In the sidebar under "Project Context", enter the path to your project's root folder. This will display a file tree.
3.  **Select Code Files:** Browse the file tree in the sidebar and select the code files that are relevant to your current task or question.
4.  **Save Context:** In the main panel (if the "Show Code Context" toggle is enabled), you'll see a preview of the selected file contents. Click "Save Context" to save this code context for the AI assistant to use.  Remember to re-save context if you change file selections for a fresh chat.
5.  **Choose LLM Provider:** In the sidebar under "Configuration" -> "LLM Provider", select your desired LLM provider (OpenAI, Azure OpenAI, or Ollama).
6.  **Enter API Keys/Configuration:** Depending on your chosen provider, enter the necessary API keys, endpoints, or base URLs in the sidebar. These settings are not persistently saved by the app itself, but you can store them in `config.yaml` for default loading.
7.  **Chat with the AI:** In the main panel under "Chat with AI Assistant", type your questions or instructions in the chat input and press Enter to send. The AI assistant will respond based on your goal, code context, and chat history.
8.  **Show/Hide Code Context:** Use the "Show Code Context" toggle button in the right column of the main panel to show or hide the code context preview window.

## Configuration

For persistent settings, you can create a `config.yaml` file in the app's directory with the following structure:

```yaml
default_llm_provider: OpenAI
default_vectorization: false

openai_api_key: "YOUR_OPENAI_API_KEY"

azure_openai_api_key: "YOUR_AZURE_API_KEY"
azure_openai_endpoint: "YOUR_AZURE_ENDPOINT"
azure_openai_deployment_name_chat: "YOUR_AZURE_CHAT_DEPLOYMENT_NAME"
azure_openai_api_version: "2024-02-01"
azure_openai_deployment_name_embedding: "YOUR_AZURE_EMBEDDING_DEPLOYMENT_NAME"

ollama_base_url: "http://localhost:11434"
ollama_model_name_chat: "llama2"
ollama_model_name_embedding: "llama2"