#!/bin/bash
sudo cp /home/ubuntu/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

sudo cp /home/ubuntu/nginx.conf /etc/nginx/sites-available/palenque_flow
sudo ln -sf /etc/nginx/sites-available/palenque_flow /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
echo "Web server setup complete."
