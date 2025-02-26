# prompts.py
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def create_prompt_templates():
    """Creates and returns system and human prompt templates."""

    system_prompt_template = SystemMessagePromptTemplate.from_template(
        "You are a helpful AI code assistant. Your role is to assist the user with their coding tasks based on the project context and their goals. "
        "Follow the user's instructions carefully and provide accurate and relevant code or information. "
        "Assume the user has been provided with project context at the start of this conversation, and conversation history is available for context."
    )

    human_prompt_template = HumanMessagePromptTemplate.from_template(
        "Project Goal:\n{goal_content}\n\n"
        "Project Code Context:\n{code_context}\n\n"
        "User Message: {user_message}"
    )

    followup_human_prompt_template = HumanMessagePromptTemplate.from_template(
        "Chat History:\n{chat_history}\n\n" # Added chat_history placeholder
        "User Message: {user_message}"
    )

    return system_prompt_template, human_prompt_template, followup_human_prompt_template