#!/bin/bash

echo "Post wird abgeholt, konvertiert und in Scan-Eingang verschoben"
#cd /home/$USER/PycharmProjects/email-ocr-pdf-merge.py/

# Check if the directory "myenv" exists
if [ ! -d ".myenv" ]; then
  # If it does not exist, create a virtual environment using Python3
  echo "Directory 'myenv' does not exist. Creating a Python virtual environment."
  python -m venv .myenv
  pip install -r requirements.txt
else
  # If it exists, print a message
  echo "Directory 'myenv' already exists. Activating virtual environment."
  
fi



python main2_gui.py
