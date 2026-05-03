#!/bin/bash
echo "Setting up Workshop 2 environment..."
pip install -r requirements.txt
jupyter nbextension enable --py widgetsnbextension --sys-prefix
python data/generate_dataset.py
echo "Done. Run: jupyter lab notebooks/"
