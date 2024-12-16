# Prompt Library App

Eine minimalistische App zur Verwaltung von Prompt-Bibliotheken.

## Installation

1. Klone das Repository:
    ```bash
    git clone <repository_url>
    cd prompt_library_app
    ```
2. Installiere die benötigten Pakete:
    ```bash
    pip install -r requirements.txt
    ```

## Verwendung

1. Starte die App:
    ```bash
    streamlit run app.py
    ```
2. Öffne die App in deinem Browser (die URL wird in der Konsole angezeigt).

## Deployment auf Replit

1. Erstelle ein neues Repl auf Replit.
2. Lade die Dateien aus dem Repository in das Repl hoch.
3. Installiere die benötigten Pakete in der Replit-Konsole:
    ```bash
    pip install -r requirements.txt
    ```
4. Führe die App aus:
    ```bash
    streamlit run app.py
    ```
5. Die App ist nun über die Replit-URL erreichbar.

## Deployment auf PythonAnywhere

1. Erstelle ein neues Konto auf PythonAnywhere.
2. Lade die Dateien aus dem Repository in dein PythonAnywhere-Konto hoch (z.B. über die "Files"-Seite).
3. Öffne eine Bash-Konsole und installiere die benötigten Pakete:
    ```bash
    pip install --user -r requirements.txt
    ```
4. Erstelle eine neue Web-App und wähle "Manual configuration" und die Python-Version, die du verwenden möchtest.
5. Gib den Pfad zu deinem Projektverzeichnis als "Source code" an (z.B. `/home/<username>/prompt_library_app`).
6. Gib den Pfad zu deinem virtuellen Environment an, falls du eines verwendest (z.B. `/home/<username>/.virtualenvs/<myenv>`).
7. Bearbeite die WSGI-Konfigurationsdatei (z.B. `/var/www/<username>_pythonanywhere_com_wsgi.py`) und füge den folgenden Code hinzu:

    ```python
    import sys
    path = '/home/<username>/prompt_library_app'
    if path not in sys.path:
        sys.path.append(path)

    from app import app as application
    ```

8. Lade die Web-App neu und sie sollte nun über die PythonAnywhere-URL erreichbar sein.