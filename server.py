import os
import requests
import mysql.connector as mysql
from websocket_server import WebsocketServer
import json
from dotenv import load_dotenv
import time
import hashlib
import logging
from src import Gmaps
from src import scraper
from src import reviews_scraper

load_dotenv()
HOST = os.environ["MYSQL_HOST"]
DATABASE = os.environ["MYSQL_DB"]
USER = os.environ["MYSQL_USER"]
PASSWORD = os.environ["MYSQL_PASSWD"]


def get_session_id(user_id):
    time_stamp = str(time.time())
    str2hash = time_stamp + user_id
    return hashlib.md5(str2hash.encode()).hexdigest()


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    server.send_message(client, "Successfully connected")


# Called when a client sends a message
def message_received(client, server, message):
    print("Client(%d) search:\n%s" % (client['id'], message))
    if is_json(message):
        res = json.loads(message)
        if res['action'] == 'get_review':
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
            cur_insert = db_connection.cursor(buffered=True)
            session_id = get_session_id(res['user_id'])
            response = {
                "result": {
                    "user_id": res['user_id'],
                    "session_id": session_id,
                    "nb_review": 0
                },
                "status": "OK",
            }
            place_data = {'query': 'Get Out Angers - Escape Game et Expériences Immersives 🔒 | Bar à Jeux 🎲',
                          'is_spending_on_ads': False, 'max': 1, 'lang': 'fr', 'geo_coordinates': None,
                          'zoom': None, 'convert_to_english': True}
            places_obj = scraper.scrape_places(place_data, cache=True, "test")
            server.send_message(client, "step_3")
            with reviews_scraper.GoogleMapsAPIScraper() as r_scraper:
                if (res['option']['select_by'] == 'date'):
                    result = r_scraper.scrape_reviews_by_date(
                        url=places_obj["places"][0]["link"], date_reviews=res['option']['select_value'], hl="fr",
                        sort_by=Gmaps.NEWEST
                    )
                else:
                    result = r_scraper.scrape_reviews(
                        url=places_obj["places"][0]["link"], n_reviews=res['option']['select_value'], hl="French", sort_by=Gmaps.NEWEST
                    )
            reviews = scraper.process_reviews(result, False)
            insert_review = (
                "INSERT INTO review (user_id, session_id, author_name, rating, relative_time_description, text) "
                "VALUES (%s, %s, %s, %s, %s, %s)")
            i = 0
            server.send_message(client, "step_6")
            for review in reviews:
                cur_insert.execute(insert_review, (
                    res['user_id'], session_id, review['review_author'], review['rating'],
                    review['published_at'], review['review_text']))
                i += 1
            response['result']['nb_review'] = i
            db_connection.commit()
            server.send_message(client, json.dumps(response))
            db_connection.close()


PORT = 5000
# IP = requests.get("https://ident.me").text
IP = "217.160.10.62"
ws_server = WebsocketServer(host=IP, port=PORT, loglevel=logging.INFO, key="/etc/certificate/_.competition-analyzer.fr_private_key.key", cert="/etc/certificate/competition-analyzer.fr_ssl_certificate.cer")
ws_server.set_fn_new_client(new_client)
ws_server.set_fn_message_received(message_received)
ws_server.run_forever()
