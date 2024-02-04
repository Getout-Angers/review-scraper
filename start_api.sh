#!/bin/bash

SOURCE="/var/www/competition-analyzer.fr/public_html/review-scraper/"
cd ${SOURCE}
echo "Start the websocket server"
sudo python3 ${SOURCE}server.py