#!/bin/bash
# Change to your project directory
cd ~/GitHub/Roentgenium

# Activate virtual environment
source .venv_build/bin/activate

# Run your Python GUI
python -m src.roentgenium

# Optional: deactivate venv
deactivate
