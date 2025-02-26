# llm.py
from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
import requests


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming to Streamlit."""
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs):
        """Stream output to a Streamlit app."""
        return token


class LLMHandler:
    def openai_chat(self, prompt, openai_api_key, model_name="gpt-4o-mini"):
        """Handle OpenAI chat completion with proper streaming."""
        streaming_handler = StreamingCallbackHandler()
        chat_openai = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            streaming=True,
            callbacks=[streaming_handler]
        )
        return chat_openai.stream(prompt)

    def azure_openai_chat(self, prompt, azure_openai_api_key, azure_openai_endpoint, azure_openai_deployment_name_chat, azure_openai_api_version, model_name="gpt-4o-mini"):
        """Handle Azure OpenAI chat completion with proper streaming."""
        streaming_handler = StreamingCallbackHandler()
        # print(azure_openai_deployment_name_chat)
        azure_chat_openai = AzureChatOpenAI(
            api_key=azure_openai_api_key,
            azure_endpoint=azure_openai_endpoint,
            deployment_name=azure_openai_deployment_name_chat,
            api_version=azure_openai_api_version,
            streaming=True,
            callbacks=[streaming_handler]
        )
        return azure_chat_openai.stream(prompt)

    
    def ollama_chat(self, prompt, ollama_base_url, model_name="llama2"):
        """Handle Ollama chat completion with proper streaming."""
        streaming_handler = StreamingCallbackHandler()
        ollama_llm = Ollama(  # Use Ollama class here
            base_url=ollama_base_url,
            model=model_name,  # Use 'model' instead of 'model_name' for Ollama class
            callbacks=[streaming_handler]
        )
        return ollama_llm.stream(prompt)


    def openai_embeddings(self, openai_api_key, model_name="text-embedding-ada-002"):
        return OpenAIEmbeddings(openai_api_key=openai_api_key, model_name=model_name)

    def azure_openai_embeddings(self, azure_openai_api_key, azure_openai_endpoint, azure_openai_deployment_name_embedding, azure_openai_api_version, model_name="text-embedding-ada-002"):
        return AzureOpenAIEmbeddings(
            api_key=azure_openai_api_key,
            azure_endpoint=azure_openai_endpoint,
            deployment_name=azure_openai_deployment_name_embedding,
            api_version=azure_openai_api_version
        )

    def ollama_embeddings(self, ollama_base_url, model_name="llama2"):
        return OllamaEmbeddings(base_url=ollama_base_url, model_name=model_name)

    def list_ollama_models(self, ollama_base_url):
        """List available Ollama models."""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                st.error(f"Failed to fetch Ollama models: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error fetching Ollama models: {e}")
            return []