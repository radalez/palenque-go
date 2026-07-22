#!/bin/bash
mkdir -p ~/palenque_flow
tar -xzf ~/deploy.tar.gz -C ~/palenque_flow
cd ~/palenque_flow
python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install -r requirements.txt
pip install psycopg2-binary gunicorn
echo "Environment setup complete."
