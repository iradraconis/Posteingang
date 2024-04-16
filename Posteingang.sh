#!/bin/sh

# Der Pfad zum aktuellen Script
SCRIPT_PATH="$(dirname "$0")"

# Ausgabe des aktuellen Pfads für Klarheit
echo "Das Script befindet sich in: $SCRIPT_PATH"

# Wechselt in das Verzeichnis, in dem das Script liegt
cd "$SCRIPT_PATH"

# Bestätigung des aktuellen Verzeichnisses nach dem Wechsel
echo "Aktuelles Verzeichnis: $(pwd)"

# Ermitteln des Betriebssystems
OS="$(uname)"
echo "Das Skript läuft auf: $OS"

echo "Post wird abgeholt, konvertiert und in Scan-Eingang verschoben"

# Entsprechend dem Betriebssystem unterschiedliche Aktionen durchführen
case "$OS" in
  "Linux") 
    # "Das Skript läuft auf einem Linux-System."

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

    python main2_gui.py
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

    python3 main2_gui.py
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

    python main2_gui.py
    ;;
  *) 
    echo "Unbekanntes Betriebssystem."
    ;;
esac