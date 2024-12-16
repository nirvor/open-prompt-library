import streamlit as st
import yaml
import os
import pyperclip

# --- Konstanten ---
YAML_FILE = "prompts.yaml"

# --- YAML-Funktionen ---
def load_prompts_from_yaml():
    """Lädt Prompts aus der YAML-Datei oder erstellt eine neue."""
    if os.path.exists(YAML_FILE):
        with open(YAML_FILE, "r") as file:
            try:
                data = yaml.safe_load(file)
                return data if data else {"prompts": []}
            except yaml.YAMLError as e:
                st.error(f"Fehler beim Lesen der YAML-Datei: {e}")
                return {"prompts": []}
    else:
         # Erstellen Sie eine neue YAML-Datei mit einigen Beispiel-Prompts
        default_data = {
            "prompts": [
                {
                    "name": "Marketing",
                    "children": [
                        {
                            "name": "Social Media",
                            "content": "Schreibe einen Tweet über unser neues Produkt.",
                        },
                        {
                            "name": "E-Mail-Kampagne",
                            "content": "Entwirf einen Newsletter für unsere bevorstehende Veranstaltung.",
                        },
                    ],
                },
                {
                    "name": "Programmierung",
                    "children": [
                        {
                            "name": "Python Grundlagen",
                            "content": "Schreibe eine Python-Funktion zur Berechnung der Fakultät.",
                        },
                    ],
                },
            ]
        }

        with open(YAML_FILE, 'w') as file:
            yaml.safe_dump(default_data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return default_data
    
def save_prompts_to_yaml(data):
    """Speichert die Prompts in der YAML-Datei."""
    with open(YAML_FILE, "w") as file:
        yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

# --- UI-Funktionen ---
def display_prompt(prompt):
    """Zeigt einen Prompt an und bietet eine Kopierfunktion."""
    if prompt and "content" in prompt:
        st.text_area("Prompt", value=prompt["content"], height=150, key=f"prompt_content_{prompt.get('name')}")
        if st.button("Kopieren", key=f"copy_{prompt.get('name')}"):
            pyperclip.copy(prompt["content"])
            st.success("Prompt in die Zwischenablage kopiert!")
    else:
        st.info("Kein Prompt ausgewählt.")


def display_folder_structure(prompts, selected_prompt, level=0, parent_path=""):
    """Zeigt die Ordnerstruktur mit Prompts in einer Baumansicht."""
    for item in prompts:
        name = item.get("name", "Unbenannt")
        path = f"{parent_path}/{name}" if parent_path else name
        if "children" in item:
            with st.expander(f"{'  ' * level}📁 {name}", expanded=True):
                display_folder_structure(item["children"], selected_prompt, level + 1, path)
        else:
            is_selected = selected_prompt == path
            if st.button(f"{'  ' * level}📄 {name}", key=path, type="primary" if is_selected else "secondary"):
                selected_prompt = path
            if is_selected:
                display_prompt(item)
    return selected_prompt

def add_prompt(prompts, parent_path, new_prompt_name, new_prompt_content):
    """Fügt einen neuen Prompt zu einem Ordner hinzu."""
    if not parent_path:
         prompts.append({
                        "name": new_prompt_name,
                        "content": new_prompt_content
                        })
    else:
        path_parts = parent_path.split('/')
        current_node = prompts
        for part in path_parts:
            for node in current_node:
                if node.get('name') == part:
                    if 'children' in node:
                        current_node = node['children']
                    else:
                         # Der Pfad endet mit einem Prompt, nicht mit einem Ordner
                         return False # Nicht möglich, da Prompt keine Children hat
                    break
            else:
               return False # Pfad wurde nicht gefunden
        
        current_node.append({
                        "name": new_prompt_name,
                        "content": new_prompt_content
                        })
    return True

def add_folder(prompts, parent_path, new_folder_name):
    """Fügt einen neuen Ordner zu einem anderen Ordner hinzu."""
    if not parent_path:
         prompts.append({
                        "name": new_folder_name,
                        "children": []
                        })
    else:
         path_parts = parent_path.split('/')
         current_node = prompts
         for part in path_parts:
            for node in current_node:
                if node.get('name') == part:
                    if 'children' in node:
                        current_node = node['children']
                    else:
                        # Der Pfad endet mit einem Prompt, nicht mit einem Ordner
                        return False  # Nicht möglich, da Prompt keine Children hat
                    break
            else:
                return False  # Pfad wurde nicht gefunden
         current_node.append({
                        "name": new_folder_name,
                        "children": []
                        })
    return True


def edit_prompt(prompts, path, new_content):
    """Bearbeitet einen Prompt in einem Pfad."""
    path_parts = path.split('/')
    current_node = prompts
    for part in path_parts:
        for node in current_node:
            if node.get('name') == part:
                if part == path_parts[-1]:
                    node['content'] = new_content
                    return True
                elif 'children' in node:
                    current_node = node['children']
                    break
        else:
            return False
    return False

def delete_item(prompts, path):
     """Löscht ein Element (Prompt oder Ordner) aus dem Pfad."""
     path_parts = path.split('/')
     item_name = path_parts[-1]
     current_node = prompts
     
     if len(path_parts) == 1:
         for i, node in enumerate(current_node):
             if node.get('name') == item_name:
                 del current_node[i]
                 return True
         return False

     for part in path_parts[:-1]:
         for node in current_node:
             if node.get('name') == part:
                 if 'children' in node:
                     current_node = node['children']
                     break
         else:
            return False
     
     for i, node in enumerate(current_node):
        if node.get('name') == item_name:
            del current_node[i]
            return True
     return False

def search_prompts(prompts, query, path="", results=None):
    """Sucht Prompts nach Name oder Inhalt."""
    if results is None:
        results = []
    for item in prompts:
        item_path = f"{path}/{item.get('name')}" if path else item.get('name')
        if query.lower() in item.get("name", "").lower() or query.lower() in item.get("content", "").lower():
            results.append((item_path, item))
        if "children" in item:
            search_prompts(item["children"], query, item_path, results)
    return results

def export_folder_to_markdown(prompts, folder_path, level=0, markdown_content=""):
    """Exportiert einen Ordner mit Prompts in eine Markdown-Datei."""
    if folder_path:
      path_parts = folder_path.split('/')
      current_node = prompts
      for part in path_parts:
         for node in current_node:
            if node.get('name') == part:
                if 'children' in node:
                    current_node = node['children']
                    break
         else:
            return ""
      prompts = current_node
    
    for item in prompts:
        markdown_content += f"{'#' * (level + 1)} {item.get('name', 'Unbenannt')}\n"
        if "content" in item:
            markdown_content += f"{item.get('content', '')}\n\n"
        if "children" in item:
             markdown_content = export_folder_to_markdown(item["children"], None, level + 1, markdown_content)
    
    return markdown_content

# --- Hauptanwendung ---
def main():
    st.set_page_config(page_title="Prompt Library", layout="wide")
    st.title("Prompt Library")

    # Laden der Prompts
    prompts_data = load_prompts_from_yaml()

    # Zustand für den ausgewählten Prompt
    selected_prompt = st.session_state.get("selected_prompt", None)

    # UI-Layout
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Ordnerstruktur")
        selected_prompt = display_folder_structure(prompts_data["prompts"], selected_prompt)
        st.session_state["selected_prompt"] = selected_prompt # Update Session State

        with st.expander("Aktionen", expanded=True):
            # Hinzufügen eines neuen Prompts
            st.subheader("Neuen Prompt hinzufügen")
            new_prompt_name = st.text_input("Name des neuen Prompts")
            new_prompt_content = st.text_area("Inhalt des neuen Prompts", height=100)
            if st.button("Prompt Hinzufügen", key="add_new_prompt"):
                if new_prompt_name and new_prompt_content:
                    if add_prompt(prompts_data["prompts"], selected_prompt, new_prompt_name, new_prompt_content):
                        save_prompts_to_yaml(prompts_data)
                        st.success(f"Prompt '{new_prompt_name}' wurde hinzugefügt.")
                        st.experimental_rerun()
                    else:
                        st.error(f"Fehler beim Hinzufügen des Prompts.")
                else:
                    st.warning("Bitte gib einen Namen und Inhalt für den Prompt ein.")

            # Hinzufügen eines neuen Ordners
            st.subheader("Neuen Ordner hinzufügen")
            new_folder_name = st.text_input("Name des neuen Ordners")
            if st.button("Ordner hinzufügen", key="add_new_folder"):
                if new_folder_name:
                    if add_folder(prompts_data["prompts"], selected_prompt, new_folder_name):
                        save_prompts_to_yaml(prompts_data)
                        st.success(f"Ordner '{new_folder_name}' wurde hinzugefügt.")
                        st.experimental_rerun()
                    else:
                        st.error(f"Fehler beim Hinzufügen des Ordners.")
                else:
                    st.warning("Bitte gib einen Namen für den Ordner ein.")
            
            # Bearbeiten eines Prompts
            if selected_prompt:
                st.subheader("Prompt bearbeiten")
                edit_content = st.text_area("Neuer Inhalt", height=100, key="edit_prompt_content")
                if st.button("Prompt bearbeiten", key="edit_prompt_button"):
                     if edit_content:
                        if edit_prompt(prompts_data["prompts"], selected_prompt, edit_content):
                            save_prompts_to_yaml(prompts_data)
                            st.success("Prompt wurde erfolgreich bearbeitet.")
                            st.experimental_rerun()
                        else:
                            st.error("Fehler beim Bearbeiten des Prompts.")
                     else:
                        st.warning("Bitte gib einen Inhalt zum Bearbeiten an.")
            
            # Löschen eines Prompts oder Ordners
            if selected_prompt:
                 if st.button("Ausgewähltes Element löschen", key="delete_item_button"):
                    if delete_item(prompts_data["prompts"], selected_prompt):
                        save_prompts_to_yaml(prompts_data)
                        st.success("Ausgewähltes Element wurde gelöscht.")
                        st.session_state["selected_prompt"] = None
                        st.experimental_rerun()
                    else:
                        st.error("Fehler beim Löschen des ausgewählten Elements.")
        
    with col2:
        # Suchfunktion
        search_query = st.text_input("Suche nach Prompts")
        if search_query:
            search_results = search_prompts(prompts_data["prompts"], search_query)
            if search_results:
                st.subheader("Suchergebnisse")
                for path, result in search_results:
                     if st.button(f"📄 {path}", key=f"search_result_{path}"):
                        selected_prompt = path
                        st.session_state["selected_prompt"] = selected_prompt
                        st.experimental_rerun()
            else:
                st.info("Keine passenden Prompts gefunden.")

        # Export-Funktion
        st.subheader("Export")
        export_folder = st.text_input("Pfad des Ordners, der exportiert werden soll", placeholder="z.B. Marketing")
        if st.button("Ordner exportieren"):
            if export_folder:
                markdown_content = export_folder_to_markdown(prompts_data["prompts"], export_folder)
                if markdown_content:
                  st.download_button(
                      label="Download Markdown-Datei",
                      data=markdown_content,
                      file_name=f"{export_folder.replace('/', '_')}_prompts.md",
                      mime="text/markdown",
                  )
                else:
                    st.error("Ordner konnte nicht exportiert werden. Bitte überprüfen Sie den Pfad.")
            else:
                 st.warning("Bitte geben Sie einen Ordner an, der exportiert werden soll")

if __name__ == "__main__":
    import os
    os.environ['STREAMLIT_SERVER_ADDRESS'] = "0.0.0.0" # Set host to 0.0.0.0 for codesandbox
    main()