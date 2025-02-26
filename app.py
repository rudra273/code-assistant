# app.py
import streamlit as st
import os
from streamlit_tree_select import tree_select
import yaml
from file_manager import (FILE_IGNORE, FOLDER_IGNORE, get_folder_tree,
                            should_ignore, get_selected_files_content,
                            get_tree_structure_string, format_output_text,
                            save_context_file, save_goal_file, read_goal_file)
from llm import LLMHandler
from llm_chain import LLMChainWrapper

def setup_page_config():
    """Configure page settings and custom CSS"""
    st.set_page_config(layout="wide")
    
    # Inject custom CSS for sidebar width and reduced top margin
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                width: 40% !important;
                max-width: 40%;
                min-width: 40%;
            }
            
            /* Reduce top margin */
            .main .block-container {
                padding-top: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_configuration():
    """Load configuration from YAML file"""
    config = {}
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        st.warning("config.yaml not found. Using default settings or prompting for API keys.")
    except yaml.YAMLError as e:
        st.error(f"Error parsing config.yaml: {e}")
    return config

def initialize_session_state(config):
    """Initialize all session state variables"""
    if 'selected_files' not in st.session_state:
        st.session_state['selected_files'] = None
    if 'goal_defined' not in st.session_state:
        st.session_state['goal_defined'] = False
    if 'system_prompt_text' not in st.session_state:
        st.session_state['system_prompt_text'] = ""
    if 'llm_provider' not in st.session_state:
        st.session_state['llm_provider'] = config.get('default_llm_provider', 'OpenAI')
    if 'vectorization_enabled' not in st.session_state:
        st.session_state['vectorization_enabled'] = config.get('default_vectorization', False)
    if 'copy_prompt_requested' not in st.session_state:
        st.session_state['copy_prompt_requested'] = False
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'chat_initialized' not in st.session_state:
        st.session_state['chat_initialized'] = False
    if 'show_context' not in st.session_state:
        st.session_state['show_context'] = True

def configure_llm_provider_settings(config):
    """Configure LLM provider selection and corresponding settings"""
    st.subheader("LLM Provider")
    llm_provider_options = ["OpenAI", "Azure OpenAI", "Ollama"]
    llm_provider = st.selectbox("Select", llm_provider_options, index=llm_provider_options.index(st.session_state['llm_provider']))
    st.session_state['llm_provider'] = llm_provider

    if llm_provider == "OpenAI":
        st.session_state['openai_api_key'] = st.text_input("OpenAI API Key", type="password", value=config.get('openai_api_key', ""), help="Enter your OpenAI API key. You can save it in config.yaml for default use.")
    elif llm_provider == "Azure OpenAI":
        st.session_state['azure_openai_api_key'] = st.text_input("Azure OpenAI API Key", type="password", value=config.get('azure_openai_api_key', ""), help="Enter your Azure OpenAI API key.")
        st.session_state['azure_openai_endpoint'] = st.text_input("Azure OpenAI Endpoint", value=config.get('azure_openai_endpoint', ""), help="Enter your Azure OpenAI Endpoint.")
        st.session_state['azure_openai_deployment_name_chat'] = st.text_input("Azure OpenAI Chat Deployment Name", value=config.get('azure_openai_deployment_name_chat', ""), help="Enter your Azure Chat Deployment Name.")
        st.session_state['azure_openai_api_version'] = st.text_input("Azure OpenAI API Version", value=config.get('azure_openai_api_version', "2023-05-15"), help="Enter your Azure API Version.", disabled=True)
        st.session_state['azure_openai_deployment_name_embedding'] = st.text_input("Azure OpenAI Embedding Deployment Name", value=config.get('azure_openai_deployment_name_embedding', ""), help="Enter your Azure Embedding Deployment Name.")
    elif llm_provider == "Ollama":
        st.session_state['ollama_base_url'] = st.text_input("Ollama Base URL", value=config.get('ollama_base_url', "http://localhost:11434"), help="Enter your Ollama Base URL (default is http://localhost:11434).")
        
        if st.session_state['ollama_base_url']:
            available_models = llm_handler.list_ollama_models(st.session_state['ollama_base_url'])
            if available_models:
                st.session_state['ollama_model_name_chat'] = st.selectbox("Ollama Chat Model", options=available_models, index=0, help="Select Ollama model for chat.")
                st.session_state['ollama_model_name_embedding'] = st.selectbox("Ollama Embedding Model", options=available_models, index=0, help="Select Ollama model for embeddings.")
            else:
                st.error("No Ollama models found. Please ensure Ollama is running and models are installed.")
        else:
            st.warning("Please enter a valid Ollama Base URL to list available models.")

def setup_code_context():
    """Setup code context panel"""
    st.subheader("Code Context")
    show_context_window = st.checkbox("Show Code Context", value=st.session_state['show_context'])
    st.session_state['show_context'] = show_context_window

    if show_context_window:
        folder_path_input = st.text_input("Enter Project path:", ".", key="folder_path_sidebar_right")
        selected_files = []

        if folder_path_input:
            if os.path.isdir(folder_path_input):
                tree_data = get_folder_tree(folder_path_input)
                selected = tree_select(tree_data, key="tree_sidebar_right")
                if selected:
                    selected_files_folders = selected.get("checked") or []
                    selected_files = [
                        item for item in selected_files_folders
                        if os.path.isfile(item) and not should_ignore(os.path.basename(item))
                    ]

                if selected_files:
                    st.session_state['file_contents'] = get_selected_files_content(selected_files, folder_path_input)
                    tree_structure_str = get_tree_structure_string(tree_data)
                    output_text = format_output_text(tree_structure_str, st.session_state['file_contents'])
                    st.text_area("Context Preview", output_text, height=300)
                    if st.button("Save Context", key="save_context_button_right"):
                        if save_context_file(output_text):
                            st.success("Context saved to context/code.txt")
                            st.session_state['chat_initialized'] = False
                else:
                    st.info("No files selected or no valid folder path provided.")

def handle_project_goal():
    """Handle project goal section"""
    initial_goal = read_goal_file()
    goal_text = st.text_area("Set Project Goal:", initial_goal, height=100)
    if st.button("Update Goal", key="update_goal_main"):
        if save_goal_file(goal_text):
            st.success("Goal updated and saved!")
        else:
            st.error("Failed to save goal.")


def handle_chat(llm_handler, llm_chain_wrapper):
    """Handle chat interface and message processing"""
    header_col, button_col = st.columns([8, 2])
    with header_col:
        st.subheader("Chat with AI Assistant")
    with button_col:
        if st.button("Clear Chat"):
            st.session_state['chat_history'] = []
            st.session_state['chat_initialized'] = False
            # Remove experimental_rerun() so the UI updates on the next interaction

    user_input = st.chat_input("Enter your message here", key="chat_input_main")
    
    # Display chat history
    for message in st.session_state['chat_history']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input:
        # Add and display user message
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            llm_config = {
                "openai_api_key": st.session_state.get('openai_api_key'),
                "azure_openai_api_key": st.session_state.get('azure_openai_api_key'),
                "azure_openai_endpoint": st.session_state.get('azure_openai_endpoint'),
                "azure_openai_deployment_name_chat": st.session_state.get('azure_openai_deployment_name_chat'),
                "azure_openai_api_version": st.session_state.get('azure_openai_api_version'),
                "ollama_base_url": st.session_state.get('ollama_base_url'),
                "ollama_model_name_chat": st.session_state.get('ollama_model_name_chat')
            }

            try:
                if not st.session_state['chat_initialized']:
                    response_generator = llm_chain_wrapper.get_initial_llm_response(
                        user_input, st.session_state['llm_provider'], llm_config
                    )
                    st.session_state['chat_initialized'] = True
                else:
                    response_generator = llm_chain_wrapper.get_followup_llm_response(
                        user_input, st.session_state['llm_provider'], llm_config, st.session_state['chat_history'][:-1]
                    )
    
                for chunk in response_generator:
                    chunk_content = extract_chunk_content(chunk)
                    if chunk_content:
                        full_response += chunk_content
                        message_placeholder.markdown(full_response + "▌")
    
                message_placeholder.markdown(full_response)
    
            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                message_placeholder.error(error_message)
                full_response = error_message
    
            if full_response:
                st.session_state['chat_history'].append({"role": "assistant", "content": full_response})

def extract_chunk_content(chunk):
    """Helper function to extract content from different chunk formats"""
    if hasattr(chunk, 'content'):
        # LangChain Message object
        return chunk.content
    elif isinstance(chunk, tuple) and len(chunk) >= 2:
        # Tuple format from some providers
        if chunk[0] == 'content':
            return chunk[1]
    elif isinstance(chunk, str):
        # Direct string format
        return chunk
    return None

def main():
    """Main application function"""
    # Setup and configuration
    setup_page_config()
    config = load_configuration()
    initialize_session_state(config)
    
    # Initialize handlers
    global llm_handler, llm_chain_wrapper
    llm_handler = LLMHandler()
    llm_chain_wrapper = LLMChainWrapper(llm_handler)
    
    # App title
    st.title("AI Code Assistant")
    
    # Left sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        configure_llm_provider_settings(config)
    
    # Right sidebar for code context
    with st.sidebar:
        setup_code_context()
    
    # Main page content
    handle_project_goal()
    handle_chat(llm_handler, llm_chain_wrapper)

if __name__ == "__main__":
    main()