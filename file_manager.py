import streamlit as st
import os
from streamlit_tree_select import tree_select

# Define ignore lists (simplified display)
FOLDER_IGNORE = {'.git', 'node_modules', '__pycache__', 'venv', '.vscode', 'dist', 'build', '.idea', '.DS_Store'}
FILE_IGNORE = {'.pyc', '.pyo', '.pyd', '.db', '.sqlite', '.sqlite3', '.sql', '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.pkl', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.DS_Store', '.env'}

def should_ignore(name, is_dir=False):
    """Check if a file or folder should be ignored."""
    if is_dir:  
        return name in FOLDER_IGNORE
    return any(name.endswith(ext) for ext in FILE_IGNORE)

def get_folder_tree(folder_path):
    """Recursively builds the tree structure for streamlit-tree-select."""
    def get_tree_nodes(path):
        nodes = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                if should_ignore(item, is_dir):
                    continue
                    
                if is_dir:
                    children = get_tree_nodes(item_path)
                    if children:
                        nodes.append({
                            "label": item,
                            "value": item_path,
                            "children": children,
                        })
                else:
                    nodes.append({"label": item, "value": item_path})
        except PermissionError:
            st.warning(f"Permission denied accessing {path}")
        return nodes

    base_name = os.path.basename(folder_path)
    return [{"label": base_name, "value": folder_path, "children": get_tree_nodes(folder_path)}]

def get_selected_files_content(selected_files, base_path):
    """Reads the content of selected files."""
    file_contents = {}
    if selected_files:
        for path in selected_files:
            if os.path.isfile(path) and not should_ignore(os.path.basename(path)):
                try:
                    # Get relative path from base directory
                    rel_path = os.path.relpath(path, base_path)
                    with open(path, 'r', encoding='utf-8') as f:
                        file_contents[rel_path] = f.read()
                except Exception as e:
                    file_contents[rel_path] = f"Error reading file: {e}"
    return file_contents

def get_tree_structure_string(tree_data):
    """Converts the tree data to a string for output."""
    def tree_to_string(nodes, indent=0):
        tree_str = ""
        for node in nodes:
            tree_str += "  " * indent + "- " + node['label'] + "\n"
            if 'children' in node:
                tree_str += tree_to_string(node['children'], indent + 1)
        return tree_str

    tree_string = ""
    if tree_data:
        tree_string = tree_to_string(tree_data)
    return tree_string

def format_output_text(tree_structure_str, file_contents):
    """Formats the output text with tree structure and file contents."""
    output_text = "Folder Tree Structure:\n"
    output_text += tree_structure_str + "\n\n"
    output_text += "Selected File Contents:\n"
    for filepath, content in file_contents.items():
        output_text += f"\n=== File: {filepath} ===\n"  
        output_text += content + "\n"
        output_text += "=" * (len(filepath) + 11) + "\n"  
    return output_text




def save_context_file(content):
    """Saves the content to a context.txt file in the code folder."""
    try:
        os.makedirs('context', exist_ok=True)
        file_path = os.path.join('context', 'code.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False


def save_goal_file(goal_text):
    """Saves the goal text to a goal.txt file in the context folder."""
    try:
        os.makedirs('context', exist_ok=True)
        file_path = os.path.join('context', 'goal.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(goal_text)
        return True
    except Exception as e:
        st.error(f"Error saving goal file: {e}")
        return False

def read_goal_file():
    """Reads the goal text from goal.txt if it exists, returns empty string if not."""
    file_path = os.path.join('context', 'goal.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        st.error(f"Error reading goal file: {e}")
        return ""