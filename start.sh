#!/bin/bash

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Activate existing venv
    source venv/bin/activate
fi

# Start the Python script
# Running it directly in the current terminal session
python src/EdgeNode.py