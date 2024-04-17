#!/bin/sh

# Der Pfad zum aktuellen Script
SCRIPT_PATH="$(dirname "$0")"

# Ausgabe des aktuellen Pfads für Klarheit
# echo "Das Script befindet sich in: $SCRIPT_PATH"

# Wechselt in das Verzeichnis, in dem das Script liegt
cd "$SCRIPT_PATH"

# Prüfen Sie, ob das lokale Repository existiert
if [ ! -d .git ]; then
    echo "Das Verzeichnis ist kein Git-Repository."
    exit 1
fi

# Holt die neuesten Änderungen vom Remote-Repository, ohne sie zu mergen
git fetch

# Überprüft, ob der lokale Branch hinter dem Remote-Branch zurückliegt
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "Das lokale Repository ist auf dem neuesten Stand."
else
    echo "Es gibt eine neuere Version auf GitHub. Die Commit-Nachrichten sind:"
    # Zeigt die Commit-Nachrichten an
    git log $LOCAL..$REMOTE --oneline

    # Fragt den Benutzer, ob er ein Update durchführen möchte
    read -p "Möchten Sie ein Update durchführen? (j/n) " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Jj]$ ]]
    then
        # Führt ein Update durch
        git pull
    fi
fi



# Bestätigung des aktuellen Verzeichnisses nach dem Wechsel
# echo "Aktuelles Verzeichnis: $(pwd)"

# Ermitteln des Betriebssystems
OS="$(uname)"
echo "Das Skript läuft auf: $OS"

# Überprüfen, ob Python installiert ist
command -v python3 &>/dev/null

if [ $? -ne 0 ]; then
    echo "Python3 ist nicht installiert. Öffne Python.org in Ihrem Webbrowser..."
    # Öffnen von Python.org in Ihrem Standard-Webbrowser
    xdg-open https://www.python.org
else
    echo "Python3 ist bereits installiert."
fi


echo "Post wird abgeholt, konvertiert und in Scan-Eingang verschoben"

# Entsprechend dem Betriebssystem unterschiedliche Aktionen durchführen
case "$OS" in
  "Linux") 
    # "Das Skript läuft auf einem Linux-System."

    DESKTOP_FILE_PATH="$HOME/.local/share/applications/Posteingang.desktop"

    if [ ! -f "$DESKTOP_FILE_PATH" ]; then
      echo "Die Datei Posteingang.desktop existiert nicht. Sie wird erstellt..."

      # Erstellen Sie die Datei mit dem angegebenen Inhalt
      echo "[Desktop Entry]
    Type=Application
    Terminal=true
    Name=Posteingang
    Icon=document-send-symbolic
    Exec=/home/max/Nextcloud/Coding/Skripte/Posteingang/Posteingang.sh
    Comment=Mails zu PDF zu Scans
    Categories=Utility;" > "$DESKTOP_FILE_PATH"
    chmod +x "$DESKTOP_FILE_PATH"
    else
      echo "Die Datei Posteingang.desktop existiert bereits."
    fi


    if [ ! -d ".myenv" ]; then
      # If it does not exist, create a virtual environment using Python3
      echo "Directory 'myenv' does not exist. Creating a Python virtual environment."
      python -m venv .myenv
      source .myenv/bin/activate
      pip install -r requirements.txt
      which python

    else
      # If it exists, print a message
      echo "Directory 'myenv' already exists. Activating virtual environment."
      source .myenv/bin/activate
      which python
    fi

    python main.py
    ;;
  "Darwin") 
    # "Das Skript läuft auf einem MacOS-System."
    # Check if the directory "myenv" exists
    if [ ! -d ".myenv" ]; then
      # If it does not exist, create a virtual environment using Python3
      echo "Directory 'myenv' does not exist. Creating a Python virtual environment."
      python3 -m venv .myenv
      source .myenv/bin/activate
      pip install -r requirements.txt
      which python3

    else
      # If it exists, print a message
      echo "Directory 'myenv' already exists. Activating virtual environment."
      source .myenv/bin/activate
      which python
    fi

    python3 main.py
    ;;
  "WindowsNT")
    # "Das Skript läuft auf einem Windows-System."
    if [ ! -d ".myenv" ]; then
      # If it does not exist, create a virtual environment using Python3
      echo "Directory 'myenv' does not exist. Creating a Python virtual environment."
      python3 -m venv .myenv
      source .myenv/bin/activate
      pip install -r requirements.txt
      which python

    else
      # If it exists, print a message
      echo "Directory 'myenv' already exists. Activating virtual environment."
      source .myenv/bin/activate
      which python
    fi

    python main.py
    ;;
  *) 
    echo "Unbekanntes Betriebssystem."
    ;;
esac