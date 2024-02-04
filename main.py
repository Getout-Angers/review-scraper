from src import Gmaps
from src import scraper
from src import reviews_scraper
import time

start_time = time.time()
#scraped_places = Gmaps.places(queries, max=1, scrape_reviews=True, use_cache=False, reviews_sort=Gmaps.NEWEST, reviews_max=10, lang="French")
#reviews_scrapped = scraped_places[0]["places"][0]
#print(reviews_scrapped)

place_data = {'query': 'Get Out Angers - Escape Game et Expériences Immersives 🔒 | Bar à Jeux 🎲', 'is_spending_on_ads': False, 'max': 1, 'lang': 'fr', 'geo_coordinates': None, 'zoom': None, 'convert_to_english': True}
places_obj = scraper.scrape_places(place_data, cache=False)
print(places_obj)
print('--- %s seconds ---' % (time.time() - start_time))
with reviews_scraper.GoogleMapsAPIScraper() as r_scraper:
   '''result = r_scraper.scrape_reviews(
      url=places_obj["places"][0]["link"], n_reviews=5, hl="French", sort_by=Gmaps.NEWEST
   )'''
   result = r_scraper.scrape_reviews_by_date(
       url=places_obj["places"][0]["link"], date_reviews="il y a un mois", hl="fr", sort_by=Gmaps.NEWEST
   )
processed = scraper.process_reviews(result, False)
print(len(processed))
print(processed[0])
print("--- %s seconds ---" % (time.time() - start_time))
