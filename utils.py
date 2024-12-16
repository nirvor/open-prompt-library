
import yaml

def load_prompts(filepath="data.yaml"):
    """Lädt Prompts aus einer YAML-Datei."""
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            yaml.dump({"prompts": []}, f)
    with open(filepath, "r") as f:
        return yaml.safe_load(f) or {"prompts": []}

def save_prompts(data, filepath="data.yaml"):
    """Speichert Prompts in einer YAML-Datei."""
    with open(filepath, "w") as f:
        yaml.dump(data, f)

def export_to_markdown(folder, level=0):
    """Exportiert einen Ordner und seine Unterordner in eine Markdown-Zeichenkette."""
    markdown = ""
    indent = "  " * level
    markdown += f"{indent}# {folder['name']}\n"
    for item in folder.get("children", []):
        if "content" in item:
            markdown += f"{indent}- {item['name']}\n"
            markdown += f"{indent}  ```\n{indent}  {item['content']}\n{indent}  ```\n"
        else:
            markdown += export_to_markdown(item, level + 1)
    return markdown

def find_prompt_path(data, query, path=None):
    """Sucht nach einem Prompt und gibt den Pfad zurück."""
    if path is None:
        path = []
    for i, item in enumerate(data.get("prompts", [])):
        current_path = path + [item["name"]]
        if query.lower() in item["name"].lower():
            return " -> ".join(current_path)
        if "content" in item and query.lower() in item["content"].lower():
            return " -> ".join(current_path)
        if "children" in item:
            result = find_prompt_path({"prompts": item["children"]}, query, current_path)
            if result:
                return result
    return None
