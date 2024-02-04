#!/bin/bash

SOURCE="/var/www/competition-analyzer.fr/public_html/api/"
echo "Start the websocket server"
sudo python3 ${SOURCE}server.py