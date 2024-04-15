#!/bin/bash

# Der Pfad zum aktuellen Script
SCRIPT_PATH="$(dirname "$0")"

# Ausgabe des aktuellen Pfads für Klarheit
echo "Das Script befindet sich in: $SCRIPT_PATH"

# Wechselt in das Verzeichnis, in dem das Script liegt
cd "$SCRIPT_PATH"

# Bestätigung des aktuellen Verzeichnisses nach dem Wechsel
echo "Aktuelles Verzeichnis: $(pwd)"

echo "Post wird abgeholt, konvertiert und in Scan-Eingang verschoben"
#cd /home/$USER/PycharmProjects/email-ocr-pdf-merge.py/

# Check if the directory "myenv" exists
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
