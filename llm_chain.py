# llm_chain.py
import streamlit as st
import os
from prompts import create_prompt_templates
from llm import LLMHandler
from langchain.prompts import ChatPromptTemplate


class LLMChainWrapper:
    def __init__(self, llm_handler: LLMHandler):
        self.llm_handler = llm_handler
        self.system_prompt_template, self.human_prompt_template, self.followup_human_prompt_template = create_prompt_templates()
        self.chat_history = [] #  No longer needed here, app.py session state is used

    def load_context_files(self):
        """Loads goal.txt and code.txt from the context folder."""
        goal_content = ""
        code_context = ""

        goal_file_path = os.path.join('context', 'goal.txt')
        code_file_path = os.path.join('context', 'code.txt')

        try:
            with open(goal_file_path, 'r', encoding='utf-8') as f:
                goal_content = f.read()
        except FileNotFoundError:
            st.warning("goal.txt not found in context folder.")
            goal_content = "No project goal set."
        except Exception as e:
            st.error(f"Error reading goal.txt: {e}")
            goal_content = "Error loading project goal."

        try:
            with open(code_file_path, 'r', encoding='utf-8') as f:
                code_context = f.read()
        except FileNotFoundError:
            st.warning("code.txt not found in context folder.")
            code_context = "No code context provided."
        except Exception as e:
            st.error(f"Error reading code.txt: {e}")
            code_context = "Error loading code context."

        return goal_content, code_context

    def get_initial_llm_response(self, user_message, llm_provider, llm_config):
        """Gets the LLM response for the first user message, including context."""
        goal_content, code_context = self.load_context_files()

        prompt = ChatPromptTemplate.from_messages([
            self.system_prompt_template,
            self.human_prompt_template
        ])

        formatted_prompt = prompt.format_messages(
            goal_content=goal_content,
            code_context=code_context,
            user_message=user_message
        )

        if llm_provider == "OpenAI":
            return self.llm_handler.openai_chat(formatted_prompt, llm_config["openai_api_key"])
        elif llm_provider == "Azure OpenAI":
            return self.llm_handler.azure_openai_chat(formatted_prompt, llm_config["azure_openai_api_key"], llm_config["azure_openai_endpoint"], llm_config["azure_openai_deployment_name_chat"], llm_config["azure_openai_api_version"])
        elif llm_provider == "Ollama":
            return self.llm_handler.ollama_chat(formatted_prompt, llm_config["ollama_base_url"], llm_config["ollama_model_name_chat"])
        else:
            return "LLM Provider not selected or supported."

    def get_followup_llm_response(self, user_message, llm_provider, llm_config, chat_history):
        """Gets LLM response for subsequent messages, including chat history but not code context."""

        # Format chat history into a readable string
        formatted_history = ""
        if chat_history:
            for message in chat_history:
                formatted_history += f"{message['role'].capitalize()}: {message['content']}\n\n"

        prompt = ChatPromptTemplate.from_messages([
            self.system_prompt_template, # System prompt is still relevant
            self.followup_human_prompt_template # Use follow-up template with history
        ])

        formatted_prompt = prompt.format_messages(
            user_message=user_message,
            chat_history=formatted_history # Include formatted chat history
        )

        if llm_provider == "OpenAI":
            return self.llm_handler.openai_chat(formatted_prompt, llm_config["openai_api_key"])
        elif llm_provider == "Azure OpenAI":
            return self.llm_handler.azure_openai_chat(formatted_prompt, llm_config["azure_openai_api_key"], llm_config["azure_openai_endpoint"], llm_config["azure_openai_deployment_name_chat"], llm_config["azure_openai_api_version"])
        elif llm_provider == "Ollama":
            return self.llm_handler.ollama_chat(formatted_prompt, llm_config["ollama_base_url"], llm_config["ollama_model_name_chat"])
        else:
            return "LLM Provider not selected or supported."