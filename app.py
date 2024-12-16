import streamlit as st
import yaml
import os
from utils import load_prompts, save_prompts, export_to_markdown, find_prompt_path
import pyperclip

def manage_prompts(prompts, path=None):
    if path is None:
        path = []

    if not prompts:
        st.sidebar.info("Keine Prompts vorhanden. Bitte erstellen Sie einen neuen Prompt oder Ordner.")

    for i, item in enumerate(prompts):
        item_path = path + [i]
        if "content" in item:
            # Prompt anzeigen
            st.sidebar.markdown(f"### {item['name']}")
            if st.sidebar.button(f"Kopieren", key=f"copy-{'-'.join(map(str, item_path))}"):
                pyperclip.copy(item["content"])
                st.sidebar.success("Prompt kopiert!")
            if st.sidebar.button(f"Bearbeiten", key=f"edit-{'-'.join(map(str, item_path))}"):
                new_content = st.sidebar.text_area("Inhalt", item["content"], key=f"edit-content-{'-'.join(map(str, item_path))}")
                if st.sidebar.button("Speichern", key=f"save-{'-'.join(map(str, item_path))}"):
                    item["content"] = new_content
                    save_prompts(data)
                    st.experimental_rerun()
            if st.sidebar.button(f"Löschen", key=f"delete-{'-'.join(map(str, item_path))}"):
                del prompts[i]
                save_prompts(data)
                st.experimental_rerun()
        else:
            # Ordner anzeigen
            st.sidebar.markdown(f"## {item['name']}")
            if st.sidebar.button(f"Unterordner/Prompt hinzufügen", key=f"add-sub-{'-'.join(map(str, item_path))}"):
                new_name = st.sidebar.text_input("Name", key=f"new-name-{'-'.join(map(str, item_path))}")
                is_folder = st.sidebar.checkbox("Ordner erstellen", key=f"is-folder-{'-'.join(map(str, item_path))}")
                if st.sidebar.button("Hinzufügen", key=f"add-confirm-{'-'.join(map(str, item_path))}"):
                    if is_folder:
                        item.setdefault("children", []).append({"name": new_name, "children": []})
                    else:
                        item.setdefault("children", []).append({"name": new_name, "content": ""})
                    save_prompts(data)
                    st.experimental_rerun()
            if st.sidebar.button(f"Löschen", key=f"delete-folder-{'-'.join(map(str, item_path))}"):
                del prompts[i]
                save_prompts(data)
                st.experimental_rerun()
            manage_prompts(item.get("children", []), item_path + ["children"])

# Laden der Prompts aus der YAML-Datei
data = load_prompts()

# Seitentitel
st.title("Prompt Library")

# Suchleiste
search_query = st.sidebar.text_input("Prompt suchen")
if search_query:
    prompt_path = find_prompt_path(data, search_query)
    if prompt_path:
        st.sidebar.success(f"Prompt gefunden unter: {prompt_path}")
    else:
        st.sidebar.error("Prompt nicht gefunden.")

# Neue Prompts oder Ordner auf oberster Ebene hinzufügen
if st.sidebar.button("Neuen Prompt/Ordner hinzufügen"):
    new_name = st.sidebar.text_input("Name")
    is_folder = st.sidebar.checkbox("Ordner erstellen")
    if st.sidebar.button("Hinzufügen"):
        if is_folder:
            data.setdefault("prompts", []).append({"name": new_name, "children": []})
        else:
            data.setdefault("prompts", []).append({"name": new_name, "content": ""})
        save_prompts(data)
        st.experimental_rerun()

# Exportfunktion
selected_folder = st.sidebar.selectbox("Ordner zum Exportieren auswählen", [item['name'] for item in data.get("prompts", []) if "children" in item])
if st.sidebar.button("In Markdown exportieren"):
    folder_to_export = next((item for item in data["prompts"] if item["name"] == selected_folder), None)
    if folder_to_export:
        markdown_content = export_to_markdown(folder_to_export)
        st.sidebar.download_button(
            label="Markdown herunterladen",
            data=markdown_content,
            file_name=f"{selected_folder}.md",
            mime="text/markdown"
        )

# Anzeigen und Verwalten der Prompts
manage_prompts(data.get("prompts", []))