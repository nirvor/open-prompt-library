import gradio as gr
import yaml
import os
from utils import load_prompts, save_prompts, export_to_markdown, find_prompt_path

def add_item(data, name, is_folder, parent_path=""):
    """Fügt einen neuen Prompt oder Ordner hinzu."""
    path_list = parent_path.split("/") if parent_path else []
    current_level = data["prompts"]
    for path_item in path_list:
        for item in current_level:
            if item["name"] == path_item:
                current_level = item.get("children", [])
                break
    if is_folder:
        current_level.append({"name": name, "children": []})
    else:
        current_level.append({"name": name, "content": ""})
    save_prompts(data)
    return data

def edit_item(data, new_content, path):
    """Bearbeitet einen vorhandenen Prompt."""
    path_list = path.split("/")
    current_level = data["prompts"]
    for i, path_item in enumerate(path_list):
        for item in current_level:
            if item["name"] == path_item:
                if i == len(path_list) - 1:
                    item["content"] = new_content
                    save_prompts(data)
                    return data
                else:
                    current_level = item.get("children", [])
                    break
    return data

def delete_item(data, path):
    """Löscht einen Prompt oder Ordner."""
    path_list = path.split("/")
    current_level = data["prompts"]
    for i, path_item in enumerate(path_list):
        for j, item in enumerate(current_level):
            if item["name"] == path_item:
                if i == len(path_list) - 1:
                    del current_level[j]
                    save_prompts(data)
                    return data
                else:
                    current_level = item.get("children", [])
                    break
    return data

def manage_prompts_gradio(action, name, is_folder, content, path, selected_folder, search_query):
    """Verwaltet die Prompts (Hinzufügen, Bearbeiten, Löschen, Suchen, Exportieren)."""
    data = load_prompts()

    if action == "add":
        data = add_item(data, name, is_folder, path)
    elif action == "edit":
        data = edit_item(data, content, path)
    elif action == "delete":
        data = delete_item(data, path)

    
    
    markdown_content = ""
    if action == "export" and selected_folder:
      folder_to_export = next((item for item in data["prompts"] if item["name"] == selected_folder), None)
      if folder_to_export:
          markdown_content = export_to_markdown(folder_to_export)

    
    search_result = ""
    if search_query:
        prompt_path = find_prompt_path(data, search_query)
        search_result = prompt_path if prompt_path else "Prompt nicht gefunden."

    # Aktualisierte Komponenten für die Anzeige
    prompts_output = create_prompt_tree_gradio(data.get("prompts", []))

    return prompts_output, markdown_content, search_result

def create_prompt_tree_gradio(prompts, parent_path="", level=0):
    """Erstellt die Baumstruktur der Prompts für die Gradio-Anzeige."""
    components = []
    for i, item in enumerate(prompts):
        path = f"{parent_path}/{item['name']}" if parent_path else item['name']
        if "content" in item:
            # Prompt
            components.append(gr.Markdown(f"{'  ' * level}### {item['name']}"))
            components.append(gr.Textbox(value=item['content'], lines=5, label=f"Inhalt von {item['name']}", interactive=True))
            components.append(gr.Button(f"Bearbeiten: {item['name']}"))
            components.append(gr.Button(f"Löschen: {item['name']}"))
            # components.append(gr.Textbox(label="Pfad", value=path, visible=False)) # Pfad verstecken

        else:
            # Ordner
            components.append(gr.Markdown(f"{'  ' * level}## {item['name']}"))
            components.append(gr.Button(f"Hinzufügen zu: {item['name']}"))
            components.append(gr.Button(f"Löschen: {item['name']}"))
            # components.append(gr.Textbox(label="Pfad", value=path, visible=False)) # Pfad verstecken
            if "children" in item and item["children"]:
                components.extend(create_prompt_tree_gradio(item["children"], path, level + 1))
    return components

# Interface erstellen
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Prompt Library")
    with gr.Row():
      with gr.Column():
        action = gr.Radio(["add", "edit", "delete"], label="Aktion")
        name = gr.Textbox(label="Name")
        is_folder = gr.Checkbox(label="Ordner erstellen")
        content = gr.Textbox(label="Inhalt", placeholder="Nur für Prompts ausfüllen")
        path = gr.Textbox(label="Pfad")
        search_query = gr.Textbox(label="Prompt suchen")
        search_button = gr.Button("Suchen")
      with gr.Column():
        with gr.Tab("Prompts"):
          prompts_output = gr.Column()
        with gr.Tab("Export"):
          selected_folder = gr.Dropdown([item['name'] for item in load_prompts().get("prompts", []) if "children" in item], label="Ordner auswählen")
          export_button = gr.Button("In Markdown exportieren")
          markdown_output = gr.File(label="Markdown herunterladen")
        with gr.Tab("Suche"):
          search_result = gr.Textbox(label="Suchergebnis") # Hinzufügen der search_result-Komponente

    
    search_button.click(
        manage_prompts_gradio,
        inputs=[action, name, is_folder, content, path, selected_folder, search_query],
        outputs=[prompts_output, markdown_output, search_result] # search_result zu outputs hinzufügen
    )

    # ... (Event-Handler für export_button und Initialisierung der Prompts bleiben unverändert) ...

demo.launch(server_name="0.0.0.0", server_port=8080)
